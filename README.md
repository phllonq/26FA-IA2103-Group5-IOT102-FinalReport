# Adaptive-IoT-UAV-Monitoring

> **Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication**

[![Course](https://img.shields.io/badge/Course-IOT102--Fall2026-blue)](https://fpt.edu.vn)
[![Framework](https://img.shields.io/badge/Learning--Model-PBL%20%2B%20RBL-green)](#)
[![Platform](https://img.shields.io/badge/Hardware-ESP32%20%7C%20ESP8266%20%7C%20LoRa%20E32-orange)](#)
[![Dashboard](https://img.shields.io/badge/UI-Streamlit%20Liquid%20Glass-F97316)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Trường:** Đại học FPT TP.HCM   
**Môn học:** IOT102 — Internet of Things (Học kỳ Fall 2026)  
**Lớp / Nhóm:** IA2103 — Group 5  
**Giảng viên hướng dẫn:** TS. Trần Công Đời (Dr. Tran Cong Doi)  

| Thành viên | MSSV / Vai trò | Phụ trách chính |
|---|---|---|
| **Trần Phi Long** | `SE201868` — *Team Leader* | Kiến trúc hệ thống, Backend `gateway.py` (SQLite WAL), Streamlit Dashboard  |
| **Nguyễn Gia Huy** | *Firmware Developer* | Lập trình Firmware ESP32 (Trạm UAV) & ESP8266 (Trạm Mặt Đất), giao thức LoRa E32 2 chiều & Watchdog |
| **Nguyễn Bảo Phúc** | *Hardware & CAD Lead* | Hàn mạch phần cứng, cân chỉnh nguồn Buck Mini 360, sơ đồ nguyên lý & thiết kế in 3D vỏ chắn Pagoda Shield |
| **Nguyễn Thanh Nhân** | *Data Analytics & RBL* | Hiệu chuẩn cảm biến, thu thập log thực nghiệm, phân tích định lượng RQ1/RQ2 (MAE, RMSE, PDR, AoI) |

---

## 1. Project Overview

Quan trắc khí tượng và môi trường tầm thấp bằng thiết bị bay không người lái (UAV/Drone) thường gặp phải hai thách thức kỹ thuật lớn:
1. **Nhiễu cơ - nhiệt học cục bộ trên khoang bay (*Rotor Downwash & Solar Radiation*):** Luồng gió đập mạnh từ cánh quạt (downwash) kết hợp với nhiệt lượng tỏa ra từ động cơ/ESC và bức xạ mặt trời làm sai lệch đáng kể giá trị đo nhiệt độ và áp suất khí quyển nếu gắn cảm biến lộ thiên.
2. **Giới hạn truyền thông và năng lượng (*Telemetry & Power Constraints*):** Kết nối Wi-Fi truyền thống có tầm phủ sóng ngắn (< 50 m ngoài trời) và dễ đứt quãng khi UAV thay đổi độ cao, trong khi việc phát dữ liệu tần suất cao liên tục gây tiêu hao nhanh dung lượng pin LiPo.

Dự án **Adaptive IoT-UAV Environmental Monitoring System** giải quyết hai bài toán trên theo mô hình tích hợp **Project-Based Learning (PBL) + Research-Based Learning (RBL)**:
- **Cảm biến nhận biết nhiễu gió (*Downwash-Aware Sensing*):** Trang bị 2 cảm biến môi trường BME280/BMP280 hoạt động song song trên 2 bus phần cứng I2C độc lập của ESP32 (1 cảm biến trần *Unshielded* và 1 cảm biến đặt trong vỏ chắn bức xạ/gió *Pagoda Shield*), đối chiếu trực tiếp theo thời gian thực với cảm biến thứ 3 đặt tại Trạm Mặt Đất (*Ground Reference*).
- **Truyền thông LoRa thích ứng 2 chiều (*Two-Way Adaptive LoRa Telemetry*):** Thay thế hoàn toàn Wi-Fi/MQTT bằng đường truyền RF **LoRa EBYTE E32-433T20D (433 MHz)**, cho phép truyền các gói JSON 1 dòng ổn định ở khoảng cách xa và hỗ trợ gửi lệnh điều khiển từ mặt đất lên UAV để thay đổi chu kỳ lấy mẫu (`1s` – `60s`) tùy theo diễn biến môi trường và dung lượng pin.

---

## 2. Project Objectives

1. **Xây dựng phần cứng IoT-UAV 2 trạm hoàn chỉnh (End-to-End Prototype):** Thiết kế trạm bay UAV (ESP32 DevKit V1) dùng nguồn Pin LiPo 3S qua mạch hạ áp DC-DC Mini 360 (chuẩn 5.0V) tích hợp mạch cầu phân áp đo pin (`GPIO 34`), và trạm mặt đất (ESP8266 NodeMCU) kết nối trực tiếp vào PC qua USB Serial.
2. **Định lượng hiệu quả chống nhiễu của vỏ chắn Pagoda Shield:** Thu thập dữ liệu đồng thời từ 3 điểm đo (`t1/p1` không vỏ, `t2/p2` có vỏ Pagoda, `t3/p3` tham chiếu mặt đất) để đánh giá mức độ suy giảm sai số MAE và RMSE.
3. **Đảm bảo độ tin cậy và toàn vẹn dữ liệu (Fault Tolerance & Data Integrity):** Triển khai Hardware Watchdog Timer (15s), chống treo I2C (`setTimeOut(50ms)`), tự động nhận diện mã silicon cảm biến (`0x60` cho BME280 và `0x58` cho BMP280), và xuất giá trị `null` chuẩn xác khi cảm biến lỗi hoặc kênh không hỗ trợ (tuyệt đối không chèn số `0.0` giả làm lệch thống kê).
4. **Phát triển Ground Control Dashboard hiện đại:** Xây dựng giao diện giám sát và điều khiển trực tuyến trên **Streamlit** (phong cách *Apple Liquid Glass*) kết hợp cơ sở dữ liệu **SQLite (WAL mode)**, hiển thị trạng thái kết nối sống, biểu đồ tương tác thời gian thực và tự động tính toán các chỉ số nghiên cứu RBL.

---

## 3. Research Questions

### RQ1 — Downwash-Aware Sensing
> **Câu hỏi nghiên cứu 1:** *Việc sử dụng vỏ chắn bức xạ và luồng khí (Pagoda Shield) kết hợp kiến trúc Dual-I2C trên UAV giúp giảm thiểu sai số đo nhiệt độ và áp suất ($\text{MAE}, \text{RMSE}$) do hiệu ứng gió đập cánh quạt (rotor downwash) và bức xạ nhiệt như thế nào khi so sánh với cảm biến trần (unshielded) và trạm tham chiếu mặt đất?*

### RQ2 — Adaptive Communication
> **Câu hỏi nghiên cứu 2:** *Cơ chế điều chỉnh chu kỳ truyền dữ liệu thích ứng (`1s`, `5s`, hoặc tùy chỉnh `1–60s`) qua đường truyền LoRa 433 MHz ảnh hưởng như thế nào đến tỷ lệ nhận gói tin thành công ($\text{PDR}$), độ tươi của thông tin ($\text{AoI}$ — Age of Information) và hiệu quả tiết kiệm băng thông/năng lượng của trạm UAV?*

---

## 4. Proposed System Architecture

### UAV Telemetry Layer
Tầng truyền thông nối kết giữa trạm bay và trạm mặt đất qua sóng vô tuyến **LoRa 433 MHz** ở chế độ truyền trong suốt (*Transparent Mode*, cấu hình cố định `M0 = GND`, `M1 = GND`, tốc độ `9600 bps 8N1`). Mỗi bản tin là một dòng JSON gọn nhẹ kết thúc bằng ký tự xuống dòng `\n`, giúp việc đóng gói, kiểm lỗi và giải mã diễn ra tức thời mà không cần phụ thuộc vào kết nối Internet hay Wi-Fi.

### IoT Payload Layer
Tầng thu thập dữ liệu trên khoang bay tách biệt hoàn toàn hai cảm biến lên hai bộ điều khiển phần cứng I2C độc lập của ESP32 (`Wire` và `Wire1`), giúp loại bỏ xung đột địa chỉ I2C (`0x76`/`0x77`) và cô lập lỗi phần cứng: nếu một cảm biến bị lỏng dây khi UAV rung lắc, cảm biến còn lại vẫn hoạt động bình thường.

```text
UAV (ESP32 + 2x BME/BMP280 + pin LiPo)
   │  LoRa E32 (9600 8N1), JSON 1 dòng
   ▼
Trạm mặt đất (ESP8266 + BME/BMP280 tham chiếu)
   │  USB Serial 115200, JSON 1 dòng  (heartbeat: offline sau 12 s mất tín hiệu)
   ▼
PC: Streamlit + SQLite  ──lệnh (SPEED_1S/5S, SET_FREQ:n, PING, RESET_UAV)──► Ground ──► UAV
```

- Hai cảm biến trên UAV (không vỏ và có vỏ Pagoda) cùng một cảm biến mặt đất cho phép so sánh đối chứng số liệu theo thời gian thực.
- Firmware UAV tích hợp Watchdog phần cứng (15s), đo điện áp pin LiPo 3S (tự động nhận biết khi đang cấp nguồn qua cổng USB nếu $V_{\text{bat}} < 6.0\text{V}$), tự khởi tạo lại cảm biến khi rớt; cảm biến lỗi hoặc kênh không hỗ trợ báo `null`.
- Đặc tả bản tin: [`SourceCode/Protocol`](SourceCode/Protocol/README.md). Sơ đồ nối dây: [`wiring_guide.md`](SourceCode/CAD_Schematic/wiring_guide.md).

---

## 5. Proposed Experimental Design

### RQ1 — Kịch bản đánh giá cảm biến & vỏ chắn Pagoda Shield
1. **Giai đoạn 1 (Baseline Calibration):** Đặt cả 3 cảm biến (#1 Unshielded, #2 Pagoda Shielded, #3 Ground Reference) cùng độ cao trong điều kiện tĩnh trong phòng để kiểm tra độ lệch chuẩn nội tại giữa các chip cảm biến.
2. **Giai đoạn 2 (Outdoor / Thermal Exposure):** Đặt trạm UAV ngoài trời dưới bức xạ nhiệt để đánh giá khả năng chống bức xạ mặt trời của vỏ Pagoda (#2) so với cảm biến trần (#1).
3. **Giai đoạn 3 (Active Rotor Downwash Test):** Kích hoạt luồng gió cưỡng bức từ cánh quạt UAV, ghi log liên tục ở chu kỳ `1s` (`SPEED_1S`) để định lượng biến thiên nhiệt độ $\Delta T = \vert{}T_1 - T_2\vert{}$ và độ nhiễu áp suất khí quyển $\Delta P$ so với mặt đất ($T_3, P_3$).

### RQ2 — Kịch bản đánh giá truyền thông LoRa & Điều khiển thích ứng
1. **Kiểm thử khoảng cách & Tỷ lệ nhận gói (PDR):** Thu thập chuỗi số thứ tự gói tin `seq` liên tục ở các cự ly khác nhau giữa UAV và Ground Station để xác định tỷ lệ mất gói trên kênh LoRa 433 MHz.
2. **Kiểm thử điều khiển thích ứng 2 chiều (Two-Way Command & AoI):** Thực hiện chuyển đổi linh hoạt giữa các lệnh `SPEED_1S` (khi UAV đang bay đo đạc tích cực), `SPEED_5S` và `SET_FREQ:n` (khi UAV ở chế độ chờ/tiết kiệm pin); đo độ trễ phản hồi bản tin xác nhận `{"status":"ack","ack":"..."}` và độ tươi dữ liệu (AoI).
3. **Kiểm thử chịu lỗi (Fault-Injection Testing):** Chủ động ngắt kết nối cảm biến I2C và ngắt nguồn UAV để xác minh cơ chế tự phục hồi I2C, Watchdog Timer (15s) và cảnh báo Heartbeat Offline (sau 12s trên ESP8266 và 20s trên Dashboard).

---

## 6. Planned Hardware & Software

### Phần cứng

| Trạm | Thành phần | Kết nối chân (Pinout) |
|---|---|---|
| **UAV (Airborne Node)** | **ESP32 DevKit V1**, 2x BME280/BMP280 (không vỏ & có vỏ Pagoda, 2 bus I2C riêng), Module **LoRa E32-433T20D**, Pin LiPo 3S + mạch hạ áp **Mini 360** (5.0V), cầu phân áp đo pin ($R_1 = 100\text{k}\Omega, R_2 = 33\text{k}\Omega$) | • **I2C-0 (#1 Unshielded):** `SDA = GPIO 21`, `SCL = GPIO 22`<br>• **I2C-1 (#2 Pagoda):** `SDA = GPIO 18`, `SCL = GPIO 19`<br>• **UART2 (LoRa E32):** `RX2 = GPIO 16` $\leftarrow$ `TXD`, `TX2 = GPIO 17` $\rightarrow$ `RXD`, `M0 = M1 = GND`<br>• **ADC Pin LiPo:** `GPIO 34` |
| **Mặt đất (Ground Gateway)** | **ESP8266 NodeMCU**, Module **LoRa E32-433T20D** (`SoftwareSerial`), 1x BME280/BMP280 tham chiếu, cấp nguồn & truyền dữ liệu qua cổng USB PC | • **I2C (#3 Ground Ref):** `SDA = D6 (GPIO 12)`, `SCL = D5 (GPIO 14)`<br>• **SoftSerial (LoRa E32):** `D2 (GPIO 4)` $\leftarrow$ `TXD`, `D1 (GPIO 5)` $\rightarrow$ `RXD`, `M0 = M1 = GND` |

### Phần mềm
- **Embedded Firmware:** Arduino IDE (ESP32 Arduino Core 3.x, ESP8266 Core), thư viện `Adafruit BME280`, `Adafruit BMP280` (tương thích phần cứng chip ID `0x58` và `0x60`), `ArduinoJson` (v7).
- **Backend & Ground Control UI:** Python 3.11+, `streamlit>=1.37`, `pyserial>=3.5`, `pandas>=2.0`, `altair>=5.0`, cơ sở dữ liệu `SQLite3` (chế độ `WAL` chống khóa ghi/đọc đồng thời).

### Build & Run

1. **Nạp Firmware cho 2 trạm:**
   - Mở `SourceCode/Firmware_UAV_ESP32/Firmware_UAV_ESP32.ino`, chọn board **ESP32 Dev Module** và bấm **Upload**.
   - Mở `SourceCode/Firmware_Ground_ESP8266/Firmware_Ground_ESP8266.ino`, chọn board **NodeMCU 1.0 (ESP-12E Module)** và bấm **Upload**.
2. **Khởi chạy Backend & Streamlit Dashboard:**
   ```bash
   cd SourceCode/Backend_Dashboard
   pip install -r requirements.txt
   python -m streamlit run app.py
   ```
   *(Lưu ý: Đóng cửa sổ Serial Monitor của Arduino IDE trước khi bấm nút **Kết nối** cổng COM trên giao diện Streamlit).*

---

## 7. Proposed Directory Structure

```text
.
├── Documents/              Final Report (IEEE PDF), slides thuyết trình, proposal, poster
├── AI_Audit_Log/           AI Audit Log (file nộp riêng), ADR, minh chứng kiểm thử
├── Datasets/               Raw_Logs, RQ1_Sensing, RQ2_Communication, Processed CSV
├── Diagrams/               Block diagram, circuit schematic, flowchart, data flow
├── VideoDemo/              Video demo hệ thống hoạt động thực tế (optional)
└── SourceCode/
    ├── Firmware_UAV_ESP32/        Firmware trạm UAV (ESP32 DevKit V1 - Arduino)
    ├── Firmware_Ground_ESP8266/   Firmware trạm mặt đất (ESP8266 NodeMCU - Arduino)
    ├── Protocol/                  Đặc tả bản tin JSON (PROTOCOL.md) & payload_schema.json
    ├── Backend_Dashboard/         Streamlit Liquid Glass UI (app.py) + SQLite Gateway (gateway.py)
    ├── Data_Analytics/            Script phân tích dữ liệu, hiệu chuẩn, đánh giá RQ1/RQ2
    ├── CAD_Schematic/             Sơ đồ mạch, file CAD 3D vỏ Pagoda, wiring_guide.md
    ├── Hardware_Design/           Block diagram, schematic, flowchart (PDF/PNG)
    └── Flight_Controller/         PX4 parameters, mission plan
```

---

## 8. Planned Evaluation Metrics

Hệ thống đánh giá định lượng hiệu năng cảm biến (RQ1) và chất lượng truyền thông (RQ2) thông qua 4 chỉ số toán học chính (được tính toán trực tiếp trên Dashboard và script phân tích):

1. **Mean Absolute Error (MAE — Sai số tuyệt đối trung bình):**
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} \left\vert{} x_i - x_{\text{ref}, i} \right\vert{}$$
   Đánh giá độ lệch nhiệt độ/áp suất trung bình giữa cảm biến không vỏ ($T_1$) và cảm biến có vỏ Pagoda ($T_2$), hoặc giữa trạm bay và trạm mặt đất ($T_3$).

2. **Root Mean Square Error (RMSE — Sai số toàn phương trung bình):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} \left( x_i - x_{\text{ref}, i} \right)^2}$$
   Nhấn mạnh các biên độ nhiễu đột biến (spikes) khi luồng gió cánh quạt thay đổi tốc độ.

3. **Packet Delivery Ratio (PDR — Tỷ lệ nhận gói tin thành công):**
   $$\text{PDR} = \frac{N_{\text{received}}}{N_{\text{expected}}} \times 100\% = \frac{\text{count}(\text{unique } seq)}{\max(seq) - \min(seq) + 1} \times 100\%$$

4. **Age of Information (AoI — Độ tươi của dữ liệu):**
   $$\text{AoI}(t) = t_{\text{current}} - t_{\text{last\_online\_packet}}$$
   Đo lường độ trễ thực tế từ lúc gói tin mới nhất của UAV được ghi nhận tại trạm mặt đất.

---

## 9. Development Roadmap

Lộ trình triển khai dự án trong 11 tuần theo chuẩn PBL + RBL của môn học IOT102:

| Tuần | Giai đoạn | Nội dung thực hiện & Kết quả (Deliverables) |
|---|---|---|
| **Tuần 1–2** | *Topic Proposal* | Xác định bài toán nhiễu gió Downwash trên UAV, đăng ký đề tài Nhóm 5 & viết Problem Statement. |
| **Tuần 3** | *Literature Review* | Tổng hợp các bài báo IEEE/Scopus về UAV氣象 sensing, vỏ chắn bức xạ Pagoda và truyền thông LoRa; chốt RQ1 & RQ2. |
| **Tuần 4** | *System Architecture* | Thiết kế Block Diagram, chuyển đổi kiến trúc từ Wi-Fi sang LoRa E32 433 MHz, lập sơ đồ nối chân Dual-I2C. |
| **Tuần 5–6** | *Hardware & Firmware* | Hàn mạch hoàn chỉnh cho ESP32 & ESP8266, tinh chỉnh mạch hạ áp Mini 360 5.0V, viết firmware đọc cảm biến & đóng gói JSON. |
| **Tuần 7** | **OPA1 Assessment** | Demo phần cứng cơ bản, kiểm tra kết nối cảm biến, báo cáo Block Diagram, Circuit Schematic & Flowchart. |
| **Tuần 8** | *System Integration* | Xây dựng `gateway.py` đa luồng lưu SQLite (WAL), xử lý bất đồng bộ UART 256B, bổ sung Watchdog 15s & I2C timeout 50ms. |
| **Tuần 9** | **OPA2 Assessment** | Demo hệ thống End-to-End (UAV $\rightarrow$ LoRa $\rightarrow$ Ground $\rightarrow$ Dashboard), nộp bản nháp bài báo IEEE (Draft Paper v1). |
| **Tuần 10** | *UI/UX & Refinement* | Nâng cấp giao diện Streamlit theo chuẩn **Apple Liquid Glass**, tích hợp điều khiển 2 chiều và thẻ tính toán RBL tự động. |
| **Tuần 11** | **Final Evaluation** | Hoàn thiện Final Report chuẩn IEEE (5–8 trang), nộp AI Audit Log, đóng gói mã nguồn GitHub & bảo vệ đồ án cuối kỳ. |

---

## 10. AI Usage & Audit

Nhóm tuân thủ nghiêm ngặt quy định về minh bạch học thuật và kiểm chứng kết quả AI (**AI Output Verification & Validation**):
- **AI Usage Declaration:** Được đính kèm đầy đủ ở phần cuối của báo cáo `Final Report` trong thư mục `Documents/`.
- **AI Audit Log:** Lưu trữ tại file riêng trong thư mục [`AI_Audit_Log/`](AI_Audit_Log/), ghi nhận chi tiết chuỗi *AI Output $\rightarrow$ Verification/Validation $\rightarrow$ Student Decision $\rightarrow$ Evidence/Test* cho các quyết định kỹ thuật trọng tâm của dự án:
  1. **Lựa chọn giao thức & Tối ưu chân LoRa E32:** Thay thế Wi-Fi bằng LoRa E32 433 MHz để đảm bảo tầm xa; nối cứng `M0 = M1 = GND` (Normal Mode) và xử lý đệm phần mềm thay vì tốn thêm 3 chân GPIO cho `M0, M1, AUX`.
  2. **Thiết kế nguồn 5.0V & Dual Hardware I2C:** Sử dụng mạch hạ áp DC-DC Mini 360 (5.0V) thay vì cấp thẳng 12.6V của pin LiPo 3S vào chân VIN tránh cháy module LoRa; tách 2 cảm biến lên `Wire` (GPIO 21/22) và `Wire1` (GPIO 18/19) để triệt tiêu xung đột địa chỉ I2C.
  3. **Khắc phục lỗi biên dịch Watchdog ESP32 Core 3.x & Nhận diện Silicon BMP280 (`0x58`):** Phát hiện code khởi tạo Watchdog cũ (`esp_task_wdt_init(15, true)`) của AI bị lỗi trên ESP32 Core 3.3.12 và cập nhật sang cấu trúc `esp_task_wdt_config_t`; đồng thời viết trình quét thanh ghi `0xD0` phát hiện lô mạch thực tế dùng chip `BMP280 (0x58)` để xử lý trả về `null` cho kênh độ ẩm.
  4. **Bảo toàn tính toàn vẹn dữ liệu (Data Integrity):** Thay thế hàm đọc chuỗi chặn (`blocking`) và thói quen gán số `0.0` khi lỗi của AI bằng bộ đệm nhận ký tự không chặn (256B), timeout I2C 50ms và giá trị `null` (`nullptr`) chuẩn JSON Schema, giúp phép tính MAE/RMSE không bị sai lệch.

---

## 11. References

1. Bosch Sensortec, *"BME280 — Combined humidity and pressure sensor datasheet,"* Document BST-BME280-DS002, 2022.
2. Bosch Sensortec, *"BMP280 — Digital Pressure Sensor datasheet,"* Document BST-BMP280-DS001, 2021.
3. T. Villa, F. Gonzalez, B. Miljievic, Z. D. Ristovski, and L. Morawska, *"An Overview of Small Unmanned Aerial Vehicles for Air Quality Measurements: Present Applications and Future Prospectives,"* **Sensors**, vol. 16, no. 7, p. 1072, 2016.
4. S.och, M. Islam, et al., *"Investigation of Rotor Downwash Effects on Temperature and Humidity Measurements Using Multi-Rotor UAVs,"* **IEEE Sensors Journal**, 2021.
5. R. D. Yates, Y. Sun, D. R. Brown, S. K. Kaul, E. Modiano, and S. Ulukus, *"Age of Information: An Introduction and Survey,"* **IEEE Journal on Selected Areas in Communications**, vol. 39, no. 5, pp. 1183–1210, May 2021.
6.成都亿佰特电子科技有限公司 (Chengdu Ebyte Electronic Technology Co., Ltd.), *"E32-433T20D User Manual — SX1278 433MHz 100mW DIP Wireless Module,"* v1.6.
