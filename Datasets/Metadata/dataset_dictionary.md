# Từ điển dữ liệu (Dataset Dictionary)

## 1. Các trường dữ liệu chung

| Trường dữ liệu | Kiểu dữ liệu | Đơn vị | Ý nghĩa |
|---|---|---|---|
| `id` | Integer | - | Mã định danh bản ghi gốc trong cơ sở dữ liệu/file xuất dữ liệu của gateway |
| `timestamp` | String | ISO 8601 | Dấu thời gian gốc từ trường dữ liệu `ts` của nguồn |
| `ts_epoch` | Numeric | Unix seconds | Dấu thời gian gốc theo định dạng Unix epoch |
| `session_id` | String | - | Mã định danh phiên thực nghiệm; để trống khi không được cung cấp từ nguồn |
| `status` | String | - | Trạng thái gốc của gateway (`online` / `offline`) |
| `seq` | Numeric/integer-like | - | Giá trị số thứ tự gốc; có thể xảy ra hiện tượng đặt lại (reset) |
| `pwr` | String | - | Nhãn nguồn cấp điện gốc |

## 2. Các trường dữ liệu cảm biến RQ1

| Trường dữ liệu | Kiểu dữ liệu | Đơn vị | Ý nghĩa |
|---|---|---|---|
| `temperature_c` | Numeric | °C | Nhiệt độ đo được từ cảm biến được xác định trong tên file |
| `pressure_hpa` | Numeric | hPa | Áp suất đo được từ cảm biến được xác định trong tên file |

### Ánh xạ cảm biến với file dữ liệu

| File | Các trường dữ liệu nguồn ban đầu | Cảm biến |
|---|---|---|
| `RQ1_S1_baseline.csv` | `t1`, `p1` | BMP280 #1, không có lớp chắn bảo vệ (unshielded) |
| `RQ1_S2_shielded.csv` | `t2`, `p2` | BMP280 #2, có tấm chắn Pagoda (Pagoda Shield) |
| `RQ1_S3_ground_reference.csv` | `t3`, `p3` | BMP280 #3, cảm biến tham chiếu mặt đất (ground reference) |

## 3. Các trường dữ liệu tổng hợp RQ1

| Trường dữ liệu | Ý nghĩa |
|---|---|
| `sensor_id` | Mã định danh cảm biến |
| `measurement` | Đại lượng đo: `temperature_c` hoặc `pressure_hpa` |
| `sample_count` | Số lượng quan sát có dữ liệu hợp lệ (không bị thiếu) |
| `mean_value` | Giá trị trung bình cộng |
| `std_dev_sample` | Độ lệch chuẩn mẫu (ddof=1) |
| `min_value` | Giá trị nhỏ nhất được ghi nhận |
| `max_value` | Giá trị lớn nhất được ghi nhận |
| `mae` | Sai số tuyệt đối trung bình (Mean Absolute Error); để trống khi không thể tính toán hợp lệ |
| `rmse` | Căn bậc hai của sai số bình phương trung bình (Root Mean Square Error); để trống khi không thể tính toán hợp lệ |
| `comparison_status` | Trạng thái của phép tính so sánh |
| `notes` | Diễn giải kết quả và các giới hạn của dữ liệu |

## 4. Các trường schema RQ2

| Trường dữ liệu | Ý nghĩa |
|---|---|
| `event` | Sự kiện gói tin, chẳng hạn TX, RX, ACK, TIMEOUT, DUPLICATE |
| `direction` | Hướng truyền gói tin, ví dụ UAV_TO_GROUND hoặc GROUND_TO_UAV |
| `rssi_dbm` | Cường độ tín hiệu nhận được, tính bằng dBm |
| `state` | Trạng thái thích ứng, nếu được firmware ghi nhận |
| `tx_interval_s` | Khoảng thời gian truyền được cấu hình, tính bằng giây |
| `tx_count` | Số lượng gói tin đã truyền |
| `rx_unique_count` | Số lượng gói tin duy nhất được nhận |
| `duplicate_count` | Số lượng gói tin nhận bị trùng lặp |
| `lost_count` | Số lượng gói tin đã truyền nhưng không được nhận |
| `packet_size_bytes` | Kích thước gói tin, tính bằng byte |
| `latency_ms` | Độ trễ đo được, tính bằng mili giây |
| `generation_timestamp` | Thời điểm dữ liệu telemetry được tạo ra |
| `average_aoi_ms` | Độ tuổi thông tin trung bình (Average Age of Information), tính bằng mili giây |

Các file CSV thuộc RQ2 hiện chỉ chứa cấu trúc schema và chưa có dữ liệu đo thực tế. Chỉ có thể sử dụng chúng làm dữ liệu thực nghiệm sau khi được cung cấp nhật ký sự kiện gói tin và các lần chạy thử nghiệm đối chứng thực tế.

## 5. Giá trị thiếu và nguyên tắc diễn giải dữ liệu

- Các trường CSV để trống biểu thị giá trị bị thiếu hoặc không có sẵn.
- Không được sử dụng giá trị 0 để thay thế cho dữ liệu bị thiếu.
- Các số thứ tự (sequence numbers) phải được diễn giải trong phạm vi một phiên thực nghiệm đã được xác thực.
- Các hàng dữ liệu được đánh dấu `offline` vẫn có thể chứa các giá trị cảm biến đã được lưu trữ; do đó, cần giữ nguyên trường `status` ban đầu.
- Không tính PDR chỉ dựa trên số thứ tự gói tin khi chưa xác định được số lượng gói tin truyền, ranh giới giữa các phiên thực nghiệm và phương pháp xử lý gói tin trùng lặp.
- Công thức PDR tiêu chuẩn:

  **PDR = (Số lượng gói tin duy nhất nhận thành công / Tổng số gói tin đã truyền) × 100.**

- Việc tính toán AoI tiêu chuẩn yêu cầu phải có dấu thời gian tạo dữ liệu (generation timestamps) và dấu thời gian nhận dữ liệu (reception timestamps).
