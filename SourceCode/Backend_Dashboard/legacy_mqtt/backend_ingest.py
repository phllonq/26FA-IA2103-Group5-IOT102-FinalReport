import json
import time
import sqlite3
import paho.mqtt.client as mqtt

DB_FILE = "uav_telemetry.db"
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot-uav/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[+] Kết nối Broker thành công! Đang lắng nghe topic: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"[-] Lỗi kết nối Broker, mã lỗi: {rc}")

def on_message(client, userdata, msg):
    try:
        # 1. Ghi nhận thời gian hệ thống nhận được gói tin (Epoch ms) để tính AoI
        t_received = int(time.time() * 1000)
        
        # 2. Giải mã Payload JSON từ Mock Publisher / ESP32
        payload = json.loads(msg.payload.decode('utf-8'))
        
        packet_id = payload.get("packet_id")
        flight_id = payload.get("flight_id", "FLIGHT_01")
        t_generated = payload.get("t_generated")
        
        # 3. Tính toán Metric RQ2: Age of Information (AoI)
        # AoI = Thời gian hiện tại trên Dashboard (nhận) - Thời gian thực tế lúc cảm biến đo
        aoi_ms = max(0, t_received - t_generated)
        
        # 4. Lưu toàn bộ dữ liệu thô và metric vào Database
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO uav_telemetry (
                    packet_id, t_generated, t_received, aoi_ms,
                    temperature, humidity, rssi, state, event,
                    latitude, longitude, altitude, flight_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                packet_id,
                t_generated,
                t_received,
                aoi_ms,
                payload.get("temperature"),
                payload.get("humidity"),
                payload.get("rssi"),
                payload.get("state"),
                1 if payload.get("event") else 0,
                payload.get("latitude"),
                payload.get("longitude"),
                payload.get("altitude"),
                flight_id
            ))
            conn.commit()
            
        print(f"[INGEST] Đã lưu Packet #{packet_id:04d} | AoI: {aoi_ms:4d} ms | State: {payload.get('state')}")

    except Exception as e:
        print(f"[-] Lỗi xử lý gói tin: {e}")

if __name__ == "__main__":
    print("[*] Khởi động Dịch vụ Nhận dữ liệu (Ingestion Daemon)...")
    client = mqtt.Client(client_id="UAV_Backend_Ingestion_Service")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[*] Đã dừng dịch vụ Ingestion.")

