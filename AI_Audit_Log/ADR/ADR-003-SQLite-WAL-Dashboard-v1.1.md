# ADR-003: Lựa chọn cơ sở dữ liệu SQLite (chế độ WAL) cho Trạm mặt đất

## 1. Trạng thái (Status)
**Đã phê duyệt (Accepted)** - Đã tích hợp vào `gateway.py` và `app.py` (Streamlit).

## 2. Bối cảnh (Context)
Trạm mặt đất cần lưu trữ dữ liệu thời gian thực gửi về từ UAV qua sóng LoRa, có thể ở tần suất cao (1 gói/giây). Đồng thời, giao diện Streamlit Dashboard cần liên tục truy xuất dữ liệu này để vẽ biểu đồ và tính toán 4 chỉ số RBL (PDR, AoI, MAE, RMSE). Yêu cầu đặt ra là hệ thống phải hoạt động offline (tại thực địa không có 4G/Wi-Fi) và không bị lỗi crash khi có 2 luồng đọc/ghi diễn ra cùng lúc.

## 3. Quyết định (Decision)
Sử dụng **SQLite** làm cơ sở dữ liệu cục bộ, bắt buộc kích hoạt chế độ **WAL (Write-Ahead Logging)** thông qua lệnh `PRAGMA journal_mode=WAL;`. Dữ liệu được chia làm 2 bảng: `readings` (lưu telemetry) và `events` (lưu nhật ký lệnh & ACK).

## 4. Các phương án thay thế đã xem xét (Alternatives Considered)
- **Lưu trực tiếp ra file CSV/JSON phẳng:** 
  *Nhược điểm:* Dễ dính lỗi "File Lock" (khóa file). Khi `gateway.py` đang mở file để ghi dòng dữ liệu mới mà Streamlit lại mở file ra để vẽ biểu đồ, ứng dụng sẽ bị crash ngay lập tức.
- **Cơ sở dữ liệu đám mây (Firebase / Supabase):** 
  *Nhược điểm:* Bắt buộc trạm mặt đất (Laptop) phải có kết nối Internet 4G. Không khả thi khi mang UAV đi test ở các khu vực trống trải, hẻo lánh hoặc sóng di động yếu.
- **Time-Series Database chuyên dụng (InfluxDB):**
  *Nhược điểm:* Phải cài đặt service nền phức tạp, nặng máy, over-engineering (quá mức cần thiết) đối với quy mô của một trạm gateway di động nhẹ gọn.

## 5. Hệ quả (Consequences)
### Tích cực (Pros):
- **Đọc/Ghi đồng thời an toàn:** Chế độ WAL cho phép `gateway.py` (ghi dữ liệu mới) và `app.py` (đọc dữ liệu cũ vẽ chart) hoạt động song song mà không bị khóa (Database is locked).
- **Hoạt động 100% Offline:** Một file `.db` duy nhất, dễ dàng copy, sao lưu và nén lại thành file zip nộp minh chứng RBL cho giảng viên.
- **Hiệu năng cao:** Phân tích dữ liệu cực nhanh thông qua thư viện `pandas` (`pd.read_sql_query`).

### Hạn chế (Cons):
- Chế độ WAL tạo ra thêm 2 file tạm (`.db-wal` và `.db-shm`) trong thư mục làm việc, cần cấu hình `.gitignore` để không push rác lên GitHub.
