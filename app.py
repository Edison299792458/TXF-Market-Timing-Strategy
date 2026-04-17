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
st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

st_autorefresh(interval=AUTO_REFRESH_MS, key="data_refresh")

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

/* 保留 header 的側邊欄切換按鈕 */
header {
    background: transparent !important;
}

/* 側邊欄收合按鈕 */
button[kind="header"] {
    color: #FAFAFA !important;
}

[data-testid="collapsedControl"] {
    color: #FAFAFA !important;
    background: rgba(24, 24, 27, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}

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
    border: 1px solid rgba(255, 255, 255, 0
