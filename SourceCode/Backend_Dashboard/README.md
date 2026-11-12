# Backend Dashboard (Streamlit + SQLite)

Đọc cổng COM của trạm mặt đất (ESP8266), lưu SQLite và hiển thị giao diện giám sát.

```
pip install -r requirements.txt
streamlit run app.py          # cần streamlit >= 1.37
python tests/test_gateway.py  # test gateway bằng cổng COM giả, không cần phần cứng
```

Trong giao diện: chọn cổng COM của ESP8266 → baud 115200 → **Kết nối**. Đóng Serial Monitor của Arduino IDE trước.

| File | Vai trò |
|---|---|
| `gateway.py` | Luồng đọc COM, parse JSON, ghi SQLite, gửi lệnh (whitelist) |
| `app.py` | Giao diện: trạng thái ONLINE/OFFLINE, số liệu, biểu đồ, gửi lệnh, xuất CSV |
| `database_schema.sql` | Schema `readings` và `events` (gateway tự tạo) |
| `legacy_mqtt/` | Bản backend MQTT giả lập ban đầu, giữ lại để tham khảo |

Dữ liệu chạy thật nằm ở `uav_data.db` (đã `.gitignore`). Định dạng bản tin: xem `../Protocol/README.md`.
