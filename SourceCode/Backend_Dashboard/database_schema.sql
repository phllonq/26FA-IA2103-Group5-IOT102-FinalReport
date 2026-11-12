-- Schema SQLite của backend serial (gateway.py tự tạo khi chạy lần đầu).
-- readings: mỗi gói online/offline từ trạm mặt đất; events: kết nối, mất/có lại tín hiệu, lệnh, ack.
-- Giá trị cảm biến lỗi/thiếu được lưu NULL (không phải 0).

CREATE TABLE IF NOT EXISTS readings (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT NOT NULL,
    ts_epoch  REAL NOT NULL,
    status    TEXT NOT NULL,
    seq INTEGER, t1 REAL, h1 REAL, p1 REAL,
    t2 REAL, h2 REAL, p2 REAL,
    bat REAL, vbat REAL, pwr TEXT,
    t3 REAL, h3 REAL, p3 REAL
);
CREATE INDEX IF NOT EXISTS idx_readings_epoch ON readings(ts_epoch);
CREATE TABLE IF NOT EXISTS events (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ts       TEXT NOT NULL,
    ts_epoch REAL NOT NULL,
    kind     TEXT NOT NULL,
    detail   TEXT
);
