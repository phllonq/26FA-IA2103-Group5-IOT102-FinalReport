# ADR-001: Chuyển đổi kiến trúc truyền thông từ Wi-Fi sang LoRa 433 MHz

## 1. Trạng thái (Status)
**Đã phê duyệt (Accepted)** - Đã triển khai thực tế trên cả 2 trạm UAV (ESP32) và Mặt đất (ESP8266).

## 2. Bối cảnh (Context)
Trong thiết kế ban đầu, nhóm dự định sử dụng ESP32 trên UAV phát Wi-Fi (chế độ Access Point) hoặc kết nối qua MQTT Broker để truyền dữ liệu. Tuy nhiên, quá trình đánh giá và thử nghiệm thực tế bộc lộ 3 vấn đề lớn với hệ sinh thái UAV:
- **Tầm xa hạn chế:** Sóng Wi-Fi 2.4GHz của mạch ESP32 rất chập chờn và dễ rớt mạng khi UAV cất cánh cách xa trạm mặt đất trên 30 mét.
- **Tiêu thụ năng lượng (Power Consumption):** Việc liên tục duy trì module Wi-Fi ngốn dòng rất lớn, làm sụt áp hệ thống và hao pin LiPo của UAV nhanh chóng.
- **Độ trễ phục hồi (Reconnection Latency):** Khi rớt mạng, giao thức TCP/IP mất nhiều thời gian để bắt tay (handshake) và cấp lại IP, làm gián đoạn nghiêm trọng dữ liệu thời gian thực.

## 3. Quyết định (Decision)
Loại bỏ hoàn toàn kết nối Wi-Fi, chuyển sang sử dụng **sóng vô tuyến LoRa Sub-GHz (Module EBYTE E32-433T20D)** cho liên kết từ xa (Telemetry).
- **Tần số:** 433 MHz (Xuyên vật cản tốt, ít nhiễu với sóng điều khiển 2.4GHz của UAV).
- **Giao tiếp MCU:** UART (9600 bps, 8N1).
- **Chế độ hoạt động:** Truyền trong suốt (Transparent Mode 0 - Chân M0=M1=GND).

## 4. Các phương án thay thế đã xem xét (Alternatives Considered)
- **Wi-Fi (ESP32 AP / MQTT):** Bị loại do tầm ngắn, tốn pin và overhead của giao thức TCP/IP quá lớn so với lượng dữ liệu nhỏ của cảm biến.
- **NRF24L01 (2.4 GHz):** Bị loại vì dùng chung băng tần 2.4 GHz với remote điều khiển của drone, dễ gây nhiễu chéo; khả năng truyền xa kém hơn tần số 433 MHz.
- **LoRa SX1278 (Giao tiếp SPI):** Bị loại vì thư viện giao tiếp SPI phức tạp, chiếm dụng nhiều chân GPIO của ESP32 hơn so với chuẩn giao tiếp Serial (UART) đơn giản của module E32.

## 5. Hệ quả (Consequences)
### Tích cực (Pros):
- **Khoảng cách:** Tăng đáng kể tầm xa liên lạc và độ ổn định tín hiệu.
- **Năng lượng:** Tiết kiệm điện năng so với phát Wi-Fi liên tục.
- **Tính linh hoạt:** Giao tiếp qua Serial giúp nhóm dễ dàng lập trình thêm cơ chế "điều khiển chu kỳ thích ứng" và thuật toán gửi gói xác nhận (ACK) hai chiều ở tầng ứng dụng.

### Hạn chế & Giải pháp khắc phục (Cons & Mitigations):
- **Hạn chế - Băng thông hẹp:** Tốc độ UART 9600 bps và đặc thù sóng LoRa không cho phép truyền dữ liệu liên tục ở tốc độ quá cao (gây nghẽn hoặc xung đột RF).
- **Giải pháp (Mitigation):** Nhóm phải tối ưu hóa Data Payload. Cụ thể, dữ liệu từ 3 kênh nhiệt độ/áp suất và điện áp pin được gom gọn thành một chuỗi JSON 1 dòng duy nhất (~110 bytes), cắt bỏ toàn bộ khoảng trắng thừa để truyền đi nhanh nhất.
