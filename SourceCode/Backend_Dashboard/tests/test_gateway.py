"""Test gateway.py bằng cổng COM giả (không cần phần cứng / pyserial). Chạy: python tests/test_gateway.py"""
import os, queue, sqlite3, sys, tempfile, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gateway import Gateway


class FakeSerial:
    def __init__(self):
        self.q, self.sent, self.closed = queue.Queue(), [], False
    def feed(self, s): self.q.put(s.encode())
    def readline(self):
        try: return self.q.get(timeout=0.2)
        except queue.Empty: return b""
    def write(self, b): self.sent.append(b)
    def flush(self): pass
    def close(self): self.closed = True


def main():
    fake = FakeSerial()
    db = os.path.join(tempfile.mkdtemp(), "t.db")
    gw = Gateway(db, serial_factory=lambda p, b: fake)
    assert gw.connect("FAKE", 115200)

    fake.feed('{"status":"online","seq":1,"t1":25.5,"h1":60,"p1":1009.8,"t2":25.1,"h2":61,"p2":1009.7,'
              '"bat":null,"vbat":null,"pwr":"usb","t3":27.1,"h3":65,"p3":1011.2}\n')
    fake.feed('rac nhieu {{\n')
    fake.feed('{"status":"ack","ack":"PING"}\n')
    fake.feed('{"status":"offline","t3":27.2,"h3":65,"p3":null}\n')
    fake.feed('{"status":"offline","t3":27.3,"h3":65,"p3":1011}\n')
    fake.feed('{"status":"online","seq":2,"t1":null,"h1":null,"p1":null,"t2":25,"h2":61,"p2":1009,'
              '"bat":80,"vbat":11.9,"pwr":"bat","t3":27,"h3":65,"p3":1011}\n')
    time.sleep(1.2)

    s = gw.snapshot()
    assert s["link_status"] == "online" and s["bad_lines"] == 1 and s["acks"][0][1] == "PING"

    assert gw.send_command("speed_1s")[0] and gw.send_command("<SET_FREQ:3>")[0] and gw.send_command("RESET_UAV")[0]
    assert not gw.send_command("SET_FREQ:99")[0] and not gw.send_command("rm -rf /")[0]
    assert fake.sent == [b"SPEED_1S\n", b"SET_FREQ:3\n", b"RESET_UAV\n"]

    con = sqlite3.connect(db)
    assert con.execute("select count(*) from readings").fetchone()[0] == 4        # ack và rác không vào DB
    kinds = [r[0] for r in con.execute("select kind from events")]
    assert kinds.count("link_down") == 1 and kinds.count("link_up") == 1          # chỉ ghi khi đổi trạng thái
    assert con.execute("select t1 from readings where seq=2").fetchone()[0] is None  # NaN -> NULL
    gw.disconnect()
    assert fake.closed
    print("GATEWAY TEST OK")


if __name__ == "__main__":
    main()
