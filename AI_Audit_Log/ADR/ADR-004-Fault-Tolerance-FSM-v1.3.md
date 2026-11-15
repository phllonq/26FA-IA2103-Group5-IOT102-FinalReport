# ADR-004: Triển khai cơ chế chịu lỗi phần cứng (Fault Tolerance) & Heartbeat

## 1. Trạng thái (Status)
**Đã phê duyệt (Accepted)** - Đã triển khai trên firmware ESP32 (UAV) và ESP8266 (Ground).

## 2. Bối cảnh (Context)
UAV là môi trường hoạt động khắc nghiệt (nhiễu từ trường motor, rung lắc mạnh, sụt áp pin). Nếu lập trình theo kiểu tuần tự dùng lệnh `delay()`, vi điều khiển rất dễ bị treo (freeze). Ngoài ra, trong môi trường vô tuyến, tín hiệu LoRa có thể bị suy hao hoặc mất gói, dẫn đến trạm mặt đất không phân biệt được là UAV đang bay ngoài tầm phủ sóng hay UAV đã bị rơi/mất điện.

## 3. Quyết định (Decision)
Nhóm quyết định loại bỏ hoàn toàn mã lập trình chặn (blocking code), áp dụng kiến trúc **Máy trạng thái hữu hạn (FSM)** và các cơ chế bảo vệ thời gian thực:
1. **Hardware Watchdog Timer (WDT) 15 giây (UAV):** Khởi tạo `esp_task_wdt`. Nếu code ESP32 bị treo (do thư viện I2C lặp vô hạn), sau 15 giây phần cứng tự động Hard-Reset để cứu vãn hệ thống.
2. **I2C Timeout 50ms (UAV):** Set `Wire.setTimeOut(50)`. Tránh treo bus I2C khi lỏng dây cảm biến. 
3. **Heartbeat FSM 12 giây (Trạm mặt đất):** ESP8266 liên tục kiểm đếm mốc thời gian nhận gói cuối. Nếu `>12s` không có sóng, tự động chuyển UI sang trạng thái OFFLINE.
4. **Xuất giá trị `null` khi lỗi (Data Integrity):** Khi cảm biến bị lỗi, xuất JSON `null` thay vì giá trị `0`.

## 4. Các phương án thay thế đã xem xét (Alternatives Considered)
- **Gửi giá trị `0.0` khi cảm biến lỗi:** 
  *Nhược điểm:* Làm hỏng hoàn toàn tập dữ liệu nghiên cứu (Dataset). Trong môi trường, 0 độ C hoặc 0 hPa là một con số vật lý có thật, khiến thuật toán tính MAE/RMSE trên Streamlit bị sai lệch nghiêm trọng. JSON `null` (tương đương `None` trong Python) giúp Pandas tự động bỏ qua (drop_na) dữ liệu rác.
- **Giữ nguyên chu kỳ gửi LoRa 1 giây cố định để làm Heartbeat:**
  *Nhược điểm:* Đề tài của nhóm là "Điều khiển chu kỳ thích ứng". Việc UAV chuyển sang ngủ 60 giây mới gửi 1 gói (tiết kiệm pin) sẽ làm trạm mặt đất tưởng lầm là rớt mạng nếu không có cơ chế quản lý trạng thái động (Adaptive Heartbeat) kết hợp với các gói ACK/PING.

## 5. Hệ quả (Consequences)
### Tích cực (Pros):
- Đảm bảo an toàn tuyệt đối cho phần mềm UAV, tự động phục hồi sau sự cố treo cảm biến.
- Dữ liệu thu thập (Dataset) đảm bảo tính toàn vẹn (Data Integrity) để báo cáo học thuật, không bị dính các điểm dị thường (outliers) do lỗi phần cứng.

### Hạn chế (Cons):
- Code firmware dài và phức tạp hơn rất nhiều so với cách viết tuyến tính truyền thống. Cần quản lý chặt chẽ các biến `millis()` để không bị tràn bộ nhớ sau 50 ngày chạy liên tục.
