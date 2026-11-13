# System Architecture, Flowchart & Data Flow Diagrams

Thư mục này lưu trữ toàn bộ bộ sơ đồ kỹ thuật chuẩn hóa của dự án **Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication (Nhóm 5 — Lớp IA2103 — Môn IOT102)**:

| STT | Tên file ảnh | Tiêu chuẩn áp dụng | Nội dung mô tả chính |
|---|---|---|---|
| **1** | `Block_Diagram.png` | Hardware Block Diagram Standard | Phân cấp khối chức năng phần cứng, biên nguồn cấp điện, hướng tín hiệu và đặc tả các Bus giao tiếp (`I2C`, `UART`, `ADC`, `LoRa RF`, `USB`, `SQL_IO`). |
| **2** | `Flowchart_FSM.png` | Chuẩn quốc tế **ANSI X3.5 / ISO 5807** | Lưu đồ thuật toán điều khiển và xử lý ngoại lệ trên Trạm bay UAV (ESP32) và Trạm mặt đất (ESP8266 & Python Gateway). |
| **3** | `System_DataFlow.png` | End-to-End Pipeline Architecture | Luồng đóng gói bản tin JSON chiều xuống (*Downlink Telemetry*) và luồng lệnh điều khiển / phản hồi 2 chiều (*Uplink Command & ACK*). |

---

## 1. Hardware Block Diagram (Sơ Đồ Khối Phần Cứng)

<!-- VỊ TRÍ HIỂN THỊ ẢNH 1: Tải file Block_Diagram.png vào thư mục Diagrams/ -->
![Hardware Block Diagram](./Block_Diagram.png)

### 1.1. Phân cấp cấu trúc khối chức năng (System Hierarchy)
Hệ thống được chia thành **Biên nguồn cấp điện** ở phía trên và **2 phân hệ chức năng độc lập** nối kết qua kênh vô tuyến LoRa 433 MHz theo chiều từ **Trái sang Phải** (Khối Cảm biến đầu vào → Khối Vi điều khiển → Khối Thu phát Vô tuyến → Trạm Mặt Đất → Khối Hiển thị & Lưu trữ):

1. **Biên Nguồn Cấp Điện (Power Distribution Boundary):**
   - **Khối Nguồn Pin LiPo (Trạm UAV):** Cung cấp điện áp một chiều `+11.1V..12.6V` (3S LiPo) và đường `GND` chung.
   - **Khối Hạ Áp DC-DC (Mini 360):** Hạ áp và ổn áp đầu ra chuẩn `+5.0V VCC` để cấp nguồn an toàn cho Vi điều khiển trung tâm UAV (`VIN`) và Khối thu phát vô tuyến LoRa E32 (`VCC`).
   - **Khối Nguồn Cổng USB (Trạm Mặt Đất):** Cấp nguồn trực tiếp `+5.0V VBUS` từ máy tính cho mạch ESP8266 NodeMCU và module LoRa E32 mặt đất, đồng thời hạ áp xuống `+3.3V VDD` cho cảm biến tham chiếu.

2. **Phân Hệ 1 — Trạm Thu Thập Trên Không (Airborne Node — ESP32 DevKit V1):**
   - **Khối Cảm Biến #1 (Không vỏ / Unshielded):** Cảm biến BMP280/BME280 gắn lộ thiên để thu thập nhiệt độ (`t1`) và áp suất (`p1`) chịu tác động trực tiếp của luồng gió đập cánh quạt (*rotor downwash*).
   - **Khối Cảm Biến #2 (Có vỏ chắn gió / Pagoda Shield):** Cảm biến BMP280/BME280 đặt bên trong vỏ chắn bức xạ & luồng khí in 3D để đo nhiệt độ (`t2`) và áp suất (`p2`) đã lọc nhiễu cơ - nhiệt.
   - **Khối Đo Mức Pin (Analog Voltage Divider):** Mạch cầu phân áp điện trở (`R1 = 100kΩ`, `R2 = 33kΩ`) đưa tín hiệu điện áp tương tự vào bộ biến đổi ADC 12-bit (`GPIO 34`) để tính điện áp `vbat`, dung lượng `bat (%)` và nhận diện chế độ nguồn `pwr` (`"bat"` hoặc `"usb"`).
   - **Khối Vi Điều Khiển Trung Tâm UAV (ESP32 32-bit MCU):** Vận hành 2 bộ điều khiển phần cứng I2C độc lập (`Wire` và `Wire1`), quản lý bộ đếm Hardware Watchdog (`15s`), kiểm tra ngưỡng vật lý và đóng gói chuỗi JSON.
   - **Khối Thu Phát Vô Tuyến RF UAV (LoRa E32-433T20D):** Hoạt động ở chế độ truyền trong suốt (*Transparent Mode 0*, `M0 = M1 = GND`), phát gói tin cảm biến và nhận lệnh điều khiển ở tần số `433 MHz`.

3. **Phân Hệ 2 — Trạm Mặt Đất & Khối Hiển Thị Trung Tâm (Ground Station — ESP8266 & PC):**
   - **Khối Thu Phát Vô Tuyến RF Mặt Đất (LoRa E32-433T20D):** Thu gói tin RF từ UAV và phát lệnh điều khiển từ mặt đất lên UAV.
   - **Khối Cảm Biến #3 (Tham chiếu Mặt đất / Ground Reference):** Cảm biến BMP280/BME280 đặt tại trạm mặt đất để đo nhiệt độ (`t3`) và áp suất (`p3`) làm mốc đối chứng thực nghiệm.
   - **Khối Vi Điều Khiển Trạm Mặt Đất (ESP8266 Gateway MCU):** Giải mã gói JSON từ bộ đệm UART 256 byte, ghép thêm dữ liệu cảm biến mặt đất, giám sát thời gian chờ mất sóng (*Heartbeat Timeout 12s*) và đẩy dữ liệu qua USB.
   - **Khối Hiển Thị & Điều Khiển Trung Tâm (Streamlit Dashboard — `app.py`):** Giao diện điều khiển trung tâm thiết kế theo chuẩn *Apple Liquid Glass*, hiển thị đồ thị thời gian thực, tính toán tự động 4 chỉ số RBL (`PDR`, `AoI`, `MAE`, `RMSE`) và phát lệnh điều khiển.
   - **Khối Lưu Trữ Dữ Liệu (SQLite Database — `uav_data.db`):** Lưu trữ bền vững chuỗi thời gian vào bảng `readings` và nhật ký hệ thống vào bảng `events` theo cơ chế `WAL (Write-Ahead Logging)`.

### 1.2. Bảng đặc tả tín hiệu và Bus giao tiếp phần cứng

| Tên Bus / Tín hiệu | Ký hiệu đường dây | Chiều truyền | Kết nối phần cứng thực tế | Đặc tả kỹ thuật |
|---|---|---|---|---|
| **`I2C0_SDA`** | Nét liền (Data) | 2 chiều (`<-->`) | `BMP280 #1 SDA` ↔ `ESP32 GPIO 21` | Bus dữ liệu I2C số 0 (8-bit, Timeout 50ms) |
| **`I2C0_SCL`** | Nét đứt (Clock) | 1 chiều (`-.->`) | `ESP32 GPIO 22` → `BMP280 #1 SCL` | Xung nhịp I2C số 0 (100 kHz) |
| **`I2C1_SDA`** | Nét liền (Data) | 2 chiều (`<-->`) | `BMP280 #2 SDA` ↔ `ESP32 GPIO 18` | Bus dữ liệu I2C số 1 (8-bit, Timeout 50ms) |
| **`I2C1_SCL`** | Nét đứt (Clock) | 1 chiều (`-.->`) | `ESP32 GPIO 19` → `BMP280 #2 SCL` | Xung nhịp I2C số 1 (100 kHz) |
| **`ADC1_CH6`** | Nét liền (Analog) | 1 chiều (`-->`) | `Cầu phân áp Pin` → `ESP32 GPIO 34` | Ngõ vào ADC 12-bit (Lấy trung bình 16 mẫu) |
| **`UART2_TX / RX`** | Nét liền (Data) | 2 chiều (`<-->`) | `ESP32 GPIO 17 (TX2) / 16 (RX2)` ↔ `LoRa RXD / TXD` | Giao tiếp UART phần cứng (9600 bps, 8N1) |
| **`CTRL_M0/M1`** | Nét đứt (Control) | Cố định mức thấp | `LoRa M0 & M1` → `GND` | Khóa chế độ truyền trong suốt (Normal Mode 0) |
| **`RF 433MHz Link`** | Nét liền & Nét đứt | Bán song công | `LoRa E32 (UAV)` ↔ `LoRa E32 (Ground)` | Sóng vô tuyến ISM 433 MHz, công suất 100mW |
| **`UART_RX / TX`** | Nét liền (Data) | 2 chiều (`<-->`) | `ESP8266 D2 (GPIO 4) / D1 (GPIO 5)` ↔ `LoRa TXD / RXD` | Giao tiếp `SoftwareSerial` (9600 bps, Buffer 256B) |
| **`I2C_SDA (Đất)`** | Nét liền (Data) | 2 chiều (`<-->`) | `BMP280 #3 SDA` ↔ `ESP8266 D5 (GPIO 14)` | Bus dữ liệu I2C trạm mặt đất (8-bit) |
| **`I2C_SCL (Đất)`** | Nét đứt (Clock) | 1 chiều (`-.->`) | `ESP8266 D6 (GPIO 12)` → `BMP280 #3 SCL` | Xung nhịp I2C trạm mặt đất (100 kHz) |
| **`USB_UART`** | Nét liền (Data) | 2 chiều (`<-->`) | `ESP8266 microUSB` ↔ `PC (gateway.py)` | Luồng JSON Telemetry & ACK (115200 bps) |
| **`CTRL_CMD Bus`** | Nét đứt (Control) | 1 chiều (`-.->`) | `Streamlit UI` → `gateway.py` → `ESP8266` | Luồng gửi lệnh điều khiển đã lọc Whitelist |
| **`SQL_IO Bus`** | Nét liền (Data) | 2 chiều (`<-->`) | `gateway.py` ↔ `uav_data.db` ↔ `app.py` | Truy vấn đọc/ghi đồng thời qua SQLite WAL |

---

## 2. System Algorithm Flowchart (Lưu Đồ Thuật Toán — Chuẩn ANSI X3.5 / ISO 5807)

<!-- VỊ TRÍ HIỂN THỊ ẢNH 2: Tải file Flowchart_FSM.png vào thư mục Diagrams/ -->
![System Algorithm Flowchart](./Flowchart_FSM.png)

### 2.1. Quy ước ký hiệu hình học chuẩn quốc tế ANSI X3.5 / ISO 5807
- **Hình bầu dục (Oval — `Bắt đầu / Kết thúc`):** Biểu diễn điểm khởi đầu (`Start`) và điểm kết thúc (`End`) của chương trình.
- **Hình chữ nhật (Rectangle — `Xử lý / Process`):** Biểu diễn các phép gán, khởi tạo ngoại vi, tính toán nội bộ hoặc đóng gói dữ liệu.
- **Hình bình hành (Parallelogram — `Nhập / Xuất / I/O`):** Biểu diễn thao tác đọc dữ liệu từ cảm biến/ADC hoặc phát/xuất bản tin qua giao tiếp `UART`, `LoRa`, `USB`.
- **Hình thoi (Diamond — `Quyết định / Decision`):** Biểu diễn các điều kiện kiểm tra logic (`Đúng` / `Sai`). Mỗi hình thoi tuân thủ quy tắc **1 đường vào ở đỉnh trên** và **2 đường ra độc lập** (đỉnh dưới và đỉnh bên phải).
- **Đường vòng lặp ngoài (Single Outer Loop Return):** Mọi nhánh rẽ trong chu kỳ đều tiến về phía dưới và hội tụ vào **duy nhất 1 đường vòng lặp ngoài** đi bên trái để quay về đầu vòng lặp, không cắt chéo bất kỳ nhánh nào.

### 2.2. Lưu đồ con A: Thuật toán Trạm bay UAV (`Firmware_UAV_ESP32.ino`)

| Bước | Hình khối ISO 5807 | Nội dung trong khối | Mô tả chi tiết xử lý & Cơ chế chịu lỗi (Exception Handling) |
|---|---|---|---|
| **A1** | Hình bầu dục | **Bắt đầu (Start)** | Cấp nguồn cho ESP32 DevKit V1 từ mạch hạ áp Mini 360 (5.0V) hoặc cổng USB. |
| **A2** | Hình chữ nhật | **Khởi tạo ngoại vi & WDT** | Khởi tạo `Serial` (115200), `Serial2` LoRa (9600), ADC `GPIO 34` (`ADC_11db`), 2 bus `Wire` (21/22) & `Wire1` (18/19) với `setTimeOut(50ms)`, và kích hoạt **Hardware Watchdog Timer 15 giây**. |
| **A3** | Hình chữ nhật | **Reset bộ đếm Watchdog** | Gọi `esp_task_wdt_reset()` ở đầu mỗi vòng lặp. Nếu MCU bị treo quá `15s`, phần cứng tự động Hard-Reset để cứu hệ thống trên không. |
| **A4** | Hình thoi | **Có lệnh từ UART?** | Kiểm tra `Serial2.available()` không chặn (*non-blocking*):<br>• **Đúng:** Chuyển sang bước **A4_IO**.<br>• **Sai:** Đi thẳng xuống bước **A5**. |
| **A4_IO** | Hình bình hành | **Nhận lệnh & gửi ACK** | Đọc từng ký tự vào `cmdBuf[32]`, thực thi lệnh (`SPEED_1S`, `SPEED_5S`, `SET_FREQ:n`, `PING`, `RESET_UAV`) và phát trả gói xác nhận `{"src":"uav","ack":"..."}`. |
| **A5** | Hình thoi | **Đủ chu kỳ lấy mẫu?** | Kiểm tra `millis() - lastReadTime >= readInterval`:<br>• **Đúng:** Đi xuống bước **A6** để lấy mẫu.<br>• **Sai (Chưa tới hạn):** Đi theo nhánh bên phải xuống cuối vòng quét (**A10**). |
| **A6** | Hình bình hành | **Đọc cảm biến & áp pin** | Đọc nhiệt độ/áp suất từ BMP280 #1 (`Wire`), BMP280 #2 (`Wire1`) và lấy trung bình 16 mẫu điện áp tại chân `GPIO 34`. |
| **A7** | Hình thoi | **Dữ liệu đo hợp lệ?** | Kiểm tra giá trị `NaN` và ngưỡng áp suất vật lý `[300, 1100] hPa`:<br>• **Đúng:** Đi thẳng xuống bước **A8**.<br>• **Sai:** Rẽ sang bước xử lý lỗi **A7_ERR**. |
| **A7_ERR** | Hình chữ nhật | **Gán null & khởi tạo lại** | Gán `nullptr` (`null` trong JSON, tuyệt đối không dùng số `0` giả) cho kênh bị lỗi và gọi lại `initBMP()` ở chu kỳ kế tiếp để tự phục hồi khi dây I2C rung lắc. |
| **A8** | Hình chữ nhật | **Đóng gói bản tin JSON** | Đóng gói `seq`, `t1, h1, p1`, `t2, h2, p2`, `bat, vbat, pwr` thành 1 dòng JSON (nếu `vbat < 6.0V` thì gán `pwr = "usb"`, `bat = null`). |
| **A9** | Hình bình hành | **Phát gói tin qua LoRa** | Gửi dòng JSON qua `Serial2.println()` sang module LoRa E32 và tăng biến đếm `seqNo++`. |
| **A10** | Hình thoi | **Ngắt nguồn / Dừng?** | Kiểm tra trạng thái dừng hệ thống:<br>• **Sai:** Quay lại đầu vòng lặp (**A3**) qua đường vòng lặp ngoài.<br>• **Đúng:** Chuyển sang khối **Kết thúc (End)**. |

### 2.3. Lưu đồ con B: Thuật toán Trạm mặt đất (`Firmware_Ground_ESP8266.ino` & `gateway.py`)

| Bước | Hình khối ISO 5807 | Nội dung trong khối | Mô tả chi tiết xử lý & Máy trạng thái (FSM) |
|---|---|---|---|
| **B1** | Hình bầu dục | **Bắt đầu (Start)** | Kết nối ESP8266 NodeMCU vào PC qua cáp microUSB và khởi chạy `gateway.py`. |
| **B2** | Hình chữ nhật | **Khởi tạo Serial, LoRa, I2C** | Mở `Serial` (115200 bps), `SoftwareSerial` LoRa (`D2=RX, D1=TX`, 9600 bps, bộ đệm **256 byte**), và I2C cho BMP280 #3 mặt đất (`SDA=D5, SCL=D6`). |
| **B3** | Hình thoi | **Nhận gói tin LoRa?** | Đọc không chặn từ `loraSerial` cho tới khi gặp ký tự `\n` và giải mã JSON:<br>• **Đúng:** Đi xuống bước **B4**.<br>• **Sai:** Rẽ phải sang kiểm tra thời gian chờ **B3_TM**. |
| **B4** | Hình chữ nhật | **Cập nhật mốc Heartbeat** | Cập nhật `lastLoraReceived = millis()`. Nếu gói nhận được là phản hồi lệnh (`ack`), xuất ngay `{"status":"ack","ack":"..."}` lên PC. |
| **B5** | Hình bình hành | **Đọc cảm biến mặt đất** | Đọc nhiệt độ `t3` và áp suất `p3` từ cảm biến tham chiếu BMP280 #3 tại mặt đất (nếu lỗi gán `null`). |
| **B6** | Hình bình hành | **Xuất gói Online qua USB** | Hợp nhất trường dữ liệu UAV và mặt đất, xuất dòng JSON `{"status":"online",...}` qua USB Serial lên `gateway.py` để lưu vào SQLite. |
| **B3_TM** | Hình thoi | **Quá hạn 12 giây?** | Kiểm tra điều kiện mất sóng `millis() - lastLoraReceived > 12000 ms`:<br>• **Đúng:** Đi xuống bước **B3_OUT**.<br>• **Sai:** Hội tụ về bước **B7**. |
| **B3_OUT** | Hình bình hành | **Xuất gói Offline USB** | Cứ mỗi `5 giây`, đọc cảm biến mặt đất (`t3, p3`) và phát gói cảnh báo `{"status":"offline","t3":...}` lên PC để Dashboard đổi sang trạng thái đỏ. |
| **B7** | Hình thoi | **Có lệnh từ máy tính?** | Kiểm tra dữ liệu từ cổng USB Serial (đã được `gateway.py` lọc qua Whitelist `ALLOWED_CMDS`):<br>• **Đúng:** Đi xuống bước **B8**.<br>• **Sai:** Chuyển thẳng xuống bước **B9**. |
| **B8** | Hình bình hành | **Truyền lệnh qua LoRa** | Đọc dòng lệnh từ PC và phát qua `loraSerial.println(cmd)` lên Trạm bay UAV. |
| **B9** | Hình thoi | **Đóng cổng / Dừng?** | Kiểm tra trạng thái ngắt kết nối:<br>• **Sai:** Quay lại đầu vòng quét (**B3**) qua đường vòng lặp ngoài.<br>• **Đúng:** Đóng cổng Serial và **Kết thúc (End)**. |

---

## 3. End-to-End Telemetry & Command Data Flow (Luồng Dữ Liệu & Điều Khiển 2 Chiều)

<!-- VỊ TRÍ HIỂN THỊ ẢNH 3: Tải file System_DataFlow.png vào thư mục Diagrams/ -->
![System Data Flow Diagram](./System_DataFlow.png)

### 3.1. Luồng dữ liệu cảm biến chiều xuống (Downlink Telemetry — Nét liền Trái sang Phải)

1. **Chặng 1 — Thu thập tại Trạm UAV (ESP32):**
   - Đọc 2 cảm biến trên 2 bus I2C tách biệt và điện áp pin LiPo trên `GPIO 34`.
   - Đóng gói thành 1 dòng JSON thuần kết thúc bằng `\n` và phát qua UART2 sang LoRa E32 (9600 bps):
     ```json
     {"seq":12,"t1":31.04,"h1":null,"p1":1005.85,"t2":30.42,"h2":null,"p2":1005.90,"bat":85,"vbat":11.82,"pwr":"bat"}
     ```

2. **Chặng 2 — Hợp nhất dữ liệu tại Trạm Mặt Đất (ESP8266 Gateway):**
   - Khi nhận gói hợp lệ từ UAV, ESP8266 đọc thêm cảm biến tham chiếu mặt đất (`t3, h3, p3`) và đẩy gói `online` qua cổng USB Serial (115200 bps):
     ```json
     {"status":"online","seq":12,"t1":31.04,"h1":null,"p1":1005.85,"t2":30.42,"h2":null,"p2":1005.90,"bat":85,"vbat":11.82,"pwr":"bat","t3":33.14,"h3":null,"p3":1005.83}
     ```
   - Nếu quá `12 giây` không nhận được tín hiệu từ UAV, ESP8266 tự động phát gói `offline` định kỳ mỗi `5 giây`:
     ```json
     {"status":"offline","t3":33.14,"h3":null,"p3":1005.83}
     ```

3. **Chặng 3 — Lưu trữ đa luồng tại Backend (`gateway.py` & SQLite WAL):**
   - Luồng đọc nền (`_reader` daemon thread) phân tích cú pháp JSON, chuyển các giá trị `NaN`/`null` thành `NULL` chuẩn trong SQLite và ghi đồng thời vào 2 bảng `readings` và `events` trong file `uav_data.db` (chế độ `PRAGMA journal_mode=WAL`).

4. **Chặng 4 — Hiển thị & Phân tích định lượng RBL trên Streamlit (`app.py`):**
   - Giao diện tự động làm mới định kỳ bằng `@st.fragment`, cập nhật 4 thẻ Telemetry, vẽ 4 biểu đồ tương tác Altair và tự động tính 4 chỉ số nghiên cứu:
     - **PDR (*Packet Delivery Ratio*):** Tính tỷ lệ nhận gói thành công từ cột `seq`.
     - **AoI (*Age of Information*):** Độ tươi dữ liệu tính từ thời điểm nhận gói `online` gần nhất.
     - **Downwash MAE & RMSE:** Sai số tuyệt đối trung bình và sai số toàn phương trung bình giữa cảm biến không vỏ (`t1`) và cảm biến có vỏ Pagoda (`t2`).

### 3.2. Luồng lệnh điều khiển & phản hồi chiều lên (Uplink Command & ACK — Nét đứt Phải sang Trái)

| Lệnh gửi từ Dashboard | Cú pháp kiểm duyệt (`ALLOWED_CMDS`) | Tác dụng trên Trạm UAV | Bản tin xác nhận trả về PC (`ACK`) |
|---|---|---|---|
| **Chu kỳ 1 giây** | `^SPEED_1S$` | Đặt `readInterval = 1000 ms` (bay đo đạc tích cực) | `{"status":"ack","ack":"SPEED_1S"}` |
| **Chu kỳ 5 giây** | `^SPEED_5S$` | Đặt `readInterval = 5000 ms` (chế độ mặc định) | `{"status":"ack","ack":"SPEED_5S"}` |
| **Chu kỳ tùy chỉnh** | `^SET_FREQ:([1-9]\|[1-5][0-9]\|60)$` | Đặt `readInterval = n * 1000 ms` (`1 ≤ n ≤ 60`) | `{"status":"ack","ack":"SET_FREQ"}` |
| **Kiểm tra kết nối** | `^PING$` | Kiểm tra đường truyền LoRa 2 chiều | `{"status":"ack","ack":"PING"}` |
| **Khởi động lại UAV** | `^RESET_UAV$` | Gọi `ESP.restart()` khởi động lại ESP32 từ xa | `{"status":"ack","ack":"RESET"}` |
