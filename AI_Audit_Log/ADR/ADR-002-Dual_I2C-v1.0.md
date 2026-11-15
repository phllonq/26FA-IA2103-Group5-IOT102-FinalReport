# ADR-002: Triển khai kiến trúc Dual-I2C cho mảng cảm biến kép trên UAV

## 1. Trạng thái (Status)
**Đã phê duyệt (Accepted)** - Đã triển khai hàn mạch thực tế trên ESP32 DevKit V1.

## 2. Bối cảnh (Context)
Dự án yêu cầu thu thập dữ liệu đồng thời từ 2 cảm biến BMP280 trên UAV (một cái gắn trần, một cái nằm trong vỏ Pagoda) để đánh giá sai số khí động học (RQ1). Tuy nhiên, các module BMP280 bán sẵn trên thị trường đều được nhà sản xuất cố định địa chỉ I2C mặc định là `0x76`. Nếu mắc song song cả 2 cảm biến vào cùng một bus I2C (`SDA` và `SCL`), hiện tượng xung đột địa chỉ (Address Collision) sẽ xảy ra, làm treo đường truyền.

## 3. Quyết định (Decision)
Tận dụng tính năng của vi điều khiển ESP32 (có 2 bộ I2C Controller bằng phần cứng), nhóm quyết định **tách riêng 2 cảm biến ra 2 bus I2C hoàn toàn độc lập**:
- **I2C-0 (`Wire`):** Dùng chân `GPIO 21 (SDA)` và `GPIO 22 (SCL)` cho BMP280 #1 (Không vỏ).
- **I2C-1 (`Wire1`):** Dùng chân `GPIO 18 (SDA)` và `GPIO 19 (SCL)` cho BMP280 #2 (Vỏ Pagoda).

## 4. Các phương án thay thế đã xem xét (Alternatives Considered)
- **Hàn thay đổi địa chỉ cứng trên module (Hardware Mod):** Nối chân `SDO` của một module lên `3.3V` để chuyển địa chỉ thành `0x77`. 
  *Nhược điểm:* Đòi hỏi can thiệp mỏ hàn vào linh kiện dán (SMD) rất nhỏ, dễ gây hỏng module nhiệt nhạy cảm như BMP280, khó thay thế nhanh khi hỏng hóc trên thực địa.
- **Sử dụng IC ghép kênh I2C (I2C Multiplexer - TCA9548A):**
  *Nhược điểm:* Tăng số lượng linh kiện, tăng trọng lượng (payload) cho UAV và làm code phức tạp thêm không cần thiết.

## 5. Hệ quả (Consequences)
### Tích cực (Pros):
- **Cô lập lỗi phần cứng (Fault Isolation):** Đây là ưu điểm lớn nhất. UAV khi bay có độ rung lắc cơ học rất mạnh. Nếu một cảm biến bị đứt dây hoặc kéo chập chân SDA xuống GND, bus I2C còn lại vẫn hoạt động bình thường, không làm sập toàn bộ hệ thống thu thập.
- **Plug-and-Play:** Có thể mua bất kỳ module BMP280 mặc định nào thay thế ngay lập tức mà không cần hàn đổi chân.
- Tốc độ đọc dữ liệu ổn định và song song.

### Hạn chế (Cons):
- Tiêu tốn thêm 2 chân GPIO trên ESP32 (Hoàn toàn chấp nhận được vì ESP32 còn dư nhiều chân).
