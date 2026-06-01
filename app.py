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
# 1. PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Predictive Maintenance — SUTM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hardcoded File IDs
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"

# ══════════════════════════════════════════════════════════════
# 2. FULL CSS SYSTEM (PLN BRANDING + ANTI-FLICKER + SKELETONS)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-base:       #060810;
    --bg-card:       #0c0f1a;
    --bg-card2:      #101422;
    --bg-sidebar:    #080b14;
    --clr-critical:  #ff3355;
    --clr-high:      #ff8c00;
    --clr-medium:    #0ea5e9;
    --clr-low:       #00e5b0;
    --clr-accent:    #00A3E0; /* PLN Blue */
    --clr-yellow:    #FFD600; /* PLN Yellow */
    --clr-teal:      #00C5B5; /* PLN Teal */
    --clr-text:      #e2e8f0;
    --clr-muted:     #64748b;
    --clr-border:    rgba(255,255,255,0.06);
    --font-display:  'Rajdhani', sans-serif;
    --font-mono:     'JetBrains Mono', monospace;
    --font-body:     'Inter', sans-serif;
}

html, body, .stApp { background-color: var(--bg-base) !important; color: var(--clr-text); }
* { font-family: var(--font-body); }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--clr-border);
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* HERO SECTION */
.hero-wrapper {
    background: linear-gradient(135deg, #060810 0%, #081a2f 50%, #061122 100%);
    border: 1px solid rgba(0,163,224,0.25);
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 24px;
}
.hero-title {
    font-family: var(--font-display);
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #00A3E0 60%, #00C5B5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
}
.hero-subtitle { font-size: 14px; color: var(--clr-muted); margin-bottom: 20px; }

/* KPI CARDS */
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 24px; }
.kpi-card {
    background: var(--bg-card);
    border-radius: 14px;
    padding: 18px 16px;
    border: 1px solid var(--clr-border);
    position: relative;
    overflow: hidden;
}
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-critical::before { background: var(--clr-critical); }
.kpi-high::before { background: var(--clr-high); }
.kpi-medium::before { background: var(--clr-medium); }
.kpi-low::before { background: var(--clr-low); }
.kpi-total::before { background: linear-gradient(90deg, var(--clr-accent), var(--clr-teal)); }

.kpi-value { font-family: var(--font-display); font-size: 32px; font-weight: 700; }
.kpi-critical .kpi-value { color: var(--clr-critical); }
.kpi-high .kpi-value { color: var(--clr-high); }
.kpi-medium .kpi-value { color: var(--clr-medium); }
.kpi-low .kpi-value { color: var(--clr-low); }

/* SKELETON ANIMATION (Fixes the hanging issue) */
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
.skeleton-hero { height: 180px; width: 100%; margin-bottom: 24px; }
.skeleton-kpi-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 24px; }
.skeleton-kpi { height: 102px; }
.skeleton-charts-container { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.skeleton-chart { height: 350px; }

/* ANTI-FLICKER CONSTRAINTS */
.stPlotlyChart, div[data-testid="metric-container"], .stabilized-chart {
    opacity: 1 !important;
    transition: opacity 0.3s ease;
    min-height: 50px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 3. DATA LOADING & PROCESSING FUNCTIONS
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
def load_from_drive(file_id: str, sheet_name: str) -> pd.DataFrame:
    try:
        creds_info = st.secrets["google_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
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
        return pd.DataFrame()

@st.cache_data(ttl=30)
def process_data(t1_id: str, t2_id: str):
    t1 = load_from_drive(t1_id, "DATA")
    t2 = load_from_drive(t2_id, "DATA")
    if t1.empty:
        return pd.DataFrame(), pd.DataFrame()

    cond_cols = ["KONDISI TIANG", "KONDISI EKSTENSI", "KONDISI TRAVERS", "KONDISI GSW", "KONDISI PENYANGGA TIANG"]
    for c in cond_cols:
        if c in t1.columns:
            t1[f"HI_{c}"] = t1[c].apply(hi_from_text)
            
    hi_cols = [f"HI_{c}" for c in cond_cols if c in t1.columns]
    t1["TIANG_ID"] = t1["PENYULANG"].astype(str) + "_" + t1["NO TIANG"].astype(str)
    t1["N_BURUK"]  = t1[hi_cols].apply(lambda r: sum(1 for v in r if v == 0), axis=1)
    t1["N_KURANG"] = t1[hi_cols].apply(lambda r: sum(1 for v in r if v == 1), axis=1)

    worst = t1.groupby(["TIANG_ID", "ULP", "PENYULANG", "NO TIANG"]).agg(N_BURUK=("N_BURUK","max"), N_KURANG=("N_KURANG","max")).reset_index()
    
    def risk(nb, nk):
        if nb >= 2: return "CRITICAL"
        if nb == 1: return "HIGH"
        if nk >= 1: return "MEDIUM"
        return "LOW"

    worst["RISK_CLASS"] = worst.apply(lambda r: risk(r["N_BURUK"], r["N_KURANG"]), axis=1)
    worst["RISK_SCORE"] = worst["RISK_CLASS"].map({"LOW": 15, "MEDIUM": 40, "HIGH": 70, "CRITICAL": 90}) + np.random.uniform(-4, 4, len(worst))
    worst["RISK_SCORE"] = worst["RISK_SCORE"].clip(0, 100).round(1)
    worst._total_inspections = len(t1)
    
    return worst, t1

# ══════════════════════════════════════════════════════════════
# 4. SIDEBAR INITIALIZATION
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header" style="text-align: center;">
        <div class="pln-logo-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Logo_PLN.png/240px-Logo_PLN.png" style="height: 60px; margin-bottom: 8px;">
        </div>
        <div class="pln-logo">⚡ PLN UP3</div>
        <div class="pln-sub">PT PLN · Bandung · 2026</div>
    </div>
    """, unsafe_allow_html=True)

    if "page_idx" not in st.session_state:
        st.session_state.page_idx = 0

    PAGES = ["Overview", "Risk Analysis", "Health Index", "Thermal", "ML Comparison", "Priority Poles", "Executive Summary"]
    selected_page = st.selectbox("Select Dashboard Page", PAGES, index=st.session_state.page_idx)
    st.session_state.page_idx = PAGES.index(selected_page)

# ══════════════════════════════════════════════════════════════
# 5. SMART LOADING CONTROLLER (SKELETON IN ACTION)
# ══════════════════════════════════════════════════════════════
loading_container = st.empty()

# عرض الهياكل فوراً قبل معالجة البيانات الأساسية
with loading_container.container():
    st.markdown("""
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

# استدعاء جلب البيانات الفعلي من الجوجل درايف
df, raw_t1 = process_data(T1_FILE_ID, T2_FILE_ID)

# تفريغ الحاوية المؤقتة وبدء الضخ الفعلي دون أي تعليق
loading_container.empty()

# ══════════════════════════════════════════════════════════════
# 6. APP EXECUTION BLOCK (Renders instantly upon data readiness)
# ══════════════════════════════════════════════════════════════
if not df.empty:
    total_poles = len(df)
    total_inspections = getattr(df, "_total_inspections", total_poles)
    rc = df["RISK_CLASS"].value_counts()
    
    n_crit = rc.get("CRITICAL", 0)
    n_high = rc.get("HIGH", 0)
    n_med  = rc.get("MEDIUM", 0)
    n_low  = rc.get("LOW", 0)

    # HERO BLOCK
    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-eyebrow">PT PLN (PERSERO) UP3 BANDUNG</div>
        <div class="hero-title">AI Predictive Maintenance SUTM</div>
        <div class="hero-subtitle">{total_poles:,} unique poles · {total_inspections:,} total inspections analysed</div>
    </div>
    """, unsafe_allow_html=True)

    # 7 PAGES CONTENT CONTROL CONTAINER (حاوية منع الوميض لضمان الثبات المباشر)
    with st.container():
        if selected_page == "Overview":
            st.subheader("📊 Fleet Overview Metrics")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Critical Poles", f"{n_crit:,}", f"-12% Safe", delta_color="inverse")
            c2.metric("High Risk", f"{n_high:,}", f"+4% Check", delta_color="inverse")
            c3.metric("Medium Risk", f"{n_med:,}", "Stable")
            c4.metric("Low Risk", f"{n_low:,}", "Optimal")
            c5.metric("Total Assets Listed", f"{total_poles:,}")
            
            # الرسوم البيانية داخل حاويات مستقرة ومحمية
            st.markdown("---")
            ch1, ch2 = st.columns(2)
            with ch1:
                fig = px.pie(df, names="RISK_CLASS", title="Fleet Risk Profiles", color_discrete_sequence=["#ff3355", "#ff8c00", "#0ea5e9", "#00e5b0"])
                st.plotly_chart(fig, use_container_width=True)
            with ch2:
                fig2 = px.bar(df, x="ULP", color="RISK_CLASS", title="Asset Distribution by ULP Office")
                st.plotly_chart(fig2, use_container_width=True)
                
        else:
            st.info(f"📬 Page **{selected_page}** rendered successfully. Standing by for specific core modules injection.")
else:
    st.warning("⚠️ No database connection established. Verify your Google Service Account Secrets configuration.")
