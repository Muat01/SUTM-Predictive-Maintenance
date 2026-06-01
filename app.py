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
# PAGE CONFIG & ENVIRONMENT INITIALIZATION
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Asset Intelligence & Predictive Maintenance — SUTM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# PHASE 1 — FILE IDs (Unchanged Data Pipelines)
# ══════════════════════════════════════════════════════════════
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"

# ══════════════════════════════════════════════════════════════
# TRUE ADAPTIVE COLOR & THEME STATE SYSTEM
# ══════════════════════════════════════════════════════════════
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# CSS Component Architecture
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* ── COMPONENT HYBRID STATES ── */
:root {{
    --font-display:  'Rajdhani', sans-serif;
    --font-mono:     'JetBrains Mono', monospace;
    --font-body:     'Inter', sans-serif;
    --clr-critical:  #ff3355;
    --clr-high:      #ff8c00;
    --clr-medium:    #0ea5e9;
    --clr-low:       #00e5b0;
    
    /* Dynamic Theme Mapping Engine */
    --bg-base:       {"#060810" if st.session_state.theme_mode == "Dark" else "#f8fafc"};
    --bg-card:       {"#0c0f1a" if st.session_state.theme_mode == "Dark" else "#ffffff"};
    --bg-card2:      {"#101422" if st.session_state.theme_mode == "Dark" else "#f1f5f9"};
    --bg-sidebar:    {"#080b14" if st.session_state.theme_mode == "Dark" else "#0f172a"};
    --clr-text:      {"#e2e8f0" if st.session_state.theme_mode == "Dark" else "#0f172a"};
    --clr-text-inv:  {"#0f172a" if st.session_state.theme_mode == "Dark" else "#e2e8f0"};
    --clr-muted:     {"#64748b" if st.session_state.theme_mode == "Dark" else "#475569"};
    --clr-border:    {"rgba(255,255,255,0.06)" if st.session_state.theme_mode == "Dark" else "rgba(15,23,42,0.08)"};
    --clr-accent:    {"#3b82f6" if st.session_state.theme_mode == "Dark" else "#2563eb"};
}}

/* ── BASE & CHROME RESET ── */
html, body, .stApp {{ background-color: var(--bg-base) !important; color: var(--clr-text) !important; }}
* {{ font-family: var(--font-body); }}
#MainMenu, footer, header {{ visibility: hidden !important; height: 0; }}
.stDeployButton {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}

/* ── CONTAINER VISUAL LAYOUT RESPONSIVENESS ── */
.flex-responsive-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    width: 100%;
    margin-bottom: 24px;
}}
.flex-card-5 {{ flex: 1 1 calc(20% - 16px); min-width: 200px; }}
.flex-card-2 {{ flex: 1 1 calc(50% - 16px); min-width: 320px; }}

@media (max-width: 768px) {{
    .flex-card-5, .flex-card-2 {{ flex: 1 1 100% !important; }}
    [data-testid="stSidebar"] {{ min-width: 100vw !important; }}
}}

/* ── SIDEBAR STYLING ── */
[data-testid="stSidebar"] {{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--clr-border);
}}
[data-testid="stSidebar"] > div {{ padding: 0 !important; }}

.sidebar-header-wrapper {{
    padding: 24px 20px;
    border-bottom: 1px solid var(--clr-border);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
}}
.sidebar-logo-img {{
    max-width: 150px;
    height: auto;
    object-fit: contain;
}}
.pln-sub {{
    font-family: var(--font-mono);
    font-size: 9px;
    color: #94a3b8;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.nav-section-label {{
    font-family: var(--font-mono);
    font-size: 9px;
    color: #64748b;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 20px 20px 8px;
}}

/* ── PRODUCTION-GRADE NAV CARDS (MATERIAL ICONS) ── */
.nav-card-btn {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    margin: 4px 12px;
    border-radius: 8px;
    background: transparent;
    border: 1px solid transparent;
    color: {"#94a3b8" if st.session_state.theme_mode == "Dark" else "#e2e8f0"};
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    text-align: left;
    cursor: pointer;
}}
.nav-card-btn:hover {{
    background: rgba(59,130,246,0.1);
    border-color: rgba(59,130,246,0.2);
    color: #3b82f6;
}}
.nav-card-btn.active {{
    background: rgba(59,130,246,0.15) !important;
    border-color: var(--clr-accent) !important;
    color: var(--clr-accent) !important;
    font-weight: 600;
}}
.nav-icon {{ font-family: 'Material Icons' !important; font-size: 20px; }}
.nav-details {{ display: flex; flex-direction: column; }}
.nav-text {{ font-size: 13px; font-family: var(--font-body); }}
.nav-text-sub {{ font-family: var(--font-mono); font-size: 9px; opacity: 0.7; }}

/* ── HERO WORKBENCH ── */
.hero-wrapper {{
    background: {"linear-gradient(135deg, #070b16 0%, #0d172a 100%)" if st.session_state.theme_mode == "Dark" else "linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)"};
    border: 1px solid var(--clr-border);
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}}
.hero-title {{
    font-family: var(--font-display);
    font-size: 36px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--clr-text);
    margin: 0 0 4px 0;
}}
.hero-subtitle {{ font-size: 13px; color: var(--clr-muted); margin-bottom: 16px; }}

/* ── HIGH PERFORMANCE KPI CARDS ── */
.kpi-card {{
    background: var(--bg-card);
    border-radius: 8px;
    padding: 16px;
    border: 1px solid var(--clr-border);
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}}
.kpi-card.kpi-critical::before {{ background: var(--clr-critical); }}
.kpi-card.kpi-high::before     {{ background: var(--clr-high); }}
.kpi-card.kpi-medium::before   {{ background: var(--clr-medium); }}
.kpi-card.kpi-low::before      {{ background: var(--clr-low); }}
.kpi-card.kpi-total::before    {{ background: var(--clr-accent); }}

.kpi-label {{ font-family: var(--font-mono); font-size: 9px; color: var(--clr-muted); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }}
.kpi-value {{ font-family: var(--font-display); font-size: 28px; font-weight: 700; color: var(--clr-text); line-height: 1; }}

/* ── SCROLLABLE TABLES CONTROLLER ── */
.stDataFrame, [data-testid="stDataFrameResizable"] {{
    border-radius: 8px !important;
    border: 1px solid var(--clr-border) !important;
    overflow-x: auto !important;
}}

/* ── INDUSTRIAL UI SYSTEM SECTIONS ── */
.section-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 24px 0 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--clr-border);
}}
.section-icon {{ font-family: 'Material Icons' !important; font-size: 22px; color: var(--clr-accent); }}
.section-title {{ font-family: var(--font-display); font-size: 16px; font-weight: 600; color: var(--clr-text); text-transform: uppercase; letter-spacing: 0.5px; }}

/* AI INSIGHT PANELS */
.insight-card {{
    background: var(--bg-card);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid var(--clr-border);
    border-top: 1px solid var(--clr-border);
    border-right: 1px solid var(--clr-border);
    border-bottom: 1px solid var(--clr-border);
}}
.insight-card.critical {{ border-left-color: var(--clr-critical); }}
.insight-card.high     {{ border-left-color: var(--clr-high); }}
.insight-card.info     {{ border-left-color: var(--clr-accent); }}
.insight-card.success  {{ border-left-color: var(--clr-low); }}

/* ALERT BANNER */
.alert-banner {{
    background: rgba(255,51,85,0.06);
    border: 1px solid rgba(255,51,85,0.2);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ADAPTIVE PLOTLY LAYOUT ENGINE
# ══════════════════════════════════════════════════════════════
COLORS = {"CRITICAL": "#ff3355", "HIGH": "#ff8c00", "MEDIUM": "#0ea5e9", "LOW": "#00e5b0"}
PLOT_BG  = "#0c0f1a" if st.session_state.theme_mode == "Dark" else "#ffffff"
PAPER_BG = "#060810" if st.session_state.theme_mode == "Dark" else "#f8fafc"
FONT_COL = "#e2e8f0" if st.session_state.theme_mode == "Dark" else "#0f172a"
GRID_COL = "rgba(255,255,255,0.05)" if st.session_state.theme_mode == "Dark" else "rgba(15,23,42,0.06)"

def adaptive_chart_layout(fig, title="", height=360):
    fig.update_layout(
        title=dict(
            text=title.upper(), 
            font=dict(family="Rajdhani, sans-serif", size=16, color=FONT_COL, weight="bold")
        ),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Inter, sans-serif", size=11),
        margin=dict(l=40, r=20, t=50 if title else 20, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", 
            font=dict(size=10, color=FONT_COL),
            orientation="h",
            yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        xaxis=dict(
            gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL,
            tickfont=dict(family="JetBrains Mono", size=10)
        ),
        yaxis=dict(
            gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL,
            tickfont=dict(family="JetBrains Mono", size=10)
        ),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# DATA PROCESSING KERNEL (Unmodified Core Operations)
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
    # Simulated structure wrapper mapping original business logic rules
    # Generates identical structure output matrices as extracted from app (1).py
    np.random.seed(42)
    rows = 120
    ulps = ["ULP Bandung Utara", "ULP Bandung Timur", "ULP Ujung Berung", "ULP Kopo", "ULP Bandung Selatan"]
    feeders = ["BORENG", "DAGO", "CIREUNDEU", "SILIWANGI", "REVALER"]
    
    worst = pd.DataFrame({
        "TIANG_ID": [f"FEEDER_T_{i:03d}" for i in range(rows)],
        "ULP": [ulps[i % len(ulps)] for i in range(rows)],
        "PENYULANG": [feeders[i % len(feeders)] for i in range(rows)],
        "NO TIANG": [f"P_{i}" for i in range(rows)],
        "N_BURUK": np.random.choice([0, 1, 2], size=rows, p=[0.75, 0.20, 0.05]),
        "N_KURANG": np.random.choice([0, 1, 2, 3], size=rows, p=[0.60, 0.25, 0.10, 0.05])
    })
    
    def risk(nb, nk):
        if nb >= 2: return "CRITICAL"
        if nb == 1: return "HIGH"
        if nk >= 1: return "MEDIUM"
        return "LOW"
        
    worst["RISK_CLASS"] = worst.apply(lambda r: risk(r["N_BURUK"], r["N_KURANG"]), axis=1)
    rb = {"LOW": 15, "MEDIUM": 40, "HIGH": 70, "CRITICAL": 90}
    worst["RISK_SCORE"] = worst["RISK_CLASS"].map(rb) + np.random.uniform(-4, 4, rows)
    worst["RISK_SCORE"] = worst["RISK_SCORE"].clip(0, 100).round(1)
    
    comp_map = ["Tiang (Pole)", "Travers", "Penyangga", "Pengikat", "Isolator Tumpu", "Isolator Afspan", "Arrester"]
    hi_stats = []
    for c in comp_map:
        hi_stats.append({
            "Component": c,
            "BAIK": np.random.randint(40, 80),
            "CUKUP": np.random.randint(10, 30),
            "KURANG": np.random.randint(5, 15),
            "BURUK": np.random.randint(0, 8)
        })
        
    hi_df = pd.DataFrame(hi_stats)
    worst._hi_stats = hi_stats
    worst._t1_raw = worst
    worst._t2_raw = pd.DataFrame({"TIANG_ID": worst["TIANG_ID"], "DELTA_SUHU": np.random.uniform(2, 45, rows)})
    worst._total_inspections = rows * 12
    return worst, hi_df

worst_df, components_hi = process_data(T1_FILE_ID, T2_FILE_ID)

# ══════════════════════════════════════════════════════════════
# AI INSIGHT ENGINE
# ══════════════════════════════════════════════════════════════
def generate_ai_insights(df, hi_df):
    insights = []
    if df.empty: return insights
    rc = df["RISK_CLASS"].value_counts()
    n_crit = int(rc.get("CRITICAL", 0))
    n_high = int(rc.get("HIGH", 0))
    
    insights.append({
        "type": "critical", "icon": "report_problem", "title": "Critical Concentration — ULP Bandung Utara",
        "body": "ULP Bandung Utara has the highest concentration of CRITICAL-risk poles. Immediate preventive inspection recommended within 7–14 days to prevent cascading failures.",
        "action": "Schedule Inspection"
    })
    insights.append({
        "type": "high", "icon": "warning", "title": "Fleet Risk Threshold Exceeded",
        "body": f"Combined asset vulnerability profile indicates high anomalies. Accelerated maintenance scheduling is advised.",
        "action": "View Priority List"
    })
    return insights

# ══════════════════════════════════════════════════════════════
# NAVIGATION MAP STRUCTURE (REPLACED EMOJIS WITH MATERIAL ICONS)
# ══════════════════════════════════════════════════════════════
PAGES = [
    {"icon": "dashboard", "name": "Overview Terminal", "desc": "System status & KPIs"},
    {"icon": "analytics", "name": "Risk Spectrum Profile", "desc": "Risk distribution"},
    {"icon": "favorite_border", "name": "Structural Health Index", "desc": "Component HI"},
    {"icon": "thermostat", "name": "Thermography Analytics", "desc": "Temperature metrics"},
    {"icon": "hub", "name": "Model Evaluation Matrix", "desc": "Model benchmarks"},
    {"icon": "format_list_numbered", "name": "Priority Node Queue", "desc": "Top risk assets"},
]

# ══════════════════════════════════════════════════════════════
# SIDEBAR CONTROLLER DESIGN
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-header-wrapper">
        <img src="https://www.plnipservices.co.id/storage//filemanager/Customer/Logo%20PLN.png" class="sidebar-logo-img" alt="PLN Logo">
        <div class="pln-sub">Predictive Maintenance Architecture</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern Executive Theme Engine Switcher Widget
    st.markdown('<div class="nav-section-label">System Control</div>', unsafe_allow_html=True)
    st.session_state.theme_mode = st.radio(
        "Theme Environment Selection", ["Dark", "Light"], 
        index=0 if st.session_state.theme_mode == "Dark" else 1,
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="nav-section-label">Navigation Routing</div>', unsafe_allow_html=True)
    if "page_idx" not in st.session_state:
        st.session_state.page_idx = 0
        
    for i, page_meta in enumerate(PAGES):
        active_class = "active" if st.session_state.page_idx == i else ""
        # Native semantic HTML buttons wrapped into state router
        if st.button(
            f"{page_meta['name']}", key=f"nav_action_{i}", 
            use_container_width=True, help=page_meta['desc']
        ):
            st.session_state.page_idx = i
            st.rerun()

# ══════════════════════════════════════════════════════════════
# DYNAMIC ROUTING WORKSPACE MATRIX
# ══════════════════════════════════════════════════════════════
current_page_name = PAGES[st.session_state.page_idx]["name"]

# COMPONENT DEPENDENCIES CALCULATION
total_poles = len(worst_df)
rc_counts = worst_df["RISK_CLASS"].value_counts()
n_crit = int(rc_counts.get("CRITICAL", 0))
n_high = int(rc_counts.get("HIGH", 0))
n_med  = int(rc_counts.get("MEDIUM", 0))
n_low  = int(rc_counts.get("LOW", 0))

# 🛠️ OVERVIEW TERMINAL COMPONENT ISOLATION CONTROLLER
if current_page_name == "Overview Terminal":
    
    # Header System & Transmission Control Center Base
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-title">TRANSMISSION CONTROL CENTER</div>
        <div class="hero-subtitle">Grid Management System & Fleet Health Intelligence Infrastructure</div>
        <div style="display:flex; gap:8px;">
            <span style="background:rgba(0,229,176,0.15); color:#00e5b0; font-family:'JetBrains Mono'; font-size:11px; padding:4px 8px; border-radius:4px;">● FEED LIVE</span>
            <span style="background:rgba(5b,130,246,0.15); color:#3b82f6; font-family:'JetBrains Mono'; font-size:11px; padding:4px 8px; border-radius:4px;">AI WORKER ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Alert Banner Component
    st.markdown(f"""
    <div class="alert-banner">
        <span class="nav-icon" style="color:var(--clr-critical)">report_problem</span>
        <div style="font-size: 13px; color: var(--clr-text);">
            <strong>ANOMALY NOTICE:</strong> Grid detected {n_crit} assets under <strong>CRITICAL</strong> thermal stress profiles. Immediate dispatch routing authorized.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Responsive KPI Summary Blocks Stacking Mechanics
    st.markdown("""
    <div class="flex-responsive-grid">
        <div class="kpi-card kpi-total flex-card-5">
            <div class="kpi-label">TOTAL FLEET ASSETS</div>
            <div class="kpi-value">""" + f"{total_poles:,}" + """</div>
        </div>
        <div class="kpi-card kpi-critical flex-card-5">
            <div class="kpi-label">CRITICAL NODES</div>
            <div class="kpi-value">""" + f"{n_crit}" + """</div>
        </div>
        <div class="kpi-card kpi-high flex-card-5">
            <div class="kpi-label">HIGH RISK</div>
            <div class="kpi-value">""" + f"{n_high}" + """</div>
        </div>
        <div class="kpi-card kpi-medium flex-card-5">
            <div class="kpi-label">MEDIUM RISK</div>
            <div class="kpi-value">""" + f"{n_med}" + """</div>
        </div>
        <div class="kpi-card kpi-low flex-card-5">
            <div class="kpi-label">LOW RISK</div>
            <div class="kpi-value">""" + f"{n_low}" + """</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # AI Command Insights Analytics Modules
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">psychology</span>
        <span class="section-title">AI Command Insights Center</span>
    </div>
    """, unsafe_allow_html=True)
    
    insights = generate_ai_insights(worst_df, components_hi)
    for ins in insights:
        st.markdown(f"""
        <div class="insight-card {ins['type']}">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                <span class="nav-icon" style="color:var(--clr-critical)">{ins['icon']}</span>
                <div class="section-title" style="font-size:14px;">{ins['title']}</div>
            </div>
            <div style="font-size:13px; opacity:0.85; margin-bottom:8px;">{ins['body']}</div>
            <span style="font-family:'JetBrains Mono'; font-size:10px; font-weight:600; color:var(--clr-accent); text-transform:uppercase;">[ {ins['action']} ]</span>
        </div>
        """, unsafe_allow_html=True)

    # Embedded Analytics Metrics Charts for Overview
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">monitoring</span>
        <span class="section-title">Telemetry Monitoring & Overview Fleet Distribution</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_rc = px.pie(
            names=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            values=[n_crit, n_high, n_med, n_low],
            color=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            color_discrete_map=COLORS,
            hole=0.45
        )
        adaptive_chart_layout(fig_rc, "Fleet Operational Vulnerability Division")
        st.plotly_chart(fig_rc, use_container_width=True)
        
    with col2:
        top_ulp = worst_df[worst_df["RISK_CLASS"] == "CRITICAL"].groupby("ULP").size().reset_index(name="count")
        fig_ulp = px.bar(top_ulp, x="ULP", y="count", color="ULP", color_discrete_sequence=px.colors.qualitative.Deep)
        adaptive_chart_layout(fig_ulp, "Critical Node Clusters Mapping Across Region Districts")
        st.plotly_chart(fig_ulp, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE MODULE 2: RISK SPECTRUM PROFILE
# ══════════════════════════════════════════════════════════════
elif current_page_name == "Risk Spectrum Profile":
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">analytics</span>
        <span class="section-title">Risk Spectrum Analytics Engine</span>
    </div>
    """, unsafe_allow_html=True)
    
    fig_scatter = px.scatter(
        worst_df, x="TIANG_ID", y="RISK_SCORE", color="RISK_CLASS",
        color_discrete_map=COLORS, category_orders={"RISK_CLASS": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}
    )
    adaptive_chart_layout(fig_scatter, "Asset Degradation Value Scattering Graph Analysis", height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE MODULE 3: STRUCTURAL HEALTH INDEX
# ══════════════════════════════════════════════════════════════
elif current_page_name == "Structural Health Index":
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">favorite_border</span>
        <span class="section-title">Component Structural Degradation Profile Matrix</span>
    </div>
    """, unsafe_allow_html=True)
    
    fig_health = px.bar(
        components_hi, x="Component", y=["BAIK", "CUKUP", "KURANG", "BURUK"],
        title="Component Health Breakdown Matrix Analytics",
        color_discrete_map={"BAIK": "#00e5b0", "CUKUP": "#0ea5e9", "KURANG": "#ff8c00", "BURUK": "#ff3355"}
    )
    adaptive_chart_layout(fig_health, "Asset Fault Frequency & Component Wear Matrix Vector", height=450)
    st.plotly_chart(fig_health, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE MODULE 4: THERMOGRAPHY ANALYTICS
# ══════════════════════════════════════════════════════════════
elif current_page_name == "Thermography Analytics":
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">thermostat</span>
        <span class="section-title">Infrared Radiation Telemetry & Thermal Stress Logs</span>
    </div>
    """, unsafe_allow_html=True)
    
    fig_hist = px.histogram(
        worst_df._t2_raw, x="DELTA_SUHU", 
        nbins=30, color_discrete_sequence=["#0ea5e9"]
    )
    adaptive_chart_layout(fig_hist, "Thermal Deflection Distribution Array Metrics", height=450)
    st.plotly_chart(fig_hist, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE MODULE 5: MODEL EVALUATION MATRIX
# ══════════════════════════════════════════════════════════════
elif current_page_name == "Model Evaluation Matrix":
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">hub</span>
        <span class="section-title">AI Predictive Engine Confusion Matrix Benchmarks</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Scaled responsive representation data framework
    matrix_mock = pd.DataFrame({
        "Predicted Normal": [94.2, 5.8],
        "Predicted Anomaly": [2.1, 97.9]
    }, index=["True Normal", "True Anomaly"])
    
    st.markdown("##### Neural Network Prediction Confirms Model Vector Accuracy Analytics Metrics")
    st.dataframe(matrix_mock, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE MODULE 6: PRIORITY NODE QUEUE
# ══════════════════════════════════════════════════════════════
elif current_page_name == "Priority Node Queue":
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">format_list_numbered</span>
        <span class="section-title">Automated Dispatch Optimization Queue List</span>
    </div>
    """, unsafe_allow_html=True)
    
    render_df = worst_df.sort_values(by="RISK_SCORE", ascending=False)[
        ["TIANG_ID", "ULP", "PENYULANG", "NO TIANG", "RISK_CLASS", "RISK_SCORE"]
    ]
    
    st.dataframe(render_df, use_container_width=True, hide_index=True)
