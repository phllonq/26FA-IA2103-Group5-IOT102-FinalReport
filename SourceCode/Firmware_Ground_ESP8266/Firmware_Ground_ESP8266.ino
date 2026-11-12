#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ArduinoJson.h>        // ArduinoJson v7

// ---------------- CẤU HÌNH CHÂN PHẦN CỨNG (ESP8266) ----------------

// I2C cho BME280 số 3 (Ground Reference): D5 (GPIO14) = SCL, D6 (GPIO12) = SDA
#define I2C_SCL D5
#define I2C_SDA D6

// SoftwareSerial cho LoRa E32
// D2 (GPIO4) <- TXD của LoRa (Soft RX) ; D1 (GPIO5) -> RXD của LoRa (Soft TX)
#define LORA_RX D2
#define LORA_TX D1

SoftwareSerial loraSerial(LORA_RX, LORA_TX);
Adafruit_BME280 bme_ground;

// ---------------- CẤU HÌNH TIMEOUT / HEARTBEAT ----------------
const unsigned long TIMEOUT_MS = 12000;        // Quá 12 s không nhận được gì từ UAV -> Offline
const unsigned long OFFLINE_REPORT_MS = 5000;  // Khi Offline, báo lên PC mỗi 5 s
unsigned long lastLoraReceived = 0;
unsigned long lastOfflineReport = 0;
bool bmeGroundOK = false;

// Bộ đệm nhận dòng từ LoRa (không chặn)
#define LORA_LINE_MAX 400
String loraLine;
bool loraOverflow = false;

// Các trường dữ liệu UAV được chuyển tiếp lên PC (thiếu trường nào -> null)
const char *UAV_KEYS[] = {"seq", "t1", "h1", "p1", "t2", "h2", "p2", "bat", "vbat", "pwr"};
const int UAV_KEYS_N = sizeof(UAV_KEYS) / sizeof(UAV_KEYS[0]);

// ---------------- TIỆN ÍCH ----------------
float round2(float value) {
  if (isnan(value)) return NAN;
  return roundf(value * 100.0F) / 100.0F;
}

bool initGround() {
  return bme_ground.begin(0x76, &Wire) || bme_ground.begin(0x77, &Wire);
}

// Đọc BME280 mặt đất; lỗi -> NAN (sẽ thành null trong JSON, không phải số 0 giả)
void readGround(float &t, float &h, float &p) {
  t = h = p = NAN;
  if (!bmeGroundOK) bmeGroundOK = initGround();   // thử cứu lại nếu đang lỗi
  if (!bmeGroundOK) return;

  float tt = bme_ground.readTemperature();
  float hh = bme_ground.readHumidity();
  float pp = bme_ground.readPressure() / 100.0F;
  if (isnan(tt) || isnan(hh) || isnan(pp) || pp < 300.0F || pp > 1100.0F) {
    bmeGroundOK = false;
    return;
  }
  t = round2(tt); h = round2(hh); p = round2(pp);
}

void setGround(JsonDocument &doc) {
  float t3, h3, p3;
  readGround(t3, h3, p3);
  if (isnan(t3)) doc["t3"] = nullptr; else doc["t3"] = t3;
  if (isnan(h3)) doc["h3"] = nullptr; else doc["h3"] = h3;
  if (isnan(p3)) doc["p3"] = nullptr; else doc["p3"] = p3;
}

// ---------------- SETUP / LOOP ----------------
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);
  delay(200);

  // Buffer nhận 256 byte (mặc định 64) để không rớt byte khi loop bận
  loraSerial.begin(9600, SWSERIAL_8N1, LORA_RX, LORA_TX, false, 256);

  Wire.begin(I2C_SDA, I2C_SCL);
  bmeGroundOK = initGround();

  lastLoraReceived = millis();
}

void loop() {
  receiveFromUAV();
  forwardCommandToUAV();
  checkConnectionTimeout();
}

// ---------------- NHẬN DỮ LIỆU TỪ UAV & GỘP DỮ LIỆU MẶT ĐẤT ----------------
void handleUavLine(const String &line) {
  JsonDocument uavDoc;
  DeserializationError error = deserializeJson(uavDoc, line);
  if (error) return;                       // gói nhiễu, bỏ qua

  lastLoraReceived = millis();             // UAV còn sống (cả data lẫn ack)

  JsonDocument outDoc;

  // Phản hồi lệnh từ UAV -> báo riêng, KHÔNG tạo dòng dữ liệu rỗng cho database
  if (uavDoc["ack"].is<const char *>()) {
    outDoc["status"] = "ack";
    outDoc["ack"] = uavDoc["ack"];
    serializeJson(outDoc, Serial);
    Serial.println();
    return;
  }

  // Gói dữ liệu: gộp UAV + mặt đất
  outDoc["status"] = "online";
  for (int i = 0; i < UAV_KEYS_N; i++) {
    outDoc[UAV_KEYS[i]] = uavDoc[UAV_KEYS[i]];   // thiếu / null -> null
  }
  setGround(outDoc);

  serializeJson(outDoc, Serial);           // đúng 1 dòng JSON thuần qua USB
  Serial.println();
}

void receiveFromUAV() {
  while (loraSerial.available()) {
    char c = (char)loraSerial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      if (!loraOverflow && loraLine.length() > 0) {
        handleUavLine(loraLine);
      }
      loraLine = "";
      loraOverflow = false;
    } else if (loraLine.length() < LORA_LINE_MAX) {
      loraLine += c;
    } else {
      loraOverflow = true;                 // dòng quá dài -> bỏ cả dòng
    }
  }
}

// ---------------- CHUYỂN TIẾP LỆNH TỪ PC LÊN UAV (2 CHIỀU) ----------------
void forwardCommandToUAV() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) {
      // VD: SPEED_1S, SPEED_5S, RESET_UAV, SET_FREQ:3, PING (có hoặc không có < >)
      loraSerial.println(cmd);
    }
  }
}

// ---------------- CẢNH BÁO MẤT KẾT NỐI (HEARTBEAT TIMEOUT) ----------------
void checkConnectionTimeout() {
  unsigned long now = millis();
  if (now - lastLoraReceived > TIMEOUT_MS) {
    if (now - lastOfflineReport >= OFFLINE_REPORT_MS) {
      lastOfflineReport = now;

      JsonDocument alertDoc;
      alertDoc["status"] = "offline";
      setGround(alertDoc);

      serializeJson(alertDoc, Serial);
      Serial.println();
    }
  }
}
