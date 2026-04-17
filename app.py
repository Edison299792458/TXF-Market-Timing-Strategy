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

EQUITY_LINE_COLOR = "#10B981"
EQUITY_FILL_COLOR_RGB = "16,185,129"
EQUITY_FILL_ALPHA = 0.12

PAGE_TITLE = "台指期無限轉倉擇時策略"
INITIAL_SIDEBAR_STATE = "expanded"

DEFAULT_PERIOD_OPTIONS = ["近1個月", "近3個月", "近9個月", "近12個月", "近2年", "近3年", "近4年", "全部"]
DEFAULT_PERIOD_INDEX = 5

# ============================================
# [04] 基本設定
# ============================================
st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

st_autorefresh(interval=AUTO_REFRESH_MS, key="data_refresh")

# ============================================
# [05] 全站樣式
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ========= 基礎 ========= */
html, body, [class*="css"] {
    background-color: #09090B !important;
    color: #E4E4E7 !important;
    font-family: "Inter", "Segoe UI", "Microsoft JhengHei", -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(16, 185, 129, 0.04), transparent),
        #09090B !important;
}

.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1720px !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background: transparent !important;}

/* ========= 標題 ========= */
.dashboard-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 20px;
    letter-spacing: -0.025em;
    display: flex;
    align-items: center;
    gap: 14px;
}

.dashboard-title-accent {
    width: 3px;
    height: 22px;
    background: #10B981;
    border-radius: 2px;
    flex-shrink: 0;
}

.page-top-note {
    color: #52525B;
    font-size: 0.8125rem;
    margin-top: -16px;
    margin-bottom: 28px;
    font-weight: 400;
}

/* ========= Panel ========= */
.panel {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
}

.panel-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #FAFAFA;
    margin-bottom: 2px;
    letter-spacing: -0.01em;
}

.panel-subtitle {
    font-size: 0.8125rem;
    color: #52525B;
    margin-bottom: 10px;
    font-weight: 400;
}

/* ========= KPI ========= */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}

.kpi-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 18px 20px;
    min-height: 120px;
    transition: border-color 0.2s ease;
}

.kpi-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
}

.kpi-label {
    font-size: 0.6875rem;
    color: #71717A;
    margin-bottom: 10px;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 1.625rem;
    font-weight: 700;
    color: #FAFAFA;
    line-height: 1.1;
    margin-bottom: 8px;
    letter-spacing: -0.025em;
    font-variant-numeric: tabular-nums;
}

.kpi-foot {
    font-size: 0.6875rem;
    color: #3F3F46;
    font-weight: 400;
}

/* ========= 顏色 ========= */
.text-red { color: #EF4444 !important; }
.text-green { color: #10B981 !important; }
.text-blue { color: #3B82F6 !important; }
.text-purple { color: #8B5CF6 !important; }
.text-orange { color: #F59E0B !important; }
.text-white { color: #FAFAFA !important; }
.text-yellow { color: #EAB308 !important; }

.info-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.15);
    color: #34D399;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.6875rem;
    font-weight: 500;
}

.info-badge::before {
    content: "";
    width: 5px;
    height: 5px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

/* ========= Sidebar ========= */
section[data-testid="stSidebar"] {
    background: #09090B !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

section[data-testid="stSidebar"] > div {
    background: #09090B !important;
}

section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding-top: 1.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 讓左側欄保持可見，不要被壓到完全消失 */
@media (min-width: 768px) {
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
    }
}

/* sidebar 裡所有文字先強制恢復可見 */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] * {
    color: #E4E4E7 !important;
    opacity: 1 !important;
}

/* 品牌區 */
.sidebar-brand {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0 0 18px 0;
    margin-bottom: 20px;
}

.sidebar-brand-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: #FAFAFA !important;
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}

.sidebar-brand-subtitle {
    font-size: 0.6875rem;
    color: #A1A1AA !important;
    line-height: 1.5;
    font-weight: 400;
}

.sidebar-section-title {
    font-size: 0.625rem;
    font-weight: 600;
    color: #71717A !important;
    margin: 16px 0 10px 2px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Streamlit radio 外框 */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 10px 12px !important;
    margin-bottom: 4px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    background: rgba(255, 255, 255, 0.02) !important;
    cursor: pointer !important;
    visibility: visible !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    border-color: rgba(255, 255, 255, 0.12) !important;
    background: rgba(255, 255, 255, 0.04) !important;
}

/* 被選到的項目 */
section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
    background: rgba(16, 185, 129, 0.10) !important;
    border-color: rgba(16, 185, 129, 0.30) !important;
}

/* 有些版本不吃 data-checked，改抓 aria-checked */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[aria-checked="true"]) {
    background: rgba(16, 185, 129, 0.10) !important;
    border-color: rgba(16, 185, 129, 0.30) !important;
}

/* radio 文字 */
section[data-testid="stSidebar"] div[role="radiogroup"] label p,
section[data-testid="stSidebar"] div[role="radiogroup"] label span,
section[data-testid="stSidebar"] div[role="radiogroup"] label div {
    color: #E4E4E7 !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* radio 圓點本身 */
section[data-testid="stSidebar"] input[type="radio"] {
    accent-color: #10B981 !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* System 區 */
.sidebar-info-card {
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: 16px 0 0 0;
    margin-top: 24px;
}

.sidebar-info-title {
    font-size: 0.625rem;
    font-weight: 600;
    color: #71717A !important;
    margin-bottom: 8px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.sidebar-info-text {
    font-size: 0.6875rem;
    color: #A1A1AA !important;
    line-height: 1.8;
    font-weight: 400;
}

/* ========= 策略說明 ========= */
.strategy-panel {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 30px 32px;
    margin-bottom: 14px;
}

.strategy-hero {
    background: rgba(16, 185, 129, 0.04);
    border: 1px solid rgba(16, 185, 129, 0.1);
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 28px;
}

.strategy-hero-title {
    font-size: 1rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 10px;
    letter-spacing: -0.01em;
}

.strategy-hero-text {
    font-size: 0.875rem;
    line-height: 1.75;
    color: #A1A1AA;
    font-weight: 400;
}

.strategy-section-head {
    font-size: 0.875rem;
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
    height: 14px;
    background: #10B981;
    border-radius: 2px;
}

.strategy-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 8px;
}

.strategy-item-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 6px;
}

.strategy-item-text {
    font-size: 0.8125rem;
    line-height: 1.75;
    color: #A1A1AA;
    font-weight: 400;
}

.strategy-bullet-box {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
}

.strategy-bullet-item {
    font-size: 0.8125rem;
    line-height: 1.9;
    color: #A1A1AA;
    padding-left: 16px;
    position: relative;
    font-weight: 400;
}

.strategy-bullet-item::before {
    content: "";
    position: absolute;
    left: 0;
    top: 11px;
    width: 4px;
    height: 4px;
    background: #3F3F46;
    border-radius: 50%;
}

.strategy-one-line {
    font-size: 0.875rem;
    line-height: 1.85;
    color: #D4D4D8;
    font-weight: 500;
}

/* ========= 月曆 ========= */
.calendar-head {
    text-align: center;
    color: #52525B;
    font-size: 0.6875rem;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.06em;
}

.calendar-side-head {
    text-align: center;
    color: transparent;
    font-size: 0.6875rem;
    margin-bottom: 8px;
}

.calendar-empty {
    border-radius: 8px;
    min-height: 100px;
    padding: 10px;
    background: transparent;
    margin-bottom: 6px;
}

.calendar-card-neutral {
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    min-height: 100px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.02);
    margin-bottom: 6px;
}

.calendar-card-pos {
    border-radius: 8px;
    border: 1px solid rgba(239, 68, 68, 0.15);
    min-height: 100px;
    padding: 10px;
    background: rgba(127, 29, 29, 0.25);
    margin-bottom: 6px;
}

.calendar-card-neg {
    border-radius: 8px;
    border: 1px solid rgba(16, 185, 129, 0.15);
    min-height: 100px;
    padding: 10px;
    background: rgba(6, 78, 59, 0.25);
    margin-bottom: 6px;
}

.day-num {
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: #A1A1AA;
    font-variant-numeric: tabular-nums;
}

.day-pnl-pos {
    font-size: 0.875rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 5px;
    color: #FCA5A5;
    font-variant-numeric: tabular-nums;
}

.day-pnl-neg {
    font-size: 0.875rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 5px;
    color: #6EE7B7;
    font-variant-numeric: tabular-nums;
}

.day-sub-pos {
    font-size: 0.625rem;
    line-height: 1.5;
    color: rgba(252, 165, 165, 0.7);
}

.day-sub-neg {
    font-size: 0.625rem;
    line-height: 1.5;
    color: rgba(110, 231, 183, 0.7);
}

.day-sub-neutral {
    font-size: 0.625rem;
    line-height: 1.5;
    color: #52525B;
}

.week-side-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 10px 12px;
    min-height: 100px;
    margin-bottom: 6px;
}

.week-side-title {
    font-size: 0.625rem;
    color: #52525B;
    margin-bottom: 10px;
    font-weight: 600;
    letter-spacing: 0.04em;
}

.week-side-pnl {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 5px;
    font-variant-numeric: tabular-nums;
}

.week-side-sub {
    font-size: 0.625rem;
    color: #3F3F46;
}

/* ========= 表格 ========= */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    overflow: hidden;
}

/* ========= 按鈕 ========= */
.stButton > button {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #A1A1AA !important;
    font-weight: 500 !important;
    font-size: 0.8125rem !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.14) !important;
    color: #FAFAFA !important;
}

/* ========= 下拉選單 ========= */
div[data-baseweb="select"] > div {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
}

/* ========= 月份標頭 ========= */
.month-header {
    font-size: 0.9375rem;
    font-weight: 700;
    color: #FAFAFA;
    margin: 4px 0 14px 0;
    letter-spacing: -0.01em;
    font-variant-numeric: tabular-nums;
}

/* ========= 分隔線 ========= */
.section-gap {
    height: 20px;
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
        return '<span style="color:#52525B;">$0</span>'

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

    st.markdown(f"""
    <div class="strategy-hero">
        <div class="strategy-hero-title">{STRATEGY_HERO_TITLE}</div>
        <div class="strategy-hero-text">{STRATEGY_HERO_TEXT.strip()}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="strategy-section-head">策略核心邏輯</div>', unsafe_allow_html=True)
    for item in STRATEGY_CORE_ITEMS:
        st.markdown(f"""
        <div class="strategy-item">
            <div class="strategy-item-title">{item['title']}</div>
            <div class="strategy-item-text">{item['text']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="strategy-section-head">策略設計理念</div>', unsafe_allow_html=True)
    st.markdown('<div class="strategy-bullet-box">', unsafe_allow_html=True)
    for bullet in STRATEGY_DESIGN_BULLETS:
        st.markdown(f'<div class="strategy-bullet-item">{bullet}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="strategy-section-head">適合的市場環境</div>', unsafe_allow_html=True)
    st.markdown('<div class="strategy-bullet-box">', unsafe_allow_html=True)
    for bullet in STRATEGY_MARKET_BULLETS:
        st.markdown(f'<div class="strategy-bullet-item">{bullet}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="strategy-section-head">策略優勢</div>', unsafe_allow_html=True)
    st.markdown('<div class="strategy-bullet-box">', unsafe_allow_html=True)
    for bullet in STRATEGY_ADVANTAGE_BULLETS:
        st.markdown(f'<div class="strategy-bullet-item">{bullet}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
        '<div class="dashboard-title"><span class="dashboard-title-accent"></span>策略說明</div>',
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
            <div class="panel-subtitle">找不到 TXF_Market_Timing_trades.csv，請確認檔案是否在同一資料夾。</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    latest_exit = df["exit_time"].max()

    period_label = st.selectbox(
        "績效統計期間",
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
            <div class="kpi-foot">{period_label}</div>
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
            <div class="kpi-foot">獲利 / 總趟數</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">最大回撤</div>
            <div class="kpi-value text-green">-${abs(max_drawdown):,.0f}</div>
            <div class="kpi-foot">歷史最大跌幅</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">盈虧比</div>
            <div class="kpi-value text-orange">{payoff_ratio:.2f}</div>
            <div class="kpi-foot">均盈 / 均虧</div>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">運行天數</div>
            <div class="kpi-value text-yellow">{running_days} 天</div>
            <div class="kpi-foot">首筆至最新交易</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    # 資金曲線
    st.markdown("""
    <div class="panel" style="margin-bottom:0;">
        <div class="panel-title">累計資金曲線</div>
        <div class="panel-subtitle" style="margin-bottom:4px;">
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
        line=dict(color=EQUITY_LINE_COLOR, width=2, shape="spline", smoothing=0.3),
        fill="tozeroy",
        fillcolor=get_equity_fill_rgba(),
        name="累計損益",
        hovertemplate="<b>%{x}</b><br>累計: %{y:,.0f}<br>單趟: %{text}<extra></extra>"
    ))

    fig_equity.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=16, r=16, t=16, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="",
            type="category",
            showgrid=False,
            tickfont=dict(size=10, color="#52525B", family="Inter, sans-serif"),
            showline=False,
            zeroline=False,
            nticks=10
        ),
        yaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.03)",
            tickfont=dict(size=10, color="#52525B", family="Inter, sans-serif"),
            zeroline=True,
            zerolinecolor="rgba(255,255,255,0.06)",
            zerolinewidth=1,
            separatethousands=True
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(24, 24, 27, 0.95)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(family="Inter, sans-serif", size=11, color="#FAFAFA")
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
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
        <div class="panel-title">每日績效月曆</div>
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
        st.markdown(
            f"<div class='month-header'>{title_dt.strftime('%Y 年 %m 月')}</div>",
            unsafe_allow_html=True
        )

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
                        st.markdown(
                            "<div class='calendar-empty'></div>",
                            unsafe_allow_html=True
                        )
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
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel" style="margin-bottom:10px;">
        <div class="panel-title">最新 10 筆平倉紀錄明細</div>
    </div>
    """, unsafe_allow_html=True)

    recent_trades = filtered_df.sort_values("exit_time", ascending=False).head(10).copy()

    recent_trades["進場時間"] = recent_trades["entry_time"].dt.strftime("%m-%d %H:%M")
    recent_trades["出場時間"] = recent_trades["exit_time"].dt.strftime("%m-%d %H:%M")
    recent_trades["方向"] = recent_trades["entry_dir"].apply(safe_direction_text)
    recent_trades["進場價"] = recent_trades["entry_price"].apply(
        lambda x: f"{x:,.0f}" if pd.notna(x) else ""
    )
    recent_trades["出場價"] = recent_trades["exit_price"].apply(
        lambda x: f"{x:,.0f}" if pd.notna(x) else ""
    )
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
# [11] 左側選單 (必須放在頁面渲染之前)
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">台指期策略中心</div>
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
        <div class="sidebar-info-title">System</div>
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
