import json
import random
import time
import paho.mqtt.client as mqtt

# Cấu hình MQTT Broker dùng chung cho dự án
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_TELEMETRY = "iot-uav/telemetry"

def run_mock_publisher(mode="ADAPTIVE"):
    """
    Giả lập ESP32 phát dữ liệu vi khí hậu và telemetry lên MQTT Broker.
    mode: 'ADAPTIVE' (FSM Hysteresis + Event-triggered) hoặc 'FIXED' (1 pkt/s cố định)
    """
    client = mqtt.Client(client_id=f"MOCK_ESP32_{random.randint(1000, 9999)}")
    print(f"[*] Đang kết nối tới Broker {BROKER}:{PORT}...")
    
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
        print(f"[+] Kết nối Broker thành công! Chế độ truyền thông: {mode}\n")
    except Exception as e:
        print(f"[-] Không thể kết nối tới Broker: {e}")
        return

    packet_id = 1
    flight_id = "FLIGHT_MOCK_01"
    
    # Tọa độ và độ cao bay ban đầu
    base_lat = 10.875124
    base_lon = 106.800312
    base_alt = 15.0
    
    # Giá trị cảm biến BME280 ban đầu
    current_temp = 29.45
    current_rh = 68.20
    current_state = "GOOD"
    
    try:
        while True:
            # 1. Giả lập biến thiên RSSI theo khoảng cách bay (-95 dBm đến -70 dBm)
            rssi = random.randint(-95, -70)
            
            # 2. Máy trạng thái Adaptive FSM kèm Hysteresis (RQ2)
            if rssi > -80:
                current_state = "GOOD"
            elif rssi < -90:
                current_state = "DEGRADED"
            # Nếu -90 <= rssi <= -80: Giữ nguyên trạng thái trước đó (HOLD)

            # 3. Giả lập giá trị vi khí hậu
            temp_delta = round(random.uniform(-0.25, 0.35), 2)
            rh_delta = round(random.uniform(-0.6, 0.7), 2)
            
            # Mô phỏng đột biến vi khí hậu để kích hoạt cờ EVENT (|ΔT| >= 0.5°C hoặc |ΔH| >= 2.0%)
            is_event = False
            if random.random() < 0.07:  # 7% xác suất xuất hiện sự kiện đột biến
                temp_delta = 0.55
                is_event = True

            current_temp = round(current_temp + temp_delta, 2)
            current_rh = round(max(20.0, min(100.0, current_rh + rh_delta)), 2)

            # 4. Đóng gói JSON Payload chuẩn 100% quy chuẩn của nhóm
            t_generated = int(time.time() * 1000)  # Bắt buộc dạng Unix Epoch ms để tính AoI
            payload = {
                "packet_id": packet_id,
                "flight_id": flight_id,
                "scenario": "S3_SHIELDED" if mode == "ADAPTIVE" else "FIXED_BASELINE",
                "t_generated": t_generated,
                "temperature": current_temp,
                "humidity": current_rh,
                "rssi": rssi,
                "state": "EVENT" if is_event else current_state,
                "event": is_event,
                "latitude": round(base_lat + (packet_id * 0.000015), 6),
                "longitude": round(base_lon + (packet_id * 0.000015), 6),
                "altitude": round(base_alt + random.uniform(-0.3, 0.4), 1)
            }

            # 5. Phát gói tin lên Broker
            payload_str = json.dumps(payload)
            client.publish(TOPIC_TELEMETRY, payload_str, qos=0)
            print(f"[PUB #{packet_id:04d}] State: {payload['state']:<8} | RSSI: {rssi:3d} dBm | Temp: {current_temp:.2f}°C | Event: {is_event}")

            packet_id += 1

            # 6. Điều phối tần suất phát gói tin (RQ2 Logic)
            if mode == "FIXED":
                time.sleep(1.0)  # Baseline: Luôn cố định 1 packet/giây
            else:
                if is_event:
                    time.sleep(0.5)  # Khi có EVENT: Phát lập tức
                elif current_state == "DEGRADED":
                    time.sleep(5.0)  # Vùng sóng yếu: Giảm tải truyền dẫn xuống 1 packet/5 giây
                else:
                    time.sleep(1.0)  # Vùng sóng tốt (GOOD/HOLD): 1 packet/giây

    except KeyboardInterrupt:
        print("\n[*] Dừng chương trình giả lập Mock Publisher.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    run_mock_publisher(mode="ADAPTIVE")

