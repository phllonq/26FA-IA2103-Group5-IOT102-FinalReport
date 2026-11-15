# Bộ dữ liệu thực nghiệm

Thư mục này tổ chức dữ liệu telemetry được trích xuất từ hệ thống giám sát UAV thuộc dự án IOT102.

## Nội dung bộ dữ liệu

- `RQ1_Sensing/`: Các luồng dữ liệu cảm biến được trích xuất từ file `uav_readings.csv`.
- `RQ2_Communication/`: Các schema phục vụ thí nghiệm truyền thông. File dữ liệu được cung cấp không chứa nhật ký sự kiện gửi/nhận gói tin (packet TX/RX/ACK) hoặc một lần chạy thử nghiệm đối chứng với tốc độ cố định có thể xác định được.
- `Metadata/`: Các thông tin về cấu hình, định nghĩa trường dữ liệu và ghi chú về quá trình thu thập/nhập dữ liệu.

## Bằng chứng và giới hạn của dữ liệu

File dữ liệu nguồn chứa 910 bản ghi trong khoảng thời gian từ ngày 2026-11-12 đến ngày 2026-11-15:
- 554 bản ghi có trạng thái `online`.
- 356 bản ghi có trạng thái `offline`.
- BMP280 #1 (`t1`, `p1`): 459 bản ghi có dữ liệu đo.
- BMP280 #2 (`t2`, `p2`): 145 bản ghi có dữ liệu đo.
- BMP280 #3 (`t3`, `p3`): 476 bản ghi có dữ liệu đo.
- Độ ẩm (`h1`, `h2`, `h3`) và pin (`bat`, `vbat`): Không có giá trị được ghi nhận.

File dữ liệu nguồn ban đầu được bảo toàn tại `raw_source/uav_readings_original.csv`.

**Lưu ý quan trọng:** Không có bất kỳ giá trị dữ liệu nào được tạo giả hoặc bổ sung. Các trường `session_id` để trống cho thấy file dữ liệu nguồn không cung cấp mã định danh phiên hoạt động. Phần tổng hợp RQ1 chỉ bao gồm các thống kê mô tả. Các chỉ số MAE/RMSE, so sánh giữa các chế độ bay và các chỉ số đánh giá hiệu suất RQ2 không được đưa ra khi thiếu dữ liệu cần thiết để tính toán.
