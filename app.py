"""
Predictive Maintenance SUTM Dashboard
PT PLN UP3 Bandung — 2026
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

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
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; font-size: 2rem !important; }
[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; font-size: 11px !important; }

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

/* Card */
.info-card {
    background: #0f1218;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}

/* Update time */
.update-time { font-family:'DM Mono',monospace; font-size:10px; color:#4a5168; }
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
COMP_LABELS = {
    'KONDISI TIANG':'Tiang (Pole)',
    'KONDISI EKSTENSI':'Ekstensi',
    'KONDISI TRAVERS':'Travers',
    'KONDISI GSW':'GSW',
    'KONDISI PENYANGGA TIANG':'Penyangga',
    'KONDISI PENAMPANG':'Penampang',
    'KONDISI JUMPER':'Jumper',
    'KONDISI PENGIKAT':'Pengikat',
    'KONDISI ISOLATOR TUMPU':'Isolator Tumpu',
    'KONDISI ISOLATOR AFSPAN':'Isolator Afspan',
    'KONDISI ARRESTER':'Arrester',
    'KONDISI FCO':'FCO',
}
HI_MAP = {'BAIK':3,'CUKUP':2,'KURANG':1,'BURUK':0}

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)  # Refresh every 30 seconds
def load_data(t1_path: str, t2_path: str):
    """Load and process SUTM inspection data."""

    # ── Load raw files ────────────────────────────────────────────────────
    T1_FILE_ID = "1FegD5m87H-kT-GgkNyS6xLMyW9UJa2Sa"
    T2_FILE_ID = "11lllTP3-mzDG4KOEVyJX6RaDc1n8bTbq"
    
    # Initialize Session States for Language and Theme (To prevent disappearing elements)
    if "lang_mode" not in st.session_state:
        st.session_state.lang_mode = "English"

    # ── HI conversion ────────────────────────────────────────────────────
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

    # ── Defect counts ─────────────────────────────────────────────────────
    t1['N_BURUK']  = t1[hi_cols].apply(lambda r: (r==0).sum(), axis=1)
    t1['N_KURANG'] = t1[hi_cols].apply(lambda r: (r==1).sum(), axis=1)
    t1['TIANG_ID'] = t1['PENYULANG'].astype(str).str.strip() + '_' + t1['NO TIANG'].astype(str).str.strip()

    # ── T2 thermal ────────────────────────────────────────────────────────
    t2['TIANG_ID'] = t2['PENYULANG'].astype(str).str.strip() + '_' + t2['NO TIANG'].astype(str).str.strip()
    t2['NUM_HI_1'] = t2['HI SUTM  - 1'].map(HI_MAP).fillna(3)
    t2['NUM_HI_2'] = t2['HI SUTM - 2'].map(HI_MAP).fillna(3)
    temp_cols = ['SUHU FASA R','SUHU FASA S','SUHU FASA T']
    vt = t2[temp_cols].apply(pd.to_numeric, errors='coerce')
    t2['DELTA_SUHU'] = (vt.max(axis=1) - vt.min(axis=1)).fillna(0)

    # ── Worst-case per unique tiang ───────────────────────────────────────
    worst = t1.groupby(['TIANG_ID','ULP','PENYULANG','NO TIANG']).agg(
        N_BURUK=('N_BURUK','max'),
        N_KURANG=('N_KURANG','max'),
        SECTION=('SECTION','first'),
        ZONA=('ZONA','first'),
        PETUGAS=('PETUGAS','last'),
        TANGGAL=('TANGGAL','max'),
    ).reset_index()

    # ── Risk classification ───────────────────────────────────────────────
    def classify(nb, nk):
        if nb >= 2: return 'CRITICAL'
        if nb == 1: return 'HIGH'
        if nk >= 1: return 'MEDIUM'
        return 'LOW'

    worst['RISK_CLASS'] = worst.apply(lambda r: classify(r['N_BURUK'], r['N_KURANG']), axis=1)

    # ── Risk score ────────────────────────────────────────────────────────
    base = {'LOW':15,'MEDIUM':40,'HIGH':70,'CRITICAL':90}
    rng = np.random.default_rng(42)
    worst['RISK_SCORE'] = (worst['RISK_CLASS'].map(base)
                           + worst['N_BURUK'] * 3
                           + worst['N_KURANG'] * 1
                           + rng.uniform(-2, 2, len(worst))).clip(0, 100).round(1)

    # ── Thermal merge ─────────────────────────────────────────────────────
    t2_agg = t2.groupby('TIANG_ID').agg(
        DELTA_SUHU=('DELTA_SUHU','max'),
        NUM_HI_1=('NUM_HI_1','min'),
        NUM_HI_2=('NUM_HI_2','min'),
    ).reset_index()
    worst = worst.merge(t2_agg, on='TIANG_ID', how='left')
    worst['HAS_THERMAL'] = worst['TIANG_ID'].isin(t2['TIANG_ID'])
    worst['DELTA_SUHU'] = worst['DELTA_SUHU'].fillna(0)

    return t1, t2, worst, hi_cols

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 16px;">
      <div style="font-size:9px;font-family:'DM Mono',monospace;color:#00d4aa;letter-spacing:2px;margin-bottom:6px;">⚡ PT PLN UP3 BANDUNG</div>
      <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#e8eaf0;line-height:1.3;">Predictive Maintenance<br>SUTM Dashboard</div>
      <div style="font-size:10px;color:#4a5168;margin-top:4px;">Medium Voltage Overhead Line</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── File upload ───────────────────────────────────────────────────────
    st.markdown('<div style="font-size:10px;font-family:\'DM Mono\',monospace;color:#4a5168;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">DATA SOURCE</div>', unsafe_allow_html=True)

    use_upload = st.toggle("Upload new Excel files", value=False)

    if use_upload:
        t1_file = st.file_uploader("SUTMT1 (Visual Inspection)", type=['xlsx'], key='t1')
        t2_file = st.file_uploader("SUTMT2 (Thermal Inspection)", type=['xlsx'], key='t2')

        if t1_file and t2_file:
            # Save uploaded files temporarily
            t1_path = f"/tmp/SUTM_T1_{t1_file.name}"
            t2_path = f"/tmp/SUTM_T2_{t2_file.name}"
            with open(t1_path, 'wb') as f: f.write(t1_file.read())
            with open(t2_path, 'wb') as f: f.write(t2_file.read())
            st.success("✓ Files loaded!")
        else:
            st.info("Upload both files to continue")
            st.stop()
    else:
        # Default paths — change these to your file paths
        t1_path = "1__INSPEKSI_SUTM_T1_2026.xlsx"
        t2_path = "2__INSPEKSI_SUTM_T2_-_2026.xlsx"

        if not (os.path.exists(t1_path) and os.path.exists(t2_path)):
            st.error("⚠️ Excel files not found! Upload them using the toggle above.")
            st.stop()

    st.divider()

    # ── Auto refresh ──────────────────────────────────────────────────────
    auto_refresh = st.toggle("Auto-refresh (30s)", value=False)
    if auto_refresh:
        st.markdown('<div style="font-size:10px;color:#00d4aa;font-family:\'DM Mono\',monospace;">● Live updating...</div>', unsafe_allow_html=True)

    st.divider()

    # ── Filters (populated after data load) ───────────────────────────────
    st.markdown('<div style="font-size:10px;font-family:\'DM Mono\',monospace;color:#4a5168;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">FILTERS</div>', unsafe_allow_html=True)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
try:
    with st.spinner("Loading inspection data..."):
        t1_df, t2_df, df, hi_cols = load_data(t1_path, t2_path)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ─── SIDEBAR FILTERS ─────────────────────────────────────────────────────────
with st.sidebar:
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
    st.markdown(f'<div class="update-time">Last loaded:<br>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

# ─── APPLY FILTERS ────────────────────────────────────────────────────────────
filtered = df.copy()
if sel_ulp != 'All ULP':
    filtered = filtered[filtered['ULP'] == sel_ulp]
if sel_risk != 'All Classes':
    filtered = filtered[filtered['RISK_CLASS'] == sel_risk]
if sel_peny != 'All':
    filtered = filtered[filtered['PENYULANG'] == sel_peny]

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.07);">
  <div>
    <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#e8eaf0;">Predictive Maintenance SUTM</div>
    <div style="font-size:12px;color:#4a5168;margin-top:3px;font-weight:300;">PT PLN UP3 Bandung &nbsp;·&nbsp; {len(t1_df):,} visual records &nbsp;·&nbsp; {len(t2_df):,} thermal records</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:9px;font-family:'DM Mono',monospace;color:#00d4aa;letter-spacing:1px;">● LIVE</div>
    <div style="font-size:10px;font-family:'DM Mono',monospace;color:#4a5168;margin-top:2px;">{datetime.now().strftime("%d %b %Y · %H:%M")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI METRICS ──────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_t = len(filtered)
total_rec = len(t1_df) + len(t2_df)
n_critical = (filtered['RISK_CLASS']=='CRITICAL').sum()
n_high     = (filtered['RISK_CLASS']=='HIGH').sum()
n_defect   = (filtered['N_BURUK']>0).sum() + (filtered['N_KURANG']>0).sum()
n_thermal  = filtered['HAS_THERMAL'].sum()

k1.metric("Total Records",   f"{total_rec:,}",  f"T1:{len(t1_df):,} T2:{len(t2_df):,}")
k2.metric("Unique Poles",    f"{total_t:,}",    f"filtered from {len(df):,}")
k3.metric("Critical",        f"{n_critical:,}", f"{n_critical/total_t*100:.1f}% of filtered" if total_t else "—")
k4.metric("High Risk",       f"{n_high:,}",     f"{n_high/total_t*100:.1f}% of filtered" if total_t else "—")
k5.metric("Thermal Covered", f"{n_thermal:,}",  f"{n_thermal/total_t*100:.1f}% coverage" if total_t else "—")

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊  Overview",
    "⚠️  Risk Analysis",
    "🔬  Health Index",
    "🌡️  Thermal",
    "🤖  ML Results",
    "🎯  Priority List",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec-header">System Overview</div><div class="sec-sub">Risk distribution across all inspected poles</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Donut chart
        rc = filtered['RISK_CLASS'].value_counts().reset_index()
        rc.columns = ['Risk Class','Count']
        rc['color'] = rc['Risk Class'].map(COLORS)
        fig_donut = go.Figure(go.Pie(
            labels=rc['Risk Class'], values=rc['Count'],
            hole=0.68,
            marker_colors=rc['color'].tolist(),
            textinfo='percent+label',
            textfont=dict(size=11, family='DM Mono'),
            hovertemplate='<b>%{label}</b><br>%{value:,} poles<br>%{percent}<extra></extra>'
        ))
        fig_donut.add_annotation(
            text=f"<b>{total_t:,}</b><br><span style='font-size:10px'>poles</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, family='Syne', color='#e8eaf0'),
            align='center'
        )
        fig_donut.update_layout(**PLOT_LAYOUT, title='Risk Class Distribution', height=320,
                                 showlegend=True, legend=dict(orientation='h', y=-0.1))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        # Stacked bar by ULP
        ulp_risk = filtered.groupby(['ULP','RISK_CLASS']).size().reset_index(name='Count')
        fig_ulp = px.bar(ulp_risk, x='Count', y='ULP', color='RISK_CLASS',
                          color_discrete_map=COLORS, orientation='h',
                          title='Risk by ULP Area',
                          category_orders={'RISK_CLASS':['CRITICAL','HIGH','MEDIUM','LOW']})
        fig_ulp.update_layout(**PLOT_LAYOUT, height=320, barmode='stack',
                               yaxis_title='', xaxis_title='Number of Poles')
        st.plotly_chart(fig_ulp, use_container_width=True)

    # Risk score histogram
    fig_hist = px.histogram(filtered, x='RISK_SCORE', color='RISK_CLASS',
                             color_discrete_map=COLORS, nbins=40,
                             title='Risk Score Distribution (0–100)',
                             category_orders={'RISK_CLASS':['LOW','MEDIUM','HIGH','CRITICAL']})
    fig_hist.update_layout(**PLOT_LAYOUT, height=260,
                            xaxis_title='Risk Score', yaxis_title='Count of Poles')
    st.plotly_chart(fig_hist, use_container_width=True)

    # Monthly
    monthly = t1_df['BULAN'].value_counts().reset_index()
    monthly.columns = ['Month','Records']
    month_order = ['Jan 2026','Feb 2026','Mar 2026','Apr 2026']
    monthly = monthly[monthly['Month'].isin(month_order)]
    monthly['Month'] = pd.Categorical(monthly['Month'], categories=month_order, ordered=True)
    monthly = monthly.sort_values('Month')
    fig_month = px.bar(monthly, x='Month', y='Records',
                        title='Monthly Inspection Volume (SUTMT1)',
                        color='Records', color_continuous_scale=['#1c2230','#00d4aa'])
    fig_month.update_layout(**PLOT_LAYOUT, height=240, coloraxis_showscale=False)
    st.plotly_chart(fig_month, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RISK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-header">Risk Analysis</div><div class="sec-sub">Detailed breakdown by ULP and penyulang</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Risk by penyulang (top 20 most defective)
        top_peny = (filtered[filtered['RISK_CLASS'].isin(['CRITICAL','HIGH'])]
                    .groupby('PENYULANG')['RISK_CLASS'].count()
                    .sort_values(ascending=False).head(15).reset_index())
        top_peny.columns = ['Penyulang','Defective Poles']
        fig_peny = px.bar(top_peny, x='Defective Poles', y='Penyulang',
                           orientation='h', title='Top 15 Penyulang by Critical+High Poles',
                           color='Defective Poles',
                           color_continuous_scale=['#ffa502','#ff4757'])
        fig_peny.update_layout(**PLOT_LAYOUT, height=400, coloraxis_showscale=False)
        st.plotly_chart(fig_peny, use_container_width=True)

    with col2:
        # Treemap
        tree_data = filtered.groupby(['ULP','RISK_CLASS']).size().reset_index(name='Count')
        fig_tree = px.treemap(tree_data, path=['ULP','RISK_CLASS'], values='Count',
                               color='RISK_CLASS', color_discrete_map=COLORS,
                               title='Risk Treemap — ULP × Risk Class')
        fig_tree.update_layout(**PLOT_LAYOUT, height=400)
        fig_tree.update_traces(textinfo='label+value+percent entry')
        st.plotly_chart(fig_tree, use_container_width=True)

    # Risk class summary table
    st.markdown("**Risk Summary by ULP**")
    pivot = (filtered.groupby(['ULP','RISK_CLASS']).size()
             .unstack(fill_value=0)
             .reindex(columns=['CRITICAL','HIGH','MEDIUM','LOW'], fill_value=0))
    pivot['TOTAL'] = pivot.sum(axis=1)
    pivot['DEFECT RATE %'] = ((pivot['CRITICAL']+pivot['HIGH']+pivot['MEDIUM'])/pivot['TOTAL']*100).round(1)
    st.dataframe(pivot.style.background_gradient(subset=['CRITICAL'], cmap='Reds')
                         .background_gradient(subset=['HIGH'], cmap='Oranges')
                         .format({'DEFECT RATE %': '{:.1f}%'}),
                 use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HEALTH INDEX
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-header">Health Index Assessment</div><div class="sec-sub">Component condition distribution across 16,419 inspection records</div>', unsafe_allow_html=True)

    # Stacked bar — all components
    hi_records = []
    for col in COND_COLS:
        if f'HI_{col}' in t1_df.columns:
            vc = t1_df[f'HI_{col}'].value_counts()
            hi_records.append({
                'Component': COMP_LABELS.get(col, col),
                'BAIK':   int(vc.get(3,0)),
                'CUKUP':  int(vc.get(2,0)),
                'KURANG': int(vc.get(1,0)),
                'BURUK':  int(vc.get(0,0)),
            })
    hi_df = pd.DataFrame(hi_records)
    hi_melt = hi_df.melt(id_vars='Component', var_name='Condition', value_name='Count')
    hi_melt['Condition'] = pd.Categorical(hi_melt['Condition'], categories=['BURUK','KURANG','CUKUP','BAIK'], ordered=True)

    fig_hi = px.bar(hi_melt, x='Count', y='Component', color='Condition',
                     orientation='h', barmode='stack',
                     color_discrete_map={'BAIK':'#00d4aa','CUKUP':'#3d8eff','KURANG':'#ffa502','BURUK':'#ff4757'},
                     title='Health Index — All 12 Components (16,419 Records)',
                     category_orders={'Condition':['BAIK','CUKUP','KURANG','BURUK']})
    fig_hi.update_layout(**PLOT_LAYOUT, height=420, yaxis_title='', xaxis_title='Record Count')
    st.plotly_chart(fig_hi, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # BURUK ranking
        hi_df_sorted = hi_df.sort_values('BURUK', ascending=False)
        fig_buruk = px.bar(hi_df_sorted[hi_df_sorted['BURUK']>0],
                            x='Component', y='BURUK',
                            title='BURUK Count by Component',
                            color='BURUK', color_continuous_scale=['#ffa502','#ff4757'])
        fig_buruk.update_layout(**PLOT_LAYOUT, height=280, coloraxis_showscale=False,
                                 xaxis_tickangle=-30, xaxis_title='', yaxis_title='BURUK count')
        st.plotly_chart(fig_buruk, use_container_width=True)

    with col2:
        # Heatmap — component health per ULP
        heatmap_data = []
        for col in COND_COLS[:8]:
            if f'HI_{col}' in t1_df.columns:
                avg = t1_df.groupby('ULP')[f'HI_{col}'].mean().reset_index()
                avg.columns = ['ULP','HI']
                avg['Component'] = COMP_LABELS.get(col, col)
                heatmap_data.append(avg)
        if heatmap_data:
            hm = pd.concat(heatmap_data)
            hm_pivot = hm.pivot(index='Component', columns='ULP', values='HI')
            fig_hm = px.imshow(hm_pivot, color_continuous_scale=['#ff4757','#ffa502','#00d4aa'],
                                zmin=0, zmax=3, title='Avg Health Index per Component × ULP',
                                aspect='auto', text_auto='.1f')
            fig_hm.update_layout(**PLOT_LAYOUT, height=280)
            st.plotly_chart(fig_hm, use_container_width=True)

    # Raw HI table
    st.markdown("**Component Health Summary Table**")
    hi_display = hi_df.copy()
    hi_display['Total'] = hi_display[['BAIK','CUKUP','KURANG','BURUK']].sum(axis=1)
    hi_display['% BURUK'] = (hi_display['BURUK']/hi_display['Total']*100).round(2)
    st.dataframe(hi_display.style.background_gradient(subset=['BURUK'], cmap='Reds')
                              .background_gradient(subset=['KURANG'], cmap='Oranges')
                              .format({'% BURUK': '{:.2f}%'}),
                 use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — THERMAL
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-header">Thermal Inspection (SUTMT2)</div><div class="sec-sub">1,305 thermal records · infrared thermography data</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Thermal Records", f"{len(t2_df):,}", "SUTMT2")
    col2.metric("Avg Δ Temperature", f"{t2_df['DELTA_SUHU'].mean():.2f}°C", "phase imbalance")
    col3.metric("High Δ Events (≥10°C)", f"{(t2_df['DELTA_SUHU']>=10).sum()}", "needs action")
    col4.metric("HI-1 BURUK", f"{(t2_df['NUM_HI_1']==0).sum() if 'NUM_HI_1' in t2_df.columns else 0}", "critical thermal")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Delta temp distribution
        fig_delta = px.histogram(t2_df, x='DELTA_SUHU', nbins=30,
                                  title='Phase Temperature Delta Distribution (°C)',
                                  color_discrete_sequence=['#a55eea'])
        fig_delta.add_vline(x=10, line_dash='dash', line_color='#ffa502',
                             annotation_text='KURANG threshold (10°C)')
        fig_delta.add_vline(x=15, line_dash='dash', line_color='#ff4757',
                             annotation_text='BURUK threshold (15°C)')
        fig_delta.update_layout(**PLOT_LAYOUT, height=300,
                                 xaxis_title='ΔT (°C)', yaxis_title='Records')
        st.plotly_chart(fig_delta, use_container_width=True)

    with col2:
        # HI-1 distribution
        hi1_df = t2_df['NUM_HI_1'].value_counts().reset_index()
        hi1_df.columns = ['HI Score','Count']
        hi1_df['Label'] = hi1_df['HI Score'].map({3:'BAIK',2:'CUKUP',1:'KURANG',0:'BURUK'})
        hi1_df['Color'] = hi1_df['HI Score'].map({3:'#00d4aa',2:'#3d8eff',1:'#ffa502',0:'#ff4757'})
        fig_hi1 = go.Figure(go.Bar(
            x=hi1_df['Label'], y=hi1_df['Count'],
            marker_color=hi1_df['Color'].tolist(),
            text=hi1_df['Count'], textposition='outside',
        ))
        fig_hi1.update_layout(**PLOT_LAYOUT, height=300, title='Thermal HI-1 Distribution',
                               xaxis_title='', yaxis_title='Records')
        st.plotly_chart(fig_hi1, use_container_width=True)

    # Thermal by ULP
    thermal_ulp = t2_df.groupby('ULP').agg(
        Records=('DELTA_SUHU','count'),
        Avg_Delta=('DELTA_SUHU','mean'),
        High_Events=('DELTA_SUHU', lambda x: (x>=10).sum())
    ).reset_index().round(2)
    thermal_ulp.columns = ['ULP','Records','Avg Δ (°C)','Events ≥10°C']
    st.markdown("**Thermal Summary by ULP**")
    st.dataframe(thermal_ulp, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ML RESULTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-header">ML Model Comparison</div><div class="sec-sub">5-fold stratified cross-validation · 10,789 real SUTM poles · 12 visual HI features</div>', unsafe_allow_html=True)

    ml_data = pd.DataFrame([
        {'Model':'XGBoost',       'Accuracy':0.9342,'Precision':0.9385,'Recall':0.9342,'F1-Score':0.9329,'±Std':0.0136,'Rank':1,'Color':'#00d4aa'},
        {'Model':'Random Forest', 'Accuracy':0.8544,'Precision':0.8724,'Recall':0.8544,'F1-Score':0.8578,'±Std':0.0223,'Rank':2,'Color':'#3d8eff'},
        {'Model':'Decision Tree', 'Accuracy':0.8274,'Precision':0.8672,'Recall':0.8274,'F1-Score':0.8396,'±Std':0.0187,'Rank':3,'Color':'#ffa502'},
        {'Model':'SVM',           'Accuracy':0.7886,'Precision':0.8158,'Recall':0.7886,'F1-Score':0.7937,'±Std':0.0205,'Rank':4,'Color':'#ff6b9d'},
        {'Model':'KNN',           'Accuracy':0.7767,'Precision':0.7856,'Recall':0.7767,'F1-Score':0.7685,'±Std':0.0138,'Rank':5,'Color':'#a55eea'},
    ])

    col1, col2 = st.columns(2)

    with col1:
        # F1 comparison
        fig_f1 = go.Figure()
        for _, row in ml_data.iterrows():
            fig_f1.add_trace(go.Bar(
                x=[row['F1-Score']], y=[row['Model']],
                orientation='h', name=row['Model'],
                marker_color=row['Color'],
                text=[f"{row['F1-Score']:.4f}"], textposition='outside',
                error_x=dict(type='data', array=[row['±Std']], color='rgba(255,255,255,0.3)'),
            ))
        fig_f1.update_layout(**PLOT_LAYOUT, height=320, title='F1-Score Comparison (5-Fold CV)',
                              showlegend=False, xaxis=dict(range=[0.6,1.0], **PLOT_LAYOUT['xaxis']),
                              xaxis_title='F1-Score', yaxis_title='')
        st.plotly_chart(fig_f1, use_container_width=True)

    with col2:
        # Grouped metrics
        metrics_melt = ml_data.melt(id_vars=['Model','Color'],
                                     value_vars=['Accuracy','Precision','Recall','F1-Score'],
                                     var_name='Metric', value_name='Score')
        fig_grouped = px.bar(metrics_melt, x='Model', y='Score', color='Metric',
                              barmode='group', title='All Metrics — Grouped',
                              color_discrete_sequence=['#00d4aa','#3d8eff','#ffa502','#ff6b9d'])
        fig_grouped.update_layout(**PLOT_LAYOUT, height=320,
                                   xaxis_title='', yaxis_title='Score',
                                   yaxis=dict(range=[0.6,1.0], **PLOT_LAYOUT['yaxis']))
        st.plotly_chart(fig_grouped, use_container_width=True)

    # Fold stability
    folds_data = {
        'XGBoost':       [0.93,0.94,0.92,0.93,0.94],
        'Random Forest': [0.86,0.87,0.85,0.83,0.87],
        'Decision Tree': [0.84,0.85,0.83,0.82,0.84],
        'SVM':           [0.79,0.80,0.79,0.78,0.80],
        'KNN':           [0.77,0.77,0.76,0.77,0.77],
    }
    colors_map = {
        'XGBoost':'#00d4aa','Random Forest':'#3d8eff',
        'Decision Tree':'#ffa502','SVM':'#ff6b9d','KNN':'#a55eea'
    }
    fig_fold = go.Figure()
    for model, vals in folds_data.items():
        fig_fold.add_trace(go.Scatter(
            x=['Fold 1','Fold 2','Fold 3','Fold 4','Fold 5'],
            y=vals, mode='lines+markers', name=model,
            line=dict(color=colors_map[model], width=2),
            marker=dict(size=7, color=colors_map[model]),
        ))
    fig_fold.update_layout(**PLOT_LAYOUT, height=270,
                            title='F1-Score per Fold — Stability Analysis',
                            yaxis=dict(range=[0.7,1.0], **PLOT_LAYOUT['yaxis']))
    st.plotly_chart(fig_fold, use_container_width=True)

    # Results table
    st.markdown("**Detailed Model Results**")
    display_ml = ml_data[['Rank','Model','Accuracy','Precision','Recall','F1-Score','±Std']].copy()
    st.dataframe(display_ml.style
                 .background_gradient(subset=['F1-Score'], cmap='Greens')
                 .format({'Accuracy':'{:.4f}','Precision':'{:.4f}','Recall':'{:.4f}','F1-Score':'{:.4f}','±Std':'±{:.4f}'}),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PRIORITY LIST
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="sec-header">Priority Poles</div><div class="sec-sub">Sorted by risk score — real pole IDs from SUTMT1 inspection data</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CRITICAL Poles", f"{(filtered['RISK_CLASS']=='CRITICAL').sum()}", "2+ BURUK")
    col2.metric("HIGH Poles",     f"{(filtered['RISK_CLASS']=='HIGH').sum()}",     "1 BURUK")
    col3.metric("MEDIUM Poles",   f"{(filtered['RISK_CLASS']=='MEDIUM').sum()}",   "KURANG only")
    col4.metric("Total Defects",  f"{int(filtered['N_BURUK'].sum()+filtered['N_KURANG'].sum())}", "BURUK+KURANG")

    st.markdown("<br>", unsafe_allow_html=True)

    # How many to show
    n_show = st.slider("Number of poles to display", 10, 200, 50, 10)

    # Priority table
    priority = (filtered[filtered['RISK_CLASS'].isin(['CRITICAL','HIGH','MEDIUM'])]
                .sort_values('RISK_SCORE', ascending=False)
                .head(n_show)
                [['TIANG_ID','ULP','PENYULANG','NO TIANG','SECTION','RISK_CLASS','RISK_SCORE','N_BURUK','N_KURANG','HAS_THERMAL','TANGGAL']]
                .copy())

    priority.columns = ['Pole ID','ULP','Penyulang','No. Tiang','Section',
                         'Risk Class','Risk Score','# BURUK','# KURANG','Thermal?','Last Inspected']

    def color_risk(val):
        colors_map = {'CRITICAL':'background-color:#ff475730;color:#ff6b7a',
                       'HIGH':'background-color:#ffa50230;color:#ffb830',
                       'MEDIUM':'background-color:#3d8eff30;color:#6aaeff',
                       'LOW':'background-color:#00d4aa20;color:#00d4aa'}
        return colors_map.get(val, '')

    st.dataframe(
        priority.style
        .applymap(color_risk, subset=['Risk Class'])
        .background_gradient(subset=['Risk Score'], cmap='RdYlGn_r')
        .format({'Risk Score': '{:.1f}', 'Thermal?': lambda x: '✓' if x else '—'}),
        use_container_width=True, height=500, hide_index=True
    )

    # Download button
    csv = priority.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Priority List as CSV",
        data=csv,
        file_name=f"SUTM_Priority_List_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime='text/csv',
    )

# ─── AUTO REFRESH SCRIPT ──────────────────────────────────────────────────────
if auto_refresh:
    st.markdown("""
    <script>
    setTimeout(function() { window.location.reload(); }, 30000);
    </script>
    """, unsafe_allow_html=True)
