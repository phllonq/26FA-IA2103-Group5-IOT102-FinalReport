import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Cấu hình giao diện Streamlit mở rộng toàn màn hình
st.set_page_config(page_title="IoT-UAV Monitoring", layout="wide", page_icon="🚁")

# Tự động refresh trang mỗi 2000 milliseconds (2 giây)
st_autorefresh(interval=2000, key="data_refresh")

DB_FILE = "uav_telemetry.db"

def load_data(limit=100):
    """Đọc dữ liệu mới nhất từ SQLite phục vụ vẽ biểu đồ và hiển thị metric"""
    with sqlite3.connect(DB_FILE) as conn:
        query = f"SELECT * FROM uav_telemetry ORDER BY id DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
    # Lật ngược dataframe lại để dữ liệu mới nằm bên phải đồ thị
    return df.iloc[::-1].reset_index(drop=True) if not df.empty else df

def get_full_data():
    """Đọc toàn bộ dữ liệu từ DB để xuất file CSV theo chuẩn quy định"""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query("SELECT * FROM uav_telemetry ORDER BY id ASC", conn)
    return df

st.title("🚁 Adaptive IoT-UAV Environmental Monitoring Dashboard")
st.markdown("Hệ thống hiển thị dữ liệu thời gian thực và đánh giá hiệu năng mạng theo **RQ1 & RQ2**.")

df = load_data(100)

if df.empty:
    st.warning("Chưa có dữ liệu. Hãy đảm bảo `mock_publisher.py` và `backend_ingest.py` đang chạy.")
else:
    # Lấy hàng dữ liệu mới nhất để hiển thị Metric hiện tại
    latest = df.iloc[-1]
    
    st.header("1. Current Flight & Sensor Status")
    
    # Hàng 1: Các thông số cảm biến môi trường (Phục vụ RQ1)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature (°C)", f"{latest['temperature']:.2f} °C")
    col2.metric("Humidity (%)", f"{latest['humidity']:.2f} %")
    col3.metric("Altitude (m)", f"{latest.get('altitude', 0):.2f} m")
    col4.metric("GPS Location", f"{latest.get('latitude', 0):.4f}, {latest.get('longitude', 0):.4f}")
    
    st.markdown("---")
    
    # Hàng 2: Các thông số Truyền thông & FSM (Phục vụ RQ2)
    st.header("2. Adaptive Communication Performance")
    col5, col6, col7, col8 = st.columns(4)
    
    # Đổi màu cảnh báo trạng thái
    state_color = "green" if latest['state'] == "GOOD" else "orange" if latest['state'] == "HOLD" else "red"
    col5.markdown(f"**State:** <span style='color:{state_color}; font-size:20px; font-weight:bold;'>{latest['state']}</span>", unsafe_allow_html=True)
    
    col6.metric("RSSI (dBm)", f"{latest['rssi']} dBm")
    col7.metric("Age of Information (AoI)", f"{latest['aoi_ms']} ms")
    
    # Tính Packet Loss trong cửa sổ 100 gói tin gần nhất
    max_id = df['packet_id'].max()
    min_id = df['packet_id'].min()
    expected_packets = max_id - min_id + 1
    actual_packets = len(df)
    packet_loss_rate = ((expected_packets - actual_packets) / expected_packets) * 100 if expected_packets > 0 else 0
    col8.metric("Estimated Packet Loss", f"{packet_loss_rate:.1f} %")
    
    st.markdown("---")

    # Hàng 3: Biểu đồ trực quan
    st.header("3. Real-time Analysis Charts")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Temperature Fluctuation (RQ1)")
        fig_temp = px.line(df, x='t_generated', y='temperature', 
                           title="Biến thiên Nhiệt độ theo thời gian",
                           labels={'t_generated': 'Timestamp', 'temperature': 'Temp (°C)'},
                           template="plotly_white")
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_chart2:
        st.subheader("RSSI & FSM State Behavior (RQ2)")
        # Vẽ biểu đồ RSSI có vạch giới hạn -80 và -90 để minh họa khoảng Hysteresis
        fig_rssi = px.line(df, x='t_generated', y='rssi', 
                           title="Cường độ tín hiệu và Vùng Hysteresis",
                           labels={'t_generated': 'Timestamp', 'rssi': 'RSSI (dBm)'},
                           template="plotly_white")
        fig_rssi.add_hline(y=-80, line_dash="dash", line_color="green", annotation_text="GOOD Threshold")
        fig_rssi.add_hline(y=-90, line_dash="dash", line_color="red", annotation_text="DEGRADED Threshold")
        st.plotly_chart(fig_rssi, use_container_width=True)

    st.markdown("---")
    
    # Tính năng Export dữ liệu (Đồng bộ với Analytics)
    st.header("4. Data Export (For Calibration & Evaluation)")
    st.write("Tải tập dữ liệu gốc chuẩn hóa để thực hiện huấn luyện mô hình Linear Regression và phân tích đánh giá metrics mạng.")
    
    df_full = get_full_data()
    csv = df_full.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download dataset_cleaned.csv",
        data=csv,
        file_name='dataset_cleaned.csv',
        mime='text/csv',
    )

