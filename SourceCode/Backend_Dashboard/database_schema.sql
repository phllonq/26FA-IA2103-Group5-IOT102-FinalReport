DROP TABLE IF EXISTS uav_telemetry;

CREATE TABLE uav_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id INTEGER NOT NULL,            -- Số đếm gói tin tăng dần (tính PDR, Packet Loss cho RQ2)
    t_generated BIGINT NOT NULL,           -- Epoch ms khi ESP32 đóng gói
    t_received BIGINT NOT NULL,            -- Epoch ms khi Backend nhận được gói
    aoi_ms BIGINT,                         -- Age of Information = t_received - t_generated
    temperature REAL,                      -- Nhiệt độ thô từ BME280 (°C)
    humidity REAL,                         -- Độ ẩm tương đối thô từ BME280 (%)
    rssi INTEGER,                          -- Cường độ tín hiệu Wi-Fi (dBm)
    state TEXT,                            -- Trạng thái FSM: GOOD, HOLD, DEGRADED, EVENT
    event INTEGER DEFAULT 0,               -- Cờ kích hoạt đột biến (0: False, 1: True)
    latitude REAL,                         -- GPS Lat
    longitude REAL,                        -- GPS Lon
    altitude REAL,                         -- Độ cao (m)
    flight_id TEXT DEFAULT 'FLIGHT_01'     -- Mã đợt bay thử nghiệm
);

CREATE INDEX IF NOT EXISTS idx_t_generated ON uav_telemetry(t_generated);
CREATE INDEX IF NOT EXISTS idx_packet_id ON uav_telemetry(packet_id);
