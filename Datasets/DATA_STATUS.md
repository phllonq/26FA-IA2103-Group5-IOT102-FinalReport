# Trạng thái dữ liệu và ghi chú bàn giao

Gói dữ liệu này được tổ chức nhằm đảm bảo khả năng truy xuất và kiểm chứng nguồn dữ liệu được cung cấp cho dự án.

## Các nội dung đã hoàn thành dựa trên dữ liệu được cung cấp
- File dữ liệu xuất từ gateway ban đầu được bảo toàn nguyên trạng trong `raw_source/`.
- Ba luồng dữ liệu từ cảm biến BMP280 được tách thành các file CSV riêng biệt cho RQ1.
- Các thống kê mô tả RQ1 được tính toán dựa trên những phép đo có dữ liệu hợp lệ (không bị thiếu).
- Các tài liệu metadata, từ điển trường dữ liệu và nhật ký nhập dữ liệu đã được tạo.

## Các nội dung chưa thể hoàn thành do thiếu dữ liệu nguồn
- Nhãn chế độ bay (mặt đất / bay treo / bay tiến).
- Độ cao và tốc độ bay về phía trước.
- Mã định danh phiên thực nghiệm đã được xác minh.
- Phân tích sai số đồng bộ giữa cảm biến và giá trị tham chiếu (MAE/RMSE).
- Nhật ký RSSI/trạng thái/khoảng thời gian phục vụ cơ chế truyền dữ liệu thích ứng.
- Lần chạy thử nghiệm đối chứng với tốc độ truyền cố định.
- Nhật ký TX/RX/ACK ở cấp độ gói tin.
- Tính toán AoI (Age of Information) theo phương pháp tiêu chuẩn.

