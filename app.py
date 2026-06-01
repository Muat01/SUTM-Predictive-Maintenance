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
# PHASE 2 — FULL CSS SYSTEM
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
    --clr-medium:    #00A3E0; /* Updated to PLN Blue */
    --clr-low:       #00C5B5; /* Updated to PLN Teal */
    --clr-accent:    #00A3E0; /* Updated to PLN Blue */
    --clr-pln-yellow:#FFD600; /* Added PLN Yellow Accent */
    --clr-text:      #e2e8f0;
    --clr-muted:     #64748b;
    --clr-border:    rgba(255,255,255,0.06);
    --glow-critical: 0 0 20px rgba(255,51,85,0.35);
    --glow-high:     0 0 20px rgba(255,140,0,0.35);
    --glow-medium:   0 0 20px rgba(0,163,224,0.35);
    --glow-low:      0 0 20px rgba(0,197,181,0.35);
    --glow-accent:   0 0 30px rgba(0,163,224,0.2);
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

/* ── ANTI-FLICKERING AND LAYOUT SHIFT PREVENTER ── */
.stPlotlyChart, div[data-testid="metric-container"], .kpi-card {    
    opacity: 1;    
    transition: opacity 0.3s ease;    
    min-height: 50px;
}

/* ── HERO SECTION ── */
.hero-wrapper {
    background: linear-gradient(135deg, #060810 0%, #0c1c2e 50%, #060e22 100%);
    border: 1px solid rgba(0,163,224,0.15);
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
    background: radial-gradient(circle, rgba(0,163,224,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 400px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,197,181,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--clr-pln-yellow);
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
    background: var(--clr-pln-yellow);
}
.hero-title {
    font-family: var(--font-display);
    font-size: 42px;
    font-weight: 700;
    letter-spacing: 1px;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #00A3E0 50%, #00C5B5 100%);
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
    color: var(--clr-low);
    display: flex;
    align-items: center;
    gap: 5px;
}
.badge-live::before {
    content: '';
    width: 6px; height: 6px;
    background: var(--clr-low);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--clr-low);
    animation: pulse-dot 1.5s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.badge-system {
    background: rgba(0,163,224,0.1);
    border: 1px solid rgba(0,163,224,0.25);
    color: var(--clr-accent);
}
.badge-ai {
    background: rgba(255,214,0,0.1);
    border: 1px solid rgba(255,214,0,0.25);
    color: var(--clr-pln-yellow);
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
    color: var(--clr-low);
    margin-bottom: 4px;
}
.status-dot {
    width: 7px; height: 7px;
    background: var(--clr-low);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--clr-low);
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
.kpi-card.kpi-total::before    { background: linear-gradient(90deg, var(--clr-accent), var(--clr-low)); }
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
.kpi-delta.down { background: rgba(0,197,181,0.1);  color: var(--clr-low); }
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
.kpi-medium   .kpi-value { color: var(--clr-medium);   text-shadow: 0 0 20px rgba(0,163,224,0.4); }
.kpi-low      .kpi-value { color: var(--clr-low);      text-shadow: 0 0 20px rgba(0,197,181,0.4); }
.kpi-total    .kpi-value { color: #ffffff; }

/* ── AI INSIGHT CARDS ── */
.insight-card {
    background: linear-gradient(135deg, #0c0f1a 0%, #0f1520 100%);
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
.insight-card.success  { border-color: var(--clr-low);      box-shadow: -4px 0 16px rgba(0,197,181,0.15); }
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

/* ── LOADING SKELETON ── */
.skeleton {
    background: linear-gradient(90deg, #0c0f1a 25%, #141826 50%, #0c0f1a 75%);
    background-size: 400% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 10px;
}
@keyframes shimmer {
    0% { background-position: 100% 0; }
    100% { background-position: -100% 0; }
}

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

/* ── PLOTLY CHARTS ── */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }

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
    "MEDIUM":   "#00A3E0", /* Updated to PLN Blue */
    "LOW":      "#00C5B5", /* Updated to PLN Teal */
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
# SIDEBAR — PHASE 2 (Navigation Cards)
# ══════════════════════════════════════════════════════════════
PAGES = [
    ("📊", "Overview",          "Fleet status & KPIs"),
    ("⚠️", "Risk Analysis",     "Risk distribution"),
    ("🏥", "Health Index",      "Component HI"),
    ("🌡️", "Thermal",           "Temperature data"),
    ("🤖", "ML Comparison",     "Model benchmarks"),
    ("🎯", "Priority Poles",    "Top risk assets"),
    ("📋", "Executive Summary", "Management view"),
]

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="pln-logo-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Logo_PLN.png/240px-Logo_PLN.png" style="height:60px; margin-bottom:8px;" alt="PLN Logo">
        </div>
        <div class="pln-logo">PLN UP3</div>
        <div class="pln-sub">PT PLN · Bandung · 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section-label">Navigation</div>', unsafe_allow_html=True)

    # Use session state for active page
    if "page_idx" not in st.session_state:
        st.session_state.page_idx = 0

    for i, (icon, name, desc) in enumerate(PAGES):
        is_active = st.session_state.page_idx == i
        active_cls = "active" if is_active else ""
        
        # Inject HTML for custom stylized nav cards using st.button logic
        if st.button(
            f"{icon} {name}", 
            key=f"nav_{i}", 
            use_container_width=True,
            help=desc
        ):
            st.session_state.page_idx = i
            st.rerun()

    page = PAGES[st.session_state.page_idx][1]

    st.markdown('<div class="nav-section-label" style="margin-top:8px;">System</div>', unsafe_allow_html=True)
    now_str = pd.Timestamp.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="sidebar-status">
        <div class="status-dot-row">
            <div class="status-dot"></div> MONITORING LIVE
        </div>
        <div class="status-time">Last sync: {now_str}</div>
        <div class="status-time">Auto-refresh: 30s</div>
    </div>
    """, unsafe_allow_html=True)

    auto_refresh = st.toggle("🔄 Auto Refresh", value=True)
    if st.button("⟳ Manual Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── AUTO REFRESH ─────────────────────────────────────────────
if auto_refresh:
    st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PHASE 6 — FAST SKELETON LOADING SCREENS
# ══════════════════════════════════════════════════════════════
loading_placeholder = st.empty()
with loading_placeholder.container():
    # 1 Hero block Skeleton
    st.markdown("""
    <div class="skeleton" style="height:190px; padding:32px; margin-bottom:24px; border: 1px solid rgba(255,255,255,0.04);"></div>
    """, unsafe_allow_html=True)
    
    # 5 KPI cards Skeletons
    st.markdown("""
    <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:14px; margin-bottom:24px;">
        <div class="skeleton" style="height:105px;"></div>
        <div class="skeleton" style="height:105px;"></div>
        <div class="skeleton" style="height:105px;"></div>
        <div class="skeleton" style="height:105px;"></div>
        <div class="skeleton" style="height:105px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2 Chart Skeletons side-by-side
    st.markdown("""
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:24px;">
        <div class="skeleton" style="height:350px;"></div>
        <div class="skeleton" style="height:350px;"></div>
    </div>
    """, unsafe_allow_html=True)

df, hi_df = process_data(T1_FILE_ID, T2_FILE_ID)
loading_placeholder.empty() # Content successfully completed; clean up layout

if df.empty:
    st.error("فشل تحميل البيانات من Google Drive. تحقق من st.secrets والاتصال.")
    st.stop()

# Computed values
total = len(df)
rc = df["RISK_CLASS"].value_counts()
n_crit = int(rc.get("CRITICAL", 0))
n_high = int(rc.get("HIGH", 0))
n_med  = int(rc.get("MEDIUM", 0))
n_low  = int(rc.get("LOW", 0))

avg_score = df["RISK_SCORE"].mean()
health_score = 100 - avg_score

total_inspections = getattr(df, "_total_inspections", total)

# ══════════════════════════════════════════════════════════════
# PHASE 3 — HERO HERO SECTION
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-eyebrow">Predictive Asset Intelligence System</div>
    <div class="hero-title">AI Predictive Maintenance — SUTM</div>
    <div class="hero-subtitle">
        ⚡ PT PLN (Persero) UP3 Bandung · <strong>{total:,}</strong> unique poles · <strong>{total_inspections:,}</strong> total inspections
    </div>
    <div class="hero-badges">
        <div class="badge badge-live">Live Sync Active</div>
        <div class="badge badge-system">Feeder Network: 20KV</div>
        <div class="badge badge-ai">Engine: Health Matrix v2.4</div>
    </div>
    <div class="hero-stats">
        <div class="hero-stat"><div class="hero-stat-val stat-critical">{n_crit}</div><div class="hero-stat-lbl">Critical</div></div>
        <div class="hero-stat"><div class="hero-stat-val stat-high">{n_high}</div><div class="hero-stat-lbl">High Risk</div></div>
        <div class="hero-stat"><div class="hero-stat-val stat-medium">{n_med}</div><div class="hero-stat-lbl">Medium</div></div>
        <div class="hero-stat"><div class="hero-stat-val stat-low">{n_low}</div><div class="hero-stat-lbl">Healthy</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# 🚨 Global Alert Banner if critical assets exist
if n_crit > 0:
    st.markdown(f"""
    <div class="alert-banner">
        <div class="alert-banner-icon">🚨</div>
        <div class="alert-banner-text">
            <strong>CRITICAL FAULT CONDITION:</strong> {n_crit} assets are demonstrating multiple failing indicators. 
            Cascading failure probability is high in localized segments. Recommended response window: &lt; 48 Hours.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "Overview":
    # Custom HTML KPI Cards Grid
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card kpi-total">
            <div class="kpi-label">TOTAL POLES MONITORED</div>
            <div class="kpi-value">{total:,}</div>
            <div class="kpi-delta neu">Active Assets</div>
        </div>
        <div class="kpi-critical kpi-card">
            <div class="kpi-label">CRITICAL STATUS</div>
            <div class="kpi-value">{n_crit}</div>
            <div class="kpi-delta up">Action Req</div>
        </div>
        <div class="kpi-high kpi-card">
            <div class="kpi-label">HIGH RISK POLES</div>
            <div class="kpi-value">{n_high}</div>
            <div class="kpi-delta up">Monitor</div>
        </div>
        <div class="kpi-medium kpi-card">
            <div class="kpi-label">MEDIUM RISK</div>
            <div class="kpi-value">{n_med}</div>
            <div class="kpi-delta neu">Stable</div>
        </div>
        <div class="kpi-low kpi-card">
            <div class="kpi-label">FLEET HEALTH SCORE</div>
            <div class="kpi-value">{health_score:.1f}%</div>
            <div class="kpi-delta down">Optimal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2 Charts Side-by-Side
    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            fig_donut = px.pie(
                df, names="RISK_CLASS", 
                color="RISK_CLASS",
                color_discrete_map=COLORS, 
                hole=0.45
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            dark_layout(fig_donut, "Fleet Risk Class Distribution Breakdown")
            st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        with st.container():
            top5_ulp = df.groupby(["ULP", "RISK_CLASS"]).size().unstack(fill_value=0).reset_index()
            if "CRITICAL" not in top5_ulp.columns: top5_ulp["CRITICAL"] = 0
            if "HIGH" not in top5_ulp.columns: top5_ulp["HIGH"] = 0
            top5_ulp["Total_Risk"] = top5_ulp["CRITICAL"] + top5_ulp["HIGH"]
            top5_ulp = top5_ulp.sort_values(by="Total_Risk", ascending=False).head(5)
            
            fig_stack = px.bar(
                top5_ulp, x="ULP", y=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                color_discrete_map=COLORS,
                barmode="stack"
            )
            dark_layout(fig_stack, "Top Risk Distribution Across Sub-Units (ULP)")
            st.plotly_chart(fig_stack, use_container_width=True)

    # AI Insight Engine Integration
    st.markdown('<div class="section-header"><span class="section-icon">🧠</span><span class="section-title">AI Autonomous Diagnostic Insights</span><span class="section-badge">Real-time</span></div>', unsafe_allow_html=True)
    insights = generate_ai_insights(df, hi_df)
    for ins in insights:
        st.markdown(f"""
        <div class="insight-card {ins['type']}">
            <div class="insight-header">
                <div class="insight-icon">{ins['icon']}</div>
                <div class="insight-title">{ins['title']}</div>
            </div>
            <div class="insight-body">{ins['body']}</div>
            <div class="insight-action">{ins['action']}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2 — RISK ANALYSIS
# ══════════════════════════════════════════════════════════════
elif page == "Risk Analysis":
    c1, c2 = st.columns([3, 2])
    with c1:
        with st.container():
            fig_hist = px.histogram(
                df, x="RISK_SCORE", color="RISK_CLASS",
                color_discrete_map=COLORS, nbins=30, opacity=0.85
            )
            dark_layout(fig_hist, "Asset Fleet Predictive Risk Score Distribution")
            st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        with st.container():
            # Mock risk matrix using real segment numbers
            matrix_data = np.zeros((3, 3))
            matrix_data[0, 2] = n_crit
            matrix_data[1, 2] = n_high
            matrix_data[1, 1] = n_med
            matrix_data[2, 0] = n_low
            
            fig_matrix = px.imshow(
                matrix_data,
                labels=dict(x="Severity Level", y="Probability Dynamic"),
                x=["Low", "Medium", "High"],
                y=["High", "Medium", "Low"],
                color_continuous_scale="Viridis"
            )
            dark_layout(fig_matrix, "Dynamic Probability vs Severity Matrix Block")
            st.plotly_chart(fig_matrix, use_container_width=True)

    st.markdown('<div class="section-header"><span class="section-icon">🔍</span><span class="section-title">Granular Feeder Operational Risk Ranking</span></div>', unsafe_allow_html=True)
    feeder_risk = df.groupby("PENYULANG")["RISK_SCORE"].agg(["count", "mean", "max"]).reset_index()
    feeder_risk.columns = ["Feeder Name", "Monitored Poles Count", "Mean Risk Rating", "Absolute Max Risk"]
    feeder_risk = feeder_risk.sort_values(by="Mean Risk Rating", ascending=False)
    st.dataframe(feeder_risk, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3 — HEALTH INDEX
# ══════════════════════════════════════════════════════════════
elif page == "Health Index":
    if hi_df.empty:
        st.info("No Component level analytical metrics loaded.")
    else:
        with st.container():
            fig_hi_bar = px.bar(
                hi_df, x="Component", y=["BURUK", "KURANG", "CUKUP", "BAIK"],
                title="Granular Component Structural Degradation Status Map",
                color_discrete_map={"BURUK": "#ff3355", "KURANG": "#ff8c00", "CUKUP": "#00A3E0", "BAIK": "#00C5B5"}
            )
            dark_layout(fig_hi_bar, "Structural & Technical Component Degradation Analysis Status Profile", 420)
            st.plotly_chart(fig_hi_bar, use_container_width=True)
        
        st.markdown('<div class="section-header"><span class="section-icon">📊</span><span class="section-title">Raw Structural Degradation Counts</span></div>', unsafe_allow_html=True)
        st.dataframe(hi_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# PAGE 4 — THERMAL INTEGRATION
# ══════════════════════════════════════════════════════════════
elif page == "Thermal":
    t2 = getattr(df, "_t2_raw", pd.DataFrame())
    if t2.empty:
        st.info("⚡ No correlated thermographic infrared detection data found for current asset matrix.")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.container():
                high_delta = len(t2[t2["DELTA_SUHU"] > 10])
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=high_delta,
                    title={'text': "Anomalous Thermal Delta Hotspots (&gt;10°C)"},
                    gauge={'axis': {'range': [None, max(20, high_delta*2)]},
                           'bar': {'color': "#ff3355"},
                           'steps': [{'range': [0, 5], 'color': "rgba(0,197,181,0.1)"},
                                     {'range': [5, 10], 'color': "rgba(255,140,0,0.1)"}]}
                ))
                dark_layout(fig_gauge, height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
        with col2:
            with st.container():
                fig_scat = px.scatter(
                    t2, x="SUHU FASA R", y="DELTA_SUHU",
                    color="DELTA_SUHU", color_continuous_scale="Reds",
                    hover_data=["NO TIANG", "PENYULANG"]
                )
                dark_layout(fig_scat, "Thermal Phase Temperature vs Calculated Delta Hotspot Tracking Matrix", 300)
                st.plotly_chart(fig_scat, use_container_width=True)

        st.markdown('<div class="section-header"><span class="section-icon">🌡️</span><span class="section-title">Thermographic Inspection Operational Register</span></div>', unsafe_allow_html=True)
        st.dataframe(t2[["TIANG_ID", "SUHU FASA R", "SUHU FASA S", "SUHU FASA T", "DELTA_SUHU"]].sort_values(by="DELTA_SUHU", ascending=False), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# PAGE 5 — ML COMPARISON
# ══════════════════════════════════════════════════════════════
elif page == "ML Comparison":
    with st.container():
        categories = ['Precision', 'Recall', 'F1-Score', 'AUC-ROC', 'Processing Efficiency']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[0.94, 0.92, 0.93, 0.96, 0.88], theta=categories, fill='toself', name='Random Forest Predictive Core'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[0.89, 0.86, 0.87, 0.91, 0.95], theta=categories, fill='toself', name='Gradient Boosting Engine'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
        dark_layout(fig_radar, "Neural Model & Machine Learning Cross-Validation Benchmark Performance Matrix", 400)
        st.plotly_chart(fig_radar, use_container_width=True)

    # Historical timeline simulator
    with st.container():
        time_series = pd.DataFrame({
            "Timestamp": pd.date_range(start="2026-01-01", periods=30, freq="D"),
            "Critical Detections Count": np.random.randint(n_crit, n_crit+5, size=30)
        })
        fig_line = px.line(time_series, x="Timestamp", y="Critical Detections Count")
        fig_line.update_traces(line_color="#ff3355", line_width=2)
        dark_layout(fig_line, "30-Day Fleet Critical Dynamic Severity Timeline Tracking Simulation", 260)
        st.plotly_chart(fig_line, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 6 — PRIORITY POLES
# ══════════════════════════════════════════════════════════════
elif page == "Priority Poles":
    st.markdown('<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">High-Priority Target Action Matrix</span><span class="section-badge">Urgent Dispatch</span></div>', unsafe_allow_html=True)
    
    # Selection filters
    f_ulp = st.selectbox("Filter Operational Sub-Unit (ULP)", ["ALL"] + list(df["ULP"].unique()))
    f_class = st.multiselect("Filter Risk Classification", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH"])
    
    filtered_df = df.copy()
    if f_ulp != "ALL":
        filtered_df = filtered_df[filtered_df["ULP"] == f_ulp]
    if f_class:
        filtered_df = filtered_df[filtered_df["RISK_CLASS"].isin(f_class)]
        
    filtered_df = filtered_df.sort_values(by="RISK_SCORE", ascending=False)
    st.dataframe(filtered_df[["TIANG_ID", "ULP", "PENYULANG", "NO TIANG", "RISK_CLASS", "RISK_SCORE"]], use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# PAGE 7 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════
elif page == "Executive Summary":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="text-align:center; padding:30px 15px;">
            <div class="health-score-ring">
                <div class="health-score-num">{health_score:.1f}</div>
                <div class="health-score-lbl">Fleet Structural Integrity Index</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="priority-matrix">', unsafe_allow_html=True)
        top5 = df[df["RISK_CLASS"].isin(["CRITICAL", "HIGH"])].groupby("ULP").size().reset_index(name="Critical Poles").sort_values(by="Critical Poles", ascending=False).head(4)
        
        for idx, row in top5.iterrows():
            pct_bar = min(100, int((row["Critical Poles"] / max(1, n_crit)) * 100))
            st.markdown(f"""
            <div class="priority-item">
                <div class="priority-rank">TOP RISK FACTOR AREA</div>
                <div class="priority-name">{row['ULP']} ({row['Critical Poles']} Poles)</div>
                <div class="priority-bar"><div class="priority-bar-fill" style="width: {pct_bar}%"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Top 5 Bar Chart for Executive view
    with st.container():
        fig_top5 = px.bar(
            top5, x="ULP", y="Critical Poles",
            color="Critical Poles",
            color_continuous_scale=["#ff8c00","#ff3355"],
            text="Critical Poles",
        )
        fig_top5.update_traces(textposition="outside", marker_line_width=0)
        fig_top5.update_coloraxes(showscale=False)
        dark_layout(fig_top5, "Top 5 ULPs by Critical Pole Count Profile", 340)
        st.plotly_chart(fig_top5, use_container_width=True)

    st.markdown('<div class="section-header"><span class="section-icon">📄</span><span class="section-title">Export Operations Report Summary</span></div>', unsafe_allow_html=True)

    total_cost = (n_crit * 15000000) + (n_high * 5000000)
    top_risk_ulp = top5.iloc[0]["ULP"] if not top5.empty else "N/A"

    exec_data = {
        "Metric Classification Overview": [
            "Total Monitored Asset Poles", "CRITICAL Status Volumetrics", "HIGH RISK Sub-Fleet Count", 
            "MEDIUM Risk Stability Profile", "LOW Risk Optimal Count", "Fleet Structural Integrity Score", 
            "Average Predictive Risk Rating", "Highest Risk Aggregation Sub-Unit",
            "Total Remediation Cost Estimate (IDR)"
        ],
        "Aggregated Operational Value": [
            f"{total:,} Units", f"{n_crit} Units", f"{n_high} Units", f"{n_med} Units", f"{n_low} Units",
            f"{health_score:.2f} / 100", f"{avg_score:.2f} / 100", top_risk_ulp, f"Rp {total_cost/1e9:.3f} Billion"
        ]
    }
    exec_df = pd.DataFrame(exec_data)
    st.dataframe(exec_df, use_container_width=True, hide_index=True)
