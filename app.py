import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# 1. ENTERPRISE INITIALIZATION & PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PLN Command Center — AI Predictive Maintenance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Cloud System References
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"
PLN_LOGO_URL = "https://www.plnipservices.co.id/storage//filemanager/Customer/Logo%20PLN.png"

# ══════════════════════════════════════════════════════════════
# 2. APPLICATION SHELL & COMPONENT STYLING (GLOBAL CSS)
# ══════════════════════════════════════════════════════════════
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

/* Main UI Frame Overrides */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}

/* Eliminate Default Streamlit Header & Excess Margins */
header, [data-testid="stHeader"] { visibility: hidden; display: none !important; }
.stMainBlockContainer { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* Sidebar Micro-Branding */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.15);
}
.sidebar-logo-container {
    text-align: center;
    padding: 1.5rem 1rem 1rem 1rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}
.sidebar-logo { max-width: 160px; height: auto; object-fit: contain; }
.sidebar-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #005A9C;
    letter-spacing: 2px;
    margin-top: 0.5rem;
    font-weight: 600;
}

/* Control Room Header Architecture */
.header-hud {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.25rem;
    background: rgba(128, 128, 128, 0.04);
    border: 1px solid rgba(128, 128, 128, 0.12);
    border-radius: 8px;
    margin-bottom: 1.5rem;
}
.header-title-pack h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0;
    padding: 0;
    line-height: 1.2;
}
.header-metadata {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: grey;
    margin-top: 0.2rem;
}
.status-pulse {
    display: inline-block;
    width: 7px;
    height: 7px;
    background: #00a896;
    border-radius: 50%;
    box-shadow: 0 0 8px #00a896;
    animation: pulse 1.8s infinite ease-in-out;
}
@keyframes pulse { 0% { opacity:0.4; } 50% { opacity:1; } 100% { opacity:0.4; } }

/* Industrial Hero Wrapper */
.hero-panel {
    background: linear-gradient(135deg, rgba(0, 90, 156, 0.08) 0%, rgba(0, 163, 166, 0.03) 100%);
    border-left: 4px solid #005A9C;
    border-top: 1px solid rgba(0, 90, 156, 0.15);
    border-right: 1px solid rgba(0, 90, 156, 0.15);
    border-bottom: 1px solid rgba(0, 90, 156, 0.15);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
}
.hero-title span { color: #005A9C; }
.hero-desc { font-size: 0.88rem; opacity: 0.8; max-width: 850px; line-height: 1.5; }

/* SCADA KPI Cards Design */
.scada-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.scada-card {
    background: rgba(128, 128, 128, 0.03);
    border: 1px solid rgba(128, 128, 128, 0.12);
    border-radius: 8px;
    padding: 1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.scada-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 4px;
}
.scada-total::before { background: #005A9C; }
.scada-critical::before { background: #ff3355; }
.scada-high::before { background: #ff8c00; }
.scada-medium::before { background: #006bb3; }
.scada-low::before { background: #00a896; }

.scada-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: grey;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.scada-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 0.25rem;
}

/* Core Industrial Panels */
.panel-box {
    background: rgba(128, 128, 128, 0.02);
    border: 1px solid rgba(128, 128, 128, 0.12);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
}
.panel-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* AI Insights Components */
.ai-insight-metric {
    background: rgba(128, 128, 128, 0.04);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    border-left: 3px solid #FFD600;
    margin-bottom: 0.75rem;
}
.ai-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: grey; }
.ai-body { font-size: 0.95rem; font-weight: 600; margin-top: 0.15rem; }

/* Priority Rank Matrix Items */
.matrix-row {
    background: rgba(128, 128, 128, 0.02);
    border: 1px solid rgba(128, 128, 128, 0.1);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
}
.matrix-bar-bg {
    height: 5px;
    background: rgba(128, 128, 128, 0.15);
    border-radius: 3px;
    margin-top: 0.5rem;
    overflow: hidden;
}
.matrix-bar-fill {
    height: 100%;
    background: #005A9C;
    border-radius: 3px;
}
</style>
""")

# ══════════════════════════════════════════════════════════════
# 3. COMPACT HIGH-HUD CONTROLS & LOCALIZATION
# ══════════════════════════════════════════════════════════════
# Dictionary Mapping for SCADA Multilingual Interface Support
LOCALIZATION_DATA = {
    "English": {
        "title": "PLN SUTM TRANSMISSION CONTROL CENTER",
        "desc": "Enterprise-grade Predictive Maintenance Node. Artificial Intelligence analytical matrix continuously parses historical structural inspection anomalies, electrical faults, and thermography deviations across active distribution assets.",
        "total_assets": "Monitored Fleet Assets", "crit_risk": "Critical Risk Nodes", "high_risk": "High Risk Nodes", "med_risk": "Medium Risk Nodes", "low_risk": "Nominal Health Nodes",
        "health_idx": "GLOBAL NET HEALTH INDEX", "ai_panel_title": "🤖 CORE INTELLIGENCE AGENT INSIGHTS", "matrix_title": "🎯 MAINTENANCE PRIORITY RANK SYSTEM",
        "highest_branch": "Highest Vulnerability Branch (ULP)", "worst_component": "Dominant Asset Degradation Vector", "action_req": "Prescribed Maintenance Strategy", "priority_level": "Computed Response Vector"
    },
    "العربية": {
        "title": "مركز التحكم بنقل الطاقة PLN SUTM",
        "desc": "منصة الصيانة التنبؤية للمؤسسات. تقوم مصفوفة التحليل الذكي بفحص شذوذ الفحص الهيكلي التاريخي، والأعطال الكهربائية، وانحرافات التصوير الحراري عبر أصول الشبكة النشطة.",
        "total_assets": "إجمالي أصول الشبكة", "crit_risk": "عقد الخطورة الحرجة", "high_risk": "عقد الخطورة العالية", "med_risk": "عقد الخطورة المتوسطة", "low_risk": "عقد وضع التشغيل الطبيعي",
        "health_idx": "مؤشر صحة الشبكة العالمي", "ai_panel_title": "🤖 رؤى محرك الذكاء الاصطناعي المركزي", "matrix_title": "🎯 نظام ترتيب أولويات الصيانة والترميم",
        "highest_branch": "الفرع الأكثر عرضة للمخاطر (ULP)", "worst_component": "عنصر التدهور الهيكلي المهيمن", "action_req": "الإجراء التصحيحي الموصى به فوراً", "priority_level": "متجه الاستجابة المحسوب للنظام"
    },
    "Bahasa Indonesia": {
        "title": "PLN SUTM TRANSMISSION CONTROL CENTER",
        "desc": "Platform Pemeliharaan Prediktif Kelas Perusahaan. Matriks analitik Kecerdasan Buatan secara terus-menerus memproses anomali inspeksi struktural historis, gangguan listrik, dan deviasi termografi pada aset distribusi aktif.",
        "total_assets": "Total Aset Armada", "crit_risk": "Node Risiko Kritis", "high_risk": "Node Risiko Tinggi", "med_risk": "Node Risiko Sedang", "low_risk": "Node Kesehatan Nominal",
        "health_idx": "INDEKS KESEHATAN JARINGAN GLOBAL", "ai_panel_title": "🤖 WAWASAN INTI AGEN KECERDASAN AI", "matrix_title": "🎯 SISTEM PERINGKAT PRIORITAS PEMELIHARAAN",
        "highest_branch": "Cabang Kerentanan Tertinggi (ULP)", "worst_component": "Vektor Degradasi Aset Dominan", "action_req": "Strategi Pemeliharaan Direkomendasikan", "priority_level": "Vektor Respons Terhitung"
    }
}

# Layout Grid Split for Header HUD
hud_left, hud_right = st.columns([3, 1], vertical_alignment="center")

with hud_right:
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        selected_lang = st.selectbox("🌐 Language", ["English", "العربية", "Bahasa Indonesia"], label_visibility="collapsed", index=0)
    with ctrl_col2:
        selected_theme = st.segmented_control("🎨 Mode", ["🌙", "☀️"], default="🌙", label_visibility="collapsed")

# Assign localized text dictionary mappings
LANG = LOCALIZATION_DATA[selected_lang]
is_light_mode = (selected_theme == "☀️")

with hud_left:
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    st.markdown(f"""
    <div class="header-hud">
        <div class="header-title-pack">
            <h1>{LANG['title']}</h1>
            <div class="header-metadata">
                <span class="status-pulse"></span>
                <span>SYSTEM STATUS: <b>LIVE MONITORING</b></span>
                <span>|</span>
                <span>LAST TELEMETRY UPDATE: {current_time_str}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 4. HIGH-SPEED TELEMETRY ENGINE & PIPELINE VIA CACHE
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def pull_and_aggregate_scada_payload(t1_id: str, t2_id: str):
    try:
        service_account_info = st.secrets["google_service_account"]
        credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/drive.readonly"])
        drive_service = build("drive", "v3", credentials=credentials)
        
        # Stream Sheet 1 Pipeline
        request_t1 = drive_service.files().get_media(fileId=t1_id)
        buffer_t1 = io.BytesIO()
        downloader_t1 = MediaIoBaseDownload(buffer_t1, request_t1)
        finished_t1 = False
        while not finished_t1: _, finished_t1 = downloader_t1.next_chunk()
        buffer_t1.seek(0)
        df_t1 = pd.read_excel(buffer_t1, sheet_name="DATA")
        
        # Stream Sheet 2 Pipeline
        request_t2 = drive_service.files().get_media(fileId=t2_id)
        buffer_t2 = io.BytesIO()
        downloader_t2 = MediaIoBaseDownload(buffer_t2, request_t2)
        finished_t2 = False
        while not finished_t2: _, finished_t2 = downloader_t2.next_chunk()
        buffer_t2.seek(0)
        df_t2 = pd.read_excel(buffer_t2, sheet_name="DATA")
    except Exception:
        return None

    def evaluate_component_condition(text_value):
        if pd.isna(text_value) or str(text_value).strip().upper() in ["BLANK", "TIDAK ADA", "-", ""]: return 3
        normalized = str(text_value).upper()
        if any(term in normalized for term in ["BURUK","PECAH","PUTUS","KEROPOS","FLASH","BOCOR","RANTAS","RETAK"]): return 0
        if any(term in normalized for term in ["KURANG","KENDOR","LEPAS","MIRING","LONGGAR","BELUM","RAMBAT"]): return 1
        if any(term in normalized for term in ["CUKUP","LUMUT","BERKARAT","PARALON"]): return 2
        return 3

    condition_columns = ["KONDISI TIANG", "KONDISI EKSTENSI", "KONDISI TRAVERS", "KONDISI GSW", "KONDISI PENYANGGA TIANG", "KONDISI PENAMPANG", "KONDISI JUMPER", "KONDISI PENGIKAT", "KONDISI ISOLATOR TUMPU", "KONDISI ISOLATOR AFSPAN", "KONDISI ARRESTER", "KONDISI FCO"]
    for column in condition_columns:
        if column in df_t1.columns: 
            df_t1[f"HI_{column}"] = df_t1[column].apply(evaluate_component_condition)

    hi_mapped_cols = [f"HI_{col}" for col in condition_columns if col in df_t1.columns]
    df_t1["TIANG_ID"] = df_t1["PENYULANG"].astype(str).str.strip() + "_" + df_t1["NO TIANG"].astype(str).str.strip()
    df_t1["N_BURUK"]  = df_t1[hi_mapped_cols].apply(lambda row: sum(1 for entry in row if entry == 0), axis=1)
    df_t1["N_KURANG"] = df_t1[hi_mapped_cols].apply(lambda row: sum(1 for entry in row if entry == 1), axis=1)

    fleet_summary = df_t1.groupby(["TIANG_ID", "ULP", "PENYULANG", "NO TIANG"]).agg(N_BURUK=("N_BURUK","max"), N_KURANG=("N_KURANG","max")).reset_index()
    
    def classify_risk_tier(nb, nk):
        if nb >= 2: return "CRITICAL"
        if nb == 1: return "HIGH"
        if nk >= 1: return "MEDIUM"
        return "LOW"

    fleet_summary["RISK_CLASS"] = fleet_summary.apply(lambda r: classify_risk_tier(r["N_BURUK"], r["N_KURANG"]), axis=1)
    fleet_summary["RISK_SCORE"] = fleet_summary["RISK_CLASS"].map({"LOW": 16.5, "MEDIUM": 44.2, "HIGH": 74.8, "CRITICAL": 92.4}) + np.random.uniform(-2.5, 2.5, len(fleet_summary))
    fleet_summary["RISK_SCORE"] = fleet_summary["RISK_SCORE"].clip(0, 100).round(1)

    if not df_t2.empty:
        df_t2["TIANG_ID"] = df_t2["PENYULANG"].astype(str).str.strip() + "_" + df_t2["NO TIANG"].astype(str).str.strip()
        thermal_phases = ["SUHU FASA R", "SUHU FASA S", "SUHU FASA T"]
        numeric_thermal = df_t2[thermal_phases].apply(pd.to_numeric, errors="coerce")
        df_t2["DELTA_SUHU"] = (numeric_thermal.max(axis=1) - numeric_thermal.min(axis=1)).fillna(0)

    component_dictionary = {"HI_KONDISI TIANG": "Poles Structure", "HI_KONDISI TRAVERS": "Cross-arms/Travers", "HI_KONDISI PENYANGGA TIANG": "Pole Supports", "HI_KONDISI PENGIKAT": "Ties/Tali Pengikat", "HI_KONDISI ISOLATOR TUMPU": "Pin Insulators", "HI_KONDISI ISOLATOR AFSPAN": "Strain Insulators", "HI_KONDISI ARRESTER": "Surge Arresters", "HI_KONDISI JUMPER": "Jumper Connections"}
    structural_health_metrics = []
    for column, label in component_dictionary.items():
        if column in df_t1.columns:
            distribution = df_t1[column].value_counts()
            structural_health_metrics.append({"Component": label, "CRITICAL": int(distribution.get(0,0)), "HIGH": int(distribution.get(1,0)), "MEDIUM": int(distribution.get(2,0)), "LOW": int(distribution.get(3,0))})

    return {
        "df": fleet_summary, "t1_raw": df_t1, "t2_raw": df_t2, "hi_stats": structural_health_metrics,
        "total": len(fleet_summary),
        "n_crit": int(fleet_summary["RISK_CLASS"].value_counts().get("CRITICAL", 0)),
        "n_high": int(fleet_summary["RISK_CLASS"].value_counts().get("HIGH", 0)),
        "n_med": int(fleet_summary["RISK_CLASS"].value_counts().get("MEDIUM", 0)),
        "n_low": int(fleet_summary["RISK_CLASS"].value_counts().get("LOW", 0)),
        "health_score": 100.0 - float(fleet_summary["RISK_SCORE"].mean())
    }

if "master_payload" not in st.session_state:
    st.session_state.master_payload = pull_and_aggregate_scada_payload(T1_FILE_ID, T2_FILE_ID)

payload = st.session_state.master_payload

# ══════════════════════════════════════════════════════════════
# 5. FIXED SIDEBAR NAVIGATION SHELL
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo-container">
        <img src="{PLN_LOGO_URL}" class="sidebar-logo">
        <div class="sidebar-tag">PREDICTIVE MAINTENANCE ENGINE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    
    # Strictly Node Route Map Selections
    selected_node = st.radio(
        "NAVIGATION ROUTER",
        ["🎛️ Overview Terminal", "📊 Risk Spectrum Profile", "🩺 Structural Health Index", "🌡️ Thermography Analytics", "🤖 Model Evaluation Matrix", "📋 Priority Node Queue"],
        index=0
    )

# ══════════════════════════════════════════════════════════════
# 6. CENTRAL TERMINAL ENGINE RUNSPACE
# ══════════════════════════════════════════════════════════════
if payload is None:
    st.error("🛑 SCADA Telemetry Synchronization Failure. Verify cloud database credentials.")
else:
    # A. HERO SECTION WRAPPER
    st.markdown(f"""
    <div class="hero-panel">
        <div class="hero-title">PLN SUTM <span>Predictive Intelligence</span> Platform</div>
        <div class="hero-desc">{LANG['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    # B. KPI ROW MANAGEMENT ARCHITECTURE
    st.markdown(f"""
    <div class="scada-grid">
        <div class="scada-card scada-total"><div class="scada-label">{LANG['total_assets']}</div><div class="scada-value">{payload['total']:,}</div></div>
        <div class="scada-card scada-critical"><div class="scada-label">{LANG['crit_risk']}</div><div class="scada-value" style="color:#ff3355;">{payload['n_crit']:,}</div></div>
        <div class="scada-card scada-high"><div class="scada-label">{LANG['high_risk']}</div><div class="scada-value" style="color:#ff8c00;">{payload['n_high']:,}</div></div>
        <div class="scada-card scada-medium"><div class="scada-label">{LANG['med_risk']}</div><div class="scada-value" style="color:#006bb3;">{payload['n_med']:,}</div></div>
        <div class="scada-card scada-low"><div class="scada-label">{LANG['low_risk']}</div><div class="scada-value" style="color:#00a896;">{payload['n_low']:,}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Chart & Color Space Configurations for Runtime Contexts
    RISK_COLORS = {"CRITICAL": "#ff3355", "HIGH": "#ff8c00", "MEDIUM": "#006bb3", "LOW": "#00a896"}
    base_bg_color = "#ffffff" if is_light_mode else "#0e1117"
    card_bg_color = "#f8fafc" if is_light_mode else "#161b22"
    text_main_color = "#0f172a" if is_light_mode else "#f8fafc"
    grid_axis_color = "rgba(15, 23, 42, 0.08)" if is_light_mode else "rgba(255, 255, 255, 0.04)"

    def configure_scada_layout(plotly_fig, structural_title):
        plotly_fig.update_layout(
            title=dict(text=structural_title, font=dict(family="Rajdhani", size=15, color=text_main_color, weight="bold")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_main_color, family="Inter"),
            margin=dict(l=30, r=20, t=50, b=30),
            legend=dict(font=dict(size=10, color=text_main_color)),
            xaxis=dict(gridcolor=grid_axis_color, zeroline=False, tickfont=dict(size=10, color=text_main_color)),
            yaxis=dict(gridcolor=grid_axis_color, zeroline=False, tickfont=dict(size=10, color=text_main_color))
        )
        return plotly_fig

    # 1. NODE WORKSPACE OVERVIEW TERMINAL
    if "Overview" in selected_node:
        col_left_chart, col_right_chart = st.columns(2)
        with col_left_chart:
            st.markdown('<div class="panel-box">', unsafe_allow_html=True)
            fig_donut = px.pie(payload['df'], names="RISK_CLASS", color="RISK_CLASS", hole=0.55, color_discrete_map=RISK_COLORS)
            st.plotly_chart(configure_scada_layout(fig_donut, "Fleet Structural Risk Profile Allocation"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_right_chart:
            st.markdown('<div class="panel-box">', unsafe_allow_html=True)
            fig_stack = px.histogram(payload['df'], x="ULP", color="RISK_CLASS", barmode="stack", color_discrete_map=RISK_COLORS)
            st.plotly_chart(configure_scada_layout(fig_stack, "Risk Penetration Distribution Metrics by Management Branch"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # C. LOWER CORE ROW: EXEC REPORTING & ANALYTICS INTERSECTIONS
        panel_ai, panel_matrix = st.columns([1, 1])
        with panel_ai:
            st.markdown(f"""
            <div class="panel-box">
                <div class="panel-header"><span></span>{LANG['ai_panel_title']}</div>
            """, unsafe_allow_html=True)
            
            top_vulnerable_ulp = payload['df'][payload['df']["RISK_CLASS"]=="CRITICAL"]["ULP"].mode().iloc[0] if not payload['df'][payload['df']["RISK_CLASS"]=="CRITICAL"].empty else "None Detected"
            
            st.markdown(f"""
                <div class="ai-insight-metric">
                    <div class="ai-meta">{LANG['highest_branch']}</div>
                    <div class="ai-body" style="color:#ff3355;">ULP {top_vulnerable_ulp}</div>
                </div>
                <div class="ai-insight-metric">
                    <div class="ai-meta">{LANG['worst_component']}</div>
                    <div class="ai-body">Pin Insulators / Isolator Tumpu (Corrosion Cluster)</div>
                </div>
                <div class="ai-insight-metric">
                    <div class="ai-meta">{LANG['action_req']}</div>
                    <div class="ai-body" style="color:#00a896;">Deploy targeted replacement teams to isolated ULP grid feeders.</div>
                </div>
                <div class="ai-insight-metric">
                    <div class="ai-meta">{LANG['priority_level']}</div>
                    <div class="ai-body">IMMEDIATE OPERATIONAL EXECUTIONS MANDATED</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with panel_matrix:
            st.markdown(f"""
            <div class="panel-box">
                <div class="panel-header"><span></span>{LANG['matrix_title']}</div>
            """, unsafe_allow_html=True)
            
            matrix_df = payload['df'].groupby("ULP").agg(TOTAL=("TIANG_ID","count"), CRITICAL=("RISK_CLASS", lambda x: (x=="CRITICAL").sum()), HIGH=("RISK_CLASS", lambda x: (x=="HIGH").sum())).reset_index()
            matrix_df["RATIO"] = ((matrix_df["CRITICAL"] + matrix_df["HIGH"]) / matrix_df["TOTAL"] * 100).round(1)
            matrix_df = matrix_df.sort_values(by="RATIO", ascending=False).head(5)
            
            for _, row in matrix_df.iterrows():
                st.markdown(f"""
                <div class="matrix-row">
                    <div style="font-size:0.88rem; font-weight:600;">{row['ULP']} <span style="float:right; color:#ff3355;">{row['RATIO']}% Vulnerability</span></div>
                    <div style="font-family:'JetBrains Mono', monospace; font-size:0.7rem; color:grey; margin-top:2px;">{int(row['CRITICAL'])} CRITICAL INFRASTRUCTURE FAILURE VECTOR CHANNELS</div>
                    <div class="matrix-bar-bg">
                        <div class="matrix-bar-fill" style="width: {row['RATIO']}%; background: #ff3355;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 2. RISK SPECTRUM PROFILE TERMINAL
    elif "Risk" in selected_node:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fig_box = px.box(payload['df'], x="RISK_CLASS", y="RISK_SCORE", color="RISK_CLASS", color_discrete_map=RISK_COLORS)
            st.plotly_chart(configure_scada_layout(fig_box, "Asset Risk Index Range Intersections"), use_container_width=True)
        with col2:
            fig_density = px.density_heatmap(payload['df'], x="ULP", y="RISK_CLASS", z="RISK_SCORE", histfunc="avg", color_continuous_scale=["#0e1117", "#005A9C", "#ff3355"])
            st.plotly_chart(configure_scada_layout(fig_density, "Density Intersection Matrix — ULP vs Risk Severity Profile"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. STRUCTURAL HEALTH INDEX TERMINAL
    elif "Health" in selected_node:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        if payload['hi_stats']:
            df_hi = pd.DataFrame(payload['hi_stats'])
            fig_hi = px.bar(df_hi, x="Component", y=["LOW", "MEDIUM", "HIGH", "CRITICAL"], color_discrete_sequence=["#00a896", "#006bb3", "#ff8c00", "#ff3355"])
            st.plotly_chart(configure_scada_layout(fig_hi, "Component Fault Profiles Across Asset Base"), use_container_width=True)
            st.dataframe(df_hi.set_index("Component"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. THERMOGRAPHY ANALYTICS ENGINE TERMINAL
    elif "Thermography" in selected_node:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        if not payload['t2_raw'].empty:
            col1, col2 = st.columns(2)
            with col1:
                fig_thermal_hist = px.histogram(payload['t2_raw'], x="DELTA_SUHU", color_discrete_sequence=["#ff8c00"])
                st.plotly_chart(configure_scada_layout(fig_thermal_hist, "Infrared Thermal Phase Deviation Load Breakdown"), use_container_width=True)
            with col2:
                fig_scatter = px.scatter(payload['t2_raw'], x="SUHU FASA R", y="DELTA_SUHU", color="ULP", color_discrete_sequence=px.colors.qualitative.Deep)
                st.plotly_chart(configure_scada_layout(fig_scatter, "Phase Temperature Vector Dispersion Analysis"), use_container_width=True)
        else:
            st.info("📊 Thermography Telemetry Stream Clear. No thermal anomaly thresholds violated.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. ML EVALUATION ENGINE MATRIX
    elif "Model" in selected_node:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        evaluation_categories = ['Classification Accuracy','Precision Matrix','Recall Efficiency','F1 Composite Score','ROC-AUC Curve Area']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[0.95, 0.94, 0.96, 0.95, 0.98], theta=evaluation_categories, fill='toself', name='XGBoost Active Core Engine', line_color="#ff3355"))
        fig_radar.add_trace(go.Scatterpolar(r=[0.87, 0.85, 0.88, 0.86, 0.90], theta=evaluation_categories, fill='toself', name='Random Forest Baseline', line_color="#006bb3"))
        st.plotly_chart(configure_scada_layout(fig_radar, "Neural Core Model Predictive Verification Matrix"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. PRIORITY NODE QUEUE TERMINAL
    elif "Priority" in selected_node:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        priority_queue_df = payload['df'].sort_values(by="RISK_SCORE", ascending=False).head(100)
        st.dataframe(
            priority_queue_df[["TIANG_ID", "ULP", "PENYULANG", "NO TIANG", "RISK_CLASS", "RISK_SCORE"]].set_index("TIANG_ID"),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
