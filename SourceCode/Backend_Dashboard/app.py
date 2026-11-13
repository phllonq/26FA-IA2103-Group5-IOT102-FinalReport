import html
import sqlite3
import time

import altair as alt
import pandas as pd
import streamlit as st

from gateway import Gateway

DB_PATH = "uav_data.db"
# Nếu gateway im lặng quá ngưỡng này (ESP8266 báo offline mỗi 5 s) -> coi là mất cả cáp USB/gateway
GATEWAY_SILENT_S = 20

st.set_page_config(
    page_title="Giám sát môi trường IoT-UAV",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_html(raw_html: str):
    """Nén HTML trên một dòng để ngăn Markdown hiểu nhầm khoảng trắng thụt lề là khối code đen."""
    compact = "".join(line.strip() for line in raw_html.splitlines() if line.strip())
    st.markdown(compact, unsafe_allow_html=True)


def glass_notice(message: str, kind: str = "info"):
    """Hiển thị thông báo Liquid Glass thay cho st.error/st.info mặc định (tránh bị nền đen trong Dark Mode)."""
    icons = {
        "info": "✦",
        "success": "✓",
        "warning": "!",
        "error": "✕",
    }
    icon = icons.get(kind, "✦")
    safe_msg = html.escape(str(message))
    render_html(
        f"""
        <div class="liquid-notice {kind}">
            <div class="liquid-notice-icon {kind}">{icon}</div>
            <div class="liquid-notice-text">{safe_msg}</div>
        </div>
        """
    )


# ======================= DESIGN SYSTEM: APPLE LIQUID GLASS CSS =======================
def inject_liquid_glass_styles():
    render_html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            color-scheme: light !important;
            --primary: #F97316;
            --primary-hover: #EA580C;
            --primary-light: #FFF7ED;
            --primary-glow: rgba(249, 115, 22, 0.20);
            --bg-main: #F8FAFC;
            --glass-bg: rgba(255, 255, 255, 0.66);
            --glass-bg-strong: rgba(255, 255, 255, 0.80);
            --glass-border: rgba(255, 255, 255, 0.88);
            --glass-outline: rgba(226, 232, 240, 0.85);
            --text-primary: #171717;
            --text-secondary: #525252;
            --text-muted: #737373;
            --success: #16A34A;
            --warning: #F59E0B;
            --error: #EF4444;
            --radius-2xl: 24px;
            --radius-xl: 20px;
            --radius-lg: 16px;
            --radius-md: 14px;
            --shadow-liquid:
                0 12px 36px -6px rgba(15, 23, 42, 0.06),
                0 2px 8px -2px rgba(15, 23, 42, 0.04),
                inset 0 1.5px 0 rgba(255, 255, 255, 0.98),
                inset 0 -1px 0 rgba(255, 255, 255, 0.55);
            --shadow-liquid-hover:
                0 20px 44px -8px rgba(249, 115, 22, 0.15),
                0 4px 12px -2px rgba(249, 115, 22, 0.06),
                inset 0 1.5px 0 rgba(255, 255, 255, 1),
                inset 0 -1px 0 rgba(249, 115, 22, 0.18);
        }

        /* Nền Ambient Mesh chuẩn Liquid Glass giúp lớp kính mờ có chiều sâu khúc xạ */
        html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-primary) !important;
            background-color: #F8FAFC !important;
            background-image:
                radial-gradient(circle at 8% 12%, rgba(254, 215, 170, 0.55) 0%, transparent 38%),
                radial-gradient(circle at 92% 18%, rgba(255, 237, 213, 0.70) 0%, transparent 42%),
                radial-gradient(circle at 78% 85%, rgba(254, 215, 170, 0.45) 0%, transparent 45%),
                radial-gradient(circle at 22% 82%, rgba(255, 255, 255, 0.95) 0%, transparent 45%),
                linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 55%, #FFF7ED 100%) !important;
            background-attachment: fixed !important;
        }

        header[data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.58) !important;
            backdrop-filter: blur(24px) saturate(190%) !important;
            -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.8) !important;
        }

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1440px !important;
            animation: pageFadeIn 0.45s cubic-bezier(0.16, 1, 0.3, 1);
        }

        /* Ngăn Streamlit cắt bóng đổ và bo góc của các card bên trong cột */
        [data-testid="column"],
        [data-testid="stVerticalBlock"],
        [data-testid="stElementContainer"],
        [data-testid="stMarkdownContainer"] {
            overflow: visible !important;
        }

        @keyframes pageFadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulseGlow {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        @keyframes statusRipple {
            0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.45); }
            70% { box-shadow: 0 0 0 8px rgba(22, 163, 74, 0); }
            100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
        }

        @keyframes statusRippleError {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.45); }
            70% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        /* ======================= SIDEBAR LIQUID GLASS ======================= */
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.72) !important;
            backdrop-filter: blur(32px) saturate(200%) !important;
            -webkit-backdrop-filter: blur(32px) saturate(200%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.9) !important;
            box-shadow: 6px 0 32px rgba(15, 23, 42, 0.04) !important;
        }

        section[data-testid="stSidebar"] > div {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.4rem !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] p,
        .stCheckbox label span {
            color: #171717 !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stCaptionContainer"] p {
            color: #525252 !important;
            font-weight: 400 !important;
            line-height: 1.45 !important;
        }

        hr {
            border-color: rgba(226, 232, 240, 0.8) !important;
        }

        /* ======================= SỬA TRIỆT ĐỂ BO GÓC & NỀN ĐEN CỦA INPUT / SELECTBOX ======================= */
        /* 1. Selectbox (Cổng COM, Baudrate): xóa toàn bộ nền đen của BaseWeb và bo góc đồng nhất */
        div[data-baseweb="select"] {
            border-radius: var(--radius-md) !important;
        }

        div[data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.88) !important;
            background-color: rgba(255, 255, 255, 0.88) !important;
            backdrop-filter: blur(16px) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(203, 213, 225, 0.9) !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03), inset 0 1px 0 #FFFFFF !important;
            color: #171717 !important;
            transition: all 0.2s ease !important;
            overflow: hidden !important;
        }

        div[data-baseweb="select"] > div div,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] svg {
            background-color: transparent !important;
            color: #171717 !important;
            fill: #171717 !important;
        }

        /* 2. TextInput & NumberInput: Chỉ bo góc ở khung bao ngoài, xóa border thừa bên trong gây lỗi góc */
        div[data-baseweb="input"],
        div[data-testid="stNumberInputContainer"] {
            background: rgba(255, 255, 255, 0.88) !important;
            background-color: rgba(255, 255, 255, 0.88) !important;
            backdrop-filter: blur(16px) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(203, 213, 225, 0.9) !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03), inset 0 1px 0 #FFFFFF !important;
            overflow: hidden !important;
            transition: all 0.2s ease !important;
        }

        div[data-baseweb="base-input"],
        .stTextInput input,
        .stNumberInput input {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            outline: none !important;
            color: #171717 !important;
            -webkit-text-fill-color: #171717 !important;
        }

        /* Trạng thái Focus phát sáng màu Cam */
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"]:focus-within,
        div[data-testid="stNumberInputContainer"]:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px var(--primary-glow), inset 0 1px 0 #FFFFFF !important;
            background-color: #FFFFFF !important;
        }

        /* Menu xổ xuống của Selectbox */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        ul[data-baseweb="menu"] {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(24px) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(226, 232, 240, 0.9) !important;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.10) !important;
            overflow: hidden !important;
        }

        li[role="option"] {
            background-color: transparent !important;
            color: #171717 !important;
            font-weight: 500 !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {
            background-color: #FFF7ED !important;
            color: #EA580C !important;
            font-weight: 600 !important;
        }

        /* Nút +/- của NumberInput */
        div[data-testid="stNumberInput"] button {
            background: rgba(248, 250, 252, 0.9) !important;
            color: #171717 !important;
            border: none !important;
            border-left: 1px solid rgba(226, 232, 240, 0.9) !important;
            border-radius: 0 !important;
        }

        div[data-testid="stNumberInput"] button:hover {
            background: #FFF7ED !important;
            color: #EA580C !important;
        }

        /* Slider màu Cam */
        div[data-testid="stSlider"] div[role="slider"] {
            background-color: var(--primary) !important;
            box-shadow: 0 2px 8px rgba(249, 115, 22, 0.45) !important;
        }

        /* ======================= BUTTONS LIQUID GLASS ======================= */
        .stButton > button, .stDownloadButton > button {
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0.58rem 1rem !important;
            transition: all 0.24s cubic-bezier(0.16, 1, 0.3, 1) !important;
            border: 1px solid rgba(255, 255, 255, 0.95) !important;
            outline: 1px solid rgba(203, 213, 225, 0.75) !important;
            background: rgba(255, 255, 255, 0.78) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            color: #171717 !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04), inset 0 1px 0 #FFFFFF !important;
        }

        .stButton > button p, .stDownloadButton > button p {
            color: inherit !important;
            font-weight: 600 !important;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            outline-color: rgba(249, 115, 22, 0.45) !important;
            background: rgba(255, 247, 237, 0.92) !important;
            color: var(--primary-hover) !important;
            box-shadow: 0 10px 22px rgba(249, 115, 22, 0.14), inset 0 1px 0 #FFFFFF !important;
        }

        .stButton > button:active, .stDownloadButton > button:active {
            transform: scale(0.97) translateY(0px) !important;
        }

        /* Primary CTA Button (Liquid Orange Glass) */
        .stButton > button[kind="primary"] {
            background: linear-gradient(180deg, #FB923C 0%, #F97316 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.35) !important;
            outline: 1px solid #EA580C !important;
            box-shadow: 0 8px 20px rgba(249, 115, 22, 0.30), inset 0 1.5px 0 rgba(255, 255, 255, 0.45) !important;
        }

        .stButton > button[kind="primary"] p {
            color: #FFFFFF !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(180deg, #F97316 0%, #EA580C 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 12px 26px rgba(234, 88, 12, 0.38), inset 0 1.5px 0 rgba(255, 255, 255, 0.5) !important;
        }

        /* ======================= THÔNG BÁO LIQUID GLASS (THAY ST.ERROR / ST.INFO ĐEN) ======================= */
        .liquid-notice {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.85rem 1.15rem;
            border-radius: var(--radius-lg);
            backdrop-filter: blur(24px) saturate(190%);
            -webkit-backdrop-filter: blur(24px) saturate(190%);
            box-shadow: var(--shadow-liquid);
            margin: 0.5rem 0;
            font-size: 0.86rem;
            font-weight: 500;
            line-height: 1.45;
        }

        .liquid-notice.info {
            background: rgba(255, 247, 237, 0.82);
            border: 1px solid rgba(249, 115, 22, 0.30);
            color: #9A3412;
        }

        .liquid-notice.success {
            background: rgba(240, 253, 244, 0.85);
            border: 1px solid rgba(22, 163, 74, 0.32);
            color: #14532D;
        }

        .liquid-notice.warning {
            background: rgba(255, 251, 235, 0.88);
            border: 1px solid rgba(245, 158, 11, 0.38);
            color: #78350F;
        }

        .liquid-notice.error {
            background: rgba(254, 242, 242, 0.88);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #7F1D1D;
        }

        .liquid-notice-icon {
            width: 26px;
            height: 26px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.8rem;
            flex-shrink: 0;
        }

        .liquid-notice-icon.info {
            background: rgba(249, 115, 22, 0.15);
            color: #EA580C;
        }

        .liquid-notice-icon.success {
            background: rgba(22, 163, 74, 0.16);
            color: #16A34A;
        }

        .liquid-notice-icon.warning {
            background: rgba(245, 158, 11, 0.18);
            color: #D97706;
        }

        .liquid-notice-icon.error {
            background: rgba(239, 68, 68, 0.16);
            color: #DC2626;
        }

        .liquid-notice-text {
            word-break: break-word;
        }

        /* ======================= HERO HEADER LIQUID GLASS ======================= */
        .liquid-hero {
            background: var(--glass-bg);
            backdrop-filter: blur(28px) saturate(200%);
            -webkit-backdrop-filter: blur(28px) saturate(200%);
            border: 1.5px solid var(--glass-border);
            outline: 1px solid var(--glass-outline);
            box-shadow: var(--shadow-liquid);
            border-radius: var(--radius-2xl);
            padding: 1.4rem 1.8rem;
            margin: 0.25rem 0 1.25rem 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            position: relative;
        }

        .hero-left {
            display: flex;
            align-items: center;
            gap: 1.05rem;
        }

        .hero-icon-box {
            width: 54px;
            height: 54px;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(255, 247, 237, 0.95) 0%, rgba(255, 237, 213, 0.9) 100%);
            border: 1px solid rgba(249, 115, 22, 0.30);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.65rem;
            box-shadow: 0 8px 20px rgba(249, 115, 22, 0.14), inset 0 1.5px 0 #FFFFFF;
            animation: pulseGlow 3.2s infinite ease-in-out;
        }

        .hero-title {
            font-size: 1.55rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            color: var(--text-primary);
            margin: 0;
            line-height: 1.2;
        }

        .hero-subtitle {
            font-size: 0.86rem;
            color: var(--text-secondary);
            margin: 0.22rem 0 0 0;
            font-weight: 500;
        }

        .hero-badge-group {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }

        .glass-pill {
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(226, 232, 240, 0.95);
            padding: 0.42rem 0.92rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-secondary);
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03), inset 0 1px 0 #FFFFFF;
        }

        .glass-pill.orange {
            background: rgba(255, 247, 237, 0.92);
            border-color: rgba(249, 115, 22, 0.35);
            color: var(--primary-hover);
        }

        /* ======================= STATUS BANNER ======================= */
        .status-banner {
            border-radius: var(--radius-xl);
            padding: 0.95rem 1.4rem;
            margin-bottom: 1.35rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            backdrop-filter: blur(24px) saturate(190%);
            -webkit-backdrop-filter: blur(24px) saturate(190%);
            box-shadow: var(--shadow-liquid);
            transition: all 0.3s ease;
        }

        .status-banner.online {
            background: rgba(240, 253, 244, 0.82);
            border: 1px solid rgba(22, 163, 74, 0.35);
            color: #14532D;
        }

        .status-banner.offline, .status-banner.error {
            background: rgba(254, 242, 242, 0.84);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #7F1D1D;
        }

        .status-banner.waiting {
            background: rgba(255, 251, 235, 0.85);
            border: 1px solid rgba(245, 158, 11, 0.38);
            color: #78350F;
        }

        .status-left {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            font-weight: 600;
            font-size: 0.92rem;
        }

        .status-dot {
            width: 11px;
            height: 11px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }

        .status-dot.online {
            background: var(--success);
            animation: statusRipple 2s infinite;
        }

        .status-dot.error {
            background: var(--error);
            animation: statusRippleError 2s infinite;
        }

        .status-dot.waiting {
            background: var(--warning);
        }

        /* ======================= TELEMETRY LIQUID GLASS CARDS ======================= */
        .telemetry-card {
            background: var(--glass-bg);
            backdrop-filter: blur(28px) saturate(200%);
            -webkit-backdrop-filter: blur(28px) saturate(200%);
            border: 1.5px solid var(--glass-border);
            outline: 1px solid var(--glass-outline);
            box-shadow: var(--shadow-liquid);
            border-radius: var(--radius-2xl);
            padding: 1.3rem 1.35rem;
            margin: 0.25rem 0;
            min-height: 230px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                        box-shadow 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                        outline-color 0.28s ease;
        }

        .telemetry-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-liquid-hover);
            outline-color: rgba(249, 115, 22, 0.45);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            margin-bottom: 0.85rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid rgba(226, 232, 240, 0.75);
        }

        .card-title-wrap {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            min-width: 0;
        }

        .card-icon {
            width: 36px;
            height: 36px;
            border-radius: 11px;
            background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
            border: 1px solid rgba(249, 115, 22, 0.28);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.88rem;
            font-weight: 700;
            flex-shrink: 0;
            box-shadow: inset 0 1px 0 #FFFFFF;
        }

        .card-title {
            font-size: 0.96rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
            line-height: 1.2;
            white-space: nowrap;
        }

        .card-sub {
            font-size: 0.74rem;
            font-weight: 500;
            color: var(--text-muted);
            margin-top: 0.14rem;
            white-space: nowrap;
        }

        .card-tag {
            font-size: 0.68rem;
            font-weight: 600;
            padding: 0.24rem 0.62rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(226, 232, 240, 0.9);
            color: var(--text-secondary);
            white-space: nowrap;
            flex-shrink: 0;
        }

        .card-tag.accent {
            background: var(--primary-light);
            border-color: rgba(249, 115, 22, 0.32);
            color: var(--primary-hover);
        }

        .metric-row {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            padding: 0.48rem 0;
            border-bottom: 1px dashed rgba(226, 232, 240, 0.7);
        }

        .metric-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .metric-label {
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .metric-value-group {
            display: flex;
            align-items: baseline;
            gap: 0.45rem;
        }

        .metric-value {
            font-size: 1.18rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            font-variant-numeric: tabular-nums;
        }

        .metric-delta {
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.14rem 0.48rem;
            border-radius: 999px;
            background: var(--primary-light);
            color: var(--primary-hover);
            border: 1px solid rgba(249, 115, 22, 0.25);
            white-space: nowrap;
        }

        /* Thanh tiến trình Pin LiPo */
        .bat-bar-bg {
            width: 100%;
            height: 7px;
            background: rgba(226, 232, 240, 0.85);
            border-radius: 999px;
            overflow: hidden;
            margin: 0.35rem 0 0.45rem 0;
        }

        .bat-bar-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        }

        /* RBL Research Metrics Strip */
        .rbl-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.95rem;
            margin-top: 1.15rem;
        }

        .rbl-mini-card {
            background: var(--glass-bg);
            backdrop-filter: blur(24px) saturate(190%);
            -webkit-backdrop-filter: blur(24px) saturate(190%);
            border: 1.5px solid var(--glass-border);
            outline: 1px solid var(--glass-outline);
            border-radius: var(--radius-xl);
            padding: 0.9rem 1.15rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: var(--shadow-liquid);
            transition: all 0.24s ease;
        }

        .rbl-mini-card:hover {
            outline-color: rgba(249, 115, 22, 0.45);
            transform: translateY(-2px);
            box-shadow: var(--shadow-liquid-hover);
        }

        .rbl-label {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .rbl-sub {
            font-size: 0.72rem;
            color: var(--text-secondary);
            margin-top: 0.12rem;
        }

        .rbl-val {
            font-size: 1.18rem;
            font-weight: 700;
            color: var(--primary-hover);
            font-variant-numeric: tabular-nums;
        }

        /* Section Header */
        .section-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 1.65rem 0 0.85rem 0;
        }

        .section-heading h3 {
            font-size: 1.12rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .section-heading span.sub {
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        /* Khung chứa biểu đồ & bảng dữ liệu (Xóa border kép gây lỗi bo góc) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--glass-bg-strong) !important;
            backdrop-filter: blur(26px) saturate(190%) !important;
            -webkit-backdrop-filter: blur(26px) saturate(190%) !important;
            border: 1.5px solid var(--glass-border) !important;
            outline: 1px solid var(--glass-outline) !important;
            border-radius: var(--radius-2xl) !important;
            box-shadow: var(--shadow-liquid) !important;
            padding: 1.2rem !important;
            transition: outline-color 0.25s ease, box-shadow 0.25s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border: none !important;
            background: transparent !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            outline-color: rgba(249, 115, 22, 0.4) !important;
        }

        /* Expander Liquid Glass (Xóa viền đen bên trong của Streamlit) */
        div[data-testid="stExpander"],
        div[data-testid="stExpander"] details {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(24px) saturate(190%) !important;
            border: 1px solid var(--glass-outline) !important;
            border-radius: var(--radius-xl) !important;
            box-shadow: var(--shadow-liquid) !important;
            overflow: hidden !important;
        }

        div[data-testid="stExpander"] summary {
            background: transparent !important;
            color: #171717 !important;
            border: none !important;
        }

        div[data-testid="stExpander"] summary p,
        div[data-testid="stExpander"] summary svg {
            color: #171717 !important;
            fill: #171717 !important;
            font-weight: 600 !important;
        }

        /* Responsive Mobile & Tablet */
        @media (max-width: 768px) {
            .liquid-hero {
                padding: 1.15rem;
            }
            .hero-title {
                font-size: 1.25rem;
            }
            .telemetry-card {
                margin-bottom: 0.75rem;
            }
            .rbl-strip {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, ::before, ::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """
    )


inject_liquid_glass_styles()


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


def compute_rbl_metrics(df: pd.DataFrame, snap: dict):
    """Tính các chỉ số định lượng RBL (PDR, AoI, Downwash MAE, RMSE) từ dữ liệu thực tế."""
    aoi_str = f"{snap['last_online_age']:.1f} s" if snap.get("last_online_age") is not None else "—"
    pdr_str = "—"
    mae_str = "—"
    rmse_str = "—"

    if not df.empty:
        # 1. Tính PDR từ chuỗi số thứ tự gói tin (seq)
        seqs = pd.to_numeric(df["seq"], errors="coerce").dropna().astype(int)
        if len(seqs) >= 2:
            diffs = seqs.diff()
            valid_diffs = diffs[diffs > 0]
            expected = int(valid_diffs.sum()) + 1
            received = int((diffs > 0).sum()) + 1
            if expected > 0:
                pdr = min(100.0, (received / expected) * 100.0)
                pdr_str = f"{pdr:.1f}%"
        elif len(seqs) == 1:
            pdr_str = "100.0%"

        # 2. Tính sai số nhiệt độ Downwash (BME #1 không vỏ vs BME #2 có vỏ Pagoda)
        t1 = pd.to_numeric(df["t1"], errors="coerce")
        t2 = pd.to_numeric(df["t2"], errors="coerce")
        pair = pd.DataFrame({"t1": t1, "t2": t2}).dropna()
        if not pair.empty:
            err = (pair["t1"] - pair["t2"]).abs()
            mae = float(err.mean())
            rmse = float(((pair["t1"] - pair["t2"]) ** 2).mean() ** 0.5)
            mae_str = f"{mae:.2f} °C"
            rmse_str = f"{rmse:.2f} °C"

    return pdr_str, aoi_str, mae_str, rmse_str


def render_glass_chart(df: pd.DataFrame, cols: list, labels_map: dict, y_title: str, colors: list):
    """Vẽ biểu đồ Altair mượt mà theo chuẩn Apple Liquid Glass, xử lý an toàn cột NaN (như BMP280 không có độ ẩm)."""
    available_cols = [c for c in cols if c in df.columns]
    if not available_cols:
        glass_notice("Không tìm thấy trường dữ liệu tương ứng.", "info")
        return

    chart_df = df[["time"] + available_cols].copy()
    for c in available_cols:
        chart_df[c] = pd.to_numeric(chart_df[c], errors="coerce")

    valid_cols = [c for c in available_cols if chart_df[c].notna().any()]
    if not valid_cols:
        glass_notice(
            "Chưa có dữ liệu hợp lệ cho biểu đồ này (hoặc module BMP280 không xuất kênh độ ẩm).",
            "info",
        )
        return

    melted = chart_df.melt(
        id_vars=["time"],
        value_vars=valid_cols,
        var_name="sensor",
        value_name="value",
    ).dropna(subset=["value"])

    melted["Kênh đo"] = melted["sensor"].map(lambda x: labels_map.get(x, x))
    domain_labels = [labels_map.get(c, c) for c in valid_cols]
    range_colors = colors[: len(valid_cols)]

    chart = (
        alt.Chart(melted)
        .mark_line(interpolate="monotone", strokeWidth=2.6, point=alt.OverlayMarkDef(size=36, filled=True))
        .encode(
            x=alt.X(
                "time:T",
                title=None,
                axis=alt.Axis(format="%H:%M:%S", labelColor="#737373", gridColor="rgba(226,232,240,0.5)"),
            ),
            y=alt.Y(
                "value:Q",
                title=y_title,
                scale=alt.Scale(zero=False),
                axis=alt.Axis(labelColor="#737373", titleColor="#737373", gridColor="rgba(226,232,240,0.6)"),
            ),
            color=alt.Color(
                "Kênh đo:N",
                scale=alt.Scale(domain=domain_labels, range=range_colors),
                legend=alt.Legend(orient="top", title=None, labelColor="#171717", labelFontWeight=600),
            ),
            tooltip=[
                alt.Tooltip("time:T", title="Thời gian", format="%H:%M:%S"),
                alt.Tooltip("Kênh đo:N", title="Cảm biến"),
                alt.Tooltip("value:Q", title=y_title, format=".2f"),
            ],
        )
        .properties(height=240)
        .configure_view(strokeWidth=0)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


# ======================= SIDEBAR: KẾT NỐI & ĐIỀU KHIỂN =======================
with st.sidebar:
    render_html(
        """
        <div style="display:flex;align-items:center;gap:0.65rem;margin-bottom:0.75rem;">
            <div style="width:36px;height:36px;border-radius:10px;background:#FFF7ED;border:1px solid rgba(249,115,22,0.3);display:flex;align-items:center;justify-content:center;font-size:1.15rem;">
                🛰️
            </div>
            <div>
                <div style="font-weight:700;font-size:0.98rem;color:#171717;line-height:1.2;">Ground Control</div>
                <div style="font-size:0.74rem;color:#525252;font-weight:500;">ESP8266 Gateway • LoRa E32</div>
            </div>
        </div>
        """
    )

    st.header("Kết nối trạm mặt đất")
    ports = list_ports()
    port = st.selectbox("Cổng COM", ports if ports else ["(không thấy cổng)"])
    manual = st.text_input("Hoặc nhập tay (VD: COM5, /dev/ttyUSB0)", "")
    baud = st.selectbox("Baudrate", [115200, 9600], index=0)
    target = manual.strip() or port

    c1, c2 = st.columns(2)
    if c1.button("Kết nối", use_container_width=True, type="primary"):
        if gw.connect(target, baud):
            glass_notice(f"Đã mở {target}", "success")
        else:
            glass_notice(gw.snapshot()["error"] or f"Không mở được {target}", "error")
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
        glass_notice(cmd_result[1], "success" if cmd_result[0] else "error")


# ======================= HERO HEADER =======================
render_html(
    """
    <div class="liquid-hero">
        <div class="hero-left">
            <div class="hero-icon-box">🛰️</div>
            <div>
                <h1 class="hero-title">Giám sát môi trường IoT-UAV</h1>
                <p class="hero-subtitle">Adaptive Downwash-Aware Sensing &amp; Two-Way LoRa Telemetry Dashboard</p>
            </div>
        </div>
        <div class="hero-badge-group">
            <span class="glass-pill orange">● Dual I2C Sensor Array</span>
            <span class="glass-pill">LoRa 433 MHz Link</span>
            <span class="glass-pill">SQLite Live Stream</span>
        </div>
    </div>
    """
)


# ======================= KHU VỰC TỰ LÀM MỚI =======================
@st.fragment(run_every=refresh)
def live_view():
    snap = gw.snapshot()
    d = snap["latest"]
    active_port = html.escape(str(snap.get("port") or "Chưa chọn"))

    # ---- Banner trạng thái Liquid Glass ----
    if not snap["connected"]:
        err_msg = html.escape(snap["error"] or "Chưa kết nối cổng COM. Chọn cổng ở thanh bên rồi bấm Kết nối.")
        render_html(
            f"""
            <div class="status-banner error">
                <div class="status-left">
                    <span class="status-dot error"></span>
                    <span>{err_msg}</span>
                </div>
                <span class="glass-pill">Trạng thái: Ngắt kết nối</span>
            </div>
            """
        )
    elif snap["last_msg_age"] is None or snap["last_msg_age"] > GATEWAY_SILENT_S:
        render_html(
            f"""
            <div class="status-banner error">
                <div class="status-left">
                    <span class="status-dot error"></span>
                    <span>🔴 MẤT TÍN HIỆU TỪ GATEWAY (ESP8266 không gửi dữ liệu, kiểm tra cáp USB / nguồn).</span>
                </div>
                <span class="glass-pill">Cổng: {active_port} • Im lặng &gt; {GATEWAY_SILENT_S}s</span>
            </div>
            """
        )
    elif snap["link_status"] == "offline":
        render_html(
            f"""
            <div class="status-banner offline">
                <div class="status-left">
                    <span class="status-dot error"></span>
                    <span>🔴 UAV OFFLINE: mất kết nối LoRa với UAV.</span>
                </div>
                <span class="glass-pill">Cổng: {active_port} • Heartbeat Timeout</span>
            </div>
            """
        )
    elif snap["link_status"] == "online":
        age = snap["last_online_age"]
        render_html(
            f"""
            <div class="status-banner online">
                <div class="status-left">
                    <span class="status-dot online"></span>
                    <span>🟢 UAV ONLINE (gói cuối cách đây {age:.0f} s)</span>
                </div>
                <span class="glass-pill orange">Cổng: {active_port} • Làm mới: {refresh}s</span>
            </div>
            """
        )
    else:
        render_html(
            f"""
            <div class="status-banner waiting">
                <div class="status-left">
                    <span class="status-dot waiting"></span>
                    <span>🟡 Đã mở cổng, đang chờ gói dữ liệu đầu tiên...</span>
                </div>
                <span class="glass-pill">Cổng: {active_port} • Listening...</span>
            </div>
            """
        )

    # ---- Số liệu hiện tại ----
    uav_ok = snap["link_status"] == "online" and snap["connected"]
    sub_status = "Thời gian thực từ cảm biến" if uav_ok else "Lưu trữ lần cuối nhận được"
    render_html(
        f"""
        <div class="section-heading">
            <h3>Số liệu hiện tại{"" if uav_ok else " (lần cuối nhận được)"}</h3>
            <span class="sub">{sub_status}</span>
        </div>
        """
    )

    d_t1_t2 = delta(d.get("t1"), d.get("t2"), " °C vs #2")
    d_t2_t3 = delta(d.get("t2"), d.get("t3"), " °C UAV−đất")
    d_p2_p3 = delta(d.get("p2"), d.get("p3"), " hPa UAV−đất")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_html_1 = f'<span class="metric-delta">{html.escape(d_t1_t2)}</span>' if d_t1_t2 else ""
        render_html(
            f"""
            <div class="telemetry-card">
                <div class="card-header">
                    <div class="card-title-wrap">
                        <div class="card-icon">01</div>
                        <div>
                            <h4 class="card-title">BME280 #1</h4>
                            <div class="card-sub">Không vỏ • Unshielded</div>
                        </div>
                    </div>
                    <span class="card-tag">I2C-0</span>
                </div>
                <div>
                    <div class="metric-row">
                        <span class="metric-label">Nhiệt độ</span>
                        <div class="metric-value-group">
                            <span class="metric-value">{fmt(d.get("t1"), " °C")}</span>
                            {delta_html_1}
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Độ ẩm</span>
                        <span class="metric-value">{fmt(d.get("h1"), " %")}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Áp suất</span>
                        <span class="metric-value">{fmt(d.get("p1"), " hPa")}</span>
                    </div>
                </div>
            </div>
            """
        )

    with col2:
        render_html(
            f"""
            <div class="telemetry-card">
                <div class="card-header">
                    <div class="card-title-wrap">
                        <div class="card-icon">02</div>
                        <div>
                            <h4 class="card-title">BME280 #2</h4>
                            <div class="card-sub">Có vỏ • Pagoda Shield</div>
                        </div>
                    </div>
                    <span class="card-tag accent">I2C-1</span>
                </div>
                <div>
                    <div class="metric-row">
                        <span class="metric-label">Nhiệt độ</span>
                        <span class="metric-value">{fmt(d.get("t2"), " °C")}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Độ ẩm</span>
                        <span class="metric-value">{fmt(d.get("h2"), " %")}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Áp suất</span>
                        <span class="metric-value">{fmt(d.get("p2"), " hPa")}</span>
                    </div>
                </div>
            </div>
            """
        )

    with col3:
        delta_html_t3 = f'<span class="metric-delta">{html.escape(d_t2_t3)}</span>' if d_t2_t3 else ""
        delta_html_p3 = f'<span class="metric-delta">{html.escape(d_p2_p3)}</span>' if d_p2_p3 else ""
        render_html(
            f"""
            <div class="telemetry-card">
                <div class="card-header">
                    <div class="card-title-wrap">
                        <div class="card-icon">03</div>
                        <div>
                            <h4 class="card-title">BME280 #3</h4>
                            <div class="card-sub">Trạm mặt đất • Ground</div>
                        </div>
                    </div>
                    <span class="card-tag">Ref</span>
                </div>
                <div>
                    <div class="metric-row">
                        <span class="metric-label">Nhiệt độ</span>
                        <div class="metric-value-group">
                            <span class="metric-value">{fmt(d.get("t3"), " °C")}</span>
                            {delta_html_t3}
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Độ ẩm</span>
                        <span class="metric-value">{fmt(d.get("h3"), " %")}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Áp suất</span>
                        <div class="metric-value-group">
                            <span class="metric-value">{fmt(d.get("p3"), " hPa")}</span>
                            {delta_html_p3}
                        </div>
                    </div>
                </div>
            </div>
            """
        )

    with col4:
        is_usb = d.get("pwr") == "usb" or d.get("bat") is None
        bat_val = d.get("bat")
        seq_val = fmt(d.get("seq"), "", 0)
        seq_display = "—" if seq_val == "—" else f"#{seq_val}"
        if is_usb:
            pwr_label = "USB 5V" if d.get("pwr") == "usb" else "—"
            bat_bar_html = ""
            vbat_badge = '<span class="card-tag accent">Trực tiếp</span>'
        else:
            pwr_label = fmt(bat_val, " %", 0)
            vbat_str = fmt(d.get("vbat"), " V")
            vbat_badge = f'<span class="metric-delta">{vbat_str}</span>'
            try:
                pct_num = max(0.0, min(100.0, float(bat_val)))
            except (TypeError, ValueError):
                pct_num = 0.0
            bar_color = "#EF4444" if pct_num <= 10 else ("#F59E0B" if pct_num <= 20 else "#F97316")
            bat_bar_html = (
                f'<div class="bat-bar-bg">'
                f'<div class="bat-bar-fill" style="width:{pct_num}%;background:{bar_color};"></div>'
                f'</div>'
            )

        render_html(
            f"""
            <div class="telemetry-card">
                <div class="card-header">
                    <div class="card-title-wrap">
                        <div class="card-icon">⚡</div>
                        <div>
                            <h4 class="card-title">Nguồn UAV</h4>
                            <div class="card-sub">3S LiPo &amp; Gói tin</div>
                        </div>
                    </div>
                    <span class="card-tag accent">Power</span>
                </div>
                <div>
                    <div class="metric-row">
                        <span class="metric-label">{"Pin" if is_usb else "Pin LiPo"}</span>
                        <div class="metric-value-group">
                            <span class="metric-value">{pwr_label}</span>
                            {vbat_badge}
                        </div>
                    </div>
                    {bat_bar_html}
                    <div class="metric-row">
                        <span class="metric-label">Số thứ tự gói</span>
                        <span class="metric-value">{seq_display}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Dòng lỗi bỏ qua</span>
                        <span class="metric-value" style="font-size:1rem;color:#525252;">{snap['bad_lines']}</span>
                    </div>
                </div>
            </div>
            """
        )

        if not is_usb:
            try:
                if float(bat_val) <= 10:
                    glass_notice("PIN NGUY HIỂM! Hạ cánh ngay.", "error")
                elif float(bat_val) <= 20:
                    glass_notice("Pin yếu", "warning")
            except (TypeError, ValueError):
                pass

    # ---- Biểu đồ & Chỉ số thực nghiệm RBL ----
    df, ev = load_history(minutes)
    pdr_str, aoi_str, mae_str, rmse_str = compute_rbl_metrics(df, snap)

    render_html(
        f"""
        <div class="rbl-strip">
            <div class="rbl-mini-card">
                <div>
                    <div class="rbl-label">PDR (Tỷ lệ nhận gói)</div>
                    <div class="rbl-sub">Trong {minutes} phút gần nhất</div>
                </div>
                <div class="rbl-val">{pdr_str}</div>
            </div>
            <div class="rbl-mini-card">
                <div>
                    <div class="rbl-label">AoI (Độ tươi dữ liệu)</div>
                    <div class="rbl-sub">Age of Information</div>
                </div>
                <div class="rbl-val">{aoi_str}</div>
            </div>
            <div class="rbl-mini-card">
                <div>
                    <div class="rbl-label">Downwash MAE</div>
                    <div class="rbl-sub">|T1 Unshielded − T2 Shielded|</div>
                </div>
                <div class="rbl-val">{mae_str}</div>
            </div>
            <div class="rbl-mini-card">
                <div>
                    <div class="rbl-label">Downwash RMSE</div>
                    <div class="rbl-sub">Sai số toàn phương trung bình</div>
                </div>
                <div class="rbl-val">{rmse_str}</div>
            </div>
        </div>
        """
    )

    render_html(
        f"""
        <div class="section-heading">
            <h3>Biểu đồ {minutes} phút gần nhất</h3>
            <span class="sub">Tương tác trực tiếp: cuộn để phóng to, di chuột xem chi tiết</span>
        </div>
        """
    )

    if df.empty:
        glass_notice("Chưa có dữ liệu trong khoảng thời gian này.", "info")
    else:
        g1, g2 = st.columns(2)
        with g1:
            with st.container(border=True):
                st.markdown("**Nhiệt độ (°C)**")
                render_glass_chart(
                    df,
                    ["t1", "t2", "t3"],
                    {"t1": "#1 Không vỏ", "t2": "#2 Có vỏ (Pagoda)", "t3": "#3 Mặt đất"},
                    "Nhiệt độ (°C)",
                    ["#FB923C", "#EA580C", "#64748B"],
                )
        with g2:
            with st.container(border=True):
                st.markdown("**Độ ẩm (%)**")
                render_glass_chart(
                    df,
                    ["h1", "h2", "h3"],
                    {"h1": "#1 Không vỏ", "h2": "#2 Có vỏ (Pagoda)", "h3": "#3 Mặt đất"},
                    "Độ ẩm (%)",
                    ["#F97316", "#0EA5E9", "#94A3B8"],
                )

        g3, g4 = st.columns(2)
        with g3:
            with st.container(border=True):
                st.markdown("**Áp suất (hPa)**")
                render_glass_chart(
                    df,
                    ["p1", "p2", "p3"],
                    {"p1": "#1 Không vỏ", "p2": "#2 Có vỏ (Pagoda)", "p3": "#3 Mặt đất"},
                    "Áp suất (hPa)",
                    ["#F97316", "#EA580C", "#475569"],
                )
        with g4:
            with st.container(border=True):
                st.markdown("**Pin UAV (%)**")
                render_glass_chart(
                    df,
                    ["bat"],
                    {"bat": "Dung lượng Pin LiPo (%)"},
                    "Pin (%)",
                    ["#F97316"],
                )

    # ---- Nhật ký ----
    render_html(
        """
        <div class="section-heading">
            <h3>Nhật ký hệ thống &amp; Phản hồi lệnh</h3>
            <span class="sub">Giám sát sự kiện kết nối và ACK từ trạm UAV</span>
        </div>
        """
    )

    l1, l2 = st.columns(2)
    with l1:
        with st.container(border=True):
            st.subheader("Sự kiện")
            if not ev.empty:
                ev_display = ev.rename(
                    columns={"ts": "Thời gian", "kind": "Loại sự kiện", "detail": "Chi tiết"}
                )
                st.dataframe(ev_display, use_container_width=True, hide_index=True, height=250)
            else:
                st.caption("Chưa có sự kiện nào được ghi nhận.")
    with l2:
        with st.container(border=True):
            st.subheader("Phản hồi lệnh từ UAV")
            if snap["acks"]:
                st.dataframe(
                    pd.DataFrame(snap["acks"], columns=["Giờ", "Phản hồi"]),
                    use_container_width=True,
                    hide_index=True,
                    height=250,
                )
            else:
                st.caption("Chưa có phản hồi.")


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
