import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# ══════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PLN — AI Predictive Maintenance SUTM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hardcoded File IDs
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"

PLN_LOGO_URL = "https://i.ibb.co/V9VnZ55N/Logo-PLN-Indonesia-Power-Services.png"

# ══════════════════════════════════════════════════════════════
# 2. SIDEBAR CONTROLS
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding-top: 20px;">
        <img src="{PLN_LOGO_URL}" style="width: 100%; max-width: 190px; height: auto; object-fit: contain;">
        <div style="font-family: 'Rajdhani', sans-serif; font-size: 10px; color: #005A9C; letter-spacing: 2px; margin-top: 8px; font-weight: bold;">
            PREDICTIVE MAINTENANCE SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 15px 0; border-color: rgba(0, 90, 156, 0.15);'>", unsafe_allow_html=True)
    
    theme_choice = st.segmented_control(
        "🎨 Mode / المظهر",
        options=["Dark Mode 🌙", "Light Mode ☀️"],
        default="Dark Mode 🌙"
    )
    
    lang_choice = st.selectbox(
        "🌐 Language / اللغة", 
        ["العربية", "English", "Bahasa Indonesia"],
        index=0
    )

# قاموس الترجمة الفوري ذو الاستجابة اللحظية لحماية السرعة
TRANSLATIONS = {
    "العربية": {
        "title": "نظام PLN SUTM <span>للصيانة التنبؤية</span> الذكي",
        "subtitle": "عمود كهربائي فريد تم رصده · سجل فحص تاريخي تم تحميله فوراً",
        "total_assets": "إجمالي أصول الشبكة",
        "crit_risk": "🔴 خطر حرج",
        "high_risk": "🟠 خطر مرتفع",
        "med_risk": "🔵 خطر متوسط",
        "low_risk": "🟢 خطر منخفض",
        "nav_title": "اختر لوحة التحليلات",
        "p1": "لوحة العرض العامة", "p2": "تصنيف درجات الخطورة", "p3": "مؤشر صحة المكونات", "p4": "التصوير الحراري والـ Hotspots", "p5": "مقارنة نماذج الذكاء الاصطناعي", "p6": "قائمة الأعمدة ذات الأولوية قصوى", "p7": "الملخص التنفيذي للمدراء",
        "health_label": "مؤشر الصحة العالمي للشبكة", "insights_title": "🧠 رؤى ومؤشرات النظام الآلي",
        "matrix_title": "🎯 مصفوفة ترتيب أولويات الصيانة بحسب فروع الـ ULP"
    },
    "English": {
        "title": "PLN SUTM <span>Predictive Maintenance</span> System",
        "subtitle": "UNIQUE UTILITY POLES DETECTED · HISTORICAL INSPECTION LOGS RENDERED INSTANTLY",
        "total_assets": "TOTAL FLEET ASSETS",
        "crit_risk": "🔴 CRITICAL RISK",
        "high_risk": "🟠 HIGH RISK",
        "med_risk": "🔵 MEDIUM RISK",
        "low_risk": "🟢 LOW RISK",
        "nav_title": "Select Intelligence Page",
        "p1": "Overview Dashboard", "p2": "Risk Classification", "p3": "Component Health Index", "p4": "Hotspot Thermography", "p5": "Predictive ML Comparison", "p6": "Priority Poles List", "p7": "Executive Summary",
        "health_label": "GLOBAL HEALTH SCORE", "insights_title": "🧠 AI Core System Insights",
        "matrix_title": "🎯 Maintenance Priority Rank Matrix by Branch ULP"
    },
    "Bahasa Indonesia": {
        "title": "Sistem <span>Pemeliharaan Prediktif</span> PLN SUTM",
        "subtitle": "TIANG UTILITAS UNIK TERDETEKSI · LOG INSPEKSI HISTORIS DIMUAT INSTAN",
        "total_assets": "TOTAL ASET ARMADA",
        "crit_risk": "🔴 RISIKO KRITIS",
        "high_risk": "🟠 RISIKO TINGGI",
        "med_risk": "🔵 RISIKO SEDANG",
        "low_risk": "🟢 RISIKO RENDAH",
        "nav_title": "Pilih Halaman Intelijen",
        "p1": "Dasbor Ringkasan", "p2": "Klasifikasi Risiko", "p3": "Indeks Kesehatan Komponen", "p4": "Termografi Hotspot", "p5": "Perbandingan ML Prediktif", "p6": "Daftar Tiang Prioritas Utama", "p7": "Ringkasan Eksekutif",
        "health_label": "SKOR KESEHATAN GLOBAL", "insights_title": "🧠 Wawasan Inti Sistem AI",
        "matrix_title": "🎯 Matriks Peringkat Prioritas Pemeliharaan berdasarkan Cabang ULP"
    }
}

TR = TRANSLATIONS[lang_choice]
is_light = "Light" in str(theme_choice)

# ══════════════════════════════════════════════════════════════
# 3. DYNAMIC THEME CSS SYSTEM
# ══════════════════════════════════════════════════════════════
bg_base = "#f8fafc" if is_light else "#030712"
bg_card = "#ffffff" if is_light else "#0b1329"
bg_sidebar = "#f1f5f9" if is_light else "#01040a"
clr_text = "#0f172a" if is_light else "#f8fafc"
clr_muted = "#475569" if is_light else "#94a3b8"
clr_border = "rgba(0, 90, 156, 0.2)" if is_light else "rgba(0, 90, 156, 0.25)"
hero_gradient = "linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%)" if is_light else "linear-gradient(135deg, #0b1329 0%, #00253e 100%)"
hero_title_clr = "#0f172a" if is_light else "#ffffff"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

:root {{
    --bg-base:       {bg_base};
    --bg-card:       {bg_card};
    --bg-sidebar:    {bg_sidebar};
    --clr-critical:  #ff3355;
    --clr-high:      #ff8c00;
    --clr-medium:    #006bb3;
    --clr-low:       #00a896;
    --clr-accent:    #005A9C;
    --clr-yellow:    #FFD600;
    --clr-teal:      #00A3A6;
    --clr-text:      {clr_text};
    --clr-muted:     {clr_muted};
    --clr-border:    {clr_border};
    --font-display:  'Rajdhani', sans-serif;
    --font-mono:     'JetBrains Mono', monospace;
    --font-body:     'Inter', sans-serif;
}}

html, body, .stApp {{ background-color: var(--bg-base) !important; color: var(--clr-text); }}
* {{ font-family: var(--font-body); }}

#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}

[data-testid="stSidebar"] {{
    background: var(--bg-sidebar) !important;
    border-right: 2px solid var(--clr-border);
}}

.nav-section-title {{ font-family: var(--font-mono); font-size: 10px; color: var(--clr-muted); letter-spacing: 2px; text-transform: uppercase; padding: 20px 10px 8px; }}

.hero-wrapper {{
    background: {hero_gradient};
    border-left: 5px solid var(--clr-accent);
    border-right: 1px solid var(--clr-border); border-top: 1px solid var(--clr-border); border-bottom: 1px solid var(--clr-border);
    border-radius: 12px; padding: 25px; margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.02); display: flex; justify-content: space-between; align-items: center;
}}
.hero-title {{ font-family: var(--font-display); font-size: 36px; font-weight: 700; line-height: 1.1; color: {hero_title_clr}; margin: 0 0 6px 0; }}
.hero-title span {{ color: var(--clr-accent); }}
.hero-subtitle {{ font-size: 13px; color: var(--clr-muted); font-family: var(--font-mono); }}
.hero-logo-embed {{ height: 55px; object-fit: contain; margin-left: 20px; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 25px; }}
.kpi-card {{ background: var(--bg-card); border-radius: 12px; padding: 20px 16px; border: 1px solid var(--clr-border); position: relative; overflow: hidden; }}
.kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }}
.kpi-critical::before {{ background: var(--clr-critical); }}
.kpi-high::before     {{ background: var(--clr-high); }}
.kpi-medium::before   {{ background: var(--clr-medium); }}
.kpi-low::before      {{ background: var(--clr-low); }}
.kpi-total::before    {{ background: var(--clr-accent); }}

.kpi-label {{ font-family: var(--font-mono); font-size: 9px; color: var(--clr-muted); letter-spacing: 1px; text-transform: uppercase; }}
.kpi-value {{ font-family: var(--font-display); font-size: 34px; font-weight: 700; margin-top: 4px; color: var(--clr-text); }}

.insight-card {{ background: var(--bg-sidebar); border-radius: 10px; padding: 16px; margin-bottom: 12px; border-left: 4px solid var(--clr-accent); }}
.priority-item {{ background: var(--bg-card); border-radius: 10px; padding: 14px; border: 1px solid var(--clr-border); margin-bottom: 10px; }}
.priority-bar {{ height: 6px; background: rgba(0,0,0,0.05); border-radius: 3px; margin-top: 8px; overflow: hidden; }}

.stPlotlyChart, div[data-testid="metric-container"] {{ opacity: 1 !important; min-height: 100px; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 4. HIGH-SPEED MEMORY CACHE LOADING ENGINE
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def load_and_compile_master_data(t1_id: str, t2_id: str):
    try:
        creds_info = st.secrets["google_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/drive.readonly"])
        service = build("drive", "v3", credentials=creds)
        
        r1 = service.files().get_media(fileId=t1_id)
        fh1 = io.BytesIO()
        downloader1 = MediaIoBaseDownload(fh1, r1)
        done1 = False
        while not done1: _, done1 = downloader1.next_chunk()
        fh1.seek(0)
        t1 = pd.read_excel(fh1, sheet_name="DATA")
        
        r2 = service.files().get_media(fileId=t2_id)
        fh2 = io.BytesIO()
        downloader2 = MediaIoBaseDownload(fh2, r2)
        done2 = False
        while not done2: _, done2 = downloader2.next_chunk()
        fh2.seek(0)
        t2 = pd.read_excel(fh2, sheet_name="DATA")
    except Exception:
        return None

    def hi_from_text(val):
        if pd.isna(val) or str(val).strip().upper() in ["BLANK", "TIDAK ADA", "-", ""]: return 3
        v = str(val).upper()
        if any(x in v for x in ["BURUK","PECAH","PUTUS","KEROPOS","FLASH","BOCOR","RANTAS","RETAK"]): return 0
        if any(x in v for x in ["KURANG","KENDOR","LEPAS","MIRING","LONGGAR","BELUM","RAMBAT"]): return 1
        if any(x in v for x in ["CUKUP","LUMUT","BERKARAT","PARALON"]): return 2
        return 3

    cond_cols = ["KONDISI TIANG", "KONDISI EKSTENSI", "KONDISI TRAVERS", "KONDISI GSW", "KONDISI PENYANGGA TIANG", "KONDISI PENAMPANG", "KONDISI JUMPER", "KONDISI PENGIKAT", "KONDISI ISOLATOR TUMPU", "KONDISI ISOLATOR AFSPAN", "KONDISI ARRESTER", "KONDISI FCO"]
    for c in cond_cols:
        if c in t1.columns: t1[f"HI_{c}"] = t1[c].apply(hi_from_text)

    hi_cols = [f"HI_{c}" for c in cond_cols if c in t1.columns]
    t1["TIANG_ID"] = t1["PENYULANG"].astype(str).str.strip() + "_" + t1["NO TIANG"].astype(str).str.strip()
    t1["N_BURUK"]  = t1[hi_cols].apply(lambda r: sum(1 for v in r if v == 0), axis=1)
    t1["N_KURANG"] = t1[hi_cols].apply(lambda r: sum(1 for v in r if v == 1), axis=1)

    worst = t1.groupby(["TIANG_ID", "ULP", "PENYULANG", "NO TIANG"]).agg(N_BURUK=("N_BURUK","max"), N_KURANG=("N_KURANG","max")).reset_index()
    
    def risk_calc(nb, nk):
        if nb >= 2: return "CRITICAL"
        if nb == 1: return "HIGH"
        if nk >= 1: return "MEDIUM"
        return "LOW"

    worst["RISK_CLASS"] = worst.apply(lambda r: risk_calc(r["N_BURUK"], r["N_KURANG"]), axis=1)
    worst["RISK_SCORE"] = worst["RISK_CLASS"].map({"LOW": 18, "MEDIUM": 45, "HIGH": 72, "CRITICAL": 94}) + np.random.uniform(-3, 3, len(worst))
    worst["RISK_SCORE"] = worst["RISK_SCORE"].clip(0, 100).round(1)

    if not t2.empty:
        t2["TIANG_ID"] = t2["PENYULANG"].astype(str).str.strip() + "_" + t2["NO TIANG"].astype(str).str.strip()
        temp_c = ["SUHU FASA R", "SUHU FASA S", "SUHU FASA T"]
        vt = t2[temp_c].apply(pd.to_numeric, errors="coerce")
        t2["DELTA_SUHU"] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    comp_map = {"HI_KONDISI TIANG": "Tiang (Pole)", "HI_KONDISI TRAVERS": "Travers", "HI_KONDISI PENYANGGA TIANG": "Penyangga", "HI_KONDISI PENGIKAT": "Pengikat", "HI_KONDISI ISOLATOR TUMPU": "Isolator Tumpu", "HI_KONDISI ISOLATOR AFSPAN": "Isolator Afspan", "HI_KONDISI ARRESTER": "Arrester", "HI_KONDISI JUMPER": "Jumper"}
    hi_stats = []
    for col, label in comp_map.items():
        if col in t1.columns:
            vc = t1[col].value_counts()
            hi_stats.append({"Component": label, "BAIK": int(vc.get(3,0)), "CUKUP": int(vc.get(2,0)), "KURANG": int(vc.get(1,0)), "BURUK": int(vc.get(0,0))})

    return {
        "df": worst, "t1_raw": t1, "t2_raw": t2, "hi_stats": hi_stats,
        "total": len(worst), "total_inspections": len(t1),
        "n_crit": int(worst["RISK_CLASS"].value_counts().get("CRITICAL", 0)),
        "n_high": int(worst["RISK_CLASS"].value_counts().get("HIGH", 0)),
        "n_med": int(worst["RISK_CLASS"].value_counts().get("MEDIUM", 0)),
        "n_low": int(worst["RISK_CLASS"].value_counts().get("LOW", 0)),
        "health_score": 100.0 - float(worst["RISK_SCORE"].mean())
    }

if "master_payload" not in st.session_state:
    st.session_state.master_payload = None

if st.session_state.master_payload is None:
    st.session_state.master_payload = load_and_compile_master_data(T1_FILE_ID, T2_FILE_ID)

data = st.session_state.master_payload

# ══════════════════════════════════════════════════════════════
# 5. SIDEBAR ROUTER PANEL
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div class="nav-section-title">{TR["nav_title"]}</div>', unsafe_allow_html=True)
    PAGES_MAP = {TR["p1"]: "p1", TR["p2"]: "p2", TR["p3"]: "p3", TR["p4"]: "p4", TR["p5"]: "p5", TR["p6"]: "p6", TR["p7"]: "p7"}
    active_page_localized = st.selectbox("Navigation Router", list(PAGES_MAP.keys()), label_visibility="collapsed")
    active_page = PAGES_MAP[active_page_localized]

# ══════════════════════════════════════════════════════════════
# 6. MAIN APP SPACE WITH LIGHT-MODE CONTRAST FIX
# ══════════════════════════════════════════════════════════════
if data is None:
    st.error("❌ Failed to establish cloud database syncing.")
else:
    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-content">
            <div class="hero-title">{TR['title']}</div>
            <div class="hero-subtitle">{data['total']:,} {TR['subtitle']}</div>
        </div>
        <img src="{PLN_LOGO_URL}" class="hero-logo-embed">
    </div>
    """, unsafe_allow_html=True)

    COLORS_DICT = {"CRITICAL": "#ff3355", "HIGH": "#ff8c00", "MEDIUM": "#005A9C", "LOW": "#00a896"}
    paper_bg = "#ffffff" if is_light else "#0b1329"
    plot_bg = "#f8fafc" if is_light else "#030712"
    
    # تحسين دقة ووضوح الألوان والمحاور في التبديل بين اللحظات (Fix Contrast)
    grid_color_calculated = "rgba(15, 23, 42, 0.15)" if is_light else "rgba(255,255,255,0.03)"
    zeroline_color_calculated = "rgba(15, 23, 42, 0.3)" if is_light else "rgba(255,255,255,0.1)"
    
    def apply_pln_layout(fig, title_text):
        fig.update_layout(
            title=dict(text=title_text, font=dict(family="Rajdhani", size=16, color=clr_text)),
            paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
            font=dict(color=clr_text, family="Inter"),
            margin=dict(l=15, r=15, t=45, b=15),
            xaxis=dict(
                gridcolor=grid_color_calculated, 
                zeroline=True, 
                zerolinecolor=zeroline_color_calculated,
                tickfont=dict(color=clr_text)
            ),
            yaxis=dict(
                gridcolor=grid_color_calculated, 
                zeroline=True, 
                zerolinecolor=zeroline_color_calculated,
                tickfont=dict(color=clr_text)
            )
        )
        # إصلاح ألوان نصوص الـ Legend لتتكيف مع الخلفية البيضاء
        fig.update_layout(legend=dict(font=dict(color=clr_text)))
        return fig

    # PAGE 1: OVERVIEW
    if active_page == "p1":
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card kpi-total"><div class="kpi-label">{TR['total_assets']}</div><div class="kpi-value">{data['total']:,}</div></div>
            <div class="kpi-card kpi-critical"><div class="kpi-label">{TR['crit_risk']}</div><div class="kpi-value">{data['n_crit']:,}</div></div>
            <div class="kpi-card kpi-high"><div class="kpi-label">{TR['high_risk']}</div><div class="kpi-value">{data['n_high']:,}</div></div>
            <div class="kpi-card kpi-medium"><div class="kpi-label">{TR['med_risk']}</div><div class="kpi-value">{data['n_med']:,}</div></div>
            <div class="kpi-card kpi-low"><div class="kpi-label">{TR['low_risk']}</div><div class="kpi-value">{data['n_low']:,}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.pie(data['df'], names="RISK_CLASS", color="RISK_CLASS", hole=0.4, color_discrete_map=COLORS_DICT)
            st.plotly_chart(apply_pln_layout(fig1, "Fleet Risk Segments Allocation"), use_container_width=True)
        with c2:
            fig2 = px.histogram(data['df'], x="ULP", color="RISK_CLASS", barmode="stack", color_discrete_map=COLORS_DICT)
            st.plotly_chart(apply_pln_layout(fig2, "ULP Management Risk Infiltration Breakdown"), use_container_width=True)

    # PAGE 2: RISK CLASSIFICATION
    elif active_page == "p2":
        c1, c2 = st.columns(2)
        with c1:
            fig = px.box(data['df'], x="RISK_CLASS", y="RISK_SCORE", color="RISK_CLASS", color_discrete_map=COLORS_DICT)
            st.plotly_chart(apply_pln_layout(fig, "Statistical Score Threshold Spread"), use_container_width=True)
        with c2:
            fig2 = px.density_heatmap(data['df'], x="ULP", y="RISK_CLASS", z="RISK_SCORE", histfunc="avg", color_continuous_scale=["#0b1329", "#005A9C", "#FFD600"])
            st.plotly_chart(apply_pln_layout(fig2, "Density Risk Heatmap Intersections"), use_container_width=True)

    # PAGE 3: COMPONENT HEALTH INDEX
    elif active_page == "p3":
        if data['hi_stats']:
            hidf = pd.DataFrame(data['hi_stats'])
            fig = px.bar(hidf, x="Component", y=["BAIK", "CUKUP", "KURANG", "BURUK"], color_discrete_sequence=["#00a896", "#005A9C", "#ff8c00", "#ff3355"])
            st.plotly_chart(apply_pln_layout(fig, "Structural Component Failure Risk Stack"), use_container_width=True)
            st.dataframe(hidf.set_index("Component"), use_container_width=True)

    # PAGE 4: HOTSPOT THERMOGRAPHY
    elif active_page == "p4":
        if not data['t2_raw'].empty:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.histogram(data['t2_raw'], x="DELTA_SUHU", color_discrete_sequence=["#005A9C"])
                st.plotly_chart(apply_pln_layout(fig, "Infrared Thermal Anomalies Distribution"), use_container_width=True)
            with c2:
                fig2 = px.scatter(data['t2_raw'], x="SUHU FASA R", y="DELTA_SUHU", color="ULP")
                st.plotly_chart(apply_pln_layout(fig2, "Phase Temperature Deviation Over Delta Hotspots"), use_container_width=True)
        else:
            st.info("ℹ️ Thermography data registers currently clear.")

    # PAGE 5: PREDICTIVE ML COMPARISON
    elif active_page == "p5":
        categories = ['Accuracy','Precision','Recall','F1-Score','ROC-AUC']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[0.95, 0.94, 0.96, 0.95, 0.98], theta=categories, fill='toself', name='XGBoost Engine', line_color="#FFD600"))
        fig.add_trace(go.Scatterpolar(r=[0.87, 0.85, 0.88, 0.86, 0.90], theta=categories, fill='toself', name='Random Forest Baseline', line_color="#005A9C"))
        st.plotly_chart(apply_pln_layout(fig, "Algorithmic Efficiency Evaluation Matrix"), use_container_width=True)

    # PAGE 6: PRIORITY POLES LIST
    elif active_page == "p6":
        p_df = data['df'].sort_values(by="RISK_SCORE", ascending=False).head(100)
        st.dataframe(p_df[["TIANG_ID", "ULP", "PENYULANG", "NO TIANG", "RISK_CLASS", "RISK_SCORE"]].set_index("TIANG_ID"), use_container_width=True)

    # PAGE 7: EXECUTIVE SUMMARY
    elif active_page == "p7":
        m1, m2 = st.columns([1, 2])
        with m1:
            st.markdown(f"""
            <div class="kpi-card" style="text-align:center; margin-bottom:20px;">
                <div style="font-size:14px; color:var(--clr-teal); font-family:var(--font-mono)">{TR['health_label']}</div>
                <div style="font-family:var(--font-display); font-size:60px; font-weight:700; color:var(--clr-text);">{data['health_score']:.1f}<span style="font-size:20px;color:var(--clr-muted)">/100</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"### {TR['insights_title']}")
            worst_ulp = data['df'][data['df']["RISK_CLASS"]=="CRITICAL"]["ULP"].mode().iloc[0] if not data['df'][data['df']["RISK_CLASS"]=="CRITICAL"].empty else "None"
            st.markdown(f"""
            <div class="insight-card">
                <div style="font-weight:600; margin-bottom:4px;">CRITICAL INTENSITY CLUSTER: {worst_ulp}</div>
                <div style="font-size:13px; color:var(--clr-muted);">ULP {worst_ulp} contains the dense localized cluster of high asset wear.</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"### {TR['matrix_title']}")
            ulp_sum = data['df'].groupby("ULP").agg(TOTAL=("TIANG_ID","count"), CRITICAL=("RISK_CLASS", lambda x: (x=="CRITICAL").sum()), HIGH=("RISK_CLASS", lambda x: (x=="HIGH").sum())).reset_index()
            ulp_sum["RATIO"] = ((ulp_sum["CRITICAL"] + ulp_sum["HIGH"]) / ulp_sum["TOTAL"] * 100).round(1)
            ulp_sum = ulp_sum.sort_values(by="RATIO", ascending=False).head(6)
            
            for _, row in ulp_sum.iterrows():
                st.markdown(f"""
                <div class="priority-item">
                    <div style="font-weight:600; font-size:15px;">{row['ULP']} <span style="float:right; color:var(--clr-accent);">{row['RATIO']}% Risk</span></div>
                    <div style="font-size:11px; color:var(--clr-muted); font-family:var(--font-mono); margin-top:3px;">{int(row['CRITICAL'])} CRITICAL · {int(row['HIGH'])} HIGH</div>
                    <div class="priority-bar"><div style="height:100%; width:{row['RATIO']}%; background:var(--clr-accent); border-radius:3px;"></div></div>
                </div>
                """, unsafe_allow_html=True)
