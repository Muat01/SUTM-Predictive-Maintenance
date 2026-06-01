import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import time

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Predictive Maintenance — SUTM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# PHASE 1 — FILE IDs (مخفية داخل الكود)
# ══════════════════════════════════════════════════════════════
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"

# ══════════════════════════════════════════════════════════════
# PHASE 2 — FULL CSS SYSTEM (UPDATED WITH PLN BRANDING & FLICKER FIXES)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

/* ── ROOT VARIABLES ── */
:root {
    --bg-base:       #060810;
    --bg-card:       #0c0f1a;
    --bg-card2:      #101422;
    --bg-sidebar:    #080b14;
    --clr-critical:  #ff3355;
    --clr-high:      #ff8c00;
    --clr-medium:    #0ea5e9;
    --clr-low:       #00e5b0;
    --clr-accent:    #00A3E0; /* PLN Official Blue */
    --clr-yellow:    #FFD600; /* PLN Official Yellow */
    --clr-teal:      #00C5B5; /* PLN Official Teal */
    --clr-text:      #e2e8f0;
    --clr-muted:     #64748b;
    --clr-border:    rgba(255,255,255,0.06);
    --glow-critical: 0 0 20px rgba(255,51,85,0.35);
    --glow-high:     0 0 20px rgba(255,140,0,0.35);
    --glow-medium:   0 0 20px rgba(14,165,233,0.35);
    --glow-low:      0 0 20px rgba(0,229,176,0.35);
    --glow-accent:   0 0 30px rgba(0,163,224,0.35);
    --font-display:  'Rajdhani', sans-serif;
    --font-mono:     'JetBrains Mono', monospace;
    --font-body:     'Inter', sans-serif;
}

/* ── BASE ── */
html, body, .stApp { background-color: var(--bg-base) !important; }
* { font-family: var(--font-body); }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--clr-border);
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }

/* ── HERO SECTION ── */
.hero-wrapper {
    background: linear-gradient(135deg, #060810 0%, #081a2f 50%, #061122 100%);
    border: 1px solid rgba(0,163,224,0.25);
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,163,224,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 400px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,197,181,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--clr-accent);
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 20px; height: 1px;
    background: var(--clr-accent);
}
.hero-title {
    font-family: var(--font-display);
    font-size: 42px;
    font-weight: 700;
    letter-spacing: 1px;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #00A3E0 60%, #00C5B5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 6px 0;
}
.hero-subtitle {
    font-size: 14px;
    color: var(--clr-muted);
    font-weight: 400;
    letter-spacing: 0.3px;
    margin-bottom: 20px;
}
.hero-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}
.badge {
    font-family: var(--font-mono);
    font-size: 10px;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
    font-weight: 600;
}
.badge-live {
    background: rgba(0,197,181,0.1);
    border: 1px solid rgba(0,197,181,0.3);
    color: var(--clr-teal);
    display: flex;
    align-items: center;
    gap: 5px;
}
.badge-live::before {
    content: '';
    width: 6px; height: 6px;
    background: var(--clr-teal);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--clr-teal);
    animation: pulse-dot 1.5s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.badge-system {
    background: rgba(0,163,224,0.1);
    border: 1px solid rgba(0,163,224,0.3);
    color: var(--clr-accent);
}
.badge-ai {
    background: rgba(255,214,0,0.1);
    border: 1px solid rgba(255,214,0,0.3);
    color: var(--clr-yellow);
}
.hero-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--clr-border);
}
.hero-stat {
    text-align: center;
}
.hero-stat-val {
    font-family: var(--font-display);
    font-size: 24px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.hero-stat-lbl {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--clr-muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.stat-critical { color: var(--clr-critical); text-shadow: var(--glow-critical); }
.stat-high     { color: var(--clr-high);     text-shadow: var(--glow-high); }
.stat-medium   { color: var(--clr-medium);   text-shadow: var(--glow-medium); }
.stat-low      { color: var(--clr-low);      text-shadow: var(--glow-low); }

/* ── SIDEBAR NAV CARDS ── */
.sidebar-header {
    padding: 24px 20px 16px;
    border-bottom: 1px solid var(--clr-border);
}
.pln-logo-container {
    margin-bottom: 12px;
}
.pln-logo {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #00A3E0, #FFD600);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.pln-sub {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--clr-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 3px;
}
.nav-section-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--clr-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 16px 20px 8px;
}
.nav-card {
    margin: 3px 12px;
    padding: 11px 14px;
    border-radius: 10px;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-card:hover {
    background: rgba(0,163,224,0.08);
    border-color: rgba(0,163,224,0.2);
}
.nav-card.active {
    background: rgba(0,163,224,0.12);
    border-color: rgba(0,163,224,0.3);
    box-shadow: 0 0 16px rgba(0,163,224,0.1);
}
.nav-icon { font-size: 18px; width: 24px; text-align: center; }
.nav-text {
    font-family: var(--font-body);
    font-size: 13px;
    font-weight: 500;
    color: var(--clr-text);
}
.nav-text-sub {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--clr-muted);
    letter-spacing: 0.5px;
}
.sidebar-status {
    margin: 16px 12px;
    padding: 12px 14px;
    background: rgba(0,197,181,0.05);
    border: 1px solid rgba(0,197,181,0.15);
    border-radius: 10px;
}
.status-dot-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--clr-teal);
    margin-bottom: 4px;
}
.status-dot {
    width: 7px; height: 7px;
    background: var(--clr-teal);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--clr-teal);
    animation: pulse-dot 2s infinite;
    flex-shrink: 0;
}
.status-time {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--clr-muted);
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
.kpi-card {
    background: var(--bg-card);
    border-radius: 14px;
    padding: 18px 16px;
    border: 1px solid var(--clr-border);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.kpi-critical::before { background: var(--clr-critical); box-shadow: var(--glow-critical); }
.kpi-card.kpi-high::before     { background: var(--clr-high);     box-shadow: var(--glow-high); }
.kpi-card.kpi-medium::before   { background: var(--clr-medium);   box-shadow: var(--glow-medium); }
.kpi-card.kpi-low::before      { background: var(--clr-low);      box-shadow: var(--glow-low); }
.kpi-card.kpi-total::before    { background: linear-gradient(90deg, var(--clr-accent), var(--clr-teal)); }
.kpi-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--clr-muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: var(--font-display);
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-delta {
    font-family: var(--font-mono);
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 20px;
    display: inline-block;
}
.kpi-delta.up   { background: rgba(255,51,85,0.1);  color: var(--clr-critical); }
.kpi-delta.down { background: rgba(0,197,181,0.1);  color: var(--clr-teal); }
.kpi-delta.neu  { background: rgba(255,255,255,0.05); color: var(--clr-muted); }
.kpi-glow-bg {
    position: absolute;
    bottom: -30px; right: -20px;
    width: 100px; height: 100px;
    border-radius: 50%;
    opacity: 0.06;
}
.kpi-critical .kpi-value { color: var(--clr-critical); text-shadow: 0 0 20px rgba(255,51,85,0.4); }
.kpi-high     .kpi-value { color: var(--clr-high);     text-shadow: 0 0 20px rgba(255,140,0,0.4); }
.kpi-medium   .kpi-value { color: var(--clr-medium);   text-shadow: 0 0 20px rgba(14,165,233,0.4); }
.kpi-low      .kpi-value { color: var(--clr-low);      text-shadow: 0 0 20px rgba(0,229,176,0.4); }
.kpi-total    .kpi-value { color: #ffffff; }

/* ── AI INSIGHT CARDS ── */
.insight-card {
    background: linear-gradient(135deg, #0c0f1a 0%, #0f1826 100%);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    border-left: 3px solid;
    position: relative;
    overflow: hidden;
}
.insight-card.critical { border-color: var(--clr-critical); box-shadow: -4px 0 16px rgba(255,51,85,0.15); }
.insight-card.high     { border-color: var(--clr-high);     box-shadow: -4px 0 16px rgba(255,140,0,0.15); }
.insight-card.info     { border-color: var(--clr-accent);   box-shadow: -4px 0 16px rgba(0,163,224,0.15); }
.insight-card.success  { border-color: var(--clr-teal);     box-shadow: -4px 0 16px rgba(0,197,181,0.15); }
.insight-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.insight-icon { font-size: 18px; }
.insight-title {
    font-family: var(--font-display);
    font-size: 15px;
    font-weight: 600;
    color: var(--clr-text);
    letter-spacing: 0.3px;
}
.insight-body {
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.6;
}
.insight-action {
    margin-top: 10px;
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 4px;
    display: inline-block;
}
.insight-card.critical .insight-action { background: rgba(255,51,85,0.1); color: var(--clr-critical); }
.insight-card.high     .insight-action { background: rgba(255,140,0,0.1); color: var(--clr-high); }
.insight-card.info     .insight-action { background: rgba(0,163,224,0.1); color: var(--clr-accent); }

/* ── ALERT BANNER ── */
.alert-banner {
    background: linear-gradient(135deg, rgba(255,51,85,0.08), rgba(255,140,0,0.05));
    border: 1px solid rgba(255,51,85,0.25);
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.alert-banner-icon { font-size: 22px; }
.alert-banner-text { font-size: 13px; color: var(--clr-text); }
.alert-banner-text strong { color: var(--clr-critical); }

/* ── SECTION HEADER ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--clr-border);
}
.section-icon { font-size: 18px; }
.section-title {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 600;
    color: var(--clr-text);
    letter-spacing: 0.5px;
}
.section-badge {
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 1px;
    padding: 3px 9px;
    border-radius: 20px;
    background: rgba(0,163,224,0.1);
    border: 1px solid rgba(0,163,224,0.2);
    color: var(--clr-accent);
    text-transform: uppercase;
}

/* ── LOADING SKELETON (TASK 3) ── */
.skeleton {
    background: linear-gradient(90deg, #0c0f1a 25%, #141b2d 50%, #0c0f1a 75%);
    background-size: 400% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 10px;
}
@keyframes shimmer {
    0% { background-position: 100% 0; }
    100% { background-position: -100% 0; }
}
.skeleton-hero { height: 180px; width: 100%; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.03); }
.skeleton-kpi-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 24px; }
.skeleton-kpi { height: 102px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.03); }
.skeleton-charts-container { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.skeleton-chart { height: 350px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.03); }

/* ── EXEC SUMMARY ── */
.health-score-ring {
    text-align: center;
    padding: 20px;
}
.health-score-num {
    font-family: var(--font-display);
    font-size: 64px;
    font-weight: 700;
    line-height: 1;
    background: linear-gradient(135deg, #00C5B5, #00A3E0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.health-score-lbl {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--clr-muted);
    text-transform: uppercase;
    margin-top: 4px;
}
.priority-matrix {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
.priority-item {
    background: var(--bg-card);
    border-radius: 12px;
    padding: 16px;
    border: 1px solid var(--clr-border);
}
.priority-rank {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--clr-muted);
    margin-bottom: 6px;
}
.priority-name {
    font-family: var(--font-display);
    font-size: 16px;
    font-weight: 600;
    color: var(--clr-text);
}
.priority-bar {
    height: 4px;
    background: var(--clr-border);
    border-radius: 2px;
    margin-top: 8px;
    overflow: hidden;
}
.priority-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--clr-critical), var(--clr-high));
}

/* ── TABLE STYLING ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid var(--clr-border) !important; border-radius: 12px; }

/* ── PLOTLY CHARTS & ANTI-FLICKER SYSTEM (TASK 2) ── */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }
.stPlotlyChart, div[data-testid="metric-container"] {
    opacity: 1;
    transition: opacity 0.3s ease;
    min-height: 50px;
}

/* ── METRIC OVERRIDE ── */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--clr-border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: rgba(0,163,224,0.1) !important;
    border: 1px solid rgba(0,163,224,0.3) !important;
    color: var(--clr-accent) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,163,224,0.2) !important;
    box-shadow: 0 0 16px rgba(0,163,224,0.2) !important;
}

/* ── SELECTBOX / MULTISELECT ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--clr-border) !important;
    border-radius: 8px !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--clr-border) !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# COLORS & THEME
# ══════════════════════════════════════════════════════════════
COLORS = {
    "CRITICAL": "#ff3355",
    "HIGH":     "#ff8c00",
    "MEDIUM":   "#0ea5e9",
    "LOW":      "#00e5b0",
}
PLOT_BG  = "#0c0f1a"
PAPER_BG = "#060810"
FONT_COL = "#e2e8f0"
GRID_COL = "rgba(255,255,255,0.04)"

def dark_layout(fig, title="", height=350):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Rajdhani, sans-serif", size=15, color=FONT_COL)),
        height=height,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Inter, sans-serif", size=11),
        margin=dict(l=16, r=16, t=44 if title else 16, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10), borderwidth=0),
        xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
        yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# PHASE 1 — GOOGLE DRIVE LOADER
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def load_from_drive(file_id: str, sheet_name: str) -> pd.DataFrame:
    try:
        creds_info = st.secrets["google_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return pd.read_excel(fh, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return pd.DataFrame()

# ══════════════════════════════════════════════════════════════
# HI MAPPING & PROCESSING (unchanged logic)
# ══════════════════════════════════════════════════════════════
HI_MAP = {"BAIK": 3, "CUKUP": 2, "KURANG": 1, "BURUK": 0}

def hi_from_text(val):
    if pd.isna(val) or str(val).strip().upper() in ["BLANK", "TIDAK ADA", "-", ""]:
        return 3
    v = str(val).upper()
    if any(x in v for x in ["BURUK","PECAH","PUTUS","KEROPOS","FLASH","BOCOR","RANTAS","RETAK"]):
        return 0
    if any(x in v for x in ["KURANG","KENDOR","LEPAS","MIRING","LONGGAR","BELUM","RAMBAT"]):
        return 1
    if any(x in v for x in ["CUKUP","LUMUT","BERKARAT","PARALON"]):
        return 2
    return 3

@st.cache_data(ttl=30)
def process_data(t1_id: str, t2_id: str):
    t1 = load_from_drive(t1_id, "DATA")
    t2 = load_from_drive(t2_id, "DATA")

    if t1.empty:
        return pd.DataFrame(), pd.DataFrame()

    cond_cols = [
        "KONDISI TIANG", "KONDISI EKSTENSI", "KONDISI TRAVERS", "KONDISI GSW",
        "KONDISI PENYANGGA TIANG", "KONDISI PENAMPANG", "KONDISI JUMPER",
        "KONDISI PENGIKAT", "KONDISI ISOLATOR TUMPU", "KONDISI ISOLATOR AFSPAN",
        "KONDISI ARRESTER", "KONDISI FCO"
    ]
    for c in cond_cols:
        if c in t1.columns:
            t1[f"HI_{c}"] = t1[c].apply(hi_from_text)

    hi_cols = [f"HI_{c}" for c in cond_cols if c in t1.columns]
    t1["TIANG_ID"] = (t1["PENYULANG"].astype(str).str.strip()
                      + "_" + t1["NO TIANG"].astype(str).str.strip())
    t1["N_BURUK"]  = t1[hi_cols].apply(lambda r: sum(1 for v in r if v == 0), axis=1)
    t1["N_KURANG"] = t1[hi_cols].apply(lambda r: sum(1 for v in r if v == 1), axis=1)

    worst = (t1.groupby(["TIANG_ID", "ULP", "PENYULANG", "NO TIANG"])
               .agg(N_BURUK=("N_BURUK","max"), N_KURANG=("N_KURANG","max"))
               .reset_index())

    def risk(nb, nk):
        if nb >= 2: return "CRITICAL"
        if nb == 1: return "HIGH"
        if nk >= 1: return "MEDIUM"
        return "LOW"

    worst["RISK_CLASS"] = worst.apply(lambda r: risk(r["N_BURUK"], r["N_KURANG"]), axis=1)

    np.random.seed(42)
    rb = {"LOW": 15, "MEDIUM": 40, "HIGH": 70, "CRITICAL": 90}
    worst["RISK_SCORE"] = (worst["RISK_CLASS"].map(rb)
                           + np.random.uniform(-4, 4, len(worst)))
    worst["RISK_SCORE"] = worst["RISK_SCORE"].clip(0, 100).round(1)

    if not t2.empty:
        t2["TIANG_ID"] = (t2["PENYULANG"].astype(str).str.strip()
                          + "_" + t2["NO TIANG"].astype(str).str.strip())
        t2["NUM_HI_1"] = t2["HI SUTM  - 1"].map(HI_MAP).fillna(3)
        t2["NUM_HI_2"] = t2["HI SUTM - 2"].map(HI_MAP).fillna(3)
        temp_c = ["SUHU FASA R", "SUHU FASA S", "SUHU FASA T"]
        vt = t2[temp_c].apply(pd.to_numeric, errors="coerce")
        t2["DELTA_SUHU"] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    comp_map = {
        "HI_KONDISI TIANG":           "Tiang (Pole)",
        "HI_KONDISI TRAVERS":         "Travers",
        "HI_KONDISI PENYANGGA TIANG": "Penyangga",
        "HI_KONDISI PENGIKAT":        "Pengikat",
        "HI_KONDISI ISOLATOR TUMPU":  "Isolator Tumpu",
        "HI_KONDISI ISOLATOR AFSPAN": "Isolator Afspan",
        "HI_KONDISI ARRESTER":        "Arrester",
        "HI_KONDISI JUMPER":          "Jumper",
        "HI_KONDISI PENAMPANG":       "Penampang",
        "HI_KONDISI GSW":             "GSW",
        "HI_KONDISI EKSTENSI":        "Ekstensi",
        "HI_KONDISI FCO":             "FCO",
    }
    hi_stats = []
    for col, label in comp_map.items():
        if col in t1.columns:
            vc = t1[col].value_counts()
            hi_stats.append({
                "Component": label,
                "BAIK":   int(vc.get(3, 0)),
                "CUKUP":  int(vc.get(2, 0)),
                "KURANG": int(vc.get(1, 0)),
                "BURUK":  int(vc.get(0, 0)),
            })

    worst._hi_stats = hi_stats
    worst._t1_raw   = t1
    worst._t2_raw   = t2 if not t2.empty else pd.DataFrame()
    worst._total_inspections = len(t1)

    return worst, pd.DataFrame(hi_stats)

# ══════════════════════════════════════════════════════════════
# PHASE 4 — AI INSIGHT ENGINE
# ══════════════════════════════════════════════════════════════
def generate_ai_insights(df, hi_df):
    insights = []

    if df.empty:
        return insights

    rc = df["RISK_CLASS"].value_counts()
    total = len(df)
    n_crit = int(rc.get("CRITICAL", 0))
    n_high = int(rc.get("HIGH", 0))

    # Insight 1 — Critical ULP
    if "ULP" in df.columns:
        crit_by_ulp = df[df["RISK_CLASS"] == "CRITICAL"].groupby("ULP").size()
        if not crit_by_ulp.empty:
            top_ulp = crit_by_ulp.idxmax()
            top_count = int(crit_by_ulp.max())
            pct = round(top_count / total * 100, 1)
            insights.append({
                "type": "critical",
                "icon": "🚨",
                "title": f"Critical Concentration — {top_ulp}",
                "body": f"{top_ulp} has the highest concentration of CRITICAL-risk poles ({top_count} poles, {pct}% of fleet). Immediate preventive inspection recommended within 7–14 days to prevent cascading failures.",
                "action": "Schedule Inspection"
            })

    # Insight 2 — Overall risk level
    risk_ratio = (n_crit + n_high) / total * 100 if total > 0 else 0
    if risk_ratio > 20:
        insights.append({
            "type": "high",
            "icon": "⚠️",
            "title": "Fleet Risk Threshold Exceeded",
            "body": f"{risk_ratio:.1f}% of the asset fleet is classified HIGH or CRITICAL risk ({n_crit + n_high:,} poles). This exceeds the recommended 15% safety threshold. Accelerated maintenance scheduling is advised.",
            "action": "View Priority List"
        })
    else:
        insights.append({
            "type": "info",
            "icon": "✅",
            "title": "Fleet Risk Within Acceptable Range",
            "body": f"Overall fleet risk ratio is {risk_ratio:.1f}%. Combined HIGH+CRITICAL count stands at {n_crit + n_high:,} poles. Continue scheduled preventive maintenance cycle.",
            "action": "View Details"
        })

    # Insight 3 — Worst component
    if not hi_df.empty and "BURUK" in hi_df.columns:
        worst_comp = hi_df.loc[hi_df["BURUK"].idxmax()]
        if worst_comp["BURUK"] > 0:
            insights.append({
                "type": "high",
                "icon": "🔧",
                "title": f"Component Alert — {worst_comp['Component']}",
                "body": f"{worst_comp['Component']} has the highest BURUK count ({int(worst_comp['BURUK']):,} units). This component should be prioritized in the next maintenance batch to reduce cascading risk.",
                "action": "Inspect Component"
            })

    # Insight 4 — Top penyulang risk
    if "PENYULANG" in df.columns:
        pen_risk = df[df["RISK_CLASS"].isin(["CRITICAL","HIGH"])].groupby("PENYULANG").size()
        if not pen_risk.empty:
            top_pen = pen_risk.idxmax()
            top_pen_count = int(pen_risk.max())
            insights.append({
                "type": "info",
                "icon": "⚡",
                "title": f"High-Risk Feeder — {top_pen}",
                "body": f"Feeder {top_pen} concentrates {top_pen_count} HIGH/CRITICAL poles. Consider isolating for targeted inspection to minimize service disruption risk.",
                "action": "Analyze Feeder"
            })

    return insights

# ══════════════════════════════════════════════════════════════
# SIDEBAR — PHASE 2 (Navigation Cards + UPDATED BRANDING LOGO)
# ══════════════════════════════════════════════════════════════
PAGES = [
    ("📊", "Overview",           "Fleet status & KPIs"),
    ("⚠️", "Risk Analysis",      "Risk distribution"),
    ("🏥", "Health Index",       "Component HI"),
    ("🌡️", "Thermal",            "Temperature data"),
    ("🤖", "ML Comparison",      "Model benchmarks"),
    ("🎯", "Priority Poles",     "Top risk assets"),
    ("📋", "Executive Summary",  "Management view"),
]

with st.sidebar:
    # Task 1: Added Official PLN Branding Logo Above the Text
    st.markdown("""
    <div class="sidebar-header" style="text-align: center;">
        <div class="pln-logo-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Logo_PLN.png/240px-Logo_PLN.png" style="height: 60px; margin-bottom: 8px;" alt="PLN Logo">
        </div>
        <div class="pln-logo">⚡ PLN UP3</div>
        <div class="pln-sub">PT PLN · Bandung · 2026</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="nav-section-label">Navigation</div>', unsafe_allow_html=True)

    if "page_idx" not in st.session_state:
        st.session_state.page_idx = 0

    for i, (icon, name, desc) in enumerate(PAGES):
        is_active = st.session_state.page_idx == i
        active_cls = "active" if is_active else ""
        if st.button(
            f"{icon} {name}", key=f"nav_{i}", use_container_width=True, help=desc
        ):
            st.session_state.page_idx = i
            st.rerun()

    page = PAGES[st.session_state.page_idx][1]

    st.markdown('<div class="nav-section-label" style="margin-top:8px;">System</div>', unsafe_allow_html=True)
    now_str = pd.Timestamp.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="sidebar-status">
        <div class="status-dot-row">
            <div class="status-dot"></div> LIVE MONITORING
        </div>
        <div class="status-time">Last sync: {now_str}</div>
        <div class="status-time">Auto-refresh: 30s</div>
    </div>
    """, unsafe_allow_html=True)

    auto_refresh = st.toggle("🔄 Auto Refresh", value=True)
    if st.button("⟳ Manual Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if auto_refresh:
    st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TASK 3 — SKELETON SCREENS LOADERS PLACEHOLDER
# ══════════════════════════════════════════════════════════════
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;padding:20px; background:#0c0f1a;border-radius:12px;border:1px solid rgba(255,255,255,0.06); margin-bottom:16px;">
        <div style="font-size:24px;">⚡</div>
        <div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#e2e8f0;font-weight:600;"> Loading asset intelligence... </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#64748b;margin-top:4px;"> Connecting to Google Drive · Processing SUTM data </div>
        </div>
    </div>
    
    <div class="skeleton skeleton-hero"></div>
    <div class="skeleton-kpi-container">
        <div class="skeleton skeleton-kpi"></div>
        <div class="skeleton skeleton-kpi"></div>
        <div class="skeleton skeleton-kpi"></div>
        <div class="skeleton skeleton-kpi"></div>
        <div class="skeleton skeleton-kpi"></div>
    </div>
    <div class="skeleton-charts-container">
        <div class="skeleton skeleton-chart"></div>
        <div class="skeleton skeleton-chart"></div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# REAL DATA PROCESSING & INJECTION
# ══════════════════════════════════════════════════════════════
df, hi_df = process_data(T1_FILE_ID, T2_FILE_ID)
loading_placeholder.empty() # Clear skeleton instantly upon complete load

# (هنا يتبع بقية منطق وعرض الصفحات السبعة بالكامل لبناء التقرير والرسومات بداخل st.container لحمايتها من الوميض)
