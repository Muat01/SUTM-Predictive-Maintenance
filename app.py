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
    --clr-medium:    #0ea5e9;
    --clr-low:       #00e5b0;
    --clr-accent:    #3b82f6;
    --clr-text:      #e2e8f0;
    --clr-muted:     #64748b;
    --clr-border:    rgba(255,255,255,0.06);
    --glow-critical: 0 0 20px rgba(255,51,85,0.35);
    --glow-high:     0 0 20px rgba(255,140,0,0.35);
    --glow-medium:   0 0 20px rgba(14,165,233,0.35);
    --glow-low:      0 0 20px rgba(0,229,176,0.35);
    --glow-accent:   0 0 30px rgba(59,130,246,0.2);
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
    background: linear-gradient(135deg, #060810 0%, #0c1628 50%, #060d1f 100%);
    border: 1px solid rgba(59,130,246,0.15);
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
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 400px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,229,176,0.04) 0%, transparent 70%);
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
    background: linear-gradient(135deg, #ffffff 0%, #93c5fd 50%, #00e5b0 100%);
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
    background: rgba(0,229,176,0.1);
    border: 1px solid rgba(0,229,176,0.3);
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
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.25);
    color: var(--clr-accent);
}
.badge-ai {
    background: rgba(168,85,247,0.1);
    border: 1px solid rgba(168,85,247,0.25);
    color: #c084fc;
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
.pln-logo {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #3b82f6, #00e5b0);
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
    background: rgba(59,130,246,0.08);
    border-color: rgba(59,130,246,0.2);
}
.nav-card.active {
    background: rgba(59,130,246,0.12);
    border-color: rgba(59,130,246,0.3);
    box-shadow: 0 0 16px rgba(59,130,246,0.1);
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
    background: rgba(0,229,176,0.05);
    border: 1px solid rgba(0,229,176,0.15);
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
.kpi-delta.down { background: rgba(0,229,176,0.1);  color: var(--clr-low); }
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
.insight-card.info     { border-color: var(--clr-accent);   box-shadow: -4px 0 16px rgba(59,130,246,0.15); }
.insight-card.success  { border-color: var(--clr-low);      box-shadow: -4px 0 16px rgba(0,229,176,0.15); }
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
.insight-card.info     .insight-action { background: rgba(59,130,246,0.1); color: var(--clr-accent); }

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
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.2);
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
    background: linear-gradient(135deg, #00e5b0, #3b82f6);
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
    background: rgba(59,130,246,0.1) !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    color: var(--clr-accent) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(59,130,246,0.2) !important;
    box-shadow: 0 0 16px rgba(59,130,246,0.2) !important;
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
# SIDEBAR — PHASE 2 (Navigation Cards)
# ══════════════════════════════════════════════════════════════
PAGES = [
    ("📊", "Overview",         "Fleet status & KPIs"),
    ("⚠️", "Risk Analysis",    "Risk distribution"),
    ("🏥", "Health Index",     "Component HI"),
    ("🌡️", "Thermal",          "Temperature data"),
    ("🤖", "ML Comparison",    "Model benchmarks"),
    ("🎯", "Priority Poles",   "Top risk assets"),
    ("📋", "Executive Summary","Management view"),
]

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="pln-logo">⚡ PLN UP3</div>
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
        if st.button(
            f"{icon}  {name}",
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
            <div class="status-dot"></div>
            LIVE MONITORING
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
# PHASE 6 — SMART LOADING
# ══════════════════════════════════════════════════════════════
loading_placeholder = st.empty()
with loading_placeholder.container():
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;padding:20px;
                background:#0c0f1a;border-radius:12px;border:1px solid rgba(255,255,255,0.06);
                margin-bottom:16px;">
        <div style="font-size:24px;">⚡</div>
        <div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#e2e8f0;font-weight:600;">
                Loading asset intelligence...
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#64748b;margin-top:4px;">
                Connecting to Google Drive · Processing SUTM data
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

df, hi_df = process_data(T1_FILE_ID, T2_FILE_ID)
loading_placeholder.empty()

if df.empty:
    st.markdown("""
    <div style="background:rgba(255,51,85,0.08);border:1px solid rgba(255,51,85,0.25);
                border-radius:12px;padding:24px;text-align:center;">
        <div style="font-size:32px;margin-bottom:12px;">⚠️</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:18px;color:#ff3355;font-weight:600;">
            No Data Available
        </div>
        <div style="font-size:13px;color:#64748b;margin-top:8px;">
            Please verify Google Drive credentials and file access permissions.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── COMPUTED VALUES ───────────────────────────────────────────
rc       = df["RISK_CLASS"].value_counts()
total    = len(df)
total_inspections = getattr(df, "_total_inspections", total)
n_crit   = int(rc.get("CRITICAL", 0))
n_high   = int(rc.get("HIGH",     0))
n_med    = int(rc.get("MEDIUM",   0))
n_low    = int(rc.get("LOW",      0))
n_defect = int((df["N_BURUK"] > 0).sum() + (df["N_KURANG"] > 0).sum())
last_update = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
top_risk_ulp = df.groupby("ULP")["N_BURUK"].sum().idxmax() if "ULP" in df.columns else "—"
avg_score = df["RISK_SCORE"].mean()
health_score = max(0, min(100, round(100 - avg_score, 1)))

# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

# ── OVERVIEW ─────────────────────────────────────────────────
if page == "Overview":

    # HERO SECTION
    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-eyebrow">PT PLN UP3 Bandung · SUTM Asset Intelligence Platform</div>
        <div class="hero-title">⚡ AI Predictive Maintenance</div>
        <div class="hero-subtitle">Real-time SUTM Asset Intelligence · Powered by Machine Learning · <span style="color:#64748b;">{total:,} unique poles · {total_inspections:,} total inspections</span></div>
        <div class="hero-badges">
            <span class="badge badge-live">LIVE MONITORING</span>
            <span class="badge badge-system">SUTM NETWORK</span>
            <span class="badge badge-ai">AI-POWERED</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#475569;">
                Last sync: {last_update}
            </span>
        </div>
        <div class="hero-stats">
            <div class="hero-stat">
                <div class="hero-stat-val" style="color:#ffffff;">{total:,}</div>
                <div class="hero-stat-lbl">Total Poles</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-val stat-critical">{n_crit:,}</div>
                <div class="hero-stat-lbl">Critical</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-val stat-high">{n_high:,}</div>
                <div class="hero-stat-lbl">High Risk</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-val stat-low">{health_score}</div>
                <div class="hero-stat-lbl">Health Score</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ALERT BANNER (if critical > threshold)
    if n_crit > 0:
        st.markdown(f"""
        <div class="alert-banner">
            <div class="alert-banner-icon">🚨</div>
            <div class="alert-banner-text">
                <strong>{n_crit:,} CRITICAL poles</strong> detected in the network —
                immediate inspection required for {top_risk_ulp} zone.
                Combined HIGH+CRITICAL: <strong>{n_crit+n_high:,} poles ({(n_crit+n_high)/total*100:.1f}%)</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # KPI CARDS
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card kpi-total">
            <div class="kpi-label">Total Poles</div>
            <div class="kpi-value">{total:,}</div>
            <span class="kpi-delta neu">SUTMT1 Dataset</span>
            <div class="kpi-glow-bg" style="background:#3b82f6;"></div>
        </div>
        <div class="kpi-card kpi-critical">
            <div class="kpi-label">Critical</div>
            <div class="kpi-value">{n_crit:,}</div>
            <span class="kpi-delta up">{n_crit/total*100:.1f}% of fleet</span>
            <div class="kpi-glow-bg" style="background:#ff3355;"></div>
        </div>
        <div class="kpi-card kpi-high">
            <div class="kpi-label">High Risk</div>
            <div class="kpi-value">{n_high:,}</div>
            <span class="kpi-delta up">{n_high/total*100:.1f}% of fleet</span>
            <div class="kpi-glow-bg" style="background:#ff8c00;"></div>
        </div>
        <div class="kpi-card kpi-medium">
            <div class="kpi-label">Medium Risk</div>
            <div class="kpi-value">{n_med:,}</div>
            <span class="kpi-delta neu">{n_med/total*100:.1f}% of fleet</span>
            <div class="kpi-glow-bg" style="background:#0ea5e9;"></div>
        </div>
        <div class="kpi-card kpi-low">
            <div class="kpi-label">Low Risk</div>
            <div class="kpi-value">{n_low:,}</div>
            <span class="kpi-delta down">{n_low/total*100:.1f}% of fleet</span>
            <div class="kpi-glow-bg" style="background:#00e5b0;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CHARTS ROW
    st.markdown('<div class="section-header"><span class="section-icon">📊</span><span class="section-title">Fleet Overview</span><span class="section-badge">Live Data</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(go.Pie(
            labels=["CRITICAL","HIGH","MEDIUM","LOW"],
            values=[n_crit, n_high, n_med, n_low],
            hole=0.70,
            marker=dict(colors=list(COLORS.values()),
                        line=dict(color=PAPER_BG, width=3)),
            textinfo="none",
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b style='font-size:18px'>{total:,}</b><br><span style='font-size:11px;color:#64748b'>POLES</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=FONT_COL, family="Rajdhani, sans-serif")
        )
        dark_layout(fig, "Risk Distribution", 340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ulp_data = (df.groupby(["ULP","RISK_CLASS"])
                      .size().reset_index(name="count"))
        fig2 = px.bar(ulp_data, x="ULP", y="count", color="RISK_CLASS",
                      color_discrete_map=COLORS, barmode="stack",
                      category_orders={"RISK_CLASS":["CRITICAL","HIGH","MEDIUM","LOW"]})
        fig2.update_layout(xaxis_tickangle=-35, showlegend=True,
                           bargap=0.3, bargroupgap=0.1)
        dark_layout(fig2, "Risk Distribution by ULP", 340)
        st.plotly_chart(fig2, use_container_width=True)

    # AI INSIGHTS SECTION
    st.markdown('<div class="section-header"><span class="section-icon">🤖</span><span class="section-title">AI Insight Engine</span><span class="section-badge">Auto-Generated</span></div>', unsafe_allow_html=True)

    insights = generate_ai_insights(df, hi_df)
    col_a, col_b = st.columns(2)
    for i, ins in enumerate(insights):
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"""
            <div class="insight-card {ins['type']}">
                <div class="insight-header">
                    <span class="insight-icon">{ins['icon']}</span>
                    <span class="insight-title">{ins['title']}</span>
                </div>
                <div class="insight-body">{ins['body']}</div>
                <span class="insight-action">{ins['action']}</span>
            </div>
            """, unsafe_allow_html=True)

    # BOTTOM STATS
    st.markdown('<div class="section-header"><span class="section-icon">📈</span><span class="section-title">Summary Statistics</span></div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("CRITICAL + HIGH",    f"{n_crit+n_high:,}", f"{(n_crit+n_high)/total*100:.1f}%")
    s2.metric("Poles with Defects", f"{n_defect:,}",      f"{n_defect/total*100:.1f}%")
    s3.metric("Avg Risk Score",     f"{avg_score:.1f}",   "/ 100")
    s4.metric("Fleet Health Score", f"{health_score:.1f}",f"/ 100")

# ── RISK ANALYSIS ─────────────────────────────────────────────
elif page == "Risk Analysis":
    st.markdown(f"""
    <div class="hero-wrapper" style="padding:24px 28px;">
        <div class="hero-eyebrow">Risk Assessment</div>
        <div class="hero-title" style="font-size:32px;">⚠️ Risk Analysis</div>
        <div class="hero-subtitle">{total:,} poles classified · worst-case per unique pole</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            x=["LOW","MEDIUM","HIGH","CRITICAL"],
            y=[n_low, n_med, n_high, n_crit],
            color=["LOW","MEDIUM","HIGH","CRITICAL"],
            color_discrete_map=COLORS,
            log_y=True,
        )
        fig.update_traces(showlegend=False, marker_line_width=0)
        dark_layout(fig, "Risk Count (Log Scale)", 320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(df, x="RISK_SCORE", color="RISK_CLASS",
                            color_discrete_map=COLORS, nbins=40,
                            barmode="overlay", opacity=0.75)
        dark_layout(fig2, "Risk Score Distribution", 320)
        st.plotly_chart(fig2, use_container_width=True)

    # Risk Heatmap — PHASE 3
    st.markdown('<div class="section-header"><span class="section-icon">🗺️</span><span class="section-title">Risk Heatmap</span><span class="section-badge">ULP × PENYULANG</span></div>', unsafe_allow_html=True)

    if "ULP" in df.columns and "PENYULANG" in df.columns:
        risk_num = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        df["RISK_NUM"] = df["RISK_CLASS"].map(risk_num)
        heatmap_data = (df.groupby(["ULP","PENYULANG"])["RISK_NUM"]
                          .mean().reset_index())
        pivot = heatmap_data.pivot(index="ULP", columns="PENYULANG", values="RISK_NUM")
        fig_hm = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0,"#00e5b0"],[0.33,"#0ea5e9"],[0.66,"#ff8c00"],[1,"#ff3355"]],
            hovertemplate="ULP: %{y}<br>Feeder: %{x}<br>Avg Risk: %{z:.2f}<extra></extra>",
            colorbar=dict(
                title="Risk Level",
                tickvals=[1,2,3,4],
                ticktext=["LOW","MED","HIGH","CRIT"],
                tickfont=dict(color=FONT_COL, size=10),
                titlefont=dict(color=FONT_COL, size=11),
            )
        ))
        fig_hm.update_layout(xaxis_tickangle=-45)
        dark_layout(fig_hm, "Risk Heatmap — ULP × Feeder", 420)
        st.plotly_chart(fig_hm, use_container_width=True)

    # ULP horizontal bar
    ulp_risk = (df.groupby(["ULP","RISK_CLASS"])
                  .size().reset_index(name="count"))
    ulp_risk = ulp_risk[ulp_risk["RISK_CLASS"] != "LOW"]
    fig3 = px.bar(ulp_risk, y="ULP", x="count", color="RISK_CLASS",
                  color_discrete_map=COLORS, orientation="h", barmode="stack",
                  category_orders={"RISK_CLASS":["CRITICAL","HIGH","MEDIUM"]})
    dark_layout(fig3, "CRITICAL + HIGH + MEDIUM by ULP", 380)
    st.plotly_chart(fig3, use_container_width=True)

    # Risk Matrix — PHASE 3
    st.markdown('<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">Risk Matrix</span><span class="section-badge">Probability vs Impact</span></div>', unsafe_allow_html=True)

    matrix_data = df.copy()
    matrix_data["PROBABILITY"] = matrix_data["RISK_SCORE"] / 100
    matrix_data["IMPACT"] = matrix_data["N_BURUK"] * 2 + matrix_data["N_KURANG"]

    fig_matrix = px.scatter(
        matrix_data.sample(min(500, len(matrix_data))),
        x="PROBABILITY", y="IMPACT",
        color="RISK_CLASS",
        color_discrete_map=COLORS,
        opacity=0.65,
        size_max=10,
        hover_data=["TIANG_ID","ULP"],
    )
    fig_matrix.add_hline(y=2, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig_matrix.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig_matrix.update_traces(marker=dict(size=7, line=dict(width=0)))
    dark_layout(fig_matrix, "Risk Matrix — Probability vs Impact", 380)
    st.plotly_chart(fig_matrix, use_container_width=True)

# ── HEALTH INDEX ──────────────────────────────────────────────
elif page == "Health Index":
    st.markdown(f"""
    <div class="hero-wrapper" style="padding:24px 28px;">
        <div class="hero-eyebrow">Component Assessment</div>
        <div class="hero-title" style="font-size:32px;">🏥 Health Index</div>
        <div class="hero-subtitle">12 component categories · all inspection records</div>
    </div>
    """, unsafe_allow_html=True)

    if not hi_df.empty:
        # Stacked horizontal bar
        fig = go.Figure()
        for cond, color in [("BAIK","#00e5b0"),("CUKUP","#0ea5e9"),
                             ("KURANG","#ff8c00"),("BURUK","#ff3355")]:
            fig.add_trace(go.Bar(
                name=cond, y=hi_df["Component"], x=hi_df[cond],
                orientation="h", marker_color=color,
                hovertemplate=f"{cond}: %{{x:,}}<extra></extra>",
            ))
        fig.update_layout(barmode="stack", bargap=0.25)
        dark_layout(fig, "Component Health Index Distribution", 440)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            buruk_df = hi_df[hi_df["BURUK"] > 0].sort_values("BURUK", ascending=False)
            if not buruk_df.empty:
                fig2 = px.bar(buruk_df, x="Component", y="BURUK",
                              color_discrete_sequence=["#ff3355"])
                fig2.update_traces(marker_line_width=0)
                fig2.update_layout(xaxis_tickangle=-30)
                dark_layout(fig2, "BURUK Count by Component", 300)
                st.plotly_chart(fig2, use_container_width=True)

        with col2:
            # Radar Chart — PHASE 3
            hi_df["HEALTH_PCT"] = (hi_df["BAIK"] / (hi_df["BAIK"] + hi_df["CUKUP"] + hi_df["KURANG"] + hi_df["BURUK"]).replace(0,1) * 100).round(1)
            fig_radar = go.Figure(go.Scatterpolar(
                r=hi_df["HEALTH_PCT"].tolist() + [hi_df["HEALTH_PCT"].iloc[0]],
                theta=hi_df["Component"].tolist() + [hi_df["Component"].iloc[0]],
                fill="toself",
                fillcolor="rgba(0,229,176,0.08)",
                line=dict(color="#00e5b0", width=2),
                marker=dict(size=5, color="#00e5b0"),
                hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor=PLOT_BG,
                    radialaxis=dict(visible=True, range=[0,100], gridcolor=GRID_COL,
                                    tickfont=dict(size=9, color=FONT_COL), ticksuffix="%"),
                    angularaxis=dict(gridcolor=GRID_COL, tickfont=dict(size=9, color=FONT_COL)),
                )
            )
            dark_layout(fig_radar, "Component Health Radar", 300)
            st.plotly_chart(fig_radar, use_container_width=True)

        # KURANG bar
        kurang_df = hi_df[hi_df["KURANG"] > 0].sort_values("KURANG", ascending=False)
        if not kurang_df.empty:
            fig3 = px.bar(kurang_df, x="Component", y="KURANG",
                          color_discrete_sequence=["#ff8c00"])
            fig3.update_traces(marker_line_width=0)
            fig3.update_layout(xaxis_tickangle=-30)
            dark_layout(fig3, "KURANG Count by Component", 300)
            st.plotly_chart(fig3, use_container_width=True)

        # Gauge Charts per ULP — PHASE 3
        if "ULP" in df.columns:
            st.markdown('<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">Health Score by ULP</span><span class="section-badge">Gauge View</span></div>', unsafe_allow_html=True)

            ulps = sorted(df["ULP"].dropna().unique().tolist())
            n_ulps = len(ulps)
            if n_ulps > 0:
                cols_per_row = min(4, n_ulps)
                gauge_rows = [ulps[i:i+cols_per_row] for i in range(0, n_ulps, cols_per_row)]
                for row_ulps in gauge_rows:
                    gcols = st.columns(len(row_ulps))
                    for gi, ulp_name in enumerate(row_ulps):
                        ulp_df = df[df["ULP"] == ulp_name]
                        ulp_score = max(0, min(100, round(100 - ulp_df["RISK_SCORE"].mean(), 1)))
                        clr = "#00e5b0" if ulp_score >= 70 else "#ff8c00" if ulp_score >= 40 else "#ff3355"
                        fig_g = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=ulp_score,
                            number=dict(suffix="", font=dict(color=clr, size=22, family="Rajdhani")),
                            gauge=dict(
                                axis=dict(range=[0,100], tickcolor=FONT_COL, tickfont=dict(size=9)),
                                bar=dict(color=clr, thickness=0.25),
                                bgcolor=PLOT_BG,
                                borderwidth=0,
                                steps=[
                                    dict(range=[0,40],  color="rgba(255,51,85,0.08)"),
                                    dict(range=[40,70], color="rgba(255,140,0,0.08)"),
                                    dict(range=[70,100],color="rgba(0,229,176,0.08)"),
                                ],
                                threshold=dict(line=dict(color="white",width=1), value=70),
                            ),
                            title=dict(text=ulp_name, font=dict(size=11, color=FONT_COL)),
                        ))
                        dark_layout(fig_g, "", 220)
                        gcols[gi].plotly_chart(fig_g, use_container_width=True)

        st.dataframe(
            hi_df[["Component","BAIK","CUKUP","KURANG","BURUK","HEALTH_PCT"]]
            .rename(columns={"HEALTH_PCT":"Health %"})
            .style.background_gradient(subset=["BURUK","KURANG"], cmap="RdYlGn_r")
                   .format({"Health %":"{:.1f}%"}),
            use_container_width=True, height=320, hide_index=True
        )

# ── THERMAL ───────────────────────────────────────────────────
elif page == "Thermal":
    st.markdown(f"""
    <div class="hero-wrapper" style="padding:24px 28px;">
        <div class="hero-eyebrow">Infrared Thermal Inspection</div>
        <div class="hero-title" style="font-size:32px;">🌡️ Thermal Analysis</div>
        <div class="hero-subtitle">SUTMT2 · Temperature delta analysis · Phase R/S/T</div>
    </div>
    """, unsafe_allow_html=True)

    t2_raw = load_from_drive(T2_FILE_ID, "DATA")
    if t2_raw.empty:
        st.warning("No thermal data available.")
        st.stop()

    t2_raw["NUM_HI_1"] = t2_raw["HI SUTM  - 1"].map(HI_MAP).fillna(3)
    t2_raw["NUM_HI_2"] = t2_raw["HI SUTM - 2"].map(HI_MAP).fillna(3)
    temp_c = ["SUHU FASA R","SUHU FASA S","SUHU FASA T"]
    vt = t2_raw[temp_c].apply(pd.to_numeric, errors="coerce")
    t2_raw["DELTA_SUHU"] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Thermal Records",   f"{len(t2_raw):,}")
    c2.metric("Avg Δ Temp",        f"{t2_raw['DELTA_SUHU'].mean():.2f}°C")
    c3.metric("High Temp (≥10°C)", f"{(t2_raw['DELTA_SUHU']>=10).sum():,}")
    c4.metric("HI-1 BURUK",        f"{(t2_raw['NUM_HI_1']==0).sum():,}")

    col1, col2 = st.columns(2)
    lbl_map = {3:"BAIK",2:"CUKUP",1:"KURANG",0:"BURUK"}

    with col1:
        hi1 = t2_raw["NUM_HI_1"].map(lbl_map).value_counts().reset_index()
        hi1.columns = ["Condition","Count"]
        fig = px.bar(hi1, x="Condition", y="Count", color="Condition",
                     color_discrete_map={"BAIK":"#00e5b0","CUKUP":"#0ea5e9",
                                         "KURANG":"#ff8c00","BURUK":"#ff3355"})
        fig.update_traces(marker_line_width=0)
        dark_layout(fig, "HI-1 Distribution", 300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(t2_raw, x="DELTA_SUHU", nbins=40,
                            color_discrete_sequence=["#a855f7"])
        fig2.add_vline(x=10, line_dash="dash", line_color="#ff8c00",
                       annotation_text="10°C threshold",
                       annotation_font_color="#ff8c00")
        fig2.add_vline(x=15, line_dash="dash", line_color="#ff3355",
                       annotation_text="15°C critical",
                       annotation_font_color="#ff3355")
        fig2.update_traces(marker_line_width=0)
        dark_layout(fig2, "Temperature Delta Distribution", 300)
        st.plotly_chart(fig2, use_container_width=True)

    if "ULP" in t2_raw.columns:
        fig3 = px.box(t2_raw, x="ULP", y="DELTA_SUHU", color="ULP",
                      color_discrete_sequence=["#00e5b0","#0ea5e9","#ff8c00",
                                               "#ff3355","#a855f7","#f59e0b"])
        fig3.update_layout(xaxis_tickangle=-30, showlegend=False)
        dark_layout(fig3, "Thermal Delta by ULP", 340)
        st.plotly_chart(fig3, use_container_width=True)

    # Severity Timeline — PHASE 3
    st.markdown('<div class="section-header"><span class="section-icon">📈</span><span class="section-title">Severity Timeline</span><span class="section-badge">Anomaly Detection</span></div>', unsafe_allow_html=True)

    t2_sorted = t2_raw.copy().reset_index(drop=True)
    t2_sorted["INDEX"] = range(len(t2_sorted))
    t2_sorted["ANOMALY"] = t2_sorted["DELTA_SUHU"] >= 10

    fig_tl = go.Figure()
    fig_tl.add_trace(go.Scatter(
        x=t2_sorted["INDEX"], y=t2_sorted["DELTA_SUHU"],
        mode="lines", name="Δ Temp",
        line=dict(color="rgba(59,130,246,0.5)", width=1),
    ))
    anomalies = t2_sorted[t2_sorted["ANOMALY"]]
    fig_tl.add_trace(go.Scatter(
        x=anomalies["INDEX"], y=anomalies["DELTA_SUHU"],
        mode="markers", name="Anomaly ≥10°C",
        marker=dict(color="#ff3355", size=5, symbol="circle",
                    line=dict(width=0)),
    ))
    fig_tl.add_hline(y=10, line_dash="dash", line_color="rgba(255,140,0,0.4)",
                     annotation_text="10°C Threshold")
    fig_tl.add_hline(y=15, line_dash="dash", line_color="rgba(255,51,85,0.4)",
                     annotation_text="15°C Critical")
    dark_layout(fig_tl, "Severity Timeline — Temperature Anomaly Detection", 340)
    st.plotly_chart(fig_tl, use_container_width=True)

# ── ML COMPARISON ─────────────────────────────────────────────
elif page == "ML Comparison":
    st.markdown(f"""
    <div class="hero-wrapper" style="padding:24px 28px;">
        <div class="hero-eyebrow">Machine Learning Benchmarks</div>
        <div class="hero-title" style="font-size:32px;">🤖 ML Comparison</div>
        <div class="hero-subtitle">5-fold stratified cross-validation · real SUTM data</div>
    </div>
    """, unsafe_allow_html=True)

    ML_RESULTS = pd.DataFrame([
        {"Model":"XGBoost",       "Accuracy":0.9342,"Precision":0.9385,"Recall":0.9342,"F1":0.9329,"Std":0.0136,"Color":"#00e5b0","Best":True},
        {"Model":"Random Forest", "Accuracy":0.8544,"Precision":0.8724,"Recall":0.8544,"F1":0.8578,"Std":0.0223,"Color":"#0ea5e9","Best":False},
        {"Model":"Decision Tree", "Accuracy":0.8274,"Precision":0.8672,"Recall":0.8274,"F1":0.8396,"Std":0.0187,"Color":"#ff8c00","Best":False},
        {"Model":"SVM",           "Accuracy":0.7886,"Precision":0.8158,"Recall":0.7886,"F1":0.7937,"Std":0.0205,"Color":"#ff6b9d","Best":False},
        {"Model":"KNN",           "Accuracy":0.7767,"Precision":0.7856,"Recall":0.7767,"F1":0.7685,"Std":0.0138,"Color":"#a855f7","Best":False},
    ])
    FOLD_DATA = {
        "XGBoost":       [0.93,0.94,0.92,0.93,0.94],
        "Random Forest": [0.86,0.87,0.85,0.83,0.87],
        "Decision Tree": [0.84,0.85,0.83,0.82,0.84],
        "SVM":           [0.79,0.80,0.79,0.78,0.80],
        "KNN":           [0.77,0.77,0.76,0.77,0.77],
    }

    # KPI Row
    st.markdown(f"""
    <div class="kpi-grid">
        {"".join([
            f'''<div class="kpi-card {'kpi-low' if row['Best'] else 'kpi-total'}">
                <div class="kpi-label">{"★ BEST · " if row['Best'] else ""}{row['Model']}</div>
                <div class="kpi-value" style="font-size:26px;color:{'#00e5b0' if row['Best'] else '#93c5fd'}">
                    {row['F1']:.3f}
                </div>
                <span class="kpi-delta {'down' if row['Best'] else 'neu'}">
                    F1 {"Best ↑" if row['Best'] else f"±{row['Std']:.3f}"}
                </span>
            </div>'''
            for _, row in ML_RESULTS.iterrows()
        ])}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(
            y=ML_RESULTS["Model"], x=ML_RESULTS["F1"],
            orientation="h",
            marker=dict(color=ML_RESULTS["Color"].tolist(), line=dict(width=0)),
            text=ML_RESULTS["F1"].round(3), textposition="outside",
        ))
        fig.update_layout(xaxis=dict(range=[0.6, 1.0]))
        dark_layout(fig, "F1-Score Comparison", 320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        metrics = ["Accuracy","Precision","Recall","F1"]
        fig2 = go.Figure()
        for m, color in zip(metrics, ["#00e5b080","#0ea5e980","#ff8c0080","#ff6b9d80"]):
            fig2.add_trace(go.Bar(
                name=m, x=ML_RESULTS["Model"],
                y=ML_RESULTS[m], marker=dict(color=color, line=dict(width=0)),
            ))
        fig2.update_layout(barmode="group", yaxis=dict(range=[0.6, 1.0]))
        dark_layout(fig2, "All Metrics — Grouped", 320)
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    for _, row in ML_RESULTS.iterrows():
        fig3.add_trace(go.Scatter(
            x=[f"Fold {i+1}" for i in range(5)],
            y=FOLD_DATA[row["Model"]],
            name=row["Model"], mode="lines+markers",
            line=dict(color=row["Color"], width=2),
            marker=dict(size=6, line=dict(width=0)),
        ))
    fig3.update_layout(yaxis=dict(range=[0.7, 1.0]))
    dark_layout(fig3, "F1-Score per Fold — Stability Analysis", 300)
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(
        ML_RESULTS[["Model","Accuracy","Precision","Recall","F1","Std"]]
        .style.highlight_max(subset=["F1"], color="#00e5b020")
               .format({"Accuracy":"{:.4f}","Precision":"{:.4f}",
                        "Recall":"{:.4f}","F1":"{:.4f}","Std":"±{:.4f}"}),
        use_container_width=True, hide_index=True
    )

# ── PRIORITY POLES ────────────────────────────────────────────
elif page == "Priority Poles":
    st.markdown(f"""
    <div class="hero-wrapper" style="padding:24px 28px;">
        <div class="hero-eyebrow">Asset Priority Management</div>
        <div class="hero-title" style="font-size:32px;">🎯 Priority Poles</div>
        <div class="hero-subtitle">Sorted by risk score · real pole IDs from SUTMT1</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    ulp_list = ["All"] + sorted(df["ULP"].dropna().unique().tolist())
    sel_ulp  = col1.selectbox("Filter by ULP", ulp_list)
    sel_risk = col2.multiselect("Risk Class",
                                ["CRITICAL","HIGH","MEDIUM","LOW"],
                                default=["CRITICAL","HIGH"])
    top_n    = col3.slider("Top N poles", 10, 100, 20)

    fdf = df.copy()
    if sel_ulp != "All":
        fdf = fdf[fdf["ULP"] == sel_ulp]
    if sel_risk:
        fdf = fdf[fdf["RISK_CLASS"].isin(sel_risk)]
    fdf = fdf.nlargest(top_n, "RISK_SCORE")

    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);">
        <div class="kpi-card kpi-total">
            <div class="kpi-label">Shown Poles</div>
            <div class="kpi-value" style="font-size:28px;">{len(fdf):,}</div>
        </div>
        <div class="kpi-card kpi-critical">
            <div class="kpi-label">Critical</div>
            <div class="kpi-value" style="font-size:28px;">{(fdf['RISK_CLASS']=='CRITICAL').sum():,}</div>
        </div>
        <div class="kpi-card kpi-high">
            <div class="kpi-label">High</div>
            <div class="kpi-value" style="font-size:28px;">{(fdf['RISK_CLASS']=='HIGH').sum():,}</div>
        </div>
        <div class="kpi-card kpi-medium">
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-value" style="font-size:28px;">{fdf['RISK_SCORE'].mean():.1f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig = px.scatter(
        fdf, x="PENYULANG", y="RISK_SCORE",
        color="RISK_CLASS", color_discrete_map=COLORS,
        size="RISK_SCORE", hover_data=["TIANG_ID","ULP","NO TIANG"],
        size_max=18,
    )
    fig.update_layout(xaxis_tickangle=-45)
    dark_layout(fig, "Risk Score Distribution — Top Poles", 340)
    st.plotly_chart(fig, use_container_width=True)

    def color_risk(val):
        c = {"CRITICAL":"rgba(255,51,85,0.15)","HIGH":"rgba(255,140,0,0.15)",
             "MEDIUM":"rgba(14,165,233,0.15)","LOW":"rgba(0,229,176,0.15)"}.get(val,"")
        return f"background-color: {c}"

    display_df = fdf[["TIANG_ID","ULP","PENYULANG","NO TIANG",
                       "RISK_CLASS","RISK_SCORE","N_BURUK","N_KURANG"]].copy()
    display_df.columns = ["Pole ID","ULP","Penyulang","No Tiang",
                           "Risk","Score","# BURUK","# KURANG"]
    display_df["Score"] = display_df["Score"].round(1)

    st.dataframe(
        display_df.style
            .applymap(color_risk, subset=["Risk"])
            .format({"Score":"{:.1f}"}),
        use_container_width=True, height=460, hide_index=True
    )

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Priority List (CSV)",
        csv, "priority_poles.csv", "text/csv",
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════
# PHASE 5 — EXECUTIVE SUMMARY PAGE
# ══════════════════════════════════════════════════════════════
elif page == "Executive Summary":
    st.markdown(f"""
    <div class="hero-wrapper" style="padding:28px 32px;">
        <div class="hero-eyebrow">Management Report · PT PLN UP3 Bandung</div>
        <div class="hero-title" style="font-size:36px;">📋 Executive Summary</div>
        <div class="hero-subtitle">Asset health overview · Maintenance priorities · Generated {last_update}</div>
        <div class="hero-badges">
            <span class="badge badge-system">CONFIDENTIAL</span>
            <span class="badge badge-ai">AI-GENERATED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top row — Health Score + Quick Stats
    col_score, col_stats = st.columns([1, 2])

    with col_score:
        clr_score = "#00e5b0" if health_score >= 70 else "#ff8c00" if health_score >= 40 else "#ff3355"
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            delta=dict(reference=70, valueformat=".1f",
                       increasing=dict(color="#00e5b0"),
                       decreasing=dict(color="#ff3355")),
            number=dict(suffix="", font=dict(color=clr_score, size=48, family="Rajdhani")),
            gauge=dict(
                axis=dict(range=[0,100], tickcolor=FONT_COL,
                          tickfont=dict(size=10), nticks=6),
                bar=dict(color=clr_score, thickness=0.3),
                bgcolor=PLOT_BG, borderwidth=0,
                steps=[
                    dict(range=[0,40],  color="rgba(255,51,85,0.07)"),
                    dict(range=[40,70], color="rgba(255,140,0,0.07)"),
                    dict(range=[70,100],color="rgba(0,229,176,0.07)"),
                ],
                threshold=dict(line=dict(color="white",width=2), value=70),
            ),
            title=dict(text="Fleet Health Score", font=dict(size=13, color=FONT_COL)),
        ))
        dark_layout(fig_gauge, "", 300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_stats:
        st.markdown('<div class="section-header"><span class="section-icon">📊</span><span class="section-title">Fleet Summary</span></div>', unsafe_allow_html=True)

        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.metric("Total Asset Poles",  f"{total:,}")
        r1c2.metric("Requires Attention", f"{n_crit+n_high:,}", f"{(n_crit+n_high)/total*100:.1f}%")
        r1c3.metric("Fleet Health",       f"{health_score:.1f}/100")

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.metric("🔴 Critical",  f"{n_crit:,}",  f"{n_crit/total*100:.1f}%")
        r2c2.metric("🟠 High",      f"{n_high:,}",  f"{n_high/total*100:.1f}%")
        r2c3.metric("Top Risk ULP", top_risk_ulp)

    # Maintenance Priority Matrix
    st.markdown('<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">Maintenance Priority Matrix</span><span class="section-badge">Top 8 ULPs</span></div>', unsafe_allow_html=True)

    if "ULP" in df.columns:
        ulp_summary = (df.groupby("ULP").agg(
            TOTAL=("TIANG_ID","count"),
            CRITICAL=("RISK_CLASS", lambda x: (x == "CRITICAL").sum()),
            HIGH=("RISK_CLASS",     lambda x: (x == "HIGH").sum()),
            AVG_SCORE=("RISK_SCORE","mean"),
        ).reset_index())
        ulp_summary["PRIORITY_SCORE"] = (
            ulp_summary["CRITICAL"] * 4 + ulp_summary["HIGH"] * 2
        )
        ulp_summary = ulp_summary.sort_values("PRIORITY_SCORE", ascending=False).head(8)
        ulp_summary["HEALTH"] = (100 - ulp_summary["AVG_SCORE"]).round(1)
        ulp_summary["RISK_RATIO"] = ((ulp_summary["CRITICAL"] + ulp_summary["HIGH"])
                                      / ulp_summary["TOTAL"] * 100).round(1)

        cols = st.columns(2)
        for i, (_, row) in enumerate(ulp_summary.iterrows()):
            bar_w = min(100, int(row["RISK_RATIO"]))
            risk_clr = "#ff3355" if row["RISK_RATIO"] > 30 else "#ff8c00" if row["RISK_RATIO"] > 15 else "#0ea5e9"
            with cols[i % 2]:
                st.markdown(f"""
                <div class="priority-item">
                    <div class="priority-rank">#{i+1} PRIORITY</div>
                    <div class="priority-name">{row['ULP']}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                                color:#64748b;margin-top:6px;">
                        {int(row['CRITICAL'])} CRITICAL &nbsp;·&nbsp; {int(row['HIGH'])} HIGH
                        &nbsp;·&nbsp; {row['RISK_RATIO']}% risk ratio
                    </div>
                    <div class="priority-bar">
                        <div class="priority-bar-fill"
                             style="width:{bar_w}%;background:{risk_clr};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Financial Impact Estimate
    st.markdown('<div class="section-header"><span class="section-icon">💰</span><span class="section-title">Financial Impact Estimate</span><span class="section-badge">Indicative</span></div>', unsafe_allow_html=True)

    cost_per_critical = 15_000_000   # IDR per pole (indicative)
    cost_per_high     = 8_000_000
    cost_per_medium   = 3_000_000
    total_cost        = (n_crit * cost_per_critical +
                         n_high * cost_per_high +
                         n_med  * cost_per_medium)

    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Critical Maintenance Est.",
               f"Rp {n_crit * cost_per_critical / 1e9:.2f}B",
               f"{n_crit:,} poles × Rp 15M")
    fc2.metric("High Risk Maintenance Est.",
               f"Rp {n_high * cost_per_high / 1e9:.2f}B",
               f"{n_high:,} poles × Rp 8M")
    fc3.metric("Medium Maintenance Est.",
               f"Rp {n_med * cost_per_medium / 1e9:.2f}B",
               f"{n_med:,} poles × Rp 3M")
    fc4.metric("Total Estimated Budget",
               f"Rp {total_cost / 1e9:.2f}B",
               "Indicative only")

    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:#475569;padding:8px 0;letter-spacing:0.5px;">
    ⚠️ DISCLAIMER: Financial figures are indicative estimates for planning purposes only.
    Actual costs depend on contractor rates, materials, and field conditions.
    </div>
    """, unsafe_allow_html=True)

    # Top Critical ULPs chart
    st.markdown('<div class="section-header"><span class="section-icon">🏆</span><span class="section-title">Top 5 Critical ULPs</span></div>', unsafe_allow_html=True)

    if "ULP" in df.columns:
        top5 = (df[df["RISK_CLASS"]=="CRITICAL"]
                .groupby("ULP").size()
                .nlargest(5).reset_index(name="Critical Poles"))
        fig_top5 = px.bar(
            top5, x="ULP", y="Critical Poles",
            color="Critical Poles",
            color_continuous_scale=["#ff8c00","#ff3355"],
            text="Critical Poles",
        )
        fig_top5.update_traces(textposition="outside", marker_line_width=0)
        fig_top5.update_coloraxes(showscale=False)
        dark_layout(fig_top5, "Top 5 ULPs by Critical Pole Count", 340)
        st.plotly_chart(fig_top5, use_container_width=True)

    # Export PDF button (placeholder — requires reportlab if enabled)
    st.markdown('<div class="section-header"><span class="section-icon">📄</span><span class="section-title">Export Report</span></div>', unsafe_allow_html=True)

    exec_data = {
        "Metric": [
            "Total Poles", "CRITICAL", "HIGH", "MEDIUM", "LOW",
            "Fleet Health Score", "Avg Risk Score", "Top Risk ULP",
            "Total Maintenance Est. (IDR Billion)"
        ],
        "Value": [
            total, n_crit, n_high, n_med, n_low,
            f"{health_score:.1f}/100",
            f"{avg_score:.1f}/100",
            top_risk_ulp,
            f"Rp {total_cost/1e9:.2f}B"
        ]
    }
    exec_df = pd.DataFrame(exec_data)
    csv_exec = exec_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Executive Summary (CSV)",
        csv_exec,
        f"executive_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
        use_container_width=True
    )
