# ============================================
# [01] Imports
# ============================================
import os
import calendar
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ============================================
# [02] 🔧 策略描述文字 (要修改策略說明，改這裡就好)
# ============================================
# ------ 主標題區 ------
STRATEGY_HERO_TITLE = "台指期量化順勢策略：核心概念與優勢"
STRATEGY_HERO_TEXT = """
本策略專注於台灣加權指數期貨（台指期），透過量化回測與獨家籌碼濾網，
旨在順應台股長期趨勢的同時，有效避開無效波動與大幅回撤。
"""

# ------ 核心邏輯 ------
STRATEGY_CORE_ITEMS = [
    {
        "title": "1. 專注作多 (Long-Only)",
        "text": "順應台股長期具備向上成長的牛市特性，策略專注於捕捉多頭波段，不逆勢放空，降低多空雙巴的風險。"
    },
    {
        "title": "2. 籌碼情緒濾網",
        "text": "這是本策略的防護罩與進場依據。策略會每日追蹤特定的市場散戶籌碼指標（如小台、微台的多空情緒）。只有當市場呈現「散戶偏空、籌碼面有利於多方」的特定型態時，策略才會允許進場或續抱多單；一旦籌碼優勢消失，便會果斷出場。"
    },
]

# ------ 設計理念 ------
STRATEGY_DESIGN_BULLETS = [
    "不是單純看到價格上漲就追，而是要同時通過趨勢與籌碼條件。",
    "重視風險控管，避免在雜訊過多、優勢不明顯的區域頻繁交易。",
    "核心目標不是每一段都做到，而是盡量做「勝率與盈虧比都較有優勢」的行情。",
]

# ------ 適合市場環境 ------
STRATEGY_MARKET_BULLETS = [
    "中期偏多、結構穩定的趨勢市場。",
    "市場情緒過度悲觀，但實際上籌碼已逐漸轉向有利多方的時期。",
    "適合希望參與台股多頭波段、但又不想完全暴露在短線噪音中的資金配置。",
]

# ------ 策略優勢 (支援粗體: 用 <b></b>) ------
STRATEGY_ADVANTAGE_BULLETS = [
    "<b>順勢而為：</b>與長期多頭方向一致，不與大趨勢對抗。",
    "<b>加入籌碼濾網：</b>降低假突破與無效進場的機率。",
    "<b>風險意識明確：</b>當條件不再有利時，退出市場而不是硬抱。",
    "<b>量化執行：</b>規則固定、可驗證、可持續追蹤績效。",
]

# ------ 一句話總結 ------
STRATEGY_ONE_LINE = """
這是一套以台股長期多頭趨勢為基礎，再搭配散戶籌碼情緒濾網的量化順勢策略，
目的在於用更有紀律的方式，參與大方向、避開雜訊、控制回撤。
"""

# ============================================
# [03] 可調參數
# ============================================
AUTO_REFRESH_MS = 60000

# ===== 累積損益曲線顏色 =====
EQUITY_LINE_COLOR = "#10B981"
EQUITY_FILL_COLOR_RGB = "16,185,129"
EQUITY_FILL_ALPHA = 0.15

# ===== 頁面設定 =====
PAGE_TITLE = "台指期無限轉倉擇時策略"
INITIAL_SIDEBAR_STATE = "expanded"

# ===== 預設績效期間 =====
DEFAULT_PERIOD_OPTIONS = ["近1個月", "近3個月", "近9個月", "近12個月", "近2年", "近3年", "近4年", "全部"]
DEFAULT_PERIOD_INDEX = 5

# ============================================
# [04] 基本設定
# ============================================
st_autorefresh(interval=AUTO_REFRESH_MS, key="data_refresh")

st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# ============================================
# [05] 全站樣式 (精緻高級版)
# ============================================
st.markdown("""
<style>
/* ========= 基礎 ========= */
html, body, [class*="css"]  {
    background-color: #0A0A0B !important;
    color: #E4E4E7 !important;
    font-family: "Inter", "Segoe UI", "Microsoft JhengHei", -apple-system, sans-serif !important;
    font-feature-settings: "cv11", "ss01", "ss03";
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(16, 185, 129, 0.06), transparent),
        radial-gradient(ellipse 60% 50% at 80% 50%, rgba(59, 130, 246, 0.04), transparent),
        linear-gradient(180deg, #0A0A0B 0%, #09090B 100%) !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1720px !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ========= 主要標題 ========= */
.dashboard-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 0.25rem;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 12px;
}

.dashboard-title-accent {
    width: 4px;
    height: 28px;
    background: linear-gradient(180deg, #10B981 0%, #059669 100%);
    border-radius: 2px;
}

.page-top-note {
    color: #71717A;
    font-size: 0.875rem;
    margin-top: 4px;
    margin-bottom: 28px;
    font-weight: 400;
}

/* ========= 通用 panel ========= */
.panel {
    background: linear-gradient(180deg, rgba(24, 24, 27, 0.6) 0%, rgba(15, 15, 17, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.04) inset,
        0 20px 40px -12px rgba(0, 0, 0, 0.4);
    margin-bottom: 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}

.panel-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #FAFAFA;
    margin-bottom: 2px;
    letter-spacing: -0.01em;
}

.panel-subtitle {
    font-size: 0.8125rem;
    color: #71717A;
    margin-bottom: 12px;
    font-weight: 400;
}

/* ========= KPI ========= */
.kpi-card {
    background: linear-gradient(180deg, rgba(24, 24, 27, 0.6) 0%, rgba(15, 15, 17, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 20px 22px;
    min-height: 130px;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.04) inset,
        0 10px 30px -10px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
}

.kpi-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateY(-1px);
}

.kpi-label {
    font-size: 0.8125rem;
    color: #A1A1AA;
    margin-bottom: 10px;
    font-weight: 500;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    font-size: 0.75rem;
}

.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #FAFAFA;
    line-height: 1.1;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
    font-feature-settings: "tnum";
}

.kpi-foot {
    font-size: 0.75rem;
    color: #52525B;
    font-weight: 400;
}

/* ========= 文字顏色 ========= */
.text-red { color: #EF4444 !important; }
.text-green { color: #10B981 !important; }
.text-blue { color: #3B82F6 !important; }
.text-purple { color: #8B5CF6 !important; }
.text-orange { color: #F59E0B !important; }
.text-white { color: #FAFAFA !important; }

.info-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: #34D399;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 8px;
}

.info-badge::before {
    content: "";
    width: 6px;
    height: 6px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}

/* ========= Sidebar ========= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(9, 9, 11, 0.98) 0%, rgba(6, 6, 8, 0.99) 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    min-width: 290px !important;
    max-width: 290px !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.sidebar-brand {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.04) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 18px 18px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.sidebar-brand::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.3), transparent);
}

.sidebar-brand-title {
    font-size: 0.9375rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}

.sidebar-brand-subtitle {
    font-size: 0.75rem;
    color: #A1A1AA;
    line-height: 1.6;
    font-weight: 400;
}

.sidebar-section-title {
    font-size: 0.6875rem;
    font-weight: 600;
    color: #71717A;
    margin: 14px 0 10px 4px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

div[role="radiogroup"] {
    gap: 6px !important;
}

div[role="radiogroup"] > label {
    background: rgba(24, 24, 27, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 11px 14px;
    margin-bottom: 4px;
    transition: all 0.15s ease;
}

div[role="radiogroup"] > label:hover {
    border: 1px solid rgba(16, 185, 129, 0.25);
    background: rgba(24, 24, 27, 0.7);
}

div[role="radiogroup"] > label p {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}

.sidebar-info-card {
    background: rgba(24, 24, 27, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 20px;
}

.sidebar-info-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #E4E4E7;
    margin-bottom: 8px;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.sidebar-info-text {
    font-size: 0.75rem;
    color: #A1A1AA;
    line-height: 1.7;
    font-weight: 400;
}

/* ========= 策略說明 ========= */
.strategy-panel {
    background: linear-gradient(180deg, rgba(24, 24, 27, 0.6) 0%, rgba(15, 15, 17, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 18px;
    padding: 32px 36px;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.04) inset,
        0 20px 40px -12px rgba(0, 0, 0, 0.4);
    margin-bottom: 16px;
}

.strategy-hero {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.04) 100%);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 14px;
    padding: 22px 24px;
    margin-top: 4px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.strategy-hero::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.4), transparent);
}

.strategy-hero-title {
    font-size: 1.0625rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 10px;
    letter-spacing: -0.01em;
}

.strategy-hero-text {
    font-size: 0.9375rem;
    line-height: 1.75;
    color: #D4D4D8;
    font-weight: 400;
}

.strategy-section-head {
    font-size: 1rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-top: 24px;
    margin-bottom: 12px;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 10px;
}

.strategy-section-head::before {
    content: "";
    width: 3px;
    height: 16px;
    background: linear-gradient(180deg, #10B981, #059669);
    border-radius: 2px;
}

.strategy-item {
    background: rgba(24, 24, 27, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}

.strategy-item:hover {
    border-color: rgba(255, 255, 255, 0.08);
    background: rgba(24, 24, 27, 0.6);
}

.strategy-item-title {
    font-size: 0.9375rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 8px;
    letter-spacing: -0.01em;
}

.strategy-item-text {
    font-size: 0.875rem;
    line-height: 1.75;
    color: #A1A1AA;
    font-weight: 400;
}

.strategy-bullet-box {
    background: rgba(24, 24, 27, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 10px;
}

.strategy-bullet-item {
    font-size: 0.875rem;
    line-height: 1.9;
    color: #D4D4D8;
    padding-left: 18px;
    position: relative;
    font-weight: 400;
}

.strategy-bullet-item::before {
    content: "";
    position: absolute;
    left: 0;
    top: 12px;
    width: 5px;
    height: 5px;
    background: #10B981;
    border-radius: 50%;
}

.strategy-one-line {
    font-size: 0.9375rem;
    line-height: 1.85;
    color: #E4E4E7;
    font-weight: 500;
    letter-spacing: -0.005em;
}

/* ========= 月曆 ========= */
.calendar-head {
    text-align: center;
    color: #71717A;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 10px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.calendar-side-head {
    text-align: center;
    color: transparent;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 10px;
}

.calendar-empty {
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.03);
    min-height: 110px;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.01);
    margin-bottom: 8px;
}

.calendar-card-neutral {
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    min-height: 110px;
    padding: 10px 12px;
    background: rgba(24, 24, 27, 0.5);
    margin-bottom: 8px;
    transition: all 0.15s ease;
}

.calendar-card-neutral:hover {
    border-color: rgba(255, 255, 255, 0.1);
}

.calendar-card-pos {
    border-radius: 10px;
    border: 1px solid rgba(239, 68, 68, 0.2);
    min-height: 110px;
    padding: 10px 12px;
    background: linear-gradient(180deg, rgba(127, 29, 29, 0.5) 0%, rgba(87, 20, 20, 0.7) 100%);
    margin-bottom: 8px;
    transition: all 0.15s ease;
}

.calendar-card-pos:hover {
    border-color: rgba(239, 68, 68, 0.35);
}

.calendar-card-neg {
    border-radius: 10px;
    border: 1px solid rgba(16, 185, 129, 0.2);
    min-height: 110px;
    padding: 10px 12px;
    background: linear-gradient(180deg, rgba(6, 78, 59, 0.5) 0%, rgba(4, 52, 40, 0.7) 100%);
    margin-bottom: 8px;
    transition: all 0.15s ease;
}

.calendar-card-neg:hover {
    border-color: rgba(16, 185, 129, 0.35);
}

.day-num {
    font-size: 0.8125rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: #E4E4E7;
    font-feature-settings: "tnum";
}

.day-pnl-pos {
    font-size: 0.9375rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 6px;
    color: #FCA5A5;
    font-feature-settings: "tnum";
    letter-spacing: -0.01em;
}

.day-pnl-neg {
    font-size: 0.9375rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 6px;
    color: #6EE7B7;
    font-feature-settings: "tnum";
    letter-spacing: -0.01em;
}

.day-sub-pos {
    font-size: 0.6875rem;
    line-height: 1.5;
    color: #FECACA;
    font-weight: 400;
}

.day-sub-neg {
    font-size: 0.6875rem;
    line-height: 1.5;
    color: #A7F3D0;
    font-weight: 400;
}

.day-sub-neutral {
    font-size: 0.6875rem;
    line-height: 1.5;
    color: #A1A1AA;
    font-weight: 400;
}

.week-side-card {
    background: rgba(24, 24, 27, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 12px 14px;
    min-height: 110px;
    margin-bottom: 8px;
    transition: all 0.15s ease;
}

.week-side-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
}

.week-side-title {
    font-size: 0.6875rem;
    color: #71717A;
    margin-bottom: 10px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.week-side-pnl {
    font-size: 1.0625rem;
    font-weight: 700;
    margin-bottom: 6px;
    font-feature-settings: "tnum";
    letter-spacing: -0.01em;
}

.week-side-sub {
    font-size: 0.6875rem;
    color: #71717A;
    font-weight: 400;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    overflow: hidden;
}

/* ========= Buttons ========= */
.stButton > button {
    background: rgba(24, 24, 27, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #E4E4E7 !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background: rgba(24, 24, 27, 0.9) !important;
    border-color: rgba(16, 185, 129, 0.3) !important;
    color: #FAFAFA !important;
}

/* ========= Selectbox ========= */
div[data-baseweb="select"] > div {
    background: rgba(24, 24, 27, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
}

/* ========= Monthly header ========= */
.month-header {
    font-size: 1.125rem;
    font-weight: 700;
    color: #FAFAFA;
    margin: 8px 0 16px 0;
    letter-spacing: -0.01em;
    font-feature-settings: "tnum";
}
</style>
""", unsafe_allow_html=True)

# ============================================
# [06] 共用函式
# ============================================
def get_equity_fill_rgba():
    return f"rgba({EQUITY_FILL_COLOR_RGB},{EQUITY_FILL_ALPHA})"

def format_currency_tw(val):
    if pd.isna(val):
        val = 0
    if val > 0:
        return f'<span class="text-red">+${val:,.0f}</span>'
    elif val < 0:
        return f'<span class="text-green">-${abs(val):,.0f}</span>'
    else:
        return '<span style="color:#A1A1AA;">$0</span>'

def format_currency_text(val):
    if pd.isna(val):
        val = 0
    if val > 0:
        return f"+${val:,.0f}"
    elif val < 0:
        return f"-${abs(val):,.0f}"
    else:
        return "$0"

def pnl_class_name(val):
    if pd.isna(val) or val == 0:
        return "text-white"
    return "text-red" if val > 0 else "text-green"

def get_period_start(latest_dt, period_label):
    if period_label == "近1個月":
        return latest_dt - pd.DateOffset(months=1)
    elif period_label == "近3個月":
        return latest_dt - pd.DateOffset(months=3)
    elif period_label == "近9個月":
        return latest_dt - pd.DateOffset(months=9)
    elif period_label == "近12個月":
        return latest_dt - pd.DateOffset(months=12)
    elif period_label == "近2年":
        return latest_dt - pd.DateOffset(years=2)
    elif period_label == "近3年":
        return latest_dt - pd.DateOffset(years=3)
    elif period_label == "近4年":
        return latest_dt - pd.DateOffset(years=4)
    return None

def get_month_options(df):
    if df.empty:
        return []
    return (
        df["exit_time"]
        .dt.to_period("M")
        .astype(str)
        .drop_duplicates()
        .sort_values(ascending=False)
        .tolist()
    )

def safe_direction_text(x):
    x = str(x).upper()
    if x == "LONG":
        return "多 (LONG)"
    elif x == "SHORT":
        return "空 (SHORT)"
    return x

def get_day_card_info(pnl_value):
    if pd.isna(pnl_value) or pnl_value == 0:
        return {
            "card_class": "calendar-card-neutral",
            "pnl_class": "day-sub-neutral",
            "sub_class": "day-sub-neutral"
        }
    elif pnl_value > 0:
        return {
            "card_class": "calendar-card-pos",
            "pnl_class": "day-pnl-pos",
            "sub_class": "day-sub-pos"
        }
    else:
        return {
            "card_class": "calendar-card-neg",
            "pnl_class": "day-pnl-neg",
            "sub_class": "day-sub-neg"
        }

# ============================================
# [07] 讀取資料
# ============================================
@st.cache_data(ttl=60)
def load_data():
    file_path = "TXF_Market_Timing_trades.csv"

    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    required_cols = [
        "entry_time", "exit_time", "export_net_pnl",
        "entry_price", "exit_price", "exit_reason", "entry_dir"
    ]
    for c in required_cols:
        if c not in df.columns:
            df[c] = None

    df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
    df["exit_time"] = pd.to_datetime(df["exit_time"], errors="coerce")

    df = df.dropna(subset=["exit_time"]).sort_values("exit_time").reset_index(drop=True)
    df["duration"] = df["exit_time"] - df["entry_time"]

    df["日期文字"] = df["exit_time"].dt.strftime("%Y-%m-%d")
    df["Hover顯示"] = df["export_net_pnl"].fillna(0).apply(
        lambda x: f"+{x:,.0f}" if x > 0 else (f"-{abs(x):,.0f}" if x < 0 else "0")
    )

    return df

# ============================================
# [08] 策略說明內容區塊
# ============================================
def render_strategy_description_block():
    st.markdown('<div class="strategy-panel">', unsafe_allow_html=True)

    # Hero 區
    st.markdown(f"""
    <div class="strategy-hero">
        <div class="strategy-hero-title">{STRATEGY_HERO_TITLE}</div>
        <div class="strategy-hero-text">{STRATEGY_HERO_TEXT.strip()}</div>
    </div>
    """, unsafe_allow_html=True)

    # 核心邏輯
    st.markdown('<div class="strategy-section-head">策略核心邏輯</div>', unsafe_allow_html=True)
    for item in STRATEGY_CORE_ITEMS:
        st.markdown(f"""
        <div class="strategy-item">
            <div class="strategy-item-title">{item['title']}</div>
            <div class="strategy-item-text">{item['text']}</div>
        </div>
        """, unsafe_allow_html=True)

    # 設計理念
    st.markdown('<div class="strategy-section-head">策略設計理念</div>', unsafe_allow_html=True)
    st.markdown('<div class="strategy-bullet-box">', unsafe_allow_html=True)
    for bullet in STRATEGY_DESIGN_BULLETS:
        st.markdown(f'<div class="strategy-bullet-item">{bullet}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 適合市場環境
    st.markdown('<div class="strategy-section-head">適合的市場環境</div>', unsafe_allow_html=True)
    st.markdown('<div class="strategy-bullet-box">', unsafe_allow_html=True)
    for bullet in STRATEGY_MARKET_BULLETS:
        st.markdown(f'<div class="strategy-bullet-item">{bullet}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 策略優勢
    st.markdown('<div class="strategy-section-head">策略優勢</div>', unsafe_allow_html=True)
    st.markdown('<div class="strategy-bullet-box">', unsafe_allow_html=True)
    for bullet in STRATEGY_ADVANTAGE_BULLETS:
        st.markdown(f'<div class="strategy-bullet-item">{bullet}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 一句話
    st.markdown('<div class="strategy-section-head">一句話版本</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="strategy-bullet-box">
        <div class="strategy-one-line">{STRATEGY_ONE_LINE.strip()}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# [09] 頁面：策略說明
# ============================================
def render_strategy_description_page():
    st.markdown(
        '<div class="dashboard-title"><span class="dashboard-title-accent"></span>台指期量化順勢策略說明</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="page-top-note">完整策略理念、核心邏輯與市場適用性說明</div>',
        unsafe_allow_html=True
    )
    render_strategy_description_block()

# ============================================
# [10] 頁面：儀表板
# ============================================
def render_dashboard_page():
    st.markdown(
        '<div class="dashboard-title"><span class="dashboard-title-accent"></span>台指期無限轉倉擇時策略</div>',
        unsafe_allow_html=True
    )

    if st.button("🔄 獲取最新資料"):
        st.cache_data.clear()
        st.rerun()

    df = load_data()

    if df.empty:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">找不到資料</div>
            <div class="panel-subtitle">找不到 `TXF_Market_Timing_trades.csv`，請確認檔案是否在同一資料夾。</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    latest_exit = df["exit_time"].max()

    ctrl_col1, ctrl_col2 = st.columns([1.2, 2.8])

    with ctrl_col1:
        period_label = st.selectbox(
            "📆 績效統計期間",
            DEFAULT_PERIOD_OPTIONS,
            index=DEFAULT_PERIOD_INDEX
        )

    period_start = get_period_start(latest_exit, period_label)
    if period_start is not None:
        filtered_df = df[df["exit_time"] >= period_start].copy()
    else:
        filtered_df = df.copy()

    filtered_df = filtered_df.sort_values("exit_time").reset_index(drop=True)

    if filtered_df.empty:
        st.warning("所選期間內沒有資料。")
        st.stop()

    filtered_df["cum_pnl"] = filtered_df["export_net_pnl"].fillna(0).cumsum()
    filtered_df["cum_peak"] = filtered_df["cum_pnl"].cummax()
    filtered_df["drawdown"] = filtered_df["cum_pnl"] - filtered_df["cum_peak"]

    month_options = get_month_options(filtered_df)

    # KPI
    total_pnl = filtered_df["export_net_pnl"].fillna(0).sum()
    total_trades = len(filtered_df)
    win_trades = (filtered_df["export_net_pnl"].fillna(0) > 0).sum()
    win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0

    running_days = (filtered_df["exit_time"].max() - filtered_df["entry_time"].min()).days
    running_days = max(running_days, 1)

    avg_win = filtered_df.loc[filtered_df["export_net_pnl"] > 0, "export_net_pnl"].mean()
    avg_loss = filtered_df.loc[filtered_df["export_net_pnl"] < 0, "export_net_pnl"].mean()
    avg_win = 0 if pd.isna(avg_win) else avg_win
    avg_loss = 0 if pd.isna(avg_loss) else avg_loss
    payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    max_drawdown = filtered_df["drawdown"].min()

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">總累計淨損益</div>
            <div class="kpi-value">{format_currency_tw(total_pnl)}</div>
            <div class="kpi-foot">{period_label} 統計</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">總交易次數</div>
            <div class="kpi-value text-blue">{total_trades}</div>
            <div class="kpi-foot">完整平倉趟數</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">交易勝率</div>
            <div class="kpi-value text-purple">{win_rate:.1f}%</div>
            <div class="kpi-foot">獲利趟數 / 總趟數</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">最大連續回撤</div>
            <div class="kpi-value text-green">-${abs(max_drawdown):,.0f}</div>
            <div class="kpi-foot">歷史最大跌幅</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">盈虧比 (Payoff)</div>
            <div class="kpi-value text-orange">{payoff_ratio:.2f}</div>
            <div class="kpi-foot">均盈 / 均虧</div>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">實績運行天數</div>
            <div class="kpi-value" style="color:#FCD34D;">{running_days} 天</div>
            <div class="kpi-foot">首筆至最新交易日</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # 資金曲線 (全寬)
    st.markdown("""
    <div class="panel" style="margin-bottom:0px;">
        <div class="panel-title">累計資金曲線 (Equity Curve)</div>
        <div class="panel-subtitle" style="margin-bottom:6px;">
            <span class="info-badge">策略淨值</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_equity = go.Figure()

    fig_equity.add_trace(go.Scatter(
        x=filtered_df["日期文字"],
        y=filtered_df["cum_pnl"],
        text=filtered_df["Hover顯示"],
        mode="lines",
        line=dict(color=EQUITY_LINE_COLOR, width=2.5, shape="spline", smoothing=0.3),
        fill="tozeroy",
        fillcolor=get_equity_fill_rgba(),
        name="累計損益",
        hovertemplate="<b>%{x}</b><br>累計損益: %{y:,.0f}<br>單趟: %{text}<extra></extra>"
    ))

    fig_equity.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="",
            type="category",
            showgrid=False,
            tickfont=dict(size=11, color="#71717A", family="Inter, sans-serif"),
            showline=False,
            zeroline=False,
            nticks=10
        ),
        yaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(size=11, color="#71717A", family="Inter, sans-serif"),
            zeroline=True,
            zerolinecolor="rgba(255,255,255,0.1)",
            zerolinewidth=1,
            separatethousands=True
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(24, 24, 27, 0.95)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(family="Inter, sans-serif", size=12, color="#FAFAFA")
        )
    )

    st.plotly_chart(fig_equity, use_container_width=True, config={"displayModeBar": False})

    if len(month_options) > 0:
        selected_month = st.selectbox(
            "🗓️ 選擇月曆月份",
            options=month_options,
            index=0,
            key="calendar_month_select"
        )
    else:
        selected_month = None

    # 每日績效月曆
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
        <div class="panel-title">每日績效月曆</div>
        <div class="panel-subtitle">紅色為獲利、綠色為虧損 (台股顏色慣例)</div>
    </div>
    """, unsafe_allow_html=True)

    if selected_month is not None:
        year, month = map(int, selected_month.split("-"))

        month_df = filtered_df[
            filtered_df["exit_time"].dt.to_period("M").astype(str) == selected_month
        ].copy()

        month_df["exit_date"] = month_df["exit_time"].dt.date

        month_df["display_date"] = month_df["exit_date"].apply(
            lambda d: d - pd.Timedelta(days=1) if pd.Timestamp(d).weekday() == 5 else d
        )

        daily_df = month_df.groupby("display_date").agg(
            day_pnl=("export_net_pnl", "sum"),
            trades=("export_net_pnl", "size"),
            win_rate=("export_net_pnl", lambda s: (s.gt(0).mean() * 100) if len(s) > 0 else 0)
        ).reset_index()

        daily_map = {
            row["display_date"]: {
                "pnl": row["day_pnl"],
                "trades": int(row["trades"]),
                "win_rate": row["win_rate"]
            }
            for _, row in daily_df.iterrows()
        }

        title_dt = datetime(year, month, 1)
        st.markdown(f"<div class='month-header'>{title_dt.strftime('%Y 年 %m 月')}</div>", unsafe_allow_html=True)

        col_widths = [1, 1, 1, 1, 1, 1, 1, 1.45]

        head_cols = st.columns(col_widths)
        weekday_names = ["日", "一", "二", "三", "四", "五", "六"]

        for i in range(7):
            with head_cols[i]:
                st.markdown(
                    f"<div class='calendar-head'>{weekday_names[i]}</div>",
                    unsafe_allow_html=True
                )

        with head_cols[7]:
            st.markdown(
                "<div class='calendar-side-head'>週統計</div>",
                unsafe_allow_html=True
            )

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdatescalendar(year, month)

        for week_idx, week in enumerate(weeks, start=1):
            row_cols = st.columns(col_widths)

            week_pnl = 0
            week_days_with_trade = 0

            for i, day in enumerate(week):
                with row_cols[i]:
                    if day.month != month:
                        st.markdown("<div class='calendar-empty'></div>", unsafe_allow_html=True)
                    else:
                        info = daily_map.get(day, None)

                        if info is None:
                            st.markdown(f"""
                            <div class="calendar-card-neutral">
                                <div class="day-num">{day.day}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            pnl = info["pnl"]
                            trades = info["trades"]
                            wr = info["win_rate"]

                            week_pnl += pnl
                            week_days_with_trade += 1

                            style_info = get_day_card_info(pnl)

                            st.markdown(f"""
                            <div class="{style_info['card_class']}">
                                <div class="day-num">{day.day}</div>
                                <div class="{style_info['pnl_class']}">{format_currency_text(pnl)}</div>
                                <div class="{style_info['sub_class']}">{trades} 筆交易</div>
                                <div class="{style_info['sub_class']}">勝率 {wr:.1f}%</div>
                            </div>
                            """, unsafe_allow_html=True)

            with row_cols[7]:
                pnl_cls = pnl_class_name(week_pnl)
                st.markdown(f"""
                <div class="week-side-card">
                    <div class="week-side-title">第 {week_idx} 週</div>
                    <div class="week-side-pnl {pnl_cls}">{format_currency_text(week_pnl)}</div>
                    <div class="week-side-sub">{week_days_with_trade} 天</div>
                </div>
                """, unsafe_allow_html=True)

    # 最新 10 筆平倉紀錄明細
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="panel" style="margin-bottom:10px;">
        <div class="panel-title">最新 10 筆平倉紀錄明細</div>
        <div class="panel-subtitle">依出場時間倒序排列</div>
    </div>
    """, unsafe_allow_html=True)

    recent_trades = filtered_df.sort_values("exit_time", ascending=False).head(10).copy()

    recent_trades["進場時間"] = recent_trades["entry_time"].dt.strftime("%m-%d %H:%M")
    recent_trades["出場時間"] = recent_trades["exit_time"].dt.strftime("%m-%d %H:%M")
    recent_trades["方向"] = recent_trades["entry_dir"].apply(safe_direction_text)
    recent_trades["進場價"] = recent_trades["entry_price"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
    recent_trades["出場價"] = recent_trades["exit_price"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
    recent_trades["淨損益 (NTD)"] = recent_trades["export_net_pnl"].apply(format_currency_text)
    recent_trades["出場原因"] = recent_trades["exit_reason"].fillna("").astype(str)

    show_cols = ["進場時間", "出場時間", "方向", "進場價", "出場價", "淨損益 (NTD)", "出場原因"]
    recent_show_df = recent_trades[show_cols].reset_index(drop=True)

    def highlight_pnl(val):
        if isinstance(val, str):
            if val.startswith("+$"):
                return "color:#EF4444; font-weight:600;"
            elif val.startswith("-$"):
                return "color:#10B981; font-weight:600;"
        return ""

    def highlight_direction(val):
        if val == "多 (LONG)":
            return "color:#EF4444; font-weight:600;"
        elif val == "空 (SHORT)":
            return "color:#10B981; font-weight:600;"
        return ""

    styled_df = (
        recent_show_df.style
        .map(highlight_pnl, subset=["淨損益 (NTD)"])
        .map(highlight_direction, subset=["方向"])
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=390
    )

# ============================================
# [11] 左側選單
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">📊 台指期策略中心</div>
        <div class="sidebar-brand-subtitle">
            績效展示 · 資金曲線 · 月曆檢視 · 策略介紹
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        "頁面切換",
        ["策略績效儀表板", "策略說明"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(f"""
    <div class="sidebar-info-card">
        <div class="sidebar-info-title">System Info</div>
        <div class="sidebar-info-text">
            資料每 {AUTO_REFRESH_MS // 1000} 秒自動刷新<br>
            可隨時切換統計期間<br>
            資料來源：TXF_Market_Timing_trades.csv
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# [12] 主頁面切換
# ============================================
if page == "策略說明":
    render_strategy_description_page()
else:
    render_dashboard_page()
