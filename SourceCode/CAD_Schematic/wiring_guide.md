# Wiring Guide

Sơ đồ nối dây cho hai trạm. Firmware tương ứng: `SourceCode/Firmware_UAV_ESP32/` và `SourceCode/Firmware_Ground_ESP8266/`.

> Gắn anten vào module LoRa E32 **trước khi** cấp nguồn.

## 1. Trạm UAV (ESP32 DevKit V1)

### Nguồn (Mini 360 hạ áp)

| Từ | Đến |
|---|---|
| Pin LiPo (+) / (−) | IN+ / IN− của Mini 360 |
| OUT+ (chỉnh đúng **5.0 V** trước khi nối) | VIN (5V) của ESP32 **và** VCC của LoRa E32 |
| OUT− (GND) | GND của ESP32 (mass chung toàn mạch) |

Khi cấp nguồn từ pin, **rút cáp USB khỏi ESP32** để tránh hai nguồn 5 V chạy song song.

### LoRa E32 (UART2)

| E32 | ESP32 |
|---|---|
| VCC | 5 V (OUT+ Mini 360) |
| GND | GND |
| TXD | GPIO 16 (RX2) |
| RXD | GPIO 17 (TX2) |
| M0, M1 | Hàn chập với nhau, nối xuống GND (chế độ truyền trong suốt) |
| AUX | Bỏ trống |

### BME280 số 1 (không vỏ) — I2C bus 0 (`Wire`)

| BME280 | ESP32 |
|---|---|
| VIN | 3V3 |
| GND | GND |
| SCL | GPIO 22 |
| SDA | GPIO 21 |

### BME280 số 2 (có vỏ Pagoda) — I2C bus 1 (`Wire1`)

| BME280 | ESP32 |
|---|---|
| VIN | 3V3 |
| GND | GND |
| SCL | GPIO 19 |
| SDA | GPIO 18 |

### Đo pin LiPo (cầu phân áp → ADC)

| Điểm nối | Ghi chú |
|---|---|
| Cực (+) pin → R1 → **GPIO 34** | R1 = 100 kΩ |
| GPIO 34 → R2 → GND | R2 = 33 kΩ trong code hiện tại |

- Code giả định pin **3S** (`BAT_CELLS = 3`). Với R2 = 33 kΩ, pin đầy 12,6 V cho ≈ 3,13 V tại ADC, sát ngưỡng bão hòa của ESP32. Nên cân nhắc R2 = 27 kΩ (hệ số ≈ 4,7).
- Nếu đổi điện trở, sửa `R1`, `R2` trong code; đối chiếu với đồng hồ đo rồi chỉnh `BAT_CAL`.
- Chưa gắn pin (cấp nguồn bằng USB): firmware báo `"pwr":"usb"`, `bat = null`.

## 2. Trạm mặt đất (ESP8266 NodeMCU)

### Nguồn

Cáp USB 5 V cắm trực tiếp vào cổng microUSB của board (đồng thời là cáp dữ liệu tới PC).

### LoRa E32 (SoftwareSerial)

| E32 | NodeMCU |
|---|---|
| VCC | VIN (5 V từ USB) |
| GND | G |
| TXD | D2 (GPIO 4, Soft RX) |
| RXD | D1 (GPIO 5, Soft TX) |
| M0, M1 | Hàn chập với nhau, nối xuống G |
| AUX | Bỏ trống |

### BME280 số 3 (Ground Reference)

| BME280 | NodeMCU |
|---|---|
| VIN | 3V (3.3 V) |
| GND | G |
| SCL | D5 (GPIO 14) |
| SDA | D6 (GPIO 12) |

## 3. Lưu ý chung

- Nhiều module ghi nhãn chung "BME/BMP280". Chip BMP280 (mã `0x58`) **không có cảm biến độ ẩm**; firmware vẫn chạy được nhưng độ ẩm là `null`. Muốn có độ ẩm cần BME280 thật (mã `0x60`). Có thể kiểm tra mã chip bằng sketch quét I2C.

- Hai module E32 phải cùng dòng/băng tần và cùng cấu hình (địa chỉ, kênh, tốc độ truyền); giữ mặc định 9600 8N1.
- Module E32 công suất cao có thể kéo dòng lớn khi phát; cấp nguồn bằng cổng USB laptop có thể gây sụt áp và reset ngẫu nhiên.
