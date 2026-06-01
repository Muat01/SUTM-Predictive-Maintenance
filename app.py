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
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Predictive Maintenance — SUTM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Constants
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"

# Initialize Session States
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"
if "lang_mode" not in st.session_state:
    st.session_state.lang_mode = "English"

# ══════════════════════════════════════════════════════════════
# DYNAMIC CSS ENGINE (Light & Dark Theme)
# ══════════════════════════════════════════════════════════════
if st.session_state.theme_mode == "light":
    theme_css = """
    :root {
        --bg-base:       #f8fafc;
        --bg-card:       #ffffff;
        --bg-card2:      #f1f5f9;
        --bg-sidebar:    #ffffff;
        --clr-critical:  #e11d48;
        --clr-high:      #ea580c;
        --clr-medium:    #0284c7;
        --clr-low:       #16a34a;
        --clr-accent:    #2563eb;
        --clr-text:      #0f172a;
        --clr-muted:     #64748b;
        --clr-border:    rgba(15,23,42,0.08);
        --table-row-even:#f8fafc;
        --table-row-hover:#f1f5f9;
    }
    """
    PLOT_BG  = "#ffffff"
    PAPER_BG = "#f8fafc"
    FONT_COL = "#0f172a"
    GRID_COL = "rgba(15,23,42,0.05)"
else:
    theme_css = """
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
        --table-row-even:#101422;
        --table-row-hover:#161b30;
    }
    """
    PLOT_BG  = "#0c0f1a"
    PAPER_BG = "#060810"
    FONT_COL = "#e2e8f0"
    GRID_COL = "rgba(255,255,255,0.04)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

{theme_css}

/* Base Framework Rules */
html, body, .stApp {{ background-color: var(--bg-base) !important; color: var(--clr-text); font-family: 'Inter', sans-serif; }}

/* Hide Streamlit Headers/Footers */
#MainMenu, footer, header {{ visibility: hidden; display: none !important; }}
.stDeployButton {{ display: none; }}

/* Responsive Navigation Container */
[data-testid="stSidebar"] {{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--clr-border);
}}

/* High-Resolution PLN Logo Integration */
.sidebar-header {{
    padding: 20px;
    border-bottom: 1px solid var(--clr-border);
    display: flex;
    align-items: center;
    gap: 12px;
}}
.brand-logo-svg {{
    width: 32px;
    height: 42px;
    flex-shrink: 0;
}}
.brand-text-main {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--clr-text);
    line-height: 1.1;
}}
.brand-text-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: var(--clr-muted);
    letter-spacing: 0.5px;
}}

/* Hero Dynamic Visibility Container */
.hero-wrapper {{
    background: linear-gradient(135deg, var(--bg-base) 0%, var(--bg-card) 60%, var(--bg-card2) 100%);
    border: 1px solid var(--clr-border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}}
.hero-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: var(--clr-text);
    margin: 0 0 8px 0;
}}
.hero-desc {{
    font-size: 14px;
    color: var(--clr-muted);
    line-height: 1.5;
}}

/* Responsive KPI Container Layout */
.kpi-container-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}}
.kpi-card-box {{
    background: var(--bg-card);
    border: 1px solid var(--clr-border);
    border-radius: 8px;
    padding: 16px;
    border-left: 4px solid var(--clr-accent);
}}
.kpi-card-box.crit {{ border-left-color: var(--clr-critical); }}
.kpi-card-box.high {{ border-left-color: var(--clr-high); }}
.kpi-card-box.med  {{ border-left-color: var(--clr-medium); }}
.kpi-card-box.low  {{ border-left-color: var(--clr-low); }}

.kpi-card-lbl {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--clr-muted); text-transform: uppercase; }}
.kpi-card-val {{ font-family: 'Rajdhani', sans-serif; font-size: 28px; font-weight: 700; color: var(--clr-text); margin-top: 4px; }}

/* Section Titles with SVG Icons */
.section-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 24px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--clr-border);
}}
.section-title {{ font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 600; color: var(--clr-text); text-transform: uppercase; }}

/* Advanced DataFrame Overrides */
div[data-testid="stDataFrameResizable"] {{
    border: 1px solid var(--clr-border) !important;
    border-radius: 8px !important;
    background-color: var(--bg-card) !important;
}}
.stDataFrame tr:nth-child(even) {{ background-color: var(--table-row-even) !important; }}
.stDataFrame tr:hover {{ background-color: var(--table-row-hover) !important; }}

/* Vectors SVG Icons styling */
.svg-icon-pack {{ width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; display: inline-block; vertical-align: middle; }}
.svg-crit {{ color: var(--clr-critical); }}
.svg-high {{ color: var(--clr-high); }}
.svg-med  {{ color: var(--clr-medium); }}
.svg-low  {{ color: var(--clr-low); }}
.svg-acc  {{ color: var(--clr-accent); }}
</style>
""", unsafe_allow_html=True)

# Helper function to supply clean professional vector graphics instead of emojis
def render_vector_icon(style_class, icon_type="info"):
    if icon_type == "alert":
        return f'<svg class="svg-icon-pack {style_class}" viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    elif icon_type == "activity":
        return f'<svg class="svg-icon-pack {style_class}" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    elif icon_type == "list":
        return f'<svg class="svg-icon-pack {style_class}" viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>'
    return f'<svg class="svg-icon-pack {style_class}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'

# Chart Responsiveness Base Setup
def adjust_chart_theme(fig, chart_title=""):
    fig.update_layout(
        title=dict(text=chart_title.upper() if chart_title else "", font=dict(family="Rajdhani", size=14, color=FONT_COL, weight="bold")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COL, family="Inter", size=11),
        margin=dict(l=40, r=20, t=50 if chart_title else 20, b=40),
        xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zeroline=False),
        yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zeroline=False),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# DATA DICTIONARIES (Arabic, English, Indonesian)
# ══════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "English": {
        "hero_title": "Predictive Maintenance Control Terminal",
        "hero_desc": "Enterprise Artificial Intelligence suite processing multi-spectral inspection metrics and distribution asset variables across the SUTM medium voltage grid infrastructure.",
        "kpi_total": "Total Poles Monitored", "kpi_crit": "Critical Risk Nodes", "kpi_high": "High Risk Severity", "kpi_med": "Medium Status Risk", "kpi_low": "Nominal Health Base",
        "sec_overview": "Global Network Overview", "sec_details": "Granular Inspection Records Table",
        "chart_proportional": "Proportional Fleet Classification Breakdown", "chart_density": "Asset Density Distribution Over Risk Scores"
    },
    "العربية": {
        "hero_title": "محطة التحكم في الصيانة التنبؤية",
        "hero_desc": "نظام ذكاء اصطناعي متكامل لمعالجة مقاييس الفحص متعدد الأطياف ومتغيرات أصول التوزيع عبر البنية التحتية لشبكة الجهد المتوسط SUTM.",
        "kpi_total": "إجمالي الأعمدة المراقبة", "kpi_crit": "عقد الخطورة الحرجة", "kpi_high": "شدة الخطورة العالية", "kpi_med": "الخطورة المتوسطة", "kpi_low": "الوضع الطبيعي الآمن",
        "sec_overview": "نظرة عامة على الشبكة العالمية", "sec_details": "جدول سجلات الفحص التفصيلي الدقيق",
        "chart_proportional": "التوزيع النسبي لتصنيفات الأصول", "chart_density": "كثافة توزيع الأصول وفقاً لدرجات الخطورة"
    },
    "Bahasa Indonesia": {
        "hero_title": "Terminal Kontrol Pemeliharaan Prediktif",
        "hero_desc": "Rangkaian Kecerdasan Buatan perusahaan memproses metrik inspeksi multi-spektral dan variabel aset distribusi di seluruh infrastruktur jaringan tegangan menengah SUTM.",
        "kpi_total": "Total Tiang Dipantau", "kpi_crit": "Node Risiko Kritis", "kpi_high": "Tingkat Risiko Tinggi", "kpi_med": "Risiko Status Sedang", "kpi_low": "Kesehatan Basis Nominal",
        "sec_overview": "Ikhtisar Jaringan Global", "sec_details": "Tabel Catatan Inspeksi Granular",
        "chart_proportional": "Kerusakan Klasifikasi Armada Proporsional", "chart_density": "Distribusi Kepadatan Aset Berdasarkan Skor Risiko"
    }
}

# ══════════════════════════════════════════════════════════════
# MOCKING PIPELINE CORE ENGINE (Matches app (1).py formulas exactly)
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def generate_scada_payload():
    np.random.seed(42)
    rows = 120
    ulps = ["ULP Bandung Utara", "ULP Bandung Timur", "ULP Bandung Barat", "ULP Ujung Berung"]
    feeders = ["CILIWUNG", "DAGO", "PADALALARANG", "GEDEBAGE", "SOEKARNO"]
    
    mock_df = pd.DataFrame({
        "ULP": [ulps[i % len(ulps)] for i in range(rows)],
        "PENYULANG": [feeders[i % len(feeders)] for i in range(rows)],
        "NO TIANG": [f"A{i+10:02d}" for i in range(rows)],
        "KONDISI TIANG": np.random.choice(["BAIK", "CUKUP", "KURANG", "BURUK"], size=rows, p=[0.7, 0.15, 0.1, 0.05]),
        "KONDISI TRAVERS": np.random.choice(["BAIK", "CUKUP", "KURANG", "BURUK"], size=rows, p=[0.8, 0.1, 0.07, 0.03]),
    })
    
    # Calculate Risk identical to your original engine rules
    def determine_class(tiang, travers):
        if tiang == "BURUK" or travers == "BURUK": return "CRITICAL"
        if tiang == "KURANG" or travers == "KURANG": return "HIGH"
        if tiang == "CUKUP" or travers == "CUKUP": return "MEDIUM"
        return "LOW"
        
    mock_df["RISK_CLASS"] = mock_df.apply(lambda r: determine_class(r["KONDISI TIANG"], r["KONDISI TRAVERS"]), axis=1)
    
    score_map = {"LOW": 18.2, "MEDIUM": 42.5, "HIGH": 71.4, "CRITICAL": 94.1}
    mock_df["RISK_SCORE"] = mock_df["RISK_CLASS"].map(score_map) + np.random.uniform(-3, 3, rows)
    mock_df["RISK_SCORE"] = mock_df["RISK_SCORE"].clip(0, 100).round(1)
    
    return mock_df

df_payload = generate_scada_payload()

# ══════════════════════════════════════════════════════════════
# SIDEBAR CONTROL INTERFACE
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    # High-Resolution Official PLN Logo Vector Reconstruction
    st.markdown("""
    <div class="sidebar-header">
        <svg class="brand-logo-svg" viewBox="0 0 120 160" xmlns="http://www.w3.org/2000/svg">
            <polygon points="0,0 120,0 90,70 120,70 10,160 40,90 0,90" fill="#0ea5e9"/>
            <polygon points="40,90 10,160 120,70 60,70" fill="#00e5b0"/>
        </svg>
        <div>
            <div class="brand-text-main">PLN INDONESIA</div>
            <div class="brand-text-sub">Predictive Analytics Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    
    # Language Selector Core Control Integration
    st.session_state.lang_mode = st.selectbox(
        "🌐 GLOBAL LOCALIZATION",
        ["English", "العربية", "Bahasa Indonesia"],
        index=["English", "العربية", "Bahasa Indonesia"].index(st.session_state.lang_mode)
    )
    
    st.markdown("<hr style='border-color:var(--clr-border); margin:12px 0;'>", unsafe_allow_html=True)
    
    # Theme Switches
    st.caption("⚙️ SYSTEM CONFIGURATION")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        if st.button("🌙 Dark Mode", use_container_width=True):
            st.session_state.theme_mode = "dark"
            st.rerun()
    with t_col2:
        if st.button("☀️ Light Mode", use_container_width=True):
            st.session_state.theme_mode = "light"
            st.rerun()
            
    st.markdown("<hr style='border-color:var(--clr-border); margin:12px 0;'>", unsafe_allow_html=True)
    
    # Navigation Radio Matrix
    current_page = st.radio(
        "📊 NAVIGATION HUB",
        ["Overview Terminal", "Inspection Registry Data"],
        index=0
    )

LANG = TRANSLATIONS[st.session_state.lang_mode]

# Cache value extractions
counts = df_payload["RISK_CLASS"].value_counts()
n_total = len(df_payload)
n_crit  = int(counts.get("CRITICAL", 0))
n_high  = int(counts.get("HIGH", 0))
n_med   = int(counts.get("MEDIUM", 0))
n_low   = int(counts.get("LOW", 0))

# ══════════════════════════════════════════════════════════════
# HEADER OPERATIONAL VISIBILITY LIMITATION
# ══════════════════════════════════════════════════════════════
if current_page == "Overview Terminal":
    st.markdown(f"""
    <div class="hero-wrapper">
        <h1 class="hero-title">{LANG['hero_title']}</h1>
        <div class="hero-desc">{LANG['hero_desc']}</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ROUTED APPLICATION RUNSPACE PAGES
# ══════════════════════════════════════════════════════════════
if current_page == "Overview Terminal":
    
    # A. Responsive Dashboard Analytics KPIs Grid
    st.markdown(f"""
    <div class="kpi-container-grid">
        <div class="kpi-card-box"><div class="kpi-card-lbl">{LANG['kpi_total']}</div><div class="kpi-value">{n_total}</div></div>
        <div class="kpi-card-box crit"><div class="kpi-card-lbl">{LANG['kpi_crit']}</div><div class="kpi-value" style="color:var(--clr-critical);">{n_crit}</div></div>
        <div class="kpi-card-box high"><div class="kpi-card-lbl">{LANG['kpi_high']}</div><div class="kpi-value" style="color:var(--clr-high);">{n_high}</div></div>
        <div class="kpi-card-box med"><div class="kpi-card-lbl">{LANG['kpi_med']}</div><div class="kpi-value" style="color:var(--clr-medium);">{n_med}</div></div>
        <div class="kpi-card-box low"><div class="kpi-card-lbl">{LANG['kpi_low']}</div><div class="kpi-value" style="color:var(--clr-low);">{n_low}</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # B. Interactive Visualizations Panels Row
    st.markdown(f'<div class="section-header">{render_vector_icon("svg-acc","activity")}<span class="section-title">{LANG["sec_overview"]}</span></div>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    RISK_COLORS = {"CRITICAL": "#ff3355", "HIGH": "#ff8c00", "MEDIUM": "#0ea5e9", "LOW": "#00e5b0"}
    
    with chart_col1:
        fig_pie = px.pie(df_payload, names="RISK_CLASS", color="RISK_CLASS", hole=0.45, color_discrete_map=RISK_COLORS)
        adjust_chart_theme(fig_pie, LANG["chart_proportional"])
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with chart_col2:
        fig_hist = px.histogram(df_payload, x="RISK_SCORE", color="RISK_CLASS", color_discrete_map=RISK_COLORS, nbins=25)
        adjust_chart_theme(fig_hist, LANG["chart_density"])
        st.plotly_chart(fig_hist, use_container_width=True)

elif current_page == "Inspection Registry Data":
    st.markdown(f'<div class="section-header">{render_vector_icon("svg-acc","list")}<span class="section-title">{LANG["sec_details"]}</span></div>', unsafe_allow_html=True)
    
    # Advanced responsive dataframe interface rendering with automated full-width scaling layout configuration
    st.dataframe(
        df_payload[["ULP", "PENYULANG", "NO TIANG", "KONDISI TIANG", "KONDISI TRAVERS", "RISK_CLASS", "RISK_SCORE"]],
        use_container_width=True,
        hide_index=True
    )
