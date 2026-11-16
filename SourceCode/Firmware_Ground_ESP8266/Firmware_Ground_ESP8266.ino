
#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>

// ============================================================
// 1. CAU HINH CHAN ESP8266 NODEMCU
// ============================================================

// BMP280/BME280 Ground Reference:
// D5 (GPIO14) = SDA
// D6 (GPIO12) = SCL
#define I2C_SDA D5
#define I2C_SCL D6

// LoRa E32:
// D2 (GPIO4) = RX cua ESP8266 <- TXD LoRa
// D1 (GPIO5) = TX cua ESP8266 -> RXD LoRa
#define LORA_RX D2
#define LORA_TX D1

SoftwareSerial loraSerial(LORA_RX, LORA_TX);

// ============================================================
// 2. CAM BIEN BME280 / BMP280 TU NHAN DIEN
// ============================================================

class EnvSensor {
public:
  enum Type : uint8_t {
    NONE = 0,
    BME = 1,
    BMP = 2
  };

  explicit EnvSensor(TwoWire &bus)
    : _bus(&bus), _bmp(&bus) {}

  bool ok() const {
    return _type != NONE;
  }

  bool hasHumidity() const {
    return _type == BME;
  }

  const char *name() const {
    if (_type == BME) return "BME280";
    if (_type == BMP) return "BMP280";
    return "KHONG THAY";
  }

  bool begin() {
    _type = NONE;

    const uint8_t addrs[2] = {0x76, 0x77};

    for (uint8_t i = 0; i < 2; i++) {
      uint8_t addr = addrs[i];
      uint8_t id = chipId(addr);

      if (id == 0x60) {
        if (_bme.begin(addr, _bus)) {
          _bme.setSampling(
            Adafruit_BME280::MODE_NORMAL,
            Adafruit_BME280::SAMPLING_X2,
            Adafruit_BME280::SAMPLING_X16,
            Adafruit_BME280::SAMPLING_X2,
            Adafruit_BME280::FILTER_X4,
            Adafruit_BME280::STANDBY_MS_500
          );

          _type = BME;
          return true;
        }
      }
      else if (id == 0x56 || id == 0x57 || id == 0x58) {
        if (_bmp.begin(addr, id)) {
          _bmp.setSampling(
            Adafruit_BMP280::MODE_NORMAL,
            Adafruit_BMP280::SAMPLING_X2,
            Adafruit_BMP280::SAMPLING_X16,
            Adafruit_BMP280::FILTER_X4,
            Adafruit_BMP280::STANDBY_MS_500
          );

          _type = BMP;
          return true;
        }
      }
    }

    return false;
  }

  bool read(float &t, float &h, float &p) {
    t = NAN;
    h = NAN;
    p = NAN;

    if (_type == NONE) return false;

    float temperature;
    float humidity = NAN;
    float pressure;

    if (_type == BME) {
      temperature = _bme.readTemperature();
      humidity = _bme.readHumidity();
      pressure = _bme.readPressure() / 100.0F;
    }
    else {
      temperature = _bmp.readTemperature();
      pressure = _bmp.readPressure() / 100.0F;
    }

    bool bad =
      isnan(temperature) ||
      isnan(pressure) ||
      pressure < 300.0F ||
      pressure > 1100.0F ||
      (_type == BME && isnan(humidity));

    if (bad) {
      _type = NONE;
      return false;
    }

    t = temperature;
    h = humidity;
    p = pressure;

    return true;
  }

private:
  uint8_t chipId(uint8_t addr) {
    _bus->beginTransmission(addr);
    _bus->write(0xD0);

    if (_bus->endTransmission(false) != 0) {
      return 0;
    }

    if (_bus->requestFrom((int)addr, 1) != 1) {
      return 0;
    }

    return (uint8_t)_bus->read();
  }

  TwoWire *_bus;
  Adafruit_BME280 _bme;
  Adafruit_BMP280 _bmp;

  Type _type = NONE;
};

EnvSensor bme_ground(Wire);

// ============================================================
// 3. TIMEOUT / HEARTBEAT
// ============================================================

const unsigned long MIN_TIMEOUT_MS = 12000UL;
const unsigned long OFFLINE_REPORT_MS = 5000UL;

unsigned long currentUavIntervalMs = 1000UL;
unsigned long lastLoraReceived = 0;
unsigned long lastOfflineReport = 0;

unsigned long getConnectionTimeout() {
  unsigned long calculatedTimeout =
    currentUavIntervalMs * 2UL + 5000UL;

  return calculatedTimeout > MIN_TIMEOUT_MS
    ? calculatedTimeout
    : MIN_TIMEOUT_MS;
}

// ============================================================
// 4. BO DEM NHAN LO RA
// ============================================================

#define LORA_LINE_MAX 400

String loraLine = "";
bool loraOverflow = false;

// Cac truong telemetry duoc chuyen tiep len PC
const char *UAV_KEYS[] = {
  "run_id",
  "boot_id",
  "seq",
  "uptime_ms",
  "interval_ms",
  "mode",
  "t1", "h1", "p1",
  "t2", "h2", "p2",
  "bat", "vbat", "pwr"
};

const int UAV_KEYS_N =
  sizeof(UAV_KEYS) / sizeof(UAV_KEYS[0]);

// ============================================================
// 5. CAC HAM TIEN ICH
// ============================================================

float round2(float value) {
  if (isnan(value)) return NAN;

  return roundf(value * 100.0F) / 100.0F;
}

void readGround(float &t, float &h, float &p) {
  if (!bme_ground.ok()) {
    bme_ground.begin();
  }

  if (!bme_ground.read(t, h, p)) {
    t = NAN;
    h = NAN;
    p = NAN;
    return;
  }

  t = round2(t);
  h = round2(h);
  p = round2(p);
}

void setGround(JsonDocument &doc) {
  float t3, h3, p3;

  readGround(t3, h3, p3);

  if (isnan(t3)) doc["t3"] = nullptr;
  else doc["t3"] = t3;

  if (isnan(h3)) doc["h3"] = nullptr;
  else doc["h3"] = h3;

  if (isnan(p3)) doc["p3"] = nullptr;
  else doc["p3"] = p3;
}

// Cap nhat chu ky truyen neu JSON co interval_ms hop le
void updateUavInterval(JsonDocument &doc) {
  if (doc["interval_ms"].isNull()) {
    return;
  }

  unsigned long receivedInterval =
    doc["interval_ms"].as<unsigned long>();

  if (receivedInterval >= 1000UL &&
      receivedInterval <= 60000UL) {
    currentUavIntervalMs = receivedInterval;
  }
}

// ============================================================
// 6. XU LY DU LIEU NHAN TU UAV
// ============================================================

void handleUavLine(const String &line) {
  JsonDocument uavDoc;

  DeserializationError error =
    deserializeJson(uavDoc, line);

  if (error) {
    return;
  }

  // JSON hop le tu UAV: cap nhat heartbeat
  lastLoraReceived = millis();

  // Cap nhat timeout theo chu ky UAV
  updateUavInterval(uavDoc);

  JsonDocument outDoc;

  // ----------------------------------------------------------
  // ACK tu UAV
  // ----------------------------------------------------------

  if (uavDoc["ack"].is<const char *>()) {
    outDoc["status"] = "ack";
    outDoc["ack"] = uavDoc["ack"];

    if (!uavDoc["interval_ms"].isNull()) {
      outDoc["interval_ms"] = uavDoc["interval_ms"];
    }

    serializeJson(outDoc, Serial);
    Serial.println();

    return;
  }

  // ----------------------------------------------------------
  // TELEMETRY TU UAV
  // ----------------------------------------------------------

  outDoc["status"] = "online";

  for (int i = 0; i < UAV_KEYS_N; i++) {
    outDoc[UAV_KEYS[i]] = uavDoc[UAV_KEYS[i]];
  }

  // Thoi diem Ground nhan du lieu theo uptime ESP8266
  outDoc["rx_uptime_ms"] = millis();

  // Them du lieu cam bien mat dat
  setGround(outDoc);

  serializeJson(outDoc, Serial);
  Serial.println();
}

// ============================================================
// 7. NHAN DU LIEU TU LORA
// ============================================================

void receiveFromUAV() {
  while (loraSerial.available()) {
    char c = (char)loraSerial.read();

    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      if (!loraOverflow && loraLine.length() > 0) {
        handleUavLine(loraLine);
      }

      loraLine = "";
      loraOverflow = false;
    }
    else {
      if (loraLine.length() < LORA_LINE_MAX) {
        loraLine += c;
      }
      else {
        loraOverflow = true;
      }
    }
  }
}

// ============================================================
// 8. CHUYEN LENH TU PC LEN UAV
// ============================================================

void forwardCommandToUAV() {
  if (!Serial.available()) {
    return;
  }

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();

  if (cmd.length() == 0) {
    return;
  }

  // Gui lenh qua LoRa E32
  loraSerial.println(cmd);
  loraSerial.flush();
}

// ============================================================
// 9. KIEM TRA MAT KET NOI
// ============================================================

void checkConnectionTimeout() {
  unsigned long now = millis();
  unsigned long timeoutMs = getConnectionTimeout();

  if (now - lastLoraReceived > timeoutMs) {
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

// ============================================================
// 10. SETUP
// ============================================================

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  delay(200);

  // LoRa E32 UART
  loraSerial.begin(
    9600,
    SWSERIAL_8N1,
    LORA_RX,
    LORA_TX,
    false,
    256
  );

  // I2C Ground Sensor
  Wire.begin(I2C_SDA, I2C_SCL);

  bme_ground.begin();

  lastLoraReceived = millis();
  lastOfflineReport = millis();
}

// ============================================================
// 11. LOOP - BAT BUOC PHAI CO
// ============================================================

void loop() {
  receiveFromUAV();

  forwardCommandToUAV();

  checkConnectionTimeout();

  yield();
}
