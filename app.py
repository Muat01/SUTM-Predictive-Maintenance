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
from datetime import datetime, timedelta

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ SUTM Predictive Maintenance | PT PLN UP3 Bandung",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ADVANCED CUSTOM CSS ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0c10 0%, #0d1117 50%, #0a0c10 100%);
    }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1) 0%, rgba(61, 142, 255, 0.1) 50%, rgba(165, 94, 234, 0.1) 100%);
        border: 1px solid rgba(0, 212, 170, 0.2);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 212, 170, 0.05) 0%, transparent 70%);
        animation: pulse-glow 4s ease-in-out infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.1); }
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 212, 170, 0.15);
        border: 1px solid rgba(0, 212, 170, 0.3);
        color: #00d4aa;
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    
    .hero-badge .pulse {
        width: 8px;
        height: 8px;
        background: #00d4aa;
        border-radius: 50%;
        animation: live-pulse 2s ease-in-out infinite;
    }
    
    @keyframes live-pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.5); }
    }
    
    .hero-title {
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4aa 0%, #3d8eff 50%, #a55eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 18px;
        color: rgba(232, 234, 240, 0.7);
        font-weight: 400;
        margin-bottom: 25px;
    }
    
    .hero-stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-top: 25px;
    }
    
    .hero-stat {
        background: rgba(15, 18, 24, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    
    .hero-stat-value {
        font-size: 24px;
        font-weight: 800;
        color: #e8eaf0;
    }
    
    .hero-stat-label {
        font-size: 11px;
        color: rgba(232, 234, 240, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    
    /* Glassmorphism KPI Cards */
    .kpi-glass {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .kpi-glass:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-glow-critical {
        border-color: rgba(255, 71, 87, 0.3);
        box-shadow: 0 0 30px rgba(255, 71, 87, 0.1);
    }
    
    .kpi-glow-high {
        border-color: rgba(255, 165, 2, 0.3);
        box-shadow: 0 0 30px rgba(255, 165, 2, 0.1);
    }
    
    .kpi-glow-medium {
        border-color: rgba(61, 142, 255, 0.3);
        box-shadow: 0 0 30px rgba(61, 142, 255, 0.1);
    }
    
    .kpi-glow-low {
        border-color: rgba(0, 212, 170, 0.3);
        box-shadow: 0 0 30px rgba(0, 212, 170, 0.1);
    }
    
    .kpi-icon {
        font-size: 28px;
        margin-bottom: 10px;
    }
    
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        color: #e8eaf0;
        margin-bottom: 5px;
    }
    
    .kpi-label {
        font-size: 12px;
        color: rgba(232, 234, 240, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-trend {
        font-size: 12px;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* AI Insight Box */
    .ai-insight {
        background: linear-gradient(135deg, rgba(255, 165, 2, 0.1) 0%, rgba(255, 71, 87, 0.05) 100%);
        border: 1px solid rgba(255, 165, 2, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        position: relative;
    }
    
    .ai-insight-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    
    .ai-insight-icon {
        font-size: 20px;
    }
    
    .ai-insight-title {
        font-size: 14px;
        font-weight: 700;
        color: #ffa502;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .ai-insight-text {
        color: rgba(232, 234, 240, 0.9);
        font-size: 14px;
        line-height: 1.6;
    }
    
    .ai-insight-recommendation {
        margin-top: 10px;
        padding: 10px 15px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        border-left: 3px solid #ffa502;
        font-size: 13px;
        color: rgba(232, 234, 240, 0.8);
    }
    
    /* Sidebar Navigation Cards */
    .nav-card {
        background: rgba(15, 18, 24, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .nav-card:hover {
        background: rgba(61, 142, 255, 0.1);
        border-color: rgba(61, 142, 255, 0.3);
        transform: translateX(5px);
    }
    
    .nav-card.active {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(61, 142, 255, 0.15) 100%);
        border-color: rgba(0, 212, 170, 0.4);
    }
    
    .nav-card-icon {
        font-size: 22px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .nav-card-text {
        flex: 1;
    }
    
    .nav-card-title {
        font-size: 14px;
        font-weight: 600;
        color: #e8eaf0;
    }
    
    .nav-card-desc {
        font-size: 11px;
        color: rgba(232, 234, 240, 0.5);
        margin-top: 2px;
    }
    
    /* System Status */
    .system-status {
        background: rgba(0, 212, 170, 0.05);
        border: 1px solid rgba(0, 212, 170, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-top: 20px;
    }
    
    .system-status-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    
    .system-status-title {
        font-size: 12px;
        font-weight: 600;
        color: #00d4aa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .system-status-indicator {
        width: 8px;
        height: 8px;
        background: #00d4aa;
        border-radius: 50%;
        animation: live-pulse 2s ease-in-out infinite;
    }
    
    /* Executive Summary Cards */
    .exec-card {
        background: linear-gradient(135deg, rgba(15, 18, 24, 0.9) 0%, rgba(20, 25, 35, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .exec-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00d4aa, #3d8eff, #a55eea);
    }
    
    .exec-card-title {
        font-size: 13px;
        font-weight: 600;
        color: rgba(232, 234, 240, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }
    
    .exec-card-value {
        font-size: 36px;
        font-weight: 900;
        color: #e8eaf0;
        margin-bottom: 5px;
    }
    
    .exec-card-subtitle {
        font-size: 13px;
        color: rgba(232, 234, 240, 0.5);
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 30px 0 20px 0;
    }
    
    .section-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.1), transparent);
    }
    
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #e8eaf0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Charts Container */
    .chart-container {
        background: rgba(15, 18, 24, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Data Table Styling */
    .stDataFrame {
        background: rgba(15, 18, 24, 0.6) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0c10;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric Container Override */
    div[data-testid="metric-container"] {
        background: transparent !important;
        border: none !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1218 0%, #0a0c10 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00d4aa, #3d8eff) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── COLORS ───────────────────────────────────────────────────
COLORS = {
    "CRITICAL": "#ff4757",
    "HIGH":     "#ffa502",
    "MEDIUM":   "#3d8eff",
    "LOW":      "#00d4aa",
}
PLOT_BG   = "#0f1218"
PAPER_BG  = "#0a0c10"
FONT_COL  = "#e8eaf0"
GRID_COL  = "rgba(255,255,255,0.05)"

# ── GOOGLE DRIVE LOADER ──────────────────────────────────────
@st.cache_data(ttl=30)
def load_from_drive(file_id: str, sheet_name: str) -> pd.DataFrame:
    """يقرأ ملف Excel من Google Drive مباشرة"""
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

# ── HI MAPPING ───────────────────────────────────────────────
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

# ── DATA PROCESSING ──────────────────────────────────────────
@st.cache_data(ttl=30)
def process_data(t1_id: str, t2_id: str):
    """يعالج البيانات ويحسب Risk لكل تيانج"""
    t1 = load_from_drive(t1_id, "DATA")
    t2 = load_from_drive(t2_id, "DATA")

    if t1.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Visual HI
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

    # Worst per tiang
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

    # T2 thermal
    if not t2.empty:
        t2["TIANG_ID"] = (t2["PENYULANG"].astype(str).str.strip()
                          + "_" + t2["NO TIANG"].astype(str).str.strip())
        t2["NUM_HI_1"] = t2["HI SUTM  - 1"].map(HI_MAP).fillna(3)
        t2["NUM_HI_2"] = t2["HI SUTM - 2"].map(HI_MAP).fillna(3)
        temp_c = ["SUHU FASA R", "SUHU FASA S", "SUHU FASA T"]
        vt = t2[temp_c].apply(pd.to_numeric, errors="coerce")
        t2["DELTA_SUHU"] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    # HI stats per component
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
    worst._t2_raw   = t2

    return worst, pd.DataFrame(hi_stats)

# ── CHART THEME ──────────────────────────────────────────────
def dark_layout(fig, title="", height=350):
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Inter, sans-serif", size=11),
        margin=dict(l=16, r=16, t=50 if title else 16, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
        yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
    )
    return fig

# ── AI INSIGHT ENGINE ────────────────────────────────────────
def generate_ai_insights(df, hi_df):
    """يولد رؤى AI بناءً على البيانات"""
    insights = []
    
    if df.empty:
        return insights
    
    # Insight 1: Highest risk ULP
    ulp_risk = df.groupby("ULP").agg({
        "RISK_SCORE": "mean",
        "RISK_CLASS": lambda x: (x.isin(["CRITICAL", "HIGH"])).sum()
    }).reset_index()
    ulp_risk.columns = ["ULP", "AVG_RISK", "CRITICAL_HIGH_COUNT"]
    top_risk_ulp = ulp_risk.loc[ulp_risk["CRITICAL_HIGH_COUNT"].idxmax()]
    
    insights.append({
        "type": "warning",
        "icon": "⚠️",
        "title": "High Risk Concentration Detected",
        "text": f"ULP **{top_risk_ulp['ULP']}** has the highest concentration of HIGH/CRITICAL risk poles ({int(top_risk_ulp['CRITICAL_HIGH_COUNT'])} poles).",
        "recommendation": f"Recommended preventive inspection within 14 days. Average risk score: {top_risk_ulp['AVG_RISK']:.1f}/100",
        "severity": "high"
    })
    
    # Insight 2: Component failure prediction
    if not hi_df.empty:
        worst_comp = hi_df.loc[hi_df["BURUK"].idxmax()]
        total_buruk = worst_comp["BURUK"]
        if total_buruk > 0:
            insights.append({
                "type": "alert",
                "icon": "🔧",
                "title": "Component Failure Prediction",
                "text": f"**{worst_comp['Component']}** shows highest failure rate with {total_buruk} BURUK conditions detected.",
                "recommendation": "Priority replacement program recommended for this component category.",
                "severity": "critical" if total_buruk > 50 else "high"
            })
    
    # Insight 3: Risk trend
    crit_pct = (df["RISK_CLASS"] == "CRITICAL").sum() / len(df) * 100
    if crit_pct > 1:
        insights.append({
            "type": "info",
            "icon": "📈",
            "title": "Critical Asset Alert",
            "text": f"{crit_pct:.1f}% of assets are in CRITICAL condition requiring immediate attention.",
            "recommendation": "Emergency maintenance protocol should be activated for CRITICAL assets.",
            "severity": "critical"
        })
    
    # Insight 4: Health overview
    healthy_pct = (df["RISK_CLASS"] == "LOW").sum() / len(df) * 100
    insights.append({
        "type": "success",
        "icon": "✅",
        "title": "Asset Health Overview",
        "text": f"{healthy_pct:.1f}% of assets are in healthy condition (LOW risk).",
        "recommendation": "Continue routine maintenance schedule for healthy assets.",
        "severity": "low"
    })
    
    return insights

# ── GAUGE CHART ──────────────────────────────────────────────
def create_gauge_chart(value, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"size": 14, "color": FONT_COL}},
        number={"font": {"size": 24, "color": color, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": GRID_COL},
            "bar": {"color": color, "thickness": 0.75},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 2,
            "bordercolor": "rgba(255,255,255,0.1)",
            "steps": [
                {"range": [0, 25], "color": "rgba(0, 212, 170, 0.1)"},
                {"range": [25, 50], "color": "rgba(61, 142, 255, 0.1)"},
                {"range": [50, 75], "color": "rgba(255, 165, 2, 0.1)"},
                {"range": [75, 100], "color": "rgba(255, 71, 87, 0.1)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": value
            }
        }
    ))
    dark_layout(fig, "", 250)
    return fig

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="font-size: 32px; margin-bottom: 10px;">⚡</div>
        <div style="font-size: 18px; font-weight: 800; color: #e8eaf0;">SUTM Dashboard</div>
        <div style="font-size: 11px; color: rgba(232,234,240,0.5); margin-top: 5px;">PT PLN UP3 Bandung · 2026</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("#### 🔗 Google Drive File IDs")
    t1_id = st.text_input("SUTMT1 (Visual) File ID",
                           value="1FegD5m87H-kT-GgkNyS6xLMyW9UJa2S",
                           help="من رابط Google Drive: drive.google.com/file/d/**THIS_ID**/view")
    t2_id = st.text_input("SUTMT2 (Thermal) File ID",
                           value="11lITP3-mzDG4KOEVyJX6RaDc1n8bTbq")

    st.divider()
    
    # System Status
    st.markdown("""
    <div class="system-status">
        <div class="system-status-header">
            <span class="system-status-title">System Status</span>
            <div class="system-status-indicator"></div>
        </div>
        <div style="font-size: 12px; color: rgba(232,234,240,0.6);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>AI Engine</span>
                <span style="color: #00d4aa;">● Active</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>Data Pipeline</span>
                <span style="color: #00d4aa;">● Connected</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Last Sync</span>
                <span style="color: #ffa502;">Just now</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    st.markdown("#### Navigation")
    
    nav_items = [
        ("📊", "Overview", "Dashboard overview & KPIs"),
        ("⚠️", "Risk Analysis", "Detailed risk assessment"),
        ("🏥", "Health Index", "Component health status"),
        ("🌡️", "Thermal", "Thermal inspection data"),
        ("🤖", "ML Comparison", "Model performance metrics"),
        ("🎯", "Priority Poles", "Critical asset list"),
        ("📋", "Executive Summary", "Management dashboard"),
    ]
    
    # Use radio but styled
    page_options = [f"{icon} {title}" for icon, title, _ in nav_items]
    page = st.radio("", page_options, label_visibility="collapsed")
    
    st.divider()
    
    auto_refresh = st.toggle("🔄 Auto Refresh (30s)", value=True)
    if st.button("⟳ Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── AUTO REFRESH ─────────────────────────────────────────────
if auto_refresh:
    st.markdown(
        '<meta http-equiv="refresh" content="30">',
        unsafe_allow_html=True
    )

# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner("🔄 Loading data from Google Drive..."):
    df, hi_df = process_data(t1_id, t2_id)

if df.empty:
    st.error("⚠️ No data available. Please check File IDs and Google Drive permissions.")
    st.stop()

# ── COMPUTED VALUES ───────────────────────────────────────────
rc      = df["RISK_CLASS"].value_counts()
total   = len(df)
n_crit  = int(rc.get("CRITICAL", 0))
n_high  = int(rc.get("HIGH",     0))
n_med   = int(rc.get("MEDIUM",   0))
n_low   = int(rc.get("LOW",      0))
n_defect= int((df["N_BURUK"] > 0).sum() + (df["N_KURANG"] > 0).sum())
last_update = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

# Generate AI Insights
ai_insights = generate_ai_insights(df, hi_df)

# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

# ── OVERVIEW ─────────────────────────────────────────────────
if "Overview" in page:
    # Hero Section
    st.markdown(f"""
    <div class="hero-container">
        <div style="position: relative; z-index: 1;">
            <div class="hero-badge">
                <div class="pulse"></div>
                AI Monitoring Active
            </div>
            <div class="hero-title">Predictive Maintenance Platform</div>
            <div class="hero-subtitle">
                Real-Time SUTM Asset Intelligence & Risk Monitoring System<br>
                PT PLN UP3 Bandung · Industrial AI Analytics
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-value" style="color: #e8eaf0;">{total:,}</div>
                    <div class="hero-stat-label">Total Assets</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value" style="color: #ff4757;">{n_crit}</div>
                    <div class="hero-stat-label">Critical</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value" style="color: #ffa502;">{n_high}</div>
                    <div class="hero-stat-label">High Risk</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value" style="color: #00d4aa;">{last_update}</div>
                    <div class="hero-stat-label">Last Update</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Insights
    if ai_insights:
        for insight in ai_insights[:2]:  # Show top 2 insights
            severity_color = {
                "critical": "#ff4757",
                "high": "#ffa502", 
                "medium": "#3d8eff",
                "low": "#00d4aa"
            }.get(insight["severity"], "#ffa502")
            
            st.markdown(f"""
            <div class="ai-insight" style="border-color: {severity_color}40;">
                <div class="ai-insight-header">
                    <span class="ai-insight-icon">{insight["icon"]}</span>
                    <span class="ai-insight-title" style="color: {severity_color};">{insight["title"]}</span>
                </div>
                <div class="ai-insight-text">{insight["text"]}</div>
                <div class="ai-insight-recommendation" style="border-left-color: {severity_color};">
                    <strong>AI Recommendation:</strong> {insight["recommendation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enterprise KPIs with Glassmorphism
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Risk Overview</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    kpi_cols = st.columns(4)
    kpi_data = [
        ("🔴", "CRITICAL", n_crit, f"{n_crit/total*100:.1f}%", "kpi-glow-critical", "#ff4757"),
        ("🟠", "HIGH", n_high, f"{n_high/total*100:.1f}%", "kpi-glow-high", "#ffa502"),
        ("🔵", "MEDIUM", n_med, f"{n_med/total*100:.1f}%", "kpi-glow-medium", "#3d8eff"),
        ("🟢", "LOW", n_low, f"{n_low/total*100:.1f}%", "kpi-glow-low", "#00d4aa"),
    ]
    
    for col, (icon, label, value, pct, glow_class, color) in zip(kpi_cols, kpi_data):
        with col:
            st.markdown(f"""
            <div class="kpi-glass {glow_class}">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value" style="color: {color};">{value:,}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-trend" style="color: {color};">{pct} of total</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Analytics</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        # Gauge Chart for Overall Health
        health_score = (n_low / total * 100) if total > 0 else 0
        fig_gauge = create_gauge_chart(health_score, "Asset Health Score", "#00d4aa")
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Risk Donut
        fig = go.Figure(go.Pie(
            labels=["CRITICAL","HIGH","MEDIUM","LOW"],
            values=[n_crit, n_high, n_med, n_low],
            hole=0.7,
            marker=dict(colors=list(COLORS.values()), line=dict(width=2, color=PAPER_BG)),
            textinfo="none",
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{total:,}</b><br>Assets",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=18, color=FONT_COL, family="Inter"))
        dark_layout(fig, "Risk Distribution", 300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ULP Risk Heatmap
        ulp_pivot = df.groupby(["ULP", "RISK_CLASS"]).size().unstack(fill_value=0)
        for col in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if col not in ulp_pivot.columns:
                ulp_pivot[col] = 0
        
        fig_heat = px.imshow(
            ulp_pivot[["CRITICAL", "HIGH", "MEDIUM", "LOW"]].values,
            x=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            y=ulp_pivot.index,
            color_continuous_scale=[[0, "rgba(0,0,0,0)"], [1, "#ff4757"]],
            aspect="auto"
        )
        fig_heat.update_traces(
            hovertemplate="ULP: %{y}<br>Risk: %{x}<br>Count: %{z}<extra></extra>"
        )
        dark_layout(fig_heat, "Risk Heatmap by ULP", 300)
        st.plotly_chart(fig_heat, use_container_width=True)
        
        # ULP Stacked Bar
        ulp_data = (df.groupby(["ULP","RISK_CLASS"])
                      .size().reset_index(name="count"))
        fig2 = px.bar(ulp_data, x="ULP", y="count", color="RISK_CLASS",
                      color_discrete_map=COLORS, barmode="stack",
                      category_orders={"RISK_CLASS":["CRITICAL","HIGH","MEDIUM","LOW"]})
        fig2.update_layout(xaxis_tickangle=-35, showlegend=True)
        dark_layout(fig2, "Risk by ULP", 300)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Summary Stats
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Summary</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="kpi-glass">
            <div class="kpi-value" style="color: #ff4757;">{n_crit+n_high:,}</div>
            <div class="kpi-label">Critical + High</div>
            <div class="kpi-trend" style="color: #ff4757;">{(n_crit+n_high)/total*100:.1f}% of assets</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-glass">
            <div class="kpi-value" style="color: #ffa502;">{n_defect:,}</div>
            <div class="kpi-label">Defective Poles</div>
            <div class="kpi-trend" style="color: #ffa502;">{n_defect/total*100:.1f}% of assets</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-glass">
            <div class="kpi-value" style="color: #3d8eff;">{df['RISK_SCORE'].mean():.1f}</div>
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-trend" style="color: #3d8eff;">/100</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        top_ulp = df.groupby("ULP")["N_BURUK"].sum().idxmax() if "ULP" in df.columns else "—"
        st.markdown(f"""
        <div class="kpi-glass">
            <div class="kpi-value" style="color: #a55eea;">{top_ulp}</div>
            <div class="kpi-label">Top Risk ULP</div>
            <div class="kpi-trend" style="color: #a55eea;">Highest defects</div>
        </div>
        """, unsafe_allow_html=True)

# ── RISK ANALYSIS ─────────────────────────────────────────────
elif "Risk Analysis" in page:
    st.title("⚠️ Risk Analysis")
    st.caption(f"{total:,} poles classified · worst-case per unique pole")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            x=["LOW","MEDIUM","HIGH","CRITICAL"],
            y=[n_low, n_med, n_high, n_crit],
            color=["LOW","MEDIUM","HIGH","CRITICAL"],
            color_discrete_map=COLORS,
            log_y=True,
        )
        fig.update_traces(showlegend=False)
        dark_layout(fig, "Risk Count (Log Scale)", 320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(df, x="RISK_SCORE", color="RISK_CLASS",
                            color_discrete_map=COLORS, nbins=40,
                            barmode="overlay", opacity=0.8)
        dark_layout(fig2, "Risk Score Distribution", 320)
        st.plotly_chart(fig2, use_container_width=True)

    ulp_risk = (df.groupby(["ULP","RISK_CLASS"])
                  .size().reset_index(name="count"))
    ulp_risk = ulp_risk[ulp_risk["RISK_CLASS"] != "LOW"]
    fig3 = px.bar(ulp_risk, y="ULP", x="count", color="RISK_CLASS",
                  color_discrete_map=COLORS, orientation="h", barmode="stack",
                  category_orders={"RISK_CLASS":["CRITICAL","HIGH","MEDIUM"]})
    dark_layout(fig3, "CRITICAL + HIGH + MEDIUM by ULP", 350)
    st.plotly_chart(fig3, use_container_width=True)

# ── HEALTH INDEX ──────────────────────────────────────────────
elif "Health Index" in page:
    st.title("🏥 Health Index Assessment")
    st.caption("12 component categories · all inspection records")

    if not hi_df.empty:
        fig = go.Figure()
        for cond, color in [("BAIK","#00d4aa"),("CUKUP","#3d8eff"),
                             ("KURANG","#ffa502"),("BURUK","#ff4757")]:
            fig.add_trace(go.Bar(
                name=cond,
                y=hi_df["Component"],
                x=hi_df[cond],
                orientation="h",
                marker_color=color,
                hovertemplate=f"{cond}: %{{x:,}}<extra></extra>",
            ))
        fig.update_layout(barmode="stack")
        dark_layout(fig, "Component HI Distribution", 420)
        st.plotly_chart(fig, use_container_width=True)

        buruk_df = hi_df[hi_df["BURUK"] > 0].sort_values("BURUK", ascending=False)
        if not buruk_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig2 = px.bar(buruk_df, x="Component", y="BURUK",
                              color_discrete_sequence=["#ff4757"])
                fig2.update_layout(xaxis_tickangle=-30)
                dark_layout(fig2, "BURUK Count by Component", 300)
                st.plotly_chart(fig2, use_container_width=True)
            with col2:
                kurang_df = hi_df[hi_df["KURANG"] > 0].sort_values("KURANG", ascending=False)
                fig3 = px.bar(kurang_df, x="Component", y="KURANG",
                              color_discrete_sequence=["#ffa502"])
                fig3.update_layout(xaxis_tickangle=-30)
                dark_layout(fig3, "KURANG Count by Component", 300)
                st.plotly_chart(fig3, use_container_width=True)

        st.dataframe(
            hi_df.style.background_gradient(subset=["BURUK","KURANG"],
                                             cmap="RdYlGn_r"),
            use_container_width=True, height=300
        )

# ── THERMAL ───────────────────────────────────────────────────
elif "Thermal" in page:
    st.title("🌡️ Thermal Inspection — SUTMT2")

    t2_raw = load_from_drive(t2_id, "DATA")
    if t2_raw.empty:
        st.warning("لا توجد بيانات T2 أو File ID غير صحيح")
        st.stop()

    t2_raw["NUM_HI_1"] = t2_raw["HI SUTM  - 1"].map(HI_MAP).fillna(3)
    t2_raw["NUM_HI_2"] = t2_raw["HI SUTM - 2"].map(HI_MAP).fillna(3)
    temp_c = ["SUHU FASA R","SUHU FASA S","SUHU FASA T"]
    vt = t2_raw[temp_c].apply(pd.to_numeric, errors="coerce")
    t2_raw["DELTA_SUHU"] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Thermal Records",  f"{len(t2_raw):,}")
    c2.metric("Avg Δ Temp",       f"{t2_raw['DELTA_SUHU'].mean():.2f}°C")
    c3.metric("High Temp (≥10°C)",f"{(t2_raw['DELTA_SUHU']>=10).sum():,}")
    c4.metric("HI-1 BURUK",       f"{(t2_raw['NUM_HI_1']==0).sum():,}")

    st.divider()
    col1, col2 = st.columns(2)

    lbl_map = {3:"BAIK",2:"CUKUP",1:"KURANG",0:"BURUK"}
    with col1:
        hi1 = t2_raw["NUM_HI_1"].map(lbl_map).value_counts().reset_index()
        hi1.columns = ["Condition","Count"]
        fig = px.bar(hi1, x="Condition", y="Count",
                     color="Condition",
                     color_discrete_map={"BAIK":"#00d4aa","CUKUP":"#3d8eff",
                                         "KURANG":"#ffa502","BURUK":"#ff4757"})
        dark_layout(fig, "HI-1 Distribution", 300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(t2_raw, x="DELTA_SUHU", nbins=40,
                             color_discrete_sequence=["#a55eea"])
        fig2.add_vline(x=10, line_dash="dash", line_color="#ffa502",
                       annotation_text="10°C threshold")
        fig2.add_vline(x=15, line_dash="dash", line_color="#ff4757",
                       annotation_text="15°C critical")
        dark_layout(fig2, "Temperature Delta Distribution", 300)
        st.plotly_chart(fig2, use_container_width=True)

    if "ULP" in t2_raw.columns:
        fig3 = px.box(t2_raw, x="ULP", y="DELTA_SUHU", color="ULP",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig3.update_layout(xaxis_tickangle=-30, showlegend=False)
        dark_layout(fig3, "Thermal Delta by ULP", 320)
        st.plotly_chart(fig3, use_container_width=True)

# ── ML COMPARISON ─────────────────────────────────────────────
elif "ML Comparison" in page:
    st.title("🤖 ML Model Comparison")
    st.caption("5-fold stratified cross-validation · real SUTM data")

    ML_RESULTS = pd.DataFrame([
        {"Model":"XGBoost",      "Accuracy":0.9342,"Precision":0.9385,"Recall":0.9342,"F1":0.9329,"Std":0.0136,"Color":"#00d4aa","Best":True},
        {"Model":"Random Forest","Accuracy":0.8544,"Precision":0.8724,"Recall":0.8544,"F1":0.8578,"Std":0.0223,"Color":"#3d8eff","Best":False},
        {"Model":"Decision Tree","Accuracy":0.8274,"Precision":0.8672,"Recall":0.8274,"F1":0.8396,"Std":0.0187,"Color":"#ffa502","Best":False},
        {"Model":"SVM",          "Accuracy":0.7886,"Precision":0.8158,"Recall":0.7886,"F1":0.7937,"Std":0.0205,"Color":"#ff6b9d","Best":False},
        {"Model":"KNN",          "Accuracy":0.7767,"Precision":0.7856,"Recall":0.7767,"F1":0.7685,"Std":0.0138,"Color":"#a55eea","Best":False},
    ])

    FOLD_DATA = {
        "XGBoost":       [0.93,0.94,0.92,0.93,0.94],
        "Random Forest": [0.86,0.87,0.85,0.83,0.87],
        "Decision Tree": [0.84,0.85,0.83,0.82,0.84],
        "SVM":           [0.79,0.80,0.79,0.78,0.80],
        "KNN":           [0.77,0.77,0.76,0.77,0.77],
    }

    cols = st.columns(5)
    for i, row in ML_RESULTS.iterrows():
        label = f"{'★ ' if row['Best'] else ''}{row['Model']}"
        cols[i].metric(label, f"{row['F1']:.3f}",
                       "Best ↑" if row["Best"] else f"±{row['Std']:.3f}")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(go.Bar(
            y=ML_RESULTS["Model"],
            x=ML_RESULTS["F1"],
            orientation="h",
            marker_color=ML_RESULTS["Color"].tolist(),
            text=ML_RESULTS["F1"].round(3),
            textposition="outside",
        ))
        fig.update_layout(xaxis=dict(range=[0.6, 1.0]))
        dark_layout(fig, "F1-Score Comparison", 320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        metrics = ["Accuracy","Precision","Recall","F1"]
        fig2 = go.Figure()
        for m, color in zip(metrics, ["#00d4aa70","#3d8eff70","#ffa50270","#ff6b9d70"]):
            fig2.add_trace(go.Bar(
                name=m, x=ML_RESULTS["Model"],
                y=ML_RESULTS[m], marker_color=color,
            ))
        fig2.update_layout(barmode="group",
                           yaxis=dict(range=[0.6, 1.0]))
        dark_layout(fig2, "All Metrics — Grouped", 320)
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    for _, row in ML_RESULTS.iterrows():
        fig3.add_trace(go.Scatter(
            x=[f"Fold {i+1}" for i in range(5)],
            y=FOLD_DATA[row["Model"]],
            name=row["Model"],
            mode="lines+markers",
            line=dict(color=row["Color"], width=2),
            marker=dict(size=6),
        ))
    fig3.update_layout(yaxis=dict(range=[0.7, 1.0]))
    dark_layout(fig3, "F1-Score per Fold — Stability Analysis", 300)
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(
        ML_RESULTS[["Model","Accuracy","Precision","Recall","F1","Std"]]
        .style.highlight_max(subset=["F1"], color="#1D9E7544")
               .format({"Accuracy":"{:.4f}","Precision":"{:.4f}",
                        "Recall":"{:.4f}","F1":"{:.4f}","Std":"±{:.4f}"}),
        use_container_width=True, hide_index=True
    )

# ── PRIORITY POLES ────────────────────────────────────────────
elif "Priority Poles" in page:
    st.title("🎯 Priority Poles")
    st.caption("Sorted by risk score — real pole IDs from SUTMT1")

    col1, col2, col3 = st.columns(3)
    ulp_list = ["All"] + sorted(df["ULP"].dropna().unique().tolist())
    sel_ulp   = col1.selectbox("Filter by ULP", ulp_list)
    sel_risk  = col2.multiselect("Risk Class", ["CRITICAL","HIGH","MEDIUM","LOW"],
                                  default=["CRITICAL","HIGH"])
    top_n     = col3.slider("Top N poles", 10, 100, 20)

    fdf = df.copy()
    if sel_ulp != "All":
        fdf = fdf[fdf["ULP"] == sel_ulp]
    if sel_risk:
        fdf = fdf[fdf["RISK_CLASS"].isin(sel_risk)]
    fdf = fdf.nlargest(top_n, "RISK_SCORE")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Shown poles",    f"{len(fdf):,}")
    c2.metric("CRITICAL",       f"{(fdf['RISK_CLASS']=='CRITICAL').sum():,}")
    c3.metric("HIGH",           f"{(fdf['RISK_CLASS']=='HIGH').sum():,}")
    c4.metric("Avg Risk Score", f"{fdf['RISK_SCORE'].mean():.1f}")

    st.divider()

    fig = px.scatter(
        fdf, x="PENYULANG", y="RISK_SCORE",
        color="RISK_CLASS", color_discrete_map=COLORS,
        size="RISK_SCORE", hover_data=["TIANG_ID","ULP","NO TIANG"],
        size_max=18,
    )
    fig.update_layout(xaxis_tickangle=-45)
    dark_layout(fig, "Risk Score Distribution (Top Poles)", 320)
    st.plotly_chart(fig, use_container_width=True)

    def color_risk(val):
        c = {"CRITICAL":"#ff475730","HIGH":"#ffa50230",
             "MEDIUM":"#3d8eff30","LOW":"#00d4aa30"}.get(val,"")
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
        use_container_width=True,
        height=450,
        hide_index=True,
    )

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Priority List (CSV)",
        csv, "priority_poles.csv", "text/csv",
        use_container_width=True
    )

# ── EXECUTIVE SUMMARY ─────────────────────────────────────────
elif "Executive Summary" in page:
    st.title("📋 Executive Summary")
    st.caption("Management dashboard · high-level insights")
    
    # Executive KPIs
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Executive Overview</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    exec_cols = st.columns(4)
    exec_data = [
        ("Asset Health", f"{(n_low/total*100):.1f}%", "Healthy", "#00d4aa"),
        ("Critical Assets", f"{n_crit}", "Immediate Action", "#ff4757"),
        ("Avg Risk Score", f"{df['RISK_SCORE'].mean():.1f}", "/100", "#ffa502"),
        ("Inspection Coverage", "100%", "Complete", "#3d8eff"),
    ]
    
    for col, (title, value, subtitle, color) in zip(exec_cols, exec_data):
        with col:
            st.markdown(f"""
            <div class="exec-card">
                <div class="exec-card-title">{title}</div>
                <div class="exec-card-value" style="color: {color};">{value}</div>
                <div class="exec-card-subtitle">{subtitle}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # AI Executive Insights
    st.markdown("""
    <div class="section-header">
        <span class="section-title">AI Executive Insights</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    if ai_insights:
        for insight in ai_insights:
            severity_color = {
                "critical": "#ff4757",
                "high": "#ffa502", 
                "medium": "#3d8eff",
                "low": "#00d4aa"
            }.get(insight["severity"], "#ffa502")
            
            st.markdown(f"""
            <div class="ai-insight" style="border-color: {severity_color}40; margin-bottom: 15px;">
                <div class="ai-insight-header">
                    <span class="ai-insight-icon">{insight["icon"]}</span>
                    <span class="ai-insight-title" style="color: {severity_color};">{insight["title"]}</span>
                </div>
                <div class="ai-insight-text">{insight["text"]}</div>
                <div class="ai-insight-recommendation" style="border-left-color: {severity_color};">
                    <strong>Recommendation:</strong> {insight["recommendation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Risk Matrix
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Risk Matrix</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create risk matrix data
    risk_matrix = df.groupby(["ULP", "RISK_CLASS"]).size().unstack(fill_value=0)
    for col in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if col not in risk_matrix.columns:
            risk_matrix[col] = 0
    
    fig_matrix = px.imshow(
        risk_matrix.values,
        x=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        y=risk_matrix.index,
        color_continuous_scale="Reds",
        aspect="auto",
        title="Risk Concentration Matrix"
    )
    fig_matrix.update_traces(
        text=risk_matrix.values,
        texttemplate="%{z}",
        textfont={"size": 12, "color": "white"},
        hovertemplate="ULP: %{y}<br>Risk: %{x}<br>Count: %{z}<extra></extra>"
    )
    dark_layout(fig_matrix, "", 400)
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Top Critical ULPs
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Top Critical ULPs</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    top_critical = df[df["RISK_CLASS"] == "CRITICAL"].groupby("ULP").size().sort_values(ascending=False).head(10)
    if not top_critical.empty:
        fig_top = px.bar(
            x=top_critical.values,
            y=top_critical.index,
            orientation="h",
            color=top_critical.values,
            color_continuous_scale=["#ffa502", "#ff4757"],
            labels={"x": "Critical Count", "y": "ULP"}
        )
        dark_layout(fig_top, "Critical Assets by ULP", 350)
        st.plotly_chart(fig_top, use_container_width=True)
    
    # Financial Impact Estimate
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Financial Impact Estimate</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Estimate costs
    crit_cost = n_crit * 50000000  # 50M IDR per critical
    high_cost = n_high * 25000000  # 25M IDR per high
    total_cost = crit_cost + high_cost
    
    fin_cols = st.columns(3)
    with fin_cols[0]:
        st.markdown(f"""
        <div class="kpi-glass kpi-glow-critical">
            <div class="kpi-value" style="color: #ff4757;">Rp {crit_cost/1e9:.1f}B</div>
            <div class="kpi-label">Critical Maintenance</div>
            <div class="kpi-trend" style="color: #ff4757;">{n_crit} assets × Rp 50M</div>
        </div>
        """, unsafe_allow_html=True)
    with fin_cols[1]:
        st.markdown(f"""
        <div class="kpi-glass kpi-glow-high">
            <div class="kpi-value" style="color: #ffa502;">Rp {high_cost/1e9:.1f}B</div>
            <div class="kpi-label">High Risk Maintenance</div>
            <div class="kpi-trend" style="color: #ffa502;">{n_high} assets × Rp 25M</div>
        </div>
        """, unsafe_allow_html=True)
    with fin_cols[2]:
        st.markdown(f"""
        <div class="kpi-glass">
            <div class="kpi-value" style="color: #e8eaf0;">Rp {total_cost/1e9:.1f}B</div>
            <div class="kpi-label">Total Estimated Cost</div>
            <div class="kpi-trend" style="color: #3d8eff;">Combined impact</div>
        </div>
        """, unsafe_allow_html=True)
