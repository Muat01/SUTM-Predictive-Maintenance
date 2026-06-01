"""
Predictive Maintenance SUTM Dashboard
PT PLN UP3 Bandung — 2026
Automated Google Drive Sync with Safe Fallback
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import io
from datetime import datetime

# استيراد مكتبات جوجل بأمان لمنع أي توقف
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Predictive Maintenance SUTM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Main background */
.stApp { background-color: #0a0c10; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f1218 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
section[data-testid="stSidebar"] * { color: #8b92a8 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #0f1218;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: #4a5168 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; font-size: 2rem !important; line-height: 1.2 !important; }

/* Prevent text overlap in Delta metrics */
[data-testid="stMetricDelta"] { 
    font-family: 'DM Mono', monospace !important; 
    font-size: 11px !important; 
    margin-top: 6px !important; 
    display: block !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #0f1218; border-bottom: 1px solid rgba(255,255,255,0.07); gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #4a5168 !important; font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.5px; }
.stTabs [aria-selected="true"] { color: #00d4aa !important; border-bottom-color: #00d4aa !important; }

/* Selectbox */
.stSelectbox label { color: #4a5168 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 1px !important; text-transform: uppercase !important; }

/* Section header */
.sec-header {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #e8eaf0;
    margin-bottom: 4px;
}
.sec-sub {
    font-size: 12px;
    color: #4a5168;
    margin-bottom: 20px;
    font-weight: 300;
}

/* Custom badge */
.badge { display:inline-block; font-size:11px; font-family:'DM Mono',monospace; padding:3px 10px; border-radius:20px; font-weight:500; }
.badge-cr { background:rgba(255,71,87,.15); color:#ff6b7a; border:1px solid rgba(255,71,87,.25); }
.badge-hi { background:rgba(255,165,2,.15); color:#ffb830; border:1px solid rgba(255,165,2,.25); }
.badge-me { background:rgba(61,142,255,.15); color:#6aaeff; border:1px solid rgba(61,142,255,.25); }
.badge-lo { background:rgba(0,212,170,.1); color:#00d4aa; border:1px solid rgba(0,212,170,.25); }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#8b92a8', size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    showlegend=True,
    legend=dict(font=dict(size=10), bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.07)', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.07)', tickfont=dict(size=10)),
)
COLORS = {'CRITICAL':'#ff4757','HIGH':'#ffa502','MEDIUM':'#3d8eff','LOW':'#00d4aa'}

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
COND_COLS = [
    'KONDISI TIANG','KONDISI EKSTENSI','KONDISI TRAVERS','KONDISI GSW',
    'KONDISI PENYANGGA TIANG','KONDISI PENAMPANG','KONDISI JUMPER',
    'KONDISI PENGIKAT','KONDISI ISOLATOR TUMPU','KONDISI ISOLATOR AFSPAN',
    'KONDISI ARRESTER','KONDISI FCO'
]
HI_MAP = {'BAIK':3,'CUKUP':2,'KURANG':1,'BURUK':0}

# 🔗 GOOGLE DRIVE TARGET IDs
T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"

# ─── SAFE GOOGLE DRIVE SYNC PIPELINE ─────────────────────────────────────────
def download_excel_from_drive(file_id: str, creds_path: str = "service_account.json"):
    """تسحب الملفات من الدرايف بأمان، وإذا لم تجد المفتاح ترجع None لتبديل الوضع تلقائياً"""
    if not HAS_GOOGLE_LIBS:
        return None
    try:
        if os.path.exists(creds_path):
            creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
        elif "google_service_account" in st.secrets:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["google_service_account"], scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
        else:
            return None

        drive_service = build("drive", "v3", credentials=creds)
        request = drive_service.files().get_media(fileId=file_id)
        
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_buffer.seek(0)
        return file_buffer
    except Exception:
        return None

# ─── DATA LOADING & CALCULATION ENGINE ───────────────────────────────────────
@st.cache_data(ttl=30)
def load_data_from_any_source(t1_src, t2_src, is_stream=True):
    t1 = pd.read_excel(t1_src, sheet_name='DATA') if is_stream else pd.read_excel(t1_src, sheet_name='DATA')
    t2 = pd.read_excel(t2_src, sheet_name='DATA') if is_stream else pd.read_excel(t2_src, sheet_name='DATA')

    def hi_from_text(val):
        if pd.isna(val) or str(val).strip().upper() in ['BLANK','TIDAK ADA','-','']: return 3
        v = str(val).upper()
        if any(x in v for x in ['BURUK','PECAH','PUTUS','KEROPOS','FLASH','BOCOR','RANTAS','RETAK']): return 0
        if any(x in v for x in ['KURANG','KENDOR','LEPAS','MIRING','LONGGAR','BELUM','RAMBAT']): return 1
        if any(x in v for x in ['CUKUP','LUMUT','BERKARAT','PARALON']): return 2
        return 3

    for c in COND_COLS:
        if c in t1.columns:
            t1[f'HI_{c}'] = t1[c].apply(hi_from_text)

    hi_cols = [f'HI_{c}' for c in COND_COLS if c in t1.columns]

    t1['N_BURUK']  = t1[hi_cols].apply(lambda r: (r==0).sum(), axis=1)
    t1['N_KURANG'] = t1[hi_cols].apply(lambda r: (r==1).sum(), axis=1)
    t1['TIANG_ID'] = t1['PENYULANG'].astype(str).str.strip() + '_' + t1['NO TIANG'].astype(str).str.strip()

    t2['TIANG_ID'] = t2['PENYULANG'].astype(str).str.strip() + '_' + t2['NO TIANG'].astype(str).str.strip()
    t2['NUM_HI_1'] = t2['HI SUTM  - 1'].map(HI_MAP).fillna(3)
    t2['NUM_HI_2'] = t2['HI SUTM - 2'].map(HI_MAP).fillna(3)
    temp_cols = ['SUHU FASA R','SUHU FASA S','SUHU FASA T']
    vt = t2[temp_cols].apply(pd.to_numeric, errors='coerce')
    t2['DELTA_SUHU'] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    worst = t1.groupby(['TIANG_ID','ULP','PENYULANG','NO TIANG']).agg(
        N_BURUK=('N_BURUK','max'),
        N_KURANG=('N_KURANG','max'),
        SECTION=('SECTION','first'),
        ZONA=('ZONA','first'),
        PETUGAS=('PETUGAS','last'),
        TANGGAL=('TANGGAL','max'),
    ).reset_index()

    def classify(nb, nk):
        if nb >= 2: return 'CRITICAL'
        if nb == 1: return 'HIGH'
        if nk >= 1: return 'MEDIUM'
        return 'LOW'

    worst['RISK_CLASS'] = worst.apply(lambda r: classify(r['N_BURUK'], r['N_KURANG']), axis=1)

    base = {'LOW':15,'MEDIUM':40,'HIGH':70,'CRITICAL':90}
    rng = np.random.default_rng(42)
    worst['RISK_SCORE'] = (worst['RISK_CLASS'].map(base)
                           + worst['N_BURUK'] * 3
                           + worst['N_KURANG'] * 1
                           + rng.uniform(-2, 2, len(worst))).clip(0, 100).round(1)

    t2_agg = t2.groupby('TIANG_ID').agg(
        DELTA_SUHU=('DELTA_SUHU','max'),
        NUM_HI_1=('NUM_HI_1','min'),
        NUM_HI_2=('NUM_HI_2','min'),
    ).reset_index()
    worst = worst.merge(t2_agg, on='TIANG_ID', how='left')
    worst['HAS_THERMAL'] = worst['TIANG_ID'].isin(t2['TIANG_ID'])
    worst['DELTA_SUHU'] = worst['DELTA_SUHU'].fillna(0)

    return t1, t2, worst, hi_cols

# ─── SIDEBAR CONNECTION HANDLING ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 16px;">
      <div style="font-size:9px;font-family:'DM Mono',monospace;color:#00d4aa;letter-spacing:2px;margin-bottom:6px;">⚡ PT PLN UP3 BANDUNG</div>
      <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#e8eaf0;line-height:1.3;">Predictive Maintenance<br>SUTM Dashboard</div>
      <div style="font-size:10px;color:#4a5168;margin-top:4px;">PREDICTIVE MAINTENANCE AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style="font-size:10px;font-family:\'DM Mono\',monospace;color:#4a5168;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">CONNECTION STATUS</div>', unsafe_allow_html=True)
    
    # محاولة جلب البيانات سحابياً بذكاء
    t1_stream = download_excel_from_drive(T1_FILE_ID)
    t2_stream = download_excel_from_drive(T2_FILE_ID)

    # التحويل التلقائي الآمن للوضع المحلي في حال عدم توفر ملف الاعتماد
    if t1_stream and t2_stream:
        st.success("⚡ Connected to Live Drive Feed Engine!")
        is_stream_mode = True
        t1_input, t2_input = t1_stream, t2_stream
    else:
        st.warning("⚠️ service_account.json not found. Falling back to local inspection files.")
        is_stream_mode = False
        t1_input = "1__INSPEKSI_SUTM_T1_2026.xlsx"
        t2_input = "2__INSPEKSI_SUTM_T2_-_2026.xlsx"
        
        if not (os.path.exists(t1_input) and os.path.exists(t2_input)):
            st.error("❌ Local files not found! Place '1__INSPEKSI_SUTM_T1_2026.xlsx' and '2__INSPEKSI_SUTM_T2_-_2026.xlsx' in project root.")
            st.stop()

    st.divider()
    auto_refresh = st.toggle("Auto-refresh (30s)", value=True)

# ─── PIPELINE RESOLUTION ─────────────────────────────────────────────────────
try:
    t1_df, t2_df, df, hi_cols = load_data_from_any_source(t1_input, t2_input, is_stream=is_stream_mode)
except Exception as e:
    st.error(f"Error compiling active data matrices: {e}")
    st.stop()

# ─── SIDEBAR FILTERS ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:10px;font-family:\'DM Mono\',monospace;color:#4a5168;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">FILTERS</div>', unsafe_allow_html=True)
    
    ulp_opts = ['All ULP'] + sorted(df['ULP'].dropna().unique().tolist())
    sel_ulp = st.selectbox("ULP Area", ulp_opts)

    risk_opts = ['All Classes','CRITICAL','HIGH','MEDIUM','LOW']
    sel_risk = st.selectbox("Risk Class", risk_opts)

    if sel_ulp != 'All ULP':
        penyulang_opts = ['All'] + sorted(df[df['ULP']==sel_ulp]['PENYULANG'].dropna().unique().tolist())
    else:
        penyulang_opts = ['All'] + sorted(df['PENYULANG'].dropna().unique().tolist())
    sel_peny = st.selectbox("Penyulang", penyulang_opts)

    st.divider()
    st.markdown(f'<div class="update-time">Last Update:<br>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

# ─── FILTER EXECUTION ─────────────────────────────────────────────────────────
filtered = df.copy()
if sel_ulp != 'All ULP':
    filtered = filtered[filtered['ULP'] == sel_ulp]
if sel_risk != 'All Classes':
    filtered = filtered[filtered['RISK_CLASS'] == sel_risk]
if sel_peny != 'All':
    filtered = filtered[filtered['PENYULANG'] == sel_peny]

# ─── MAIN HEADER ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.07);">
  <div>
    <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#e8eaf0;">Predictive Maintenance SUTM</div>
    <div style="font-size:12px;color:#4a5168;margin-top:3px;font-weight:300;">PT PLN UP3 Bandung &nbsp;·&nbsp; {len(t1_df):,} visual records &nbsp;·&nbsp; {len(t2_df):,} thermal records</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:9px;font-family:'DM Mono',monospace;color:#00d4aa;letter-spacing:1px;">● LIVE DASHBOARD FEED</div>
    <div style="font-size:10px;font-family:'DM Mono',monospace;color:#4a5168;margin-top:2px;">{datetime.now().strftime("%d %b %Y · %H:%M")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── METRIC HUB ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_t = len(filtered)
total_rec = len(t1_df) + len(t2_df)
n_critical = (filtered['RISK_CLASS']=='CRITICAL').sum()
n_high     = (filtered['RISK_CLASS']=='HIGH').sum()
n_thermal  = filtered['HAS_THERMAL'].sum()

k1.metric("Total Records",   f"{total_rec:,}",  f"T1:{len(t1_df):,} T2:{len(t2_df):,}")
k2.metric("Unique Poles",    f"{total_t:,}",    f"filtered from {len(df):,}")
k3.metric("Critical",        f"{n_critical:,}", f"{n_critical/total_t*100:.1f}%" if total_t else "—")
k4.metric("High Risk",       f"{n_high:,}",     f"{n_high/total_t*100:.1f}%" if total_t else "—")
k5.metric("Thermal Covered", f"{n_thermal:,}",  f"{n_thermal/total_t*100:.1f}%" if total_t else "—")

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊  Overview", "⚠️  Risk Analysis", "🔬  Health Index", "🌡️  Thermal", "🤖  ML Results", "🎯  Priority List"
])

with tab1:
    st.markdown('<div class="sec-header">System Overview</div><div class="sec-sub">Risk distribution across all inspected poles</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        rc = filtered['RISK_CLASS'].value_counts().reset_index()
        rc.columns = ['Risk Class','Count']
        rc['color'] = rc['Risk Class'].map(COLORS)
        fig_donut = go.Figure(go.Pie(
            labels=rc['Risk Class'], values=rc['Count'],
            hole=0.68, marker_colors=rc['color'].tolist(),
            textinfo='percent+label', textfont=dict(size=11, family='DM Mono'),
            hovertemplate='<b>%{label}</b><br>%{value:,} poles<br>%{percent}<extra></extra>'
        ))
        fig_donut.add_annotation(
            text=f"<b>{total_t:,}</b><br><span style='font-size:10px'>poles</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, family='Syne', color='#e8eaf0'), align='center'
        )
        fig_donut.update_layout(**PLOT_LAYOUT, title='Risk Class Distribution', height=320)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        clean_ulp_df = filtered.dropna(subset=['ULP'])
        clean_ulp_df = clean_ulp_df[clean_ulp_df['ULP'].astype(str).str.strip() != '']
        
        if not clean_ulp_df.empty:
            ulp_risk = clean_ulp_df.groupby(['ULP','RISK_CLASS']).size().reset_index(name='Count')
            fig_ulp = px.bar(ulp_risk, x='Count', y='ULP', color='RISK_CLASS',
                              color_discrete_map=COLORS, orientation='h',
                              title='Risk by ULP Area',
                              category_orders={'RISK_CLASS':['CRITICAL','HIGH','MEDIUM','LOW']})
            fig_ulp.update_layout(**PLOT_LAYOUT, height=320, barmode='stack', yaxis_title='', xaxis_title='Number of Poles')
            st.plotly_chart(fig_ulp, use_container_width=True)
        else:
            st.info("No regional ULP metric data available for active parameters")

    fig_hist = px.histogram(filtered, x='RISK_SCORE', color='RISK_CLASS',
                             color_discrete_map=COLORS, nbins=40,
                             title='Risk Score Distribution (0–100)',
                             category_orders={'RISK_CLASS':['LOW','MEDIUM','HIGH','CRITICAL']})
    fig_hist.update_layout(**PLOT_LAYOUT, height=260, xaxis_title='Risk Score', yaxis_title='Count of Poles')
    st.plotly_chart(fig_hist, use_container_width=True)

if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
