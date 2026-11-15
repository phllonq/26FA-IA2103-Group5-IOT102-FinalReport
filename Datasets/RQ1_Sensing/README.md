# RQ1 – Bộ dữ liệu cảm biến (Sensing Dataset)

## Mục đích
Thư mục này chứa ba luồng dữ liệu đo lường từ cảm biến BMP280, được trích xuất từ file CSV xuất dữ liệu của gateway được cung cấp.

## Ánh xạ cảm biến
- `RQ1_S1_baseline.csv`: BMP280 #1, không có lớp chắn bảo vệ (unshielded) (`t1`, `p1`).
- `RQ1_S2_shielded.csv`: BMP280 #2, có tấm chắn Pagoda (Pagoda Shield) (`t2`, `p2`).
- `RQ1_S3_ground_reference.csv`: BMP280 #3, cảm biến tham chiếu mặt đất (ground reference) (`t3`, `p3`).

Nhiệt độ được biểu diễn bằng °C và áp suất được biểu diễn bằng hPa. Dữ liệu độ ẩm không được đưa vào vì file dữ liệu nguồn được cung cấp không chứa các giá trị đo độ ẩm.

## Nguồn dữ liệu và quá trình trích xuất
Tất cả các hàng dữ liệu đều được trích xuất từ file `raw_source/uav_readings_original.csv`. Một hàng được đưa vào file dữ liệu riêng của từng cảm biến khi có ít nhất một trong hai trường nhiệt độ hoặc áp suất của cảm biến đó có giá trị.

Các thông tin sau được giữ lại từ dữ liệu gốc khi có sẵn: mã định danh bản ghi, dấu thời gian, dấu thời gian epoch, trạng thái, số thứ tự và trường thông tin về nguồn cấp điện.

Cột `session_id` được để trống vì file dữ liệu nguồn không chứa mã định danh phiên thực nghiệm đáng tin cậy. Không được tự suy luận ranh giới giữa các phiên thực nghiệm chỉ dựa trên hiện tượng đặt lại số thứ tự (sequence resets).

## Phân tích dữ liệu
File `RQ1_summary.csv` cung cấp các thống kê mô tả, bao gồm: số lượng mẫu, giá trị trung bình, độ lệch chuẩn mẫu, giá trị nhỏ nhất và giá trị lớn nhất.

Các chỉ số MAE và RMSE được cố ý để trống vì chưa xác định được sự tương ứng giữa các phép đo tham chiếu có đồng bộ thời gian cũng như các điều kiện môi trường có thể so sánh được. Ba cảm biến có thể được đặt tại các vị trí và độ cao khác nhau.

Chế độ bay, độ cao và tốc độ của UAV không có trong file dữ liệu nguồn, do đó không được đưa vào dưới dạng các trường dữ liệu đo lường.
