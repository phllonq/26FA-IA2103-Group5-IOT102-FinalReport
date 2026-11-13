# System Architecture, Flowchart & Data Flow Diagrams

Thư mục này chứa toàn bộ sơ đồ kỹ thuật chuẩn hóa của hệ thống **Adaptive IoT-UAV Environmental Monitoring System (Nhóm 5 — IOT102)**:
1. **Hardware Block Diagram** (*Sơ đồ khối phần cứng*)
2. **System Algorithm Flowchart — Chuẩn ANSI X3.5 / ISO 5807** (*Lưu đồ thuật toán hệ thống*)
3. **End-to-End Telemetry & Command Data Flow** (*Sơ đồ luồng dữ liệu & điều khiển 2 chiều*)

---

## 1. Hardware Block Diagram (Sơ Đồ Khối Phần Cứng)

> **Quy ước đường dây & mũi tên tín hiệu:**
> - **Nét liền 1 chiều (`-->`):** Đường cấp nguồn (`+12V DC`, `+5.0V VCC`, `+3.3V VDD`) và tín hiệu tương tự 1 chiều (`ADC1_CH6`).
> - **Nét liền 2 chiều (`<-->` / `<==>`):** Bus dữ liệu số 2 chiều (`I2C_SDA`, `UART_TX/RX`, `USB_UART`, `SQL_IO`, `RF Data`).
> - **Nét đứt (`-.->` / `<-.->`):** Tín hiệu xung nhịp (`I2C_SCL`) và tín hiệu điều khiển trạng thái (`CTRL_M0/M1`, `CTRL_CMD`, `ACK`).

```mermaid
flowchart LR
    subgraph UAV["PHÂN HỆ 1: TRẠM THU THẬP TRÊN KHÔNG (AIRBORNE NODE)"]
        direction LR
        P_LIPO["Khối Nguồn Pin LiPo<br/>(+11.1V..12.6V, GND)"] -->|"+12V DC"| P_BUCK["Khối Hạ Áp DC-DC<br/>(Ổn áp +5.0V VCC, GND)"]
        P_BUCK -->|"+5.0V VIN, GND"| MCU_UAV["Khối Vi Điều Khiển<br/>Trung Tâm UAV<br/>(MCU 32-bit)"]
        P_BUCK -->|"+5.0V VCC, GND"| RF_UAV["Khối Thu Phát<br/>Vô Tuyến RF<br/>(LoRa 433MHz)"]

        S1["Khối Cảm Biến #1<br/>Nhiệt độ & Áp suất (Trần)<br/>Nguồn: +3.3V VDD, GND"] <-->|"I2C0_SDA (8-bit Data)"| MCU_UAV
        S1 -.->|"I2C0_SCL (100kHz Clock)"| MCU_UAV

        S2["Khối Cảm Biến #2<br/>Nhiệt độ & Áp suất (Chắn gió)<br/>Nguồn: +3.3V VDD, GND"] <-->|"I2C1_SDA (8-bit Data)"| MCU_UAV
        S2 -.->|"I2C1_SCL (100kHz Clock)"| MCU_UAV

        S_BAT["Khối Đo Mức Pin<br/>Phân áp Tương tự (Analog)<br/>Đầu vào: V_BAT (+12V)"] -->|"ADC1_CH6 (12-bit Data)"| MCU_UAV

        MCU_UAV <-->|"UART2_TX/RX (8-bit Data)"| RF_UAV
        MCU_UAV -.->|"CTRL_M0/M1 (Mode Control)"| RF_UAV
    end

    subgraph GND["PHÂN HỆ 2: TRẠM MẶT ĐẤT & KHỐI HIỂN THỊ TRUNG TÂM (GROUND STATION)"]
        direction LR
        P_USB["Khối Nguồn Cổng USB<br/>(+5.0V VBUS, +3.3V, GND)"] -->|"+5.0V VCC, GND"| RF_GND["Khối Thu Phát<br/>Vô Tuyến RF<br/>(LoRa 433MHz)"]
        P_USB -->|"+5.0V / +3.3V, GND"| MCU_GND["Khối Vi Điều Khiển<br/>Trạm Mặt Đất<br/>(Gateway MCU)"]

        RF_GND <-->|"UART_RX/TX (8-bit Data)"| MCU_GND
        RF_GND <-.->|"CTRL_M0/M1 (Mode Control)"| MCU_GND

        S3["Khối Cảm Biến #3 (Đất)<br/>Tham chiếu Nhiệt độ & Áp suất<br/>Nguồn: +3.3V VDD, GND"] <-->|"I2C_SDA (8-bit Data)"| MCU_GND
        S3 -.->|"I2C_SCL (100kHz Clock)"| MCU_GND

        MCU_GND <-->|"USB_UART (115200 bps Data)"| UI_CTRL["Khối Hiển Thị &<br/>Điều Khiển Trung Tâm<br/>(Streamlit Dashboard)"]
        MCU_GND <-.->|"CTRL_CMD Bus (Control)"| UI_CTRL

        UI_CTRL <-->|"SQL_IO Bus (WAL Data)"| DB_STORE["Khối Lưu Trữ Dữ Liệu<br/>(SQLite Database WAL)"]
    end

    RF_UAV <==>|"Kênh Dữ Liệu RF (433MHz Half-Duplex)"| RF_GND
    RF_UAV <-.->|"Tín hiệu Điều khiển & ACK"| RF_GND
```

---

## 2. System Algorithm Flowchart (Lưu Đồ Thuật Toán — Chuẩn ANSI X3.5 / ISO 5807)

> **Quy ước hình khối chuẩn ISO 5807:**
> - **Hình bầu dục `([...])`:** Điểm Bắt đầu (`Start`) và Kết thúc (`End`).
> - **Hình chữ nhật `[...]`:** Bước xử lý nội bộ (`Process`).
> - **Hình bình hành `[/.../]`:** Thao tác Nhập / Xuất dữ liệu (`Input / Output`).
> - **Hình thoi `{...}`:** Điểm kiểm tra điều kiện rẽ nhánh (`Decision: Đúng / Sai`).
> - **Hình tròn nhỏ `(( ))`:** Điểm nối vòng lặp trong trang (`On-Page Connector`).

### 2.1. Lưu Đồ Con A: Thuật Toán Trạm Bay UAV (ESP32 Firmware)

```mermaid
flowchart TD
    A1(["Bắt đầu (Start)"]) --> A2["Khởi tạo ngoại vi & WDT"]
    A2 --> A_LOOP(( ))
    A_LOOP --> A3["Reset bộ đếm Watchdog"]
    A3 --> A4{"Có lệnh từ UART?"}

    A4 -->|"Đúng"| A4_IO[/"Nhận lệnh & gửi ACK"/]
    A4_IO --> A5{"Đủ chu kỳ lấy mẫu?"}
    A4 -->|"Sai"| A5

    A5 -->|"Đúng"| A6[/"Đọc cảm biến & áp pin"/]
    A6 --> A7{"Dữ liệu đo hợp lệ?"}

    A7 -->|"Sai"| A7_ERR["Gán null & khởi tạo lại"]
    A7_ERR --> A8["Đóng gói bản tin JSON"]
    A7 -->|"Đúng"| A8

    A8 --> A9[/"Phát gói tin qua LoRa"/]
    A9 --> A10{"Ngắt nguồn / Dừng?"}
    A5 -->|"Sai (Chưa tới hạn)"| A10

    A10 -->|"Sai (Lặp chu kỳ kế tiếp)"| A_LOOP
    A10 -->|"Đúng"| A11(["Kết thúc (End)"])
```

### 2.2. Lưu Đồ Con B: Thuật Toán Trạm Mặt Đất (ESP8266 & Gateway)

```mermaid
flowchart TD
    B1(["Bắt đầu (Start)"]) --> B2["Khởi tạo Serial, LoRa, I2C"]
    B2 --> B_LOOP(( ))
    B_LOOP --> B3{"Nhận gói tin LoRa?"}

    B3 -->|"Đúng"| B4["Cập nhật mốc Heartbeat"]
    B4 --> B5[/"Đọc cảm biến mặt đất"/]
    B5 --> B6[/"Xuất gói Online qua USB"/]
    B6 --> B7{"Có lệnh từ máy tính?"}

    B3 -->|"Sai"| B3_TM{"Quá hạn 12 giây?"}
    B3_TM -->|"Đúng"| B3_OUT[/"Xuất gói Offline USB"/]
    B3_OUT --> B7
    B3_TM -->|"Sai"| B7

    B7 -->|"Đúng"| B8[/"Truyền lệnh qua LoRa"/]
    B8 --> B9{"Đóng cổng / Dừng?"}
    B7 -->|"Sai"| B9

    B9 -->|"Sai (Lặp vòng quét kế tiếp)"| B_LOOP
    B9 -->|"Đúng"| B10(["Kết thúc (End)"])
```

---

## 3. End-to-End Telemetry & Command Data Flow (Luồng Dữ Liệu & Điều Khiển 2 Chiều)

> **Quy ước mũi tên tuần tự:**
> - **Mũi tên nét liền (`->>`):** Luồng dữ liệu cảm biến và lưu trữ cơ sở dữ liệu (*Data Bus*).
> - **Mũi tên nét đứt (`-->>`):** Luồng lệnh điều khiển từ người dùng và gói xác nhận (*Control & ACK*).

```mermaid
sequenceDiagram
    autonumber
    participant S1 as Khối Cảm Biến #1, #2 & Pin
    participant E32 as Khối MCU & LoRa UAV (ESP32)
    participant G82 as Khối MCU & LoRa Đất (ESP8266)
    participant PY as Khối Lưu Trữ (gateway.py + SQLite)
    participant UI as Khối Hiển Thị (Streamlit UI)

    S1->>E32: Đọc I2C0_SDA (t1, p1), I2C1_SDA (t2, p2), ADC1 (vbat)
    E32->>G82: Phát RF Data: {"seq":12,"t1":31.04,"h1":null,"p1":1005.8,...}
    G82->>G82: Đọc I2C_SDA Cảm biến #3 mặt đất (t3=33.14, p3=1005.83)
    G82->>PY: Truyền USB_UART: {"status":"online","seq":12,...,"t3":33.14,"p3":1005.83}
    PY->>PY: Ghi bảng readings & events vào SQLite WAL (uav_data.db)
    PY->>UI: Cập nhật đồ thị thời gian thực & tính PDR, AoI, MAE, RMSE
    UI-->>PY: Người dùng phát lệnh điều khiển (SPEED_1S / SET_FREQ / PING)
    PY-->>G82: Gửi CTRL_CMD "SPEED_1S\n" qua USB_UART
    G82-->>E32: Phát lệnh "SPEED_1S\n" qua kênh điều khiển RF 433MHz
    E32-->>G82: Trả gói xác nhận {"src":"uav","ack":"SPEED_1S"}
    G82-->>PY: Truyền USB_UART: {"status":"ack","ack":"SPEED_1S"}
    PY-->>UI: Hiển thị trạng thái xác nhận trong bảng ACK & Nhật ký
```
