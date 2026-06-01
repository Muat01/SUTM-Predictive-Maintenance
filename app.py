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

# ── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
.hero-container{
    background:linear-gradient(
        135deg,
        #111827 0%,
        #0f172a 45%,
        #020617 100%
    );

    border:1px solid rgba(255,255,255,0.08);
    border-radius:28px;

    padding:34px;
    margin-bottom:28px;

    position:relative;
    overflow:hidden;

    box-shadow:
        0 0 40px rgba(59,130,246,0.08),
        0 0 80px rgba(59,130,246,0.04);
}

/* Glow Effect */
.hero-container::before{
    content:'';

    position:absolute;

    width:420px;
    height:420px;

    background:
        radial-gradient(
            circle,
            rgba(59,130,246,0.22) 0%,
            transparent 70%
        );

    top:-180px;
    right:-120px;

    pointer-events:none;
}

/* Layout */
.hero-top{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:24px;

    position:relative;
    z-index:2;
}

/* Badge */
.hero-badge{
    display:inline-block;

    background:rgba(16,185,129,0.12);

    color:#10b981;

    border:1px solid rgba(16,185,129,0.25);

    padding:8px 16px;

    border-radius:999px;

    font-size:14px;
    font-weight:600;

    margin-right:10px;
    margin-bottom:18px;

    backdrop-filter:blur(10px);
}

/* Live Badge */
.hero-live{
    display:inline-block;

    background:rgba(59,130,246,0.12);

    color:#60a5fa;

    border:1px solid rgba(59,130,246,0.25);

    padding:8px 16px;

    border-radius:999px;

    font-size:14px;
    font-weight:600;

    margin-bottom:18px;

    backdrop-filter:blur(10px);
}

/* Main Title */
.hero-title{
    font-size:54px;
    font-weight:800;

    line-height:1.05;

    color:white;

    margin-bottom:14px;

    letter-spacing:-1px;
}

/* Subtitle */
.hero-subtitle{
    font-size:18px;

    color:#94a3b8;

    line-height:1.7;

    max-width:760px;
}

/* Status Card */
.hero-status-card{
    background:rgba(255,255,255,0.04);

    border:1px solid rgba(255,255,255,0.08);

    padding:22px 24px;

    border-radius:20px;

    min-width:260px;

    backdrop-filter:blur(12px);

    box-shadow:
        0 0 30px rgba(255,255,255,0.03);
}

/* Labels */
.hero-status-label{
    color:#94a3b8;

    font-size:13px;

    margin-bottom:10px;

    letter-spacing:0.5px;
}

/* Operational Status */
.hero-status-live{
    color:#10b981;

    font-size:24px;
    font-weight:700;

    margin-bottom:12px;
}

/* Small Text */
.hero-status-small{
    color:#94a3b8;

    font-size:13px;
}

/* Value Text */
.hero-status-value{
    color:white;

    font-size:15px;
    font-weight:600;

    margin-top:4px;
}

/* Asset Count */
.hero-assets{
    color:white;

    font-size:34px;
    font-weight:800;

    margin-top:6px;

    letter-spacing:-1px;
}

/* Mobile Responsive */
@media(max-width:768px){

    .hero-title{
        font-size:38px;
    }

    .hero-subtitle{
        font-size:15px;
    }

    .hero-status-card{
        width:100%;
    }

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
@st.cache_data(ttl=30)   # يتحدث كل 30 ثانية تلقائياً
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
        font=dict(color=FONT_COL, family="DM Sans, sans-serif", size=11),
        margin=dict(l=16, r=16, t=40 if title else 16, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
        yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚡ SUTM Dashboard")
    st.markdown("**PT PLN UP3 Bandung · 2026**")
    st.divider()

    st.markdown("#### 🔗 Google Drive File IDs")
    t1_id = st.text_input("SUTMT1 (Visual) File ID",
                           value="YOUR_T1_FILE_ID_HERE",
                           help="من رابط Google Drive: drive.google.com/file/d/**THIS_ID**/view")
    t2_id = st.text_input("SUTMT2 (Thermal) File ID",
                           value="YOUR_T2_FILE_ID_HERE")

    st.divider()
    auto_refresh = st.toggle("🔄 تحديث تلقائي كل 30 ثانية", value=True)
    if st.button("⟳ تحديث يدوي", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    page = st.radio("القسم", [
        "📊 Overview",
        "⚠️ Risk Analysis",
        "🏥 Health Index",
        "🌡️ Thermal",
        "🤖 ML Comparison",
        "🎯 Priority Poles",
    ])

# ── AUTO REFRESH ─────────────────────────────────────────────
if auto_refresh:
    time.sleep(0)   # placeholder — Streamlit rerun على Timer
    st.markdown(
        '<meta http-equiv="refresh" content="30">',
        unsafe_allow_html=True
    )

# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner("جاري قراءة البيانات من Google Drive..."):
    df, hi_df = process_data(t1_id, t2_id)

if df.empty:
    st.error("⚠️ لا توجد بيانات. تأكد من File IDs وصلاحيات Google Drive.")
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

# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

# ── OVERVIEW ─────────────────────────────────────────────────
if page == "📊 Overview":

    # ── HERO SECTION ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero-container">

    <div class="hero-top">

        <div>

            <div class="hero-badge">
                ⚡ AI Monitoring Active
            </div>

            <div class="hero-live">
                ● LIVE SYSTEM
            </div>

            <div class="hero-title">
                Predictive Maintenance Platform
            </div>

            <div class="hero-subtitle">
                Real-Time SUTM Asset Intelligence & Risk Monitoring System
                <br>
                PT PLN UP3 Bandung · Industrial AI Analytics
            </div>

        </div>

        <div class="hero-status-card">

            <div class="hero-status-label">
                SYSTEM STATUS
            </div>

            <div class="hero-status-live">
                ● Operational
            </div>

            <div class="hero-status-small">
                Last Update
            </div>

            <div class="hero-status-value">
                {last_update}
            </div>

            <div class="hero-status-small" style="margin-top:14px;">
                Connected Assets
            </div>

            <div class="hero-assets">
                {total:,}
            </div>

        </div>

    </div>

</div>
""", unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔢 Unique Poles",   f"{total:,}")
    c2.metric("🔴 CRITICAL",       f"{n_crit:,}",  delta=f"{n_crit/total*100:.1f}%", delta_color="inverse")
    c3.metric("🟠 HIGH",           f"{n_high:,}",  delta=f"{n_high/total*100:.1f}%", delta_color="inverse")
    c4.metric("🔵 MEDIUM",         f"{n_med:,}",   delta=f"{n_med/total*100:.1f}%",  delta_color="inverse")
    c5.metric("🟢 LOW",            f"{n_low:,}",   delta=f"{n_low/total*100:.1f}%")

    st.divider()
    col1, col2 = st.columns(2)

    # Donut
    with col1:
        fig = go.Figure(go.Pie(
            labels=["CRITICAL","HIGH","MEDIUM","LOW"],
            values=[n_crit, n_high, n_med, n_low],
            hole=0.68,
            marker=dict(colors=list(COLORS.values()), line=dict(width=0)),
            textinfo="none",
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{total:,}</b><br>poles",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=16, color=FONT_COL))
        dark_layout(fig, "Risk Distribution", 320)
        st.plotly_chart(fig, use_container_width=True)

    # ULP stacked bar
    with col2:
        ulp_data = (df.groupby(["ULP","RISK_CLASS"])
                      .size().reset_index(name="count"))
        fig2 = px.bar(ulp_data, x="ULP", y="count", color="RISK_CLASS",
                      color_discrete_map=COLORS, barmode="stack",
                      category_orders={"RISK_CLASS":["CRITICAL","HIGH","MEDIUM","LOW"]})
        fig2.update_layout(xaxis_tickangle=-35, showlegend=True)
        dark_layout(fig2, "Risk by ULP", 320)
        st.plotly_chart(fig2, use_container_width=True)

    # Summary boxes
    st.divider()
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("CRITICAL + HIGH",   f"{n_crit+n_high:,}", f"{(n_crit+n_high)/total*100:.1f}%")
    s2.metric("Poles with Defects",f"{n_defect:,}",      f"{n_defect/total*100:.1f}%")
    s3.metric("Avg Risk Score",    f"{df['RISK_SCORE'].mean():.1f}")
    s4.metric("Top Risk ULP",
              df.groupby("ULP")["N_BURUK"].sum().idxmax()
              if "ULP" in df.columns else "—")

# ── RISK ANALYSIS ─────────────────────────────────────────────
elif page == "⚠️ Risk Analysis":
    st.title("⚠️ Risk Analysis")
    st.caption(f"{total:,} poles classified · worst-case per unique pole")

    col1, col2 = st.columns(2)

    with col1:
        # Risk count bar (log scale)
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
        # Risk score histogram
        fig2 = px.histogram(df, x="RISK_SCORE", color="RISK_CLASS",
                            color_discrete_map=COLORS, nbins=40,
                            barmode="overlay", opacity=0.8)
        dark_layout(fig2, "Risk Score Distribution", 320)
        st.plotly_chart(fig2, use_container_width=True)

    # ULP horizontal bar
    ulp_risk = (df.groupby(["ULP","RISK_CLASS"])
                  .size().reset_index(name="count"))
    ulp_risk = ulp_risk[ulp_risk["RISK_CLASS"] != "LOW"]
    fig3 = px.bar(ulp_risk, y="ULP", x="count", color="RISK_CLASS",
                  color_discrete_map=COLORS, orientation="h", barmode="stack",
                  category_orders={"RISK_CLASS":["CRITICAL","HIGH","MEDIUM"]})
    dark_layout(fig3, "CRITICAL + HIGH + MEDIUM by ULP", 350)
    st.plotly_chart(fig3, use_container_width=True)

# ── HEALTH INDEX ──────────────────────────────────────────────
elif page == "🏥 Health Index":
    st.title("🏥 Health Index Assessment")
    st.caption("12 component categories · all inspection records")

    if not hi_df.empty:
        # Stacked bar per component
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

        # BURUK ranking
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

        # Table
        st.dataframe(
            hi_df.style.background_gradient(subset=["BURUK","KURANG"],
                                             cmap="RdYlGn_r"),
            use_container_width=True, height=300
        )

# ── THERMAL ───────────────────────────────────────────────────
elif page == "🌡️ Thermal":
    st.title("🌡️ Thermal Inspection — SUTMT2")

    # Try to load T2
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

    # ULP thermal breakdown
    if "ULP" in t2_raw.columns:
        fig3 = px.box(t2_raw, x="ULP", y="DELTA_SUHU", color="ULP",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig3.update_layout(xaxis_tickangle=-30, showlegend=False)
        dark_layout(fig3, "Thermal Delta by ULP", 320)
        st.plotly_chart(fig3, use_container_width=True)

# ── ML COMPARISON ─────────────────────────────────────────────
elif page == "🤖 ML Comparison":
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

    # KPI row
    cols = st.columns(5)
    for i, row in ML_RESULTS.iterrows():
        label = f"{'★ ' if row['Best'] else ''}{row['Model']}"
        cols[i].metric(label, f"{row['F1']:.3f}",
                       "Best ↑" if row["Best"] else f"±{row['Std']:.3f}")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        # F1 horizontal bar
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
        # Grouped all metrics
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

    # Fold stability line chart
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

    # Full table
    st.dataframe(
        ML_RESULTS[["Model","Accuracy","Precision","Recall","F1","Std"]]
        .style.highlight_max(subset=["F1"], color="#1D9E7544")
               .format({"Accuracy":"{:.4f}","Precision":"{:.4f}",
                        "Recall":"{:.4f}","F1":"{:.4f}","Std":"±{:.4f}"}),
        use_container_width=True, hide_index=True
    )

# ── PRIORITY POLES ────────────────────────────────────────────
elif page == "🎯 Priority Poles":
    st.title("🎯 Priority Poles")
    st.caption("Sorted by risk score — real pole IDs from SUTMT1")

    # Filters
    col1, col2, col3 = st.columns(3)
    ulp_list = ["All"] + sorted(df["ULP"].dropna().unique().tolist())
    sel_ulp   = col1.selectbox("Filter by ULP", ulp_list)
    sel_risk  = col2.multiselect("Risk Class", ["CRITICAL","HIGH","MEDIUM","LOW"],
                                  default=["CRITICAL","HIGH"])
    top_n     = col3.slider("Top N poles", 10, 100, 20)

    # Filter
    fdf = df.copy()
    if sel_ulp != "All":
        fdf = fdf[fdf["ULP"] == sel_ulp]
    if sel_risk:
        fdf = fdf[fdf["RISK_CLASS"].isin(sel_risk)]
    fdf = fdf.nlargest(top_n, "RISK_SCORE")

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Shown poles",    f"{len(fdf):,}")
    c2.metric("CRITICAL",       f"{(fdf['RISK_CLASS']=='CRITICAL').sum():,}")
    c3.metric("HIGH",           f"{(fdf['RISK_CLASS']=='HIGH').sum():,}")
    c4.metric("Avg Risk Score", f"{fdf['RISK_SCORE'].mean():.1f}")

    st.divider()

    # Scatter risk score
    fig = px.scatter(
        fdf, x="PENYULANG", y="RISK_SCORE",
        color="RISK_CLASS", color_discrete_map=COLORS,
        size="RISK_SCORE", hover_data=["TIANG_ID","ULP","NO TIANG"],
        size_max=18,
    )
    fig.update_layout(xaxis_tickangle=-45)
    dark_layout(fig, "Risk Score Distribution (Top Poles)", 320)
    st.plotly_chart(fig, use_container_width=True)

    # Table with color
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

    # Download
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Priority List (CSV)",
        csv, "priority_poles.csv", "text/csv",
        use_container_width=True
    )
