#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_BMP280.h>   // dùng khi module thực chất là BMP280
#include <ArduinoJson.h>        // ArduinoJson v7

// ---------------- CẤU HÌNH CHÂN PHẦN CỨNG (ESP8266) ----------------

// I2C cho BME280 số 3 (Ground Reference): D5 (GPIO14) = SCL, D6 (GPIO12) = SDA
#define I2C_SCL D6
#define I2C_SDA D5

// SoftwareSerial cho LoRa E32
// D2 (GPIO4) <- TXD của LoRa (Soft RX) ; D1 (GPIO5) -> RXD của LoRa (Soft TX)
#define LORA_RX D2
#define LORA_TX D1

SoftwareSerial loraSerial(LORA_RX, LORA_TX);
// ---------------- CẢM BIẾN MÔI TRƯỜNG: tự nhận BME280 / BMP280 ----------------
// Đọc mã chip (thanh ghi 0xD0): 0x60 = BME280 (có độ ẩm), 0x56/0x57/0x58 = BMP280 (KHÔNG có độ ẩm -> h = NAN).
// Khai báo trước mọi hàm của sketch (Arduino tự sinh prototype hàm lên đầu file).
class EnvSensor {
 public:
  enum Type : uint8_t { NONE = 0, BME = 1, BMP = 2 };

  explicit EnvSensor(TwoWire &bus) : _bus(&bus), _bmp(&bus) {}

  bool ok() const { return _type != NONE; }
  bool hasHumidity() const { return _type == BME; }
  const char *name() const { return _type == BME ? "BME280" : (_type == BMP ? "BMP280 (khong co do am)" : "KHONG THAY"); }

  bool begin() {
    _type = NONE;
    const uint8_t addrs[2] = {0x76, 0x77};
    for (uint8_t i = 0; i < 2; i++) {
      uint8_t a = addrs[i];
      uint8_t id = chipId(a);
      if (id == 0x60) {
        if (_bme.begin(a, _bus)) {
          _bme.setSampling(Adafruit_BME280::MODE_NORMAL, Adafruit_BME280::SAMPLING_X2,
                           Adafruit_BME280::SAMPLING_X16, Adafruit_BME280::SAMPLING_X2,
                           Adafruit_BME280::FILTER_X4, Adafruit_BME280::STANDBY_MS_500);
          _type = BME;
          return true;
        }
      } else if (id == 0x56 || id == 0x57 || id == 0x58) {
        if (_bmp.begin(a, id)) {
          _bmp.setSampling(Adafruit_BMP280::MODE_NORMAL, Adafruit_BMP280::SAMPLING_X2,
                           Adafruit_BMP280::SAMPLING_X16, Adafruit_BMP280::FILTER_X4,
                           Adafruit_BMP280::STANDBY_MS_500);
          _type = BMP;
          return true;
        }
      }
    }
    return false;
  }

  // t: °C, h: % (NAN nếu BMP280), p: hPa. Trả về false nếu đọc lỗi (tự về NONE để begin() lại ở chu kỳ sau).
  bool read(float &t, float &h, float &p) {
    t = h = p = NAN;
    if (_type == NONE) return false;
    float tt, hh = NAN, pp;
    if (_type == BME) {
      tt = _bme.readTemperature();
      hh = _bme.readHumidity();
      pp = _bme.readPressure() / 100.0F;
    } else {
      tt = _bmp.readTemperature();
      pp = _bmp.readPressure() / 100.0F;
    }
    bool bad = isnan(tt) || isnan(pp) || pp < 300.0F || pp > 1100.0F || (_type == BME && isnan(hh));
    if (bad) { _type = NONE; return false; }
    t = tt; h = hh; p = pp;
    return true;
  }

 private:
  uint8_t chipId(uint8_t a) {
    _bus->beginTransmission(a);
    _bus->write(0xD0);
    if (_bus->endTransmission(false) != 0) return 0;
    if (_bus->requestFrom((int)a, 1) != 1) return 0;
    return (uint8_t)_bus->read();
  }

  TwoWire *_bus;
  Adafruit_BME280 _bme;
  Adafruit_BMP280 _bmp;
  Type _type = NONE;
};

EnvSensor bme_ground(Wire);

// ---------------- CẤU HÌNH TIMEOUT / HEARTBEAT ----------------
const unsigned long TIMEOUT_MS = 12000;        // Quá 12 s không nhận được gì từ UAV -> Offline
const unsigned long OFFLINE_REPORT_MS = 5000;  // Khi Offline, báo lên PC mỗi 5 s
unsigned long lastLoraReceived = 0;
unsigned long lastOfflineReport = 0;

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

// Đọc cảm biến mặt đất; lỗi -> NAN (thành null trong JSON, không phải số 0 giả). BMP280: h = NAN.
void readGround(float &t, float &h, float &p) {
  if (!bme_ground.ok()) bme_ground.begin();   // thử cứu lại nếu đang lỗi
  if (!bme_ground.read(t, h, p)) { t = h = p = NAN; return; }
  t = round2(t); h = round2(h); p = round2(p);
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
  bme_ground.begin();

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
//void forwardCommandToUAV() {
//  if (Serial.available()) {
//    String cmd = Serial.readStringUntil('\n');
//    cmd.trim();
//    if (cmd.length() > 0) {
      // VD: SPEED_1S, SPEED_5S, RESET_UAV, SET_FREQ:3, PING (có hoặc không có < >)
//      loraSerial.println(cmd);
//    }
//  }
//}

void forwardCommandToUAV() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.length() == 0) {
      return;
    }

    

    loraSerial.println(cmd);
    loraSerial.flush();

    
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
