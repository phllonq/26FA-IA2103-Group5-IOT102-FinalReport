# RQ2 – Bộ dữ liệu truyền thông (Communication Dataset)

## Mục đích
Thư mục này định nghĩa cấu trúc dữ liệu phục vụ việc đánh giá cơ chế truyền thông thích ứng so với phương pháp truyền dữ liệu với tốc độ cố định.

## Bằng chứng dữ liệu hiện có
Tệp `uav_readings.csv` được cung cấp chứa các trường dữ liệu telemetry từ gateway, chẳng hạn như dấu thời gian, trạng thái, số thứ tự, dữ liệu đo cảm biến và nhãn nguồn cấp điện.

Tuy nhiên, tệp này **không chứa các sự kiện truyền dẫn vô tuyến (RF) cụ thể**, bao gồm sự kiện gửi gói tin (`TX`), nhận gói tin (`RX`), xác nhận gói tin (`ACK`), hết thời gian chờ (`timeout`), cường độ tín hiệu nhận được (`RSSI`), khoảng thời gian truyền hoặc dấu thời gian tạo gói tin.

Do đó, các tệp CSV trong thư mục này chỉ chứa cấu trúc dữ liệu (schema), chưa phải là các bộ dữ liệu thực nghiệm hoàn chỉnh:
- `D1_adaptive.csv`: Cấu trúc dữ liệu quan sát cho chế độ truyền thích ứng.
- `D2_fixed_rate.csv`: Cấu trúc dữ liệu phục vụ so sánh với chế độ truyền tốc độ cố định.
- `D3_packet_log.csv`: Cấu trúc dữ liệu nhật ký sự kiện gói tin.
- `RQ2_summary.csv`: Cấu trúc dữ liệu tổng hợp các chỉ số đánh giá.

Không có bản ghi dữ liệu tổng hợp hoặc kết quả thực nghiệm RQ2 tự tạo nào được bổ sung.

## Yêu cầu dữ liệu để tính toán các chỉ số đánh giá
- **PDR (Packet Delivery Ratio – Tỷ lệ chuyển phát gói tin):** Cần có tổng số gói tin đã truyền và số lượng gói tin duy nhất nhận thành công trong cùng một phiên thực nghiệm.
- **Packet reduction (Mức giảm số lượng gói tin truyền):** Cần có các lần chạy thử nghiệm ở chế độ truyền tốc độ cố định và chế độ truyền thích ứng với điều kiện so sánh tương đương.
- **Latency (Độ trễ):** Cần có dấu thời gian gửi và nhận tương ứng của từng gói tin, đồng thời phải xác định được mối quan hệ đồng bộ giữa các đồng hồ thời gian.
- **AoI (Age of Information – Độ tuổi thông tin):** Theo định nghĩa tiêu chuẩn, cần có dấu thời gian tạo gói tin và dấu thời gian nhận gói tin.
- **ACK success rate (Tỷ lệ xác nhận gói tin thành công):** Cần có bằng chứng về quá trình gửi/nhận gói tin ACK và xác định rõ mẫu số được sử dụng trong phép tính.

Theo định nghĩa tiêu chuẩn, PDR có giá trị trong khoảng từ 0% đến 100%. Các lần nhận gói tin trùng lặp không được tính là các gói tin được chuyển phát thành công duy nhất.
