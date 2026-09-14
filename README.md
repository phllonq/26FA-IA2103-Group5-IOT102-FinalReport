# Adaptive-IoT-UAV-Monitoring

> **Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication**

[![Course](https://img.shields.io/badge/Course-IOT102--Fall2026-blue)](https://fpt.edu.vn)
[![Framework](https://img.shields.io/badge/Learning--Model-PBL%20%2B%20RBL-green)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 1. Giới thiệu Dự án (Project Overview)
Đề tài xây dựng hệ thống giám sát môi trường tích hợp trên UAV (Unmanned Aerial Vehicle), giải quyết các thách thức thực tế về sai số đo lường do luồng gió nén từ cánh quạt (*downwash*) và tối ưu hóa hiệu năng truyền thông IoT trong điều kiện tín hiệu suy giảm.

* **Môn học:** IOT102 - Internet of Things (Học kỳ Fall 2026 - Đại học FPT)[cite: 1]
* **Mô hình tích hợp:** Project-Based Learning (PBL) kết hợp Research-Based Learning (RBL)[cite: 1]

---

## 🔍 2. Vấn đề Nghiên cứu (Research Questions)
* **RQ1 (Downwash-Aware Sensing):** Khảo sát ảnh hưởng của điều kiện bay UAV (Ground, Hover, Forward Flight) đến sai số đo đạc nhiệt độ/độ ẩm của cảm biến BME280; đánh giá hiệu quả của màng chắn thông gió (*Ventilated Pagoda Shield*) kết hợp mô hình hiệu chuẩn Hồi quy tuyến tính (*Linear Regression Calibration*).
* **RQ2 (Adaptive Communication):** Xây dựng cơ chế truyền thông thích ứng dựa trên cường độ tín hiệu RSSI kết hợp sự biến thiên cảm biến (*Sensor-value variation*) và vùng đệm chống trượt trạng thái (*Hysteresis*); đánh giá sự đánh đổi giữa tỷ lệ giảm gói tin (*Packet Reduction*), độ tin cậy giao gói (*PDR*) và độ tươi dữ liệu (*Age of Information - AoI*).

---

## 🏗️ 3. Kiến trúc Hệ thống (System Architecture)
Hệ thống được thiết kế theo **Kiến trúc 2 luồng độc lập (Dual-Layer Architecture)**:
1. **UAV Telemetry Layer:** Cảm biến UAV (GPS/IMU/Barometer) ➔ Flight Controller (PX4/ArduPilot) ➔ MAVLink Protocol ➔ Ground Control Station (QGroundControl).
2. **IoT Payload Layer:** Cảm biến BME280 (Pagoda Shield) ➔ Vi điều khiển ESP32 ➔ Giao thức MQTT ➔ MQTT Broker ➔ Database / Cloud ➔ Web Dashboard real-time.

---

## 📂 4. Cấu trúc Thư mục Dự án (Directory Structure)
```text
26FA_SE201868_G1_IOT102_FinalReport/
├── README.md                   # Hướng dẫn tổng quan & quy trình chạy dự án
├── Documents/                  # Báo cáo IEEE (PDF/LaTeX) & Slide thuyết trình[cite: 1]
├── AI_Audit_Log/               # File NỘP RIÊNG ghi nhận 3-5 quyết định kỹ thuật AI[cite: 1]
├── Dataset/                    # Dữ liệu thô thực nghiệm (RQ1 & RQ2 logs)
├── VideoDemo/                  # File txt chứa link video demo hệ thống (<= 5 phút)[cite: 1]
└── SourceCode/                 # Mã nguồn toàn bộ hệ thống[cite: 1]
    ├── Hardware_Design/        # Block Diagram, Flowchart, Schematic & File 3D Shield (.stl)[cite: 1, 2]
    ├── ESP32_Firmware/         # Code C++ đọc BME280, FSM Hysteresis & MQTT
    ├── Flight_Controller/      # Cấu hình tham số PX4 & file mission plan waypoint[cite: 2]
    ├── Data_Analysis/          # Script Python xử lý data, Linear Regression & vẽ đồ thị[cite: 2]
    └── Web_Dashboard/          # Giao diện Web hiển thị real-time & chỉ số AoI[cite: 2]
