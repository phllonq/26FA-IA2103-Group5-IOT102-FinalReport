# BÁO CÁO ĐỀ TÀI DỰ ÁN (PROJECT PROPOSAL) - TUẦN 02 (W02)
* **Môn học:** IOT102 - Internet of Things
* **Học kỳ:** Fall 2026
* **Tên nhóm / Repository:** https://github.com/phllonq/Adaptive-IoT-UAV-Monitoring

---

## 1. Tên Project (Project Title)
* **Tên tiếng Anh:** Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication
* **Tên tiếng Việt:** Hệ thống IoT giám sát môi trường trên UAV thích ứng luồng khí cánh quạt (Downwash-Aware) và truyền thông thích ứng (Adaptive Communication)

---

## 2. Lý do (Tính cần thiết) của đề tài (Problem Statement)

### 2.1. Bối cảnh thực tế
Các trạm quan trắc môi trường mặt đất cố định bị giới hạn nghiêm ngặt về không gian, không thể tiếp cận các khu vực địa hình chia cắt, độ cao biến đổi hoặc các túi nhiệt, túi khí ô nhiễm cục bộ. Việc tích hợp cảm biến đo đạc môi trường lên thiết bị bay không người lái (UAV/Drone) mang lại khả năng di động linh hoạt và quét dữ liệu không gian 3 chiều. 

Tuy nhiên, nếu chỉ gắn cảm biến lên UAV và truyền dữ liệu thông thường thì hệ thống sẽ gặp phải hai vấn đề kỹ thuật cốt lõi chưa được giải quyết triệt để trong các đề tài IoT cơ bản:

### 2.2. Vấn đề 1: Nhiễu môi trường đo đạc do luồng khí cánh quạt (Sensing Downwash Problem)
* **Thực trạng:** Khi UAV hoạt động, luồng khí cánh quạt cực mạnh (propeller airflow/downwash) phả thẳng vào khu vực gắn cảm biến.
* **Tác động:** Nhiệt tỏa ra từ khối vi điều khiển ESP32, pin LiPo và Flight Controller kết hợp với luồng xoáy downwash làm biến đổi vi khí hậu cục bộ quanh cảm biến nhiệt độ - độ ẩm (BME280).
* **Hậu quả:** Dữ liệu thu được không phản ánh đúng nhiệt độ và độ ẩm thực của môi trường xung quanh. Nếu sử dụng che chắn không đúng cách còn có thể gây hiện tượng tích tụ nhiệt (thermal trapping).

### 2.3. Vấn đề 2: Thách thức truyền thông không dây trên không (Communication Bottleneck)
* **Thực trạng:** Đường truyền vô tuyến (Wi-Fi/MQTT) giữa UAV đang bay và trạm mặt đất biến động liên tục theo khoảng cách, góc nghiêng cánh bay và nhiễu sóng (thể hiện qua chỉ số RSSI).
* **Hạn chế của phương pháp truyền thống:** Việc gửi dữ liệu theo chu kỳ cố định (Fixed Sampling, ví dụ: 1 packet/giây):
  - Gây lãng phí băng thông và tiêu hao năng lượng pin UAV khi thông số môi trường không thay đổi.
  - Tăng nguy cơ nghẽn mạng và rớt gói (Packet Loss) khi UAV bay vào vùng tín hiệu RSSI yếu.
  - Ngược lại, nếu chỉ hạ tần suất gửi đơn thuần sẽ làm giảm độ tươi mới của thông tin (Age of Information - AoI) và bỏ sót các hiện tượng bất thường (Sensor Events).

### 2.4. Tính cần thiết của đề tài
Đề tài có tính cấp thiết cao nhằm xây dựng một hệ sinh thái IoT hoàn chỉnh giải quyết đồng thời cả hai bài toán: **Nâng cao độ tin cậy của dữ liệu đo đạc (Sensing Reliability)** và **Tối ưu hóa hiệu quả truyền thông không dây (Adaptive Communication)** trên thiết bị bay di động.

---

## 3. Đặc điểm và Kết quả kỳ vọng của Project (Key Features & Expected Deliverables)

### 3.1. Phạm vi & Kiến trúc hệ thống đáp ứng chuẩn IOT102
Hệ thống bao gồm đầy đủ chuỗi cấu trúc IoT tiêu chuẩn:
1. **Thiết bị bay & Điều khiển chấp hành (Actuators & Flight Control):**
   - Nền tảng UAV điều khiển bằng Flight Controller (PX4 / ArduPilot).
   - Hỗ trợ bay tự động theo lộ trình điểm định trước (Autonomous Waypoint Navigation).
   - Truyền nhận dữ liệu bay (telemetry) qua giao thức MAVLink về phần mềm trạm mặt đất QGroundControl.
   - Điều khiển động cơ, mạch ESC và khả năng mở rộng cơ cấu chấp hành (servo/payload).
2. **Khối cảm biến & Thu thập dữ liệu (Sensing Layer):**
   - Vi điều khiển ESP32 giao tiếp I2C với cảm biến môi trường BME280 (đo Nhiệt độ và Độ ẩm tương đối).
3. **Cơ chế Downwash-Aware Sensing (Nghiên cứu RQ1):**
   - Thiết kế và đánh giá cấu trúc vỏ che thông gió hình chùa (Ventilated Pagoda Shield) so sánh đối chứng với cảm biến để hở (Unshielded).
   - Đánh giá sai số qua các trạng thái bay: Đậu mặt đất (Ground/OFF), Bay lơ lửng (Hover), Bay tiến (Forward Flight).
   - Xây dựng trạm tham chiếu mặt đất (Ground Reference Station) và áp dụng mô hình hồi quy tuyến tính nhẹ (Lightweight Linear Regression) để hiệu chuẩn (calibration) giảm thiểu sai số đo lường.
4. **Cơ chế Adaptive Communication (Nghiên cứu RQ2):**
   - Thuật toán thích ứng tự động điều chỉnh tốc độ lấy mẫu và gửi tin dựa trên: Cường độ tín hiệu sóng (RSSI), Độ biến thiên giá trị cảm biến ($\Delta$ Value), Ngưỡng trễ (Hysteresis), và Tuổi thọ thông tin (AoI).
   - Kích hoạt chế độ truyền khẩn cấp (Immediate Transmission) ngay khi phát hiện đột biến môi trường.
5. **Giao thức & Lưu trữ (Connectivity & Cloud Layer):**
   - Đóng gói dữ liệu gửi từ ESP32 qua giao thức MQTT lên Cloud / Cơ sở dữ liệu tập trung.
6. **Ứng dụng giám sát (Visualization Layer):**
   - Xây dựng Web Dashboard hiển thị biểu đồ nhiệt độ, độ ẩm, trạng thái pin, vị trí và telemetry thời gian thực.

### 3.2. Câu hỏi nghiên cứu (Research Questions)
* **RQ1 (Sensing):** Trạng thái bay của UAV và luồng khí cánh quạt ảnh hưởng như thế nào đến độ chính xác của BME280, và vỏ che thông gió có giúp giảm thiểu sai số này không?
* **RQ2 (Communication):** Cơ chế truyền tin thích ứng dựa trên RSSI và độ biến thiên dữ liệu có giúp giảm tải đường truyền mà vẫn đảm bảo độ tin cậy và độ tươi mới của dữ liệu hay không?

### 3.3. Kết quả kỳ vọng đạt được (Deliverables)
1. **Sản phẩm phần cứng:** UAV tích hợp bộ đo ESP32 + BME280 có vỏ che Pagoda Shield hoạt động an toàn và ổn định.
2. **Sản phẩm phần mềm:** 
   - Mã nguồn nhúng trên ESP32 tối ưu hóa thuật toán Adaptive Sampling.
   - Hệ thống backend tiếp nhận MQTT và Web Dashboard hiển thị trực quan.
3. **Báo cáo thực nghiệm & Dữ liệu NCKH:**
   - Bộ chỉ số định lượng đánh giá sai số cảm biến (MAE, RMSE, Standard Deviation).
   - Kết quả so sánh giữa cơ chế truyền cố định (Fixed) và thích ứng (Adaptive) chứng minh: giảm số lượng gói tin dư thừa (Packet Reduction), cải thiện tỷ lệ nhận gói thành công (PDR), duy trì độ tươi dữ liệu (AoI).
