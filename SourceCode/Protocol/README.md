# Giao thức dữ liệu IoT-UAV

```text
UAV (ESP32) --LoRa E32 (9600 8N1, truyền trong suốt)--> Ground (ESP8266) --USB Serial 115200--> PC (Streamlit + SQLite)
UAV (ESP32) <--------------------- lệnh <...> / dòng lệnh ---------------- Ground (ESP8266) <-- PC
```

Mọi bản tin là **một dòng JSON** kết thúc bằng `\n`. Giá trị không có, cảm biến lỗi hoặc kênh đo không hỗ trợ trên phần cứng là `null` (không bao giờ dùng số `0` giả).

## 1. Cấu hình Phần cứng & Tương thích Cảm biến

* **Tự động nhận diện BMP280 (`0x58`) / BME280 (`0x60`)**: Firmware quét địa chỉ I2C (`0x76` / `0x77`). Với dòng chip `BMP280 (0x58)` chỉ đo nhiệt độ và áp suất, các trường độ ẩm (`h1, h2, h3`) trả về `null` để bảo toàn tính chính xác của dữ liệu thống kê.
* **Trạm UAV (ESP32 DevKit V1)**:
  * I2C-0 (`GPIO 21` SDA, `GPIO 22` SCL): Cảm biến #1 không vỏ (*Unshielded*).
  * I2C-1 (`GPIO 18` SDA, `GPIO 19` SCL): Cảm biến #2 có vỏ chắn gió (*Pagoda Shield*).
  * UART2 (`GPIO 16` RX2, `GPIO 17` TX2): Module LoRa E32 (`M0 = M1 = GND`, bỏ trống `AUX`).
  * ADC1 (`GPIO 34`): Đo điện áp pin LiPo 3S qua cầu phân áp (`R1 = 100kΩ`, `R2 = 33kΩ`).
* **Trạm Mặt Đất (ESP8266 NodeMCU)**:
  * I2C (`D6` SDA, `D5` SCL): Cảm biến #3 tham chiếu mặt đất (*Ground Reference*).
  * SoftwareSerial (`D2` RX, `D1` TX, buffer 256B): Module LoRa E32 (`M0 = M1 = GND`).

## 2. UAV → Ground (LoRa 433 MHz)

Gói dữ liệu:

```json
{"seq":12,"t1":25.5,"h1":null,"p1":1009.8,"t2":25.1,"h2":null,"p2":1009.7,"bat":85,"vbat":11.82,"pwr":"bat"}
```

| Trường | Ý nghĩa |
|---|---|
| `seq` | Số thứ tự gói tăng dần (dùng tính tỷ lệ nhận gói **PDR**) |
| `t1,h1,p1` | Cảm biến #1 không vỏ: nhiệt độ °C, độ ẩm % (`null` nếu BMP280), áp suất hPa |
| `t2,h2,p2` | Cảm biến #2 có vỏ Pagoda |
| `bat`, `vbat` | % pin và điện áp pack (V); `null` khi cấp nguồn qua cáp USB (`vbat < 6.0V`) |
| `pwr` | `"bat"` (chạy pin LiPo) hoặc `"usb"` (cấp nguồn trực tiếp qua USB) |

Phản hồi lệnh: `{"src":"uav","ack":"<TÊN>"}` với `<TÊN>` ∈ `SPEED_1S`, `SPEED_5S`, `SET_FREQ`, `SET_FREQ_INVALID`, `PING`, `RESET`, `UNKNOWN_CMD`.

## 3. Ground → PC (USB Serial 115200 bps)

| `status` | Khi nào | Nội dung |
|---|---|---|
| `online` | Nhận gói dữ liệu hợp lệ từ UAV | Các trường của UAV (phẳng) + `t3,h3,p3` (cảm biến mặt đất) |
| `offline` | Quá `12 s` không nhận gì từ UAV (lặp mỗi `5 s`) | `t3,h3,p3` |
| `ack` | UAV phản hồi lệnh điều khiển | `ack` |

## 4. PC → Ground → UAV (Lệnh điều khiển 2 chiều)

Gửi một dòng kết thúc bằng `\n` (có hoặc không có `< >` đều hợp lệ). Backend `gateway.py` lọc theo whitelist:

| Lệnh | Tác dụng |
|---|---|
| `SPEED_1S` / `SPEED_5S` | Đổi chu kỳ đọc và gửi dữ liệu sang `1 s` / `5 s` |
| `SET_FREQ:n` | Đặt chu kỳ tùy chỉnh `n` giây (`1 ≤ n ≤ 60`) |
| `PING` | Kiểm tra kết nối 2 chiều; UAV trả về `ack: "PING"` |
| `RESET_UAV` (hoặc `FORCE_RESET`) | Khởi động lại chip ESP32 từ xa |

## 5. Cơ chế Chống treo & Heartbeat (Fault Tolerance)

* **Hardware Watchdog Timer (`15 s`)**: Kích hoạt trên ESP32 Core 3.x; tự động hard-reset nếu vòng lặp bị treo.
* **I2C Bus Timeout (`50 ms`)**: Chống treo bus I2C khi UAV rung lắc; tự động khởi tạo lại cảm biến ở chu kỳ kế tiếp.
* **Heartbeat Timeout (`12 s` / `20 s`)**: ESP8266 tự phát gói `offline` sau `12 s` mất sóng LoRa; Dashboard Streamlit cảnh báo đỏ nếu chính Gateway im lặng quá `20 s`.
