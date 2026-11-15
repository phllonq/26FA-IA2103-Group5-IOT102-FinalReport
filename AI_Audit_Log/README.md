# AI AUDIT LOG | IOT102 Fall 2026

**Nhóm:** Nhóm 5 (Lớp IA2103)  
**Đề tài:** Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication  
**Môn học:** IOT102 — Internet of Things  

Dưới đây là 4 quyết định kỹ thuật tiêu biểu (Engineering Decisions) trong quá trình phát triển dự án, thể hiện việc nhóm đối chiếu, kiểm chứng và hiệu chỉnh các đề xuất từ công cụ AI để phù hợp với môi trường vận hành thực tế của thiết bị bay (UAV).

---

### [Entry 1] Giai đoạn: System Architecture (Tuần 4)
* **AI hỗ trợ:** AI đề xuất sử dụng ESP32 phát Wi-Fi (chế độ Access Point) trên UAV và trạm mặt đất kết nối vào để lấy dữ liệu cảm biến qua MQTT.
* **Chúng tôi đã kiểm tra:** Thử nghiệm thực tế ngoài trời cho thấy sóng Wi-Fi của ESP32 rất chập chờn khi UAV cách mặt đất hơn 30 mét. Đồng thời, liên tục duy trì sóng Wi-Fi làm pin LiPo của UAV sụt giảm nhanh chóng.
* **Chúng tôi quyết định:** Bác bỏ đề xuất Wi-Fi của AI. Nhóm quyết định thay thế bằng đường truyền vô tuyến **LoRa EBYTE E32-433T20D (433 MHz)** ở chế độ truyền trong suốt (*Transparent Mode*), giúp tăng tầm xa liên lạc và đảm bảo độ trễ thấp cho luồng điều khiển.

---

### [Entry 2] Giai đoạn: Hardware Selection & Power Management (Tuần 5)
* **AI hỗ trợ:** AI gợi ý cắm nguồn thẳng từ cực dương của Pin LiPo 3S (khoảng 12.6V khi sạc đầy) vào chân `VIN` của mạch ESP32 DevKit V1 vì regulator trên mạch có thể chịu được tới 15V.
* **Chúng tôi đã kiểm tra:** Tra cứu Datasheet của chip AMS1117-3.3 trên board ESP32 cho thấy nếu cấp 12.6V và kéo dòng cao khi phát sóng vô tuyến, regulator sẽ quá nhiệt (thermal shutdown) dẫn đến sập nguồn liên tục. Ngoài ra, module LoRa E32 chỉ chịu tối đa 5.2V.
* **Chúng tôi quyết định:** Nhóm tự thiết kế bổ sung một mạch hạ áp **DC-DC Buck Converter (Mini 360)**, tinh chỉnh VOM để cấp nguồn ổn định ở mức `5.0V` cho cả ESP32 và module LoRa E32, đồng thời tách thêm một nhánh cầu phân áp (100kΩ/33kΩ) để ESP32 đo giám sát dung lượng pin an toàn.

---

### [Entry 3] Giai đoạn: Firmware / Sensor Code (Tuần 6)
* **AI hỗ trợ:** AI generate code khởi tạo 2 cảm biến BMP280 bằng cách gọi lệnh chặn `delay()` và gán giá trị mặc định là `0.0` nếu không đọc được dữ liệu để tránh crash phần mềm.
* **Chúng tôi đã kiểm tra:** Khi cho UAV chạy thực tế, việc sử dụng `delay()` làm nghẽn luồng đọc lệnh từ cổng Serial2 (LoRa). Ngoài ra, việc gán giá trị `0.0` khi cảm biến lỏng dây làm sai lệch hoàn toàn phép tính trung bình MAE và RMSE của chỉ số RBL (Research-Based Learning).
* **Chúng tôi quyết định:** Sửa đổi cấu trúc code sang đa nhiệm (*non-blocking*). Thiết lập Timeout cho bus I2C là `50ms`. Đặc biệt, khi cảm biến lỗi hoặc khi xuất dữ liệu độ ẩm (h), hệ thống xuất ra chuỗi `null` chuẩn JSON (thay vì số `0`), giúp script Python mặt đất nhận diện chính xác dữ liệu hỏng để tính toán PDR.

---

### [Entry 4] Giai đoạn: Data Analytics & Display (Tuần 10)
* **AI hỗ trợ:** AI tạo script tính toán tốc độ truyền nhận gói (PDR) bằng cách đếm số dòng dữ liệu SQLite nhận được chia cho thời gian uptime của phần mềm.
* **Chúng tôi đã kiểm tra:** Công thức này bị sai lệch khi UAV đổi chu kỳ lấy mẫu liên tục (giữa 1s, 5s và 60s), vì số lượng gói tin mong đợi (Expected Packets) thay đổi liên tục, không phải hằng số.
* **Chúng tôi quyết định:** Sửa lại thuật toán PDR bằng cách bổ sung một trường số thứ tự tịnh tiến `seq` (Sequence Number) từ UAV. PDR tại mặt đất được nhóm tự tính toán chuẩn xác dựa trên công thức `Đếm số seq duy nhất / (seq max - seq min + 1)`.
