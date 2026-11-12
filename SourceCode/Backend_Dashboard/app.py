"""
app.py - Giao diện Streamlit giám sát môi trường IoT-UAV.
Chạy:  streamlit run app.py
Yêu cầu: streamlit>=1.37, pyserial, pandas
"""
import sqlite3
import time

import pandas as pd
import streamlit as st

from gateway import Gateway

DB_PATH = "uav_data.db"
# Nếu gateway im lặng quá ngưỡng này (ESP8266 báo offline mỗi 5 s) -> coi là mất cả cáp USB/gateway
GATEWAY_SILENT_S = 20

st.set_page_config(page_title="Giám sát môi trường IoT-UAV", page_icon="🛰️", layout="wide")


@st.cache_resource
def get_gateway():
    return Gateway(DB_PATH)


gw = get_gateway()


def list_ports():
    try:
        from serial.tools import list_ports
        return [p.device for p in list_ports.comports()]
    except Exception:
        return []


def fmt(v, unit="", dec=2):
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    try:
        return f"{float(v):.{dec}f}{unit}"
    except (TypeError, ValueError):
        return str(v)


def delta(a, b, unit=""):
    try:
        if a is None or b is None:
            return None
        return f"{float(a) - float(b):+.2f}{unit}"
    except (TypeError, ValueError):
        return None


def load_history(minutes):
    since = time.time() - minutes * 60
    con = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(
            "SELECT * FROM readings WHERE ts_epoch >= ? ORDER BY ts_epoch", con, params=(since,)
        )
        ev = pd.read_sql_query(
            "SELECT ts, kind, detail FROM events ORDER BY id DESC LIMIT 30", con
        )
    finally:
        con.close()
    if not df.empty:
        df["time"] = pd.to_datetime(df["ts"])
    return df, ev


# ======================= SIDEBAR: KẾT NỐI =======================
with st.sidebar:
    st.header("Kết nối trạm mặt đất")
    ports = list_ports()
    port = st.selectbox("Cổng COM", ports if ports else ["(không thấy cổng)"])
    manual = st.text_input("Hoặc nhập tay (VD: COM5, /dev/ttyUSB0)", "")
    baud = st.selectbox("Baudrate", [115200, 9600], index=0)
    target = manual.strip() or port

    c1, c2 = st.columns(2)
    if c1.button("Kết nối", use_container_width=True, type="primary"):
        if gw.connect(target, baud):
            st.success(f"Đã mở {target}")
        else:
            st.error(gw.snapshot()["error"])
    if c2.button("Ngắt", use_container_width=True):
        gw.disconnect()

    st.caption(
        "Đóng Serial Monitor của Arduino IDE trước khi kết nối (cổng COM chỉ một chương trình dùng được). "
        "Mở cổng có thể làm ESP8266 tự reset, đó là bình thường."
    )
    st.divider()
    minutes = st.slider("Khoảng thời gian biểu đồ (phút)", 1, 120, 10)
    refresh = st.select_slider("Tự làm mới (giây)", options=[1, 2, 3, 5, 10], value=2)

    st.divider()
    st.header("Gửi lệnh lên UAV")
    cc1, cc2 = st.columns(2)
    cmd_result = None
    if cc1.button("Chu kỳ 1 s", use_container_width=True):
        cmd_result = gw.send_command("SPEED_1S")
    if cc2.button("Chu kỳ 5 s", use_container_width=True):
        cmd_result = gw.send_command("SPEED_5S")
    n = st.number_input("Chu kỳ tùy chỉnh (giây)", 1, 60, 3)
    if st.button(f"Đặt chu kỳ {n} s", use_container_width=True):
        cmd_result = gw.send_command(f"SET_FREQ:{int(n)}")
    if st.button("Ping UAV", use_container_width=True):
        cmd_result = gw.send_command("PING")
    with st.expander("Lệnh nguy hiểm"):
        sure = st.checkbox("Tôi hiểu UAV sẽ khởi động lại")
        if st.button("Reset UAV", use_container_width=True, disabled=not sure):
            cmd_result = gw.send_command("RESET_UAV")
    if cmd_result:
        (st.success if cmd_result[0] else st.error)(cmd_result[1])


# ======================= KHU VỰC TỰ LÀM MỚI =======================
@st.fragment(run_every=refresh)
def live_view():
    snap = gw.snapshot()
    d = snap["latest"]

    # ---- Banner trạng thái ----
    if not snap["connected"]:
        st.error(snap["error"] or "Chưa kết nối cổng COM. Chọn cổng ở thanh bên rồi bấm Kết nối.")
    elif snap["last_msg_age"] is None or snap["last_msg_age"] > GATEWAY_SILENT_S:
        st.error("🔴 MẤT TÍN HIỆU TỪ GATEWAY (ESP8266 không gửi dữ liệu, kiểm tra cáp USB / nguồn).")
    elif snap["link_status"] == "offline":
        st.error("🔴 UAV OFFLINE: mất kết nối LoRa với UAV.")
    elif snap["link_status"] == "online":
        age = snap["last_online_age"]
        st.success(f"🟢 UAV ONLINE (gói cuối cách đây {age:.0f} s)")
    else:
        st.warning("🟡 Đã mở cổng, đang chờ gói dữ liệu đầu tiên...")

    # ---- Số liệu hiện tại ----
    uav_ok = snap["link_status"] == "online" and snap["connected"]
    st.subheader("Số liệu hiện tại" + ("" if uav_ok else " (lần cuối nhận được)"))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**BME280 #1 (không vỏ)**")
        st.metric("Nhiệt độ", fmt(d.get("t1"), " °C"), delta(d.get("t1"), d.get("t2"), " vs #2"))
        st.metric("Độ ẩm", fmt(d.get("h1"), " %"))
        st.metric("Áp suất", fmt(d.get("p1"), " hPa"))
    with col2:
        st.markdown("**BME280 #2 (có vỏ)**")
        st.metric("Nhiệt độ", fmt(d.get("t2"), " °C"))
        st.metric("Độ ẩm", fmt(d.get("h2"), " %"))
        st.metric("Áp suất", fmt(d.get("p2"), " hPa"))
    with col3:
        st.markdown("**BME280 #3 (mặt đất)**")
        st.metric("Nhiệt độ", fmt(d.get("t3"), " °C"), delta(d.get("t2"), d.get("t3"), " UAV−đất"))
        st.metric("Độ ẩm", fmt(d.get("h3"), " %"))
        st.metric("Áp suất", fmt(d.get("p3"), " hPa"), delta(d.get("p2"), d.get("p3"), " UAV−đất"))
    with col4:
        st.markdown("**Nguồn UAV**")
        if d.get("pwr") == "usb" or d.get("bat") is None:
            st.metric("Pin", "USB" if d.get("pwr") == "usb" else "—")
        else:
            bat = d.get("bat")
            st.metric("Pin LiPo", fmt(bat, " %", 0), fmt(d.get("vbat"), " V"), delta_color="off")
            try:
                if float(bat) <= 10:
                    st.error("PIN NGUY HIỂM! Hạ cánh ngay.")
                elif float(bat) <= 20:
                    st.warning("Pin yếu")
            except (TypeError, ValueError):
                pass
        st.metric("Số thứ tự gói", fmt(d.get("seq"), "", 0))
        st.caption(f"Dòng lỗi/nhiễu bỏ qua: {snap['bad_lines']}")

    # ---- Biểu đồ ----
    df, ev = load_history(minutes)
    st.subheader(f"Biểu đồ {minutes} phút gần nhất")
    if df.empty:
        st.info("Chưa có dữ liệu trong khoảng thời gian này.")
    else:
        d_idx = df.set_index("time")
        g1, g2 = st.columns(2)
        g1.markdown("Nhiệt độ (°C)")
        g1.line_chart(d_idx[["t1", "t2", "t3"]])
        g2.markdown("Độ ẩm (%)")
        g2.line_chart(d_idx[["h1", "h2", "h3"]])
        g3, g4 = st.columns(2)
        g3.markdown("Áp suất (hPa)")
        g3.line_chart(d_idx[["p1", "p2", "p3"]])
        g4.markdown("Pin UAV (%)")
        g4.line_chart(d_idx[["bat"]])

    # ---- Nhật ký ----
    l1, l2 = st.columns(2)
    with l1:
        st.subheader("Sự kiện")
        st.dataframe(ev, use_container_width=True, hide_index=True, height=250)
    with l2:
        st.subheader("Phản hồi lệnh từ UAV")
        if snap["acks"]:
            st.dataframe(
                pd.DataFrame(snap["acks"], columns=["Giờ", "Phản hồi"]),
                use_container_width=True, hide_index=True, height=250,
            )
        else:
            st.caption("Chưa có phản hồi.")


st.title("🛰️ Giám sát môi trường IoT-UAV")
live_view()

# ======================= XUẤT DỮ LIỆU =======================
with st.expander("Tải dữ liệu (CSV)"):
    con = sqlite3.connect(DB_PATH)
    try:
        all_df = pd.read_sql_query("SELECT * FROM readings ORDER BY ts_epoch", con)
    finally:
        con.close()
    st.caption(f"Tổng số bản ghi: {len(all_df)}")
    st.download_button(
        "Tải toàn bộ readings.csv",
        all_df.to_csv(index=False).encode("utf-8"),
        file_name="uav_readings.csv",
        mime="text/csv",
    )
