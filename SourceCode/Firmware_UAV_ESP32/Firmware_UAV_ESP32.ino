#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ArduinoJson.h>        // ArduinoJson v7
#include <esp_task_wdt.h>

// ---------------- CẤU HÌNH PHẦN CỨNG ----------------

// I2C số 0 (BME280 Unshielded)
#define I2C0_SDA 21
#define I2C0_SCL 22

// I2C số 1 (BME280 Shielded - Pagoda)
#define I2C1_SDA 18
#define I2C1_SCL 19

// UART2 (LoRa E32)
#define LORA_RX_PIN 16
#define LORA_TX_PIN 17

// Đo pin LiPo (ADC1 - GPIO34)
#define BATTERY_PIN 34
const float R1 = 100000.0;      // Ω: từ cực + pin xuống chân ADC
const float R2 = 33000.0;       // Ω: từ chân ADC xuống GND
                                // LƯU Ý: pin 3S đầy 12.6V -> ~3.13V tại ADC, sát ngưỡng bão hòa.
                                // Nên đổi R2 = 27k (hệ số 4.7) hoặc 22k (hệ số 5.5) cho an toàn.
const int   BAT_CELLS = 3;      // 3S LiPo
const float BAT_CAL   = 1.0;    // hệ số hiệu chuẩn: V_đồng_hồ / V_đọc_được
const int   BAT_SAMPLES = 16;
const float BAT_PRESENT_MIN_V = 6.0;  // dưới mức này coi như chưa gắn pin (3S rỗng ~9.9V)

// ---------------- CẤU HÌNH HỆ THỐNG ----------------
#define WDT_TIMEOUT 15                 // Watchdog (giây)
unsigned long readInterval = 5000;     // Chu kỳ đọc/gửi mặc định (ms)
unsigned long lastReadTime = 0;
uint32_t seqNo = 0;

// Bộ đệm nhận lệnh (không chặn)
#define CMD_BUF_SIZE 32
char cmdBuf[CMD_BUF_SIZE];
uint8_t cmdLen = 0;

// Cảm biến
Adafruit_BME280 bme_unshielded;
Adafruit_BME280 bme_shielded;
bool bme1_ok = false;
bool bme2_ok = false;

// Khai báo trước
void sendSensorData();
void checkIncomingCommands();
void executeCommand(char *cmd);
void sendAck(const char *what);
float round2(float value);
bool initBME(Adafruit_BME280 &bme, TwoWire &bus);
bool readBME(Adafruit_BME280 &bme, bool &okFlag, float &t, float &h, float &p);
float readBatteryVoltage();
int batteryPercent(float vPack);

void setup() {
  Serial.begin(115200);
  Serial.println("Dang khoi dong Tram UAV...");

  // LoRa E32 (9600)
  Serial2.begin(9600, SERIAL_8N1, LORA_RX_PIN, LORA_TX_PIN);

  // ADC pin
  analogSetPinAttenuation(BATTERY_PIN, ADC_11db);
  pinMode(BATTERY_PIN, INPUT);

  // Watchdog (ESP32 Core 3.x)
  esp_task_wdt_config_t wdt_config = {
    .timeout_ms = WDT_TIMEOUT * 1000,
    .idle_core_mask = 0,
    .trigger_panic = true
  };
  esp_task_wdt_deinit();
  esp_task_wdt_init(&wdt_config);
  esp_task_wdt_add(NULL);

  // Dual I2C
  Wire.begin(I2C0_SDA, I2C0_SCL);
  Wire.setTimeOut(50);
  Wire1.begin(I2C1_SDA, I2C1_SCL);
  Wire1.setTimeOut(50);

  bme1_ok = initBME(bme_unshielded, Wire);
  esp_task_wdt_reset();
  bme2_ok = initBME(bme_shielded, Wire1);
  Serial.println(bme1_ok ? "BME280 Unshielded OK." : "Loi: Khong tim thay BME280 Unshielded!");
  Serial.println(bme2_ok ? "BME280 Shielded OK."   : "Loi: Khong tim thay BME280 Shielded!");
}

void loop() {
  esp_task_wdt_reset();

  checkIncomingCommands();

  if (millis() - lastReadTime >= readInterval) {
    lastReadTime = millis();
    sendSensorData();
  }
}

// ---------------- CẢM BIẾN ----------------
bool initBME(Adafruit_BME280 &bme, TwoWire &bus) {
  return bme.begin(0x76, &bus) || bme.begin(0x77, &bus);
}

// Trả về true nếu đọc hợp lệ; nếu không, đánh dấu lỗi để thử init lại ở chu kỳ sau
bool readBME(Adafruit_BME280 &bme, bool &okFlag, float &t, float &h, float &p) {
  t = h = p = NAN;
  if (!okFlag) return false;
  float tt = bme.readTemperature();
  float hh = bme.readHumidity();
  float pp = bme.readPressure() / 100.0F;
  if (isnan(tt) || isnan(hh) || isnan(pp) || pp < 300.0F || pp > 1100.0F) {
    okFlag = false;
    return false;
  }
  t = tt; h = hh; p = pp;
  return true;
}

// ---------------- PIN LiPo (3S) ----------------
float readBatteryVoltage() {
  uint32_t sum = 0;
  for (int i = 0; i < BAT_SAMPLES; i++) {
    sum += analogReadMilliVolts(BATTERY_PIN);   // đã hiệu chuẩn eFuse, chính xác hơn analogRead
    delayMicroseconds(200);
  }
  float vAdc = ((float)sum / BAT_SAMPLES) / 1000.0F;
  return vAdc * ((R1 + R2) / R2) * BAT_CAL;
}

// Đường xả LiPo theo từng cell, nội suy tuyến tính, rồi lấy điện áp pack / số cell
int batteryPercent(float vPack) {
  static const float volt[] = {3.30, 3.50, 3.60, 3.70, 3.75, 3.80, 3.90, 4.00, 4.10, 4.20};
  static const int   pct[]  = {   0,    5,   10,   20,   35,   50,   65,   80,   92,  100};
  const int n = sizeof(volt) / sizeof(volt[0]);
  float v = vPack / BAT_CELLS;
  if (v <= volt[0]) return 0;
  if (v >= volt[n - 1]) return 100;
  for (int i = 1; i < n; i++) {
    if (v <= volt[i]) {
      float r = (v - volt[i - 1]) / (volt[i] - volt[i - 1]);
      return (int)(pct[i - 1] + r * (pct[i] - pct[i - 1]) + 0.5F);
    }
  }
  return 0;
}

// ---------------- ĐỌC VÀ GỬI DỮ LIỆU LORA ----------------
void sendSensorData() {
  // Thử cứu cảm biến nếu đang lỗi
  if (!bme1_ok) bme1_ok = initBME(bme_unshielded, Wire);
  if (!bme2_ok) bme2_ok = initBME(bme_shielded, Wire1);

  float t1, h1, p1, t2, h2, p2;
  readBME(bme_unshielded, bme1_ok, t1, h1, p1);
  readBME(bme_shielded,   bme2_ok, t2, h2, p2);

  float vBattery = readBatteryVoltage();
  int batPercent = batteryPercent(vBattery);

  // Đóng gói JSON: cảm biến lỗi -> null (Streamlit nhận biết được)
  JsonDocument doc;
  doc["seq"] = seqNo++;
  if (isnan(t1)) doc["t1"] = nullptr; else doc["t1"] = round2(t1);
  if (isnan(h1)) doc["h1"] = nullptr; else doc["h1"] = round2(h1);
  if (isnan(p1)) doc["p1"] = nullptr; else doc["p1"] = round2(p1);
  if (isnan(t2)) doc["t2"] = nullptr; else doc["t2"] = round2(t2);
  if (isnan(h2)) doc["h2"] = nullptr; else doc["h2"] = round2(h2);
  if (isnan(p2)) doc["p2"] = nullptr; else doc["p2"] = round2(p2);
  // Không có pin (đang cấp nguồn bằng USB): điện áp pack thấp hơn ngưỡng tối thiểu
  // -> gửi bat/vbat = null và pwr = "usb" để không báo pin cạn giả.
  if (vBattery < BAT_PRESENT_MIN_V) {
    doc["bat"] = nullptr;
    doc["vbat"] = nullptr;
    doc["pwr"] = "usb";
  } else {
    doc["bat"] = batPercent;
    doc["vbat"] = round2(vBattery);
    doc["pwr"] = "bat";
  }

  String payload;
  serializeJson(doc, payload);

  Serial2.println(payload);               // phát qua LoRa
  Serial.print("UAV TX: ");
  Serial.println(payload);
}

// ---------------- NHẬN LỆNH ĐIỀU KHIỂN (không chặn) ----------------
// Chấp nhận cả hai dạng:  "<SPEED_1S>"  (kết thúc bằng '>')
//                          "SPEED_1S\n" (kết thúc bằng xuống dòng)
void checkIncomingCommands() {
  while (Serial2.available()) {
    char c = (char)Serial2.read();
    if (c == '<') {                        // bắt đầu khung mới
      cmdLen = 0;
    } else if (c == '>' || c == '\n') {    // kết thúc lệnh
      if (cmdLen > 0) {
        cmdBuf[cmdLen] = '\0';
        executeCommand(cmdBuf);
      }
      cmdLen = 0;
    } else if (c != '\r') {
      if (cmdLen < CMD_BUF_SIZE - 1) cmdBuf[cmdLen++] = toupper(c);
      else cmdLen = 0;                     // tràn bộ đệm -> bỏ
    }
  }
}

void executeCommand(char *cmd) {
  Serial.print("Nhan lenh tu mat dat: ");
  Serial.println(cmd);

  if (strcmp(cmd, "SPEED_1S") == 0) {
    readInterval = 1000;
    sendAck("SPEED_1S");
  } else if (strcmp(cmd, "SPEED_5S") == 0) {
    readInterval = 5000;
    sendAck("SPEED_5S");
  } else if (strncmp(cmd, "SET_FREQ:", 9) == 0) {
    long n = atol(cmd + 9);                // chu kỳ tính bằng giây
    if (n >= 1 && n <= 60) {
      readInterval = (unsigned long)n * 1000UL;
      sendAck("SET_FREQ");
    } else {
      sendAck("SET_FREQ_INVALID");
    }
  } else if (strcmp(cmd, "PING") == 0) {
    sendAck("PING");
  } else if (strcmp(cmd, "RESET_UAV") == 0 || strcmp(cmd, "FORCE_RESET") == 0) {
    sendAck("RESET");
    Serial2.flush();
    delay(300);
    ESP.restart();
  } else {
    sendAck("UNKNOWN_CMD");
  }
}

void sendAck(const char *what) {
  char buf[64];
  snprintf(buf, sizeof(buf), "{\"src\":\"uav\",\"ack\":\"%s\"}", what);
  Serial2.println(buf);
  Serial.println(buf);
}

float round2(float value) {
  if (isnan(value)) return NAN;
  return roundf(value * 100.0F) / 100.0F;
}
