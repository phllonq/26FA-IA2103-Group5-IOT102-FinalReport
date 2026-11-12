# Giao thức dữ liệu IoT-UAV

```
UAV (ESP32) --LoRa E32 (9600 8N1, truyền trong suốt)--> Ground (ESP8266) --USB Serial 115200--> PC (Streamlit + SQLite)
UAV (ESP32) <--------------------- lệnh <...> / dòng lệnh ---------------- Ground (ESP8266) <-- PC
```

Mọi bản tin là **một dòng JSON** kết thúc bằng `\n`. Giá trị không có hoặc cảm biến lỗi là `null` (không bao giờ là 0 giả).

## 1. UAV → Ground (LoRa)

Gói dữ liệu:

```json
{"seq":12,"t1":25.5,"h1":60.2,"p1":1009.8,"t2":25.1,"h2":61.0,"p2":1009.7,"bat":85,"vbat":11.82,"pwr":"bat"}
```

| Trường | Ý nghĩa |
|---|---|
| `seq` | Số thứ tự gói (phát hiện mất gói) |
| `t1,h1,p1` | BME280 #1 không vỏ: nhiệt độ °C, độ ẩm %, áp suất hPa |
| `t2,h2,p2` | BME280 #2 có vỏ Pagoda |
| `bat`, `vbat` | % pin và điện áp pack (V); `null` khi chạy nguồn USB |
| `pwr` | `"bat"` hoặc `"usb"` |

Phản hồi lệnh: `{"src":"uav","ack":"<TÊN>"}` với `<TÊN>` ∈ `SPEED_1S`, `SPEED_5S`, `SET_FREQ`, `SET_FREQ_INVALID`, `PING`, `RESET`, `UNKNOWN_CMD`.

## 2. Ground → PC (USB)

| `status` | Khi nào | Nội dung |
|---|---|---|
| `online` | Nhận gói dữ liệu từ UAV | Các trường của UAV (phẳng) + `t3,h3,p3` (BME280 mặt đất) |
| `offline` | Quá 12 s không nhận gì từ UAV (lặp mỗi 5 s) | `t3,h3,p3` |
| `ack` | UAV phản hồi lệnh | `ack` |

Schema chi tiết: [`payload_schema.json`](payload_schema.json).

## 3. PC → Ground → UAV (lệnh)

Gửi một dòng; có hoặc không có `< >` đều được. Backend chỉ cho phép:

| Lệnh | Tác dụng |
|---|---|
| `SPEED_1S` / `SPEED_5S` | Chu kỳ đọc và gửi 1 s / 5 s |
| `SET_FREQ:n` | Chu kỳ n giây, `1 ≤ n ≤ 60` |
| `PING` | UAV trả ack `PING` |
| `RESET_UAV` (hoặc `FORCE_RESET`) | UAV khởi động lại |

## 4. Heartbeat

ESP8266 ghi nhận thời điểm nhận gói cuối từ UAV (kể cả ack). Quá `TIMEOUT_MS = 12000` thì tự sinh gói `offline`. Streamlit đổi sang trạng thái đỏ; nếu chính gateway im lặng quá 20 s thì cảnh báo mất cáp USB/gateway.
