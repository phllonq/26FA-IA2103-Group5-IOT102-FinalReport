"""
gateway.py - Đọc cổng COM của trạm mặt đất (ESP8266), parse JSON, lưu SQLite, gửi lệnh.

Định dạng dòng JSON từ ESP8266:
  {"status":"online","seq":1,"t1":..,"h1":..,"p1":..,"t2":..,"h2":..,"p2":..,
   "bat":85,"vbat":11.8,"pwr":"bat","t3":..,"h3":..,"p3":..}
  {"status":"offline","t3":..,"h3":..,"p3":..}
  {"status":"ack","ack":"PING"}
Lệnh gửi xuống: SPEED_1S, SPEED_5S, RESET_UAV, SET_FREQ:n, PING
"""
import json
import re
import sqlite3
import threading
import time
from collections import deque
from datetime import datetime

ALLOWED_CMDS = [
    re.compile(r"^SPEED_1S$"),
    re.compile(r"^SPEED_5S$"),
    re.compile(r"^RESET_UAV$"),
    re.compile(r"^PING$"),
    re.compile(r"^SET_FREQ:([1-9]|[1-5][0-9]|60)$"),
]

SENSOR_COLS = ["seq", "t1", "h1", "p1", "t2", "h2", "p2",
               "bat", "vbat", "pwr", "t3", "h3", "p3"]

SCHEMA = """
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
"""


def open_serial(port, baud):
    """Mở cổng COM thật (hỗ trợ cả URL như loop:// để test)."""
    import serial  # import muộn để module vẫn import được khi chưa cài pyserial
    return serial.serial_for_url(port, baudrate=baud, timeout=1)


def _num(v):
    """Chỉ nhận số hữu hạn; còn lại -> None (NULL trong DB)."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        if v != v or v in (float("inf"), float("-inf")):
            return None
        return float(v)
    return None


class Gateway:
    def __init__(self, db_path="uav_data.db", serial_factory=open_serial):
        self.db_path = db_path
        self._serial_factory = serial_factory
        self._ser = None
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()          # bảo vệ trạng thái dùng chung
        self._tx_lock = threading.Lock()       # bảo vệ ghi cổng COM
        self._db_lock = threading.Lock()
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript(SCHEMA)
        self._db.commit()

        # trạng thái chia sẻ với UI
        self.connected = False
        self.port = None
        self.error = None
        self.link_status = "unknown"           # online | offline | unknown
        self.latest = {}                       # gói dữ liệu cuối cùng
        self.last_msg_time = None              # lần cuối nhận BẤT KỲ dòng JSON nào từ gateway
        self.last_online_time = None           # lần cuối nhận gói online từ UAV
        self.acks = deque(maxlen=20)
        self.bad_lines = 0

    # ---------------- DB ----------------
    def _event(self, kind, detail=""):
        now = time.time()
        with self._db_lock:
            self._db.execute(
                "INSERT INTO events(ts, ts_epoch, kind, detail) VALUES (?,?,?,?)",
                (datetime.fromtimestamp(now).isoformat(timespec="seconds"), now, kind, detail),
            )
            self._db.commit()

    def _insert_reading(self, msg):
        now = time.time()
        row = [datetime.fromtimestamp(now).isoformat(timespec="seconds"), now, msg["status"]]
        for col in SENSOR_COLS:
            v = msg.get(col)
            if col == "pwr":
                row.append(v if isinstance(v, str) else None)
            elif col == "seq":
                n = _num(v)
                row.append(int(n) if n is not None else None)
            else:
                row.append(_num(v))
        with self._db_lock:
            self._db.execute(
                "INSERT INTO readings(ts, ts_epoch, status, seq, t1, h1, p1, t2, h2, p2, "
                "bat, vbat, pwr, t3, h3, p3) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                row,
            )
            self._db.commit()

    # ---------------- XỬ LÝ MỘT DÒNG ----------------
    def handle_line(self, line):
        line = line.strip()
        if not line:
            return
        try:
            msg = json.loads(line)
            if not isinstance(msg, dict):
                raise ValueError("not an object")
        except ValueError:
            with self._lock:
                self.bad_lines += 1
            return

        status = msg.get("status")
        now = time.time()
        with self._lock:
            self.last_msg_time = now

        if status == "online":
            self._insert_reading(msg)
            with self._lock:
                prev = self.link_status
                self.link_status = "online"
                self.latest = msg
                self.last_online_time = now
            if prev == "offline":
                self._event("link_up", "UAV online trở lại")
        elif status == "offline":
            self._insert_reading(msg)
            with self._lock:
                prev = self.link_status
                self.link_status = "offline"
                # giữ số liệu mặt đất mới nhất, UAV để nguyên lần cuối
                merged = dict(self.latest)
                for k in ("t3", "h3", "p3"):
                    merged[k] = msg.get(k)
                merged["status"] = "offline"
                self.latest = merged
            if prev != "offline":
                self._event("link_down", "Mất kết nối LoRa với UAV")
        elif status == "ack":
            ack = str(msg.get("ack", ""))
            with self._lock:
                self.acks.appendleft((datetime.now().strftime("%H:%M:%S"), ack))
            self._event("ack", ack)
        # trạng thái lạ: bỏ qua

    # ---------------- LUỒNG ĐỌC ----------------
    def _reader(self, ser):
        buf = b""
        while not self._stop.is_set():
            try:
                chunk = ser.readline()
            except Exception as e:          # rút cáp USB, cổng bị đóng...
                with self._lock:
                    self.error = f"Mất cổng COM: {e}"
                    self.connected = False
                self._event("serial_error", str(e))
                return
            if not chunk:
                continue
            buf += chunk
            if not buf.endswith(b"\n"):
                continue                    # chưa đủ một dòng (timeout giữa chừng)
            text = buf.decode("utf-8", errors="ignore")
            buf = b""
            self.handle_line(text)

    # ---------------- ĐIỀU KHIỂN ----------------
    def connect(self, port, baud=115200):
        self.disconnect()
        try:
            ser = self._serial_factory(port, baud)
        except Exception as e:
            with self._lock:
                self.error = f"Không mở được {port}: {e}"
                self.connected = False
            return False
        self._ser = ser
        self._stop.clear()
        with self._lock:
            self.connected = True
            self.port = port
            self.error = None
            self.link_status = "unknown"
            self.last_msg_time = None
        self._thread = threading.Thread(target=self._reader, args=(ser,), daemon=True)
        self._thread.start()
        self._event("connect", f"{port} @ {baud}")
        return True

    def disconnect(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        if self._ser is not None:
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None
        with self._lock:
            was = self.connected
            self.connected = False
        if was:
            self._event("disconnect", self.port or "")

    def send_command(self, cmd):
        """Gửi lệnh (đã kiểm tra whitelist). Trả về (ok, thông báo)."""
        cmd = cmd.strip().upper().strip("<>")
        if not any(p.match(cmd) for p in ALLOWED_CMDS):
            return False, f"Lệnh không hợp lệ: {cmd}"
        if not self.connected or self._ser is None:
            return False, "Chưa kết nối cổng COM"
        try:
            with self._tx_lock:
                self._ser.write((cmd + "\n").encode("ascii"))
                self._ser.flush()
        except Exception as e:
            return False, f"Lỗi gửi lệnh: {e}"
        self._event("command", cmd)
        return True, f"Đã gửi: {cmd}"

    # ---------------- ĐỌC TRẠNG THÁI CHO UI ----------------
    def snapshot(self):
        with self._lock:
            return {
                "connected": self.connected,
                "port": self.port,
                "error": self.error,
                "link_status": self.link_status,
                "latest": dict(self.latest),
                "last_msg_age": (time.time() - self.last_msg_time) if self.last_msg_time else None,
                "last_online_age": (time.time() - self.last_online_time) if self.last_online_time else None,
                "acks": list(self.acks),
                "bad_lines": self.bad_lines,
            }
