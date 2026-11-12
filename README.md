# Adaptive-IoT-UAV-Monitoring


> **Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication**

[![Course](https://img.shields.io/badge/Course-IOT102--Fall2026-blue)](https://fpt.edu.vn)
[![Framework](https://img.shields.io/badge/Learning--Model-PBL%20%2B%20RBL-green)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---


## 1. Project Overview

## 2. Project Objectives

## 3. Research Questions
### RQ1 — Downwash-Aware Sensing
### RQ2 — Adaptive Communication

## 4. Proposed System Architecture
### UAV Telemetry Layer
### IoT Payload Layer

```
UAV (ESP32 + 2x BME280 + pin LiPo)
   │  LoRa E32 (9600 8N1), JSON 1 dòng
   ▼
Trạm mặt đất (ESP8266 + BME280 tham chiếu)
   │  USB Serial 115200, JSON 1 dòng  (heartbeat: offline sau 12 s mất tín hiệu)
   ▼
PC: Streamlit + SQLite  ──lệnh (SPEED_1S/5S, SET_FREQ:n, PING, RESET_UAV)──► Ground ──► UAV
```

- Hai BME280 trên UAV (không vỏ và có vỏ Pagoda) cùng một BME280 mặt đất cho phép so sánh số liệu cảm biến.
- Firmware UAV có Watchdog phần cứng, đo pin LiPo 3S, tự khởi tạo lại cảm biến khi rớt; cảm biến lỗi báo `null`.
- Đặc tả bản tin: [`SourceCode/Protocol`](SourceCode/Protocol/README.md). Sơ đồ nối dây: [`wiring_guide.md`](SourceCode/CAD_Schematic/wiring_guide.md).

## 5. Proposed Experimental Design
### RQ1
### RQ2

## 6. Planned Hardware & Software

**Phần cứng**

| Trạm | Thành phần |
|---|---|
| UAV | ESP32 DevKit V1, 2x BME280 (không vỏ / có vỏ Pagoda, hai bus I2C riêng), LoRa E32, pin LiPo + Mini 360 hạ áp 5 V, cầu phân áp đo pin |
| Mặt đất | ESP8266 NodeMCU, LoRa E32 (SoftwareSerial), BME280 tham chiếu, nguồn từ cổng USB |

**Phần mềm:** Arduino IDE (core esp32 3.x, esp8266), thư viện Adafruit BME280, Adafruit BMP280 (dự phòng khi module thực chất là BMP280), ArduinoJson 7; Python 3 với Streamlit, pyserial, pandas; SQLite.

### Build & Run

1. **Firmware:** mở `SourceCode/Firmware_UAV_ESP32/Firmware_UAV_ESP32.ino` (board *ESP32 Dev Module*) và `SourceCode/Firmware_Ground_ESP8266/Firmware_Ground_ESP8266.ino` (board *NodeMCU 1.0 (ESP-12E Module)*), rồi Upload.
2. **Backend:** `cd SourceCode/Backend_Dashboard && pip install -r requirements.txt && streamlit run app.py`, chọn cổng COM của ESP8266 trong giao diện.

## 7. Proposed Directory Structure

```
.
├── Documents/              Final Report, slides, proposal, poster
├── AI_Audit_Log/           AI Audit Log, ADR, evidence
├── Datasets/               Raw_Logs, RQ1_Sensing, RQ2_Communication, Processed
├── Diagrams/               Block diagram, flowchart, data flow
├── VideoDemo/              Video demo (optional)
└── SourceCode/
    ├── Firmware_UAV_ESP32/       Firmware trạm UAV (Arduino)
    ├── Firmware_Ground_ESP8266/  Firmware trạm mặt đất (Arduino)
    ├── Protocol/                 Đặc tả bản tin JSON và lệnh
    ├── Backend_Dashboard/        Streamlit + SQLite (legacy_mqtt/: bản MQTT cũ)
    ├── Data_Analytics/           Script phân tích, hiệu chuẩn, đánh giá RQ1/RQ2
    ├── CAD_Schematic/            Sơ đồ mạch, CAD vỏ Pagoda, wiring_guide.md
    ├── Hardware_Design/          Block diagram, schematic, flowchart (PDF)
    └── Flight_Controller/        PX4 parameters, mission plan
```

## 8. Planned Evaluation Metrics

## 9. Development Roadmap

## 10. AI Usage & Audit

## 11. References
