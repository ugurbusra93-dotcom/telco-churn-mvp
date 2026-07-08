"""
Churn Radar — Telco Kampanya Hedefleme MVP (Streamlit)

Calistirmak icin:
    pip install -r requirements.txt
    python3 pipeline.py          # enriched_telco.csv uretir (ilk seferde)
    streamlit run streamlit_app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import random
import datetime
import plotly.graph_objects as go

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

st.set_page_config(page_title="Churn Simulator AI", page_icon="📡", layout="wide")

DATA_PATH = "enriched_telco.csv"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

    /* ============ KOYU PREMIUM TEMA ============ */
    .stApp {
        background: #070B1F;
        background-image:
            radial-gradient(circle at 15% 0%, rgba(124,92,255,.12) 0%, transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(34,211,238,.08) 0%, transparent 40%);
    }
    [data-testid="stAppViewContainer"] { color: #E4E7F5; }
    h1, h2, h3, h4, h5, p, span, label, div { color: #E4E7F5; }
    [data-testid="stMarkdownContainer"] p { color: #A8AEC7; }

    /* Hero header */
    .crd-header {
        background: linear-gradient(135deg, rgba(124,92,255,.15) 0%, rgba(34,211,238,.08) 50%, rgba(255,93,143,.1) 100%);
        border: 1px solid rgba(255,255,255,.08);
        margin: -1rem -1rem 1.6rem -1rem;
        padding: 42px 44px 34px 44px; border-radius: 0 0 24px 24px;
        position: relative; overflow: hidden;
        backdrop-filter: blur(20px);
    }
    .crd-brand-row { display:flex; align-items:center; gap:14px; }
    .crd-brand-badge {
        width:42px; height:42px; border-radius:14px;
        background: linear-gradient(135deg, #7C5CFF, #22D3EE);
        display:flex; align-items:center; justify-content:center;
        font-size:20px; flex-shrink:0;
        box-shadow: 0 0 24px rgba(124,92,255,.4);
    }
    .crd-eyebrow {
        font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; letter-spacing: .16em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #A78BFA, #5EEAD4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0; font-weight:600;
    }
    .crd-title {
        color: #F5F6FD; font-size: 32px; font-weight: 800; margin: 0; letter-spacing:-.02em;
    }
    .crd-tagline {
        color: #9BA3C9; font-size: 14px; margin-top: 10px; font-weight:500; letter-spacing:.02em;
    }
    .crd-sub {
        color: #6C7399; font-size: 12px; margin-top: 10px; font-family: 'IBM Plex Mono', monospace;
    }

    /* KPI kartlari - glassmorphism */
    .crd-kpi-row { display:flex; gap:16px; margin: 0 0 28px 0; flex-wrap: wrap; }
    .crd-kpi {
        flex:1; min-width:210px;
        background: linear-gradient(145deg, rgba(17,24,45,.9), rgba(17,24,45,.6));
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 20px; padding:22px 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 4px 24px rgba(0,0,0,.25);
        position: relative; overflow:hidden;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .crd-kpi::before {
        content:''; position:absolute; top:0; left:0; right:0; height:3px;
        background: linear-gradient(90deg, #7C5CFF, #22D3EE);
    }
    .crd-kpi.warn::before { background: linear-gradient(90deg, #FF5D8F, #F59E0B); }
    .crd-kpi:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(124,92,255,.18);
    }
    .crd-kpi-top { display:flex; justify-content:space-between; align-items:flex-start; }
    .crd-kpi-icon { font-size:20px; opacity:.85; }
    .crd-kpi-label {
        font-family:'IBM Plex Mono', monospace; font-size:10.5px; letter-spacing:.1em;
        text-transform:uppercase; color:#7076A3; margin:10px 0 6px 0;
    }
    .crd-kpi-value {
        font-family:'IBM Plex Mono', monospace; font-size:30px; font-weight:700; color:#F5F6FD;
        letter-spacing:-.02em;
    }
    .crd-kpi.warn .crd-kpi-value { color:#FF93AF; }
    .crd-kpi-badge {
        display:inline-block; margin-top:8px; padding:2px 9px; border-radius:20px;
        font-family:'IBM Plex Mono', monospace; font-size:11px; font-weight:600;
        background: rgba(34,197,94,.12); color:#4ADE80;
    }
    .crd-kpi-badge.down { background: rgba(239,68,68,.12); color:#F87171; }

    /* AI Recommendation kart */
    .crd-ai-card {
        background: linear-gradient(135deg, rgba(124,92,255,.14), rgba(34,211,238,.06));
        border: 1px solid rgba(124,92,255,.3);
        border-radius: 22px; padding: 26px 30px; margin-bottom: 24px;
        box-shadow: 0 0 40px rgba(124,92,255,.08);
    }
    .crd-ai-eyebrow {
        font-family:'IBM Plex Mono', monospace; font-size:11px; letter-spacing:.12em;
        text-transform:uppercase; color:#A78BFA; margin-bottom:8px; font-weight:700;
    }
    .crd-ai-title { font-size:20px; font-weight:700; color:#F5F6FD; margin-bottom:18px; }
    .crd-ai-metrics { display:flex; gap:32px; flex-wrap:wrap; margin-bottom: 6px; }
    .crd-ai-metric-label {
        font-family:'IBM Plex Mono', monospace; font-size:10.5px; text-transform:uppercase;
        letter-spacing:.08em; color:#8B93C7; margin-bottom:4px;
    }
    .crd-ai-metric-value { font-size:24px; font-weight:700; color:#F5F6FD; font-family:'IBM Plex Mono', monospace;}
    .crd-ai-metric-value.pos { color:#4ADE80; }

    /* Sekme grubu */
    div[data-baseweb="tab-list"] {
        display:flex; justify-content:center; gap:6px; border-bottom:none;
        background: rgba(17,24,45,.7); padding:6px; border-radius:14px; margin:0 auto 26px auto;
        max-width:640px; border:1px solid rgba(255,255,255,.06);
        backdrop-filter: blur(12px);
    }
    button[data-baseweb="tab"] {
        font-family:'Inter', sans-serif; font-weight:600; font-size:14.5px; color:#8B93C7 !important;
        border-radius:10px; padding:10px 18px !important; border:none !important;
        transition: all .15s ease;
    }
    button[data-baseweb="tab"]:hover { background: rgba(124,92,255,.1); }
    button[aria-selected="true"] {
        background: linear-gradient(90deg, #7C5CFF, #22D3EE) !important;
        color: #070B1F !important;
        box-shadow: 0 2px 12px rgba(124,92,255,.35);
    }
    button[aria-selected="true"] p { color: #070B1F !important; font-weight:700 !important; }
    div[data-baseweb="tab-highlight"] { display:none; }
    div[data-baseweb="tab-border"] { display:none; }

    /* Risk rozetleri */
    .risk-badge {
        display:inline-block; padding:4px 11px; border-radius:20px;
        font-family:'IBM Plex Mono', monospace; font-size:12px; font-weight:600;
    }
    .risk-high { background: rgba(239,68,68,.15); color:#F87171; border:1px solid rgba(239,68,68,.25); }
    .risk-mid  { background: rgba(245,158,11,.15); color:#FBBF24; border:1px solid rgba(245,158,11,.25); }
    .risk-low  { background: rgba(34,197,94,.15); color:#4ADE80; border:1px solid rgba(34,197,94,.25); }

    /* Genel kart */
    .crd-card {
        background: linear-gradient(145deg, rgba(17,24,45,.9), rgba(17,24,45,.6));
        border-radius:20px; padding:24px 28px;
        border:1px solid rgba(255,255,255,.08);
        box-shadow: 0 4px 24px rgba(0,0,0,.2);
        backdrop-filter: blur(16px);
    }
    .crd-card h4 {
        margin-top:0; font-size:16px; color:#F5F6FD;
        display:flex; align-items:center; gap:8px; font-weight:700;
    }
    .crd-field { font-size:14px; margin-bottom:8px; color:#A8AEC7; }
    .crd-field b { color:#F5F6FD; }

    .stButton button[kind="primary"] {
        border-radius:12px; font-weight:700; font-family:'Inter',sans-serif;
        background: linear-gradient(90deg, #7C5CFF, #22D3EE) !important;
        color:#070B1F !important; border:none !important;
        transition: box-shadow .2s ease, transform .15s ease;
    }
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 0 24px rgba(124,92,255,.5);
        transform: translateY(-1px);
    }
    .stButton button[kind="secondary"] {
        border-radius:12px; font-weight:600; font-family:'Inter',sans-serif;
        background: rgba(17,24,45,.6) !important;
        color:#A8AEC7 !important; border:1px solid rgba(255,255,255,.1) !important;
        transition: all .15s ease;
    }
    .stButton button[kind="secondary"]:hover {
        background: rgba(124,92,255,.15) !important;
        color:#F5F6FD !important;
        border-color: rgba(124,92,255,.3) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0F26, #070B1F);
        border-right: 1px solid rgba(255,255,255,.06);
    }
    section[data-testid="stSidebar"] * { color: #C7CCE8 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #F5F6FD !important; font-family: 'Inter', sans-serif; font-weight:700;
    }
    section[data-testid="stSidebar"] .stAlert {
        background: rgba(124,92,255,.1); border: 1px solid rgba(124,92,255,.25); border-radius:12px;
    }
    section[data-testid="stSidebar"] label { color: #8B93C7 !important; font-size:13px; }
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(17,24,45,.9) !important; border: 1px solid rgba(255,255,255,.15) !important;
        border-radius:10px !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] span { color: #F5F6FD !important; }
    section[data-testid="stSidebar"] svg { fill: #A8AEC7 !important; }
    /* Daha agresif kapsama - Streamlit surumune gore ic yapı degisebiliyor */
    section[data-testid="stSidebar"] div[data-baseweb="select"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] div {
        background-color: rgba(17,24,45,.95) !important;
        color: #F5F6FD !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] input {
        color: #F5F6FD !important;
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.08); }

    /* Tablo */
    [data-testid="stDataFrame"] { border-radius:16px; overflow:hidden; }

    /* Ana icerikteki text_area, selectbox, input kutulari - koyu tema */
    .stTextArea textarea {
        background: rgba(17,24,45,.9) !important; color: #F5F6FD !important;
        border: 1px solid rgba(255,255,255,.12) !important; border-radius:12px !important;
    }
    .stTextInput input {
        background: rgba(17,24,45,.9) !important; color: #F5F6FD !important;
        border: 1px solid rgba(255,255,255,.12) !important; border-radius:10px !important;
    }
    div[data-baseweb="select"] > div {
        background: rgba(17,24,45,.9) !important; border: 1px solid rgba(255,255,255,.12) !important;
        border-radius:10px !important;
    }
    div[data-baseweb="select"] span { color: #F5F6FD !important; }
    div[data-baseweb="select"],
    div[data-baseweb="select"] div {
        background-color: rgba(17,24,45,.95) !important;
        color: #F5F6FD !important;
    }
    div[data-baseweb="popover"] { background: #11182D !important; }
    div[data-baseweb="popover"] li { color: #E4E7F5 !important; }
    div[data-baseweb="popover"] li:hover { background: rgba(124,92,255,.15) !important; }
    /* Slider */
    div[data-testid="stSlider"] [role="slider"] { background-color: #7C5CFF !important; }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(2) { background: #7C5CFF !important; }

    /* Expander / info / success / warning kutulari */
    [data-testid="stExpander"], .stAlert {
        background: rgba(17,24,45,.7) !important; border:1px solid rgba(255,255,255,.08) !important;
        border-radius:14px !important;
    }

    /* Rol secici basliklari */
    .role-selector-label {
        text-align:center; font-family:'IBM Plex Mono', monospace; font-size:11px;
        letter-spacing:.14em; text-transform:uppercase; color:#7076A3; margin-bottom:10px;
        font-weight:600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_html(html_str):
    """Coklu satirli HTML string'i tek satira sikistirir ve render eder.
    Streamlit/Markdown, 4+ bosluk girintili satirlari 'kod bloku' sanip
    duz metin olarak gosterebiliyor - bunu onlemek icin tum satirlari
    birlestirip girintiyi kaldiriyoruz."""
    single_line = " ".join(line.strip() for line in html_str.strip().splitlines())
    st.markdown(single_line, unsafe_allow_html=True)


def make_sparkline_svg(values, color="#7C5CFF", width=140, height=36):
    """Gercek veriden turetilmis kucuk bir SVG sparkline uretir (KPI karti icine gomulur)."""
    values = list(values)
    if len(values) < 2 or max(values) == min(values):
        return ""
    vmin, vmax = min(values), max(values)
    n = len(values)
    points = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * width
        y = height - ((v - vmin) / (vmax - vmin)) * (height - 4) - 2
        points.append(f"{x:.1f},{y:.1f}")
    line_path = "M" + " L".join(points)
    area_path = line_path + f" L{width},{height} L0,{height} Z"
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="display:block;">
        <path d="{area_path}" fill="{color}" opacity="0.12"/>
        <path d="{line_path}" fill="none" stroke="{color}" stroke-width="2"/>
    </svg>
    """


@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(
            "enriched_telco.csv bulunamadi. Once `python3 pipeline.py` calistirarak "
            "veriyi isle, sonra bu uygulamayi tekrar baslat."
        )
        st.stop()
    return pd.read_csv(DATA_PATH)


df = load_data()


@st.cache_data
def compute_best_recommendation(df):
    """Tum segmentler arasindan EN YUKSEK NET DOLAR ETKISINE (revenue-cost) sahip
    olani sec - sadece ROI orani degil, toplam is etkisi onemli (kucuk n'li
    segmentlerin sahte yuksek oranla one cikmasini engeller).
    Bu fonksiyon hem Executive Summary hem AI Copilot tarafindan kullanilir,
    boylece iki bolum arasinda CELISKILI segment onerisi cikmaz."""
    seg_stats = (
        df.groupby("ChurnReasonSegment")
        .agg(
            n_total=("customerID", "count"),
            avg_risk=("ChurnRiskScore", "mean"),
            clv_at_risk=("EstimatedCLV", "sum"),
        )
        .sort_values("clv_at_risk", ascending=False)
    )

    results = []
    for seg in seg_stats.index:
        pool = df[(df["ChurnReasonSegment"] == seg) & (df["ChurnRiskScore"] > 0.5)]
        n = len(pool)
        if n == 0:
            continue
        conv = pool["SimulatedConversionRate"].mean()
        cost = pool["CampaignCostPerCustomer"].mean()
        clv = pool["EstimatedCLV"].mean()
        retained = n * conv
        revenue = retained * clv
        total_cost = n * cost
        roi_mult = (revenue / total_cost) if total_cost > 0 else 0
        net_roi = revenue - total_cost
        results.append({
            "segment": seg, "n": n, "retained": retained, "revenue": revenue,
            "cost": total_cost, "roi_mult": roi_mult, "net_roi": net_roi,
        })

    if not results:
        return None

    best = max(results, key=lambda r: r["net_roi"])
    best["top_clv_segment"] = seg_stats.index[0]
    best["top_risk_segment"] = seg_stats.sort_values("avg_risk", ascending=False).index[0]
    return best


BEST_RECOMMENDATION = compute_best_recommendation(df)


@st.cache_data
def get_segment_stats(df):
    """Tum uygulamada tekrar tekrar hesaplanan segment ozet tablosunu TEK YERDE,
    onbellekli olarak uretir. Musteri Listesi ve Executive Summary bolumleri
    bunu paylasir - hem performans hem tutarlilik icin."""
    return (
        df.groupby("ChurnReasonSegment")
        .agg(
            n=("customerID", "count"),
            avg_risk=("ChurnRiskScore", "mean"),
            clv_at_risk=("EstimatedCLV", "sum"),
            conv=("SimulatedConversionRate", "mean"),
            cost=("CampaignCostPerCustomer", "mean"),
        )
        .rename(columns={"n": "musteri_sayisi", "avg_risk": "ortalama_risk"})
        .sort_values("clv_at_risk", ascending=False)
    )


@st.cache_data
def get_kpi_histograms(tenure_vals, risk_vals, clv_vals):
    """Sparkline'lar icin histogram bin sayimlarini onbellekler."""
    tenure_hist, _ = np.histogram(tenure_vals, bins=16)
    risk_hist, _ = (np.histogram(risk_vals, bins=16) if len(risk_vals) > 1 else (np.array([0, 0]), None))
    clv_hist, _ = (np.histogram(clv_vals, bins=16) if len(clv_vals) > 1 else (np.array([0, 0]), None))
    return tenure_hist, risk_hist, clv_hist


import base64


def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


def get_sinyo_base64():
    sinyo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sinyo.jpeg")
    if os.path.exists(sinyo_path):
        with open(sinyo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


SINYO_B64 = get_sinyo_base64()
SINYO_IMG_TAG = (
    f'<img src="data:image/jpeg;base64,{SINYO_B64}" style="width:52px; height:auto; '
    f'border-radius:12px; flex-shrink:0;" />' if SINYO_B64 else "🤖"
)


_logo_b64 = get_logo_base64()
if _logo_b64:
    render_html(
        f"""
        <div class="crd-header" style="text-align:center;">
            <img src="data:image/jpeg;base64,{_logo_b64}"
                 style="width:110px; height:110px; border-radius:20px; margin-bottom:14px;
                        box-shadow:0 0 30px rgba(124,92,255,.25);" />
            <div class="crd-tagline" style="font-size:15px;">Predict. Personalize. Retain.</div>
        </div>
        """
    )
else:
    render_html(
        """
        <div class="crd-header" style="text-align:center;">
            <div class="crd-brand-row" style="justify-content:center;">
                <div class="crd-brand-badge">◈</div>
                <div class="crd-eyebrow" style="margin:0; font-size:15px;">Churn Simulator AI</div>
            </div>
            <div class="crd-tagline" style="font-size:15px; margin-top:14px;">Predict. Personalize. Retain.</div>
        </div>
        """
    )

# ---------- Rol secici ----------
ROLES = [
    ("👔 Yönetici", "executive"),
    ("📣 Pazarlama Ekibi", "marketing"),
    ("🎯 Retention Manager", "retention"),
]

if "user_role" not in st.session_state:
    st.session_state["user_role"] = "executive"

render_html('<div class="role-selector-label">Rolünü Seç</div>')

_role_cols = st.columns(len(ROLES))
for _col, (_label, _value) in zip(_role_cols, ROLES):
    with _col:
        is_active = st.session_state["user_role"] == _value
        if st.button(
            _label,
            key=f"role_btn_{_value}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["user_role"] = _value
            st.rerun()

user_role = st.session_state["user_role"]

_env_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if _env_api_key:
    st.session_state["api_key"] = _env_api_key
else:
    st.sidebar.header("⚙️ Claude API Ayarı")
    api_key_input = st.sidebar.text_input(
        "Anthropic API Key", type="password", value=st.session_state.get("api_key", ""),
        help="SMS metni üretmek için gerekli. console.anthropic.com üzerinden alabilirsin.",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

if not ANTHROPIC_AVAILABLE:
    st.sidebar.warning("`pip install anthropic` çalıştırman gerekiyor.")

st.sidebar.markdown("---")
st.sidebar.header("Filtreler")
st.sidebar.caption("Bu filtreler sadece 📋 Müşteri Listesi sekmesindeki tabloyu etkiler.")

segments = ["Tümü"] + sorted(df["ChurnReasonSegment"].unique().tolist())
selected_segment = st.sidebar.selectbox(
    "Segment",
    segments,
    help="Sadece belirli bir churn nedenine sahip müşterileri göster. "
         "Örn. 'Fiyat Duyarlı' seçersen sadece o gruptaki müşteriler listelenir.",
)
min_risk = st.sidebar.slider(
    "Minimum Churn Riski",
    0.0, 1.0, 0.0, 0.05,
    help="Sadece bu değerin ÜZERİNDE risk skoruna sahip müşterileri göster. "
         "0.50 = müşterinin %50+ ihtimalle ayrılacağı tahmin ediliyor demek. "
         "Değeri yükselttikçe liste daralır, sadece en riskli müşteriler kalır.",
)
sort_option = st.sidebar.selectbox(
    "Sırala",
    ["Risk (yüksekten düşüğe)", "Tahmini CLV (yüksekten düşüğe)", "Tenure (düşükten yükseğe)"],
    help="Tablodaki müşterilerin hangi sıraya göre listeleneceğini belirler. "
         "Örn. 'Tahmini CLV' seçersen en değerli müşteriler en üstte çıkar.",
)

filtered = df.copy()
if selected_segment != "Tümü":
    filtered = filtered[filtered["ChurnReasonSegment"] == selected_segment]
filtered = filtered[filtered["ChurnRiskScore"] >= min_risk]
if sort_option.startswith("Risk"):
    filtered = filtered.sort_values("ChurnRiskScore", ascending=False)
elif sort_option.startswith("Tahmini"):
    filtered = filtered.sort_values("EstimatedCLV", ascending=False)
else:
    filtered = filtered.sort_values("tenure", ascending=True)

at_risk_count = len(df[df['ChurnRiskScore'] > 0.5])
at_risk_pct = at_risk_count / len(df) * 100
at_risk_clv = df[df['ChurnRiskScore'] > 0.5]['EstimatedCLV'].sum()
avg_at_risk_clv = df[df['ChurnRiskScore'] > 0.5]['EstimatedCLV'].mean()

# KPI kartlari icin SEGMENTE DUYARLI istatistikler (sol panelden segment secilince guncellenir)
if selected_segment != "Tümü":
    _segment_scope = df[df["ChurnReasonSegment"] == selected_segment]
else:
    _segment_scope = df
segment_at_risk_count = len(_segment_scope[_segment_scope["ChurnRiskScore"] > 0.5])
segment_at_risk_pct = (segment_at_risk_count / len(_segment_scope) * 100) if len(_segment_scope) > 0 else 0
segment_at_risk_clv = _segment_scope[_segment_scope["ChurnRiskScore"] > 0.5]["EstimatedCLV"].sum()
segment_avg_at_risk_clv = (
    _segment_scope[_segment_scope["ChurnRiskScore"] > 0.5]["EstimatedCLV"].mean()
    if segment_at_risk_count > 0 else 0
)
_risk_badge_text = f"%{segment_at_risk_pct:.1f} of {'segment' if selected_segment != 'Tümü' else 'total'}"

# Sparkline verileri - gercek dagilimlardan turetilmis, onbellekli hesaplanir
_segment_at_risk_pool = _segment_scope[_segment_scope["ChurnRiskScore"] > 0.5]
tenure_hist, risk_hist, atrisk_clv_hist = get_kpi_histograms(
    df["tenure"], _segment_scope["ChurnRiskScore"], _segment_at_risk_pool["EstimatedCLV"]
)
filtered_risk_hist, _ = np.histogram(filtered["ChurnRiskScore"], bins=16) if len(filtered) > 1 else (np.array([0, 0]), None)

render_html(
    f"""
    <div class="crd-kpi-row">
        <div class="crd-kpi">
            <div class="crd-kpi-top">
                <div class="crd-kpi-icon">👥</div>
            </div>
            <div class="crd-kpi-label">Toplam Müşteri</div>
            <div class="crd-kpi-value">{len(df):,}</div>
            <div class="crd-kpi-badge">Ort. tenure {df['tenure'].mean():.0f} ay</div>
            {make_sparkline_svg(tenure_hist, "#7C5CFF")}
        </div>
        <div class="crd-kpi warn">
            <div class="crd-kpi-top">
                <div class="crd-kpi-icon">⚠️</div>
            </div>
            <div class="crd-kpi-label">Yüksek Risk (&gt;%50){' — ' + selected_segment if selected_segment != 'Tümü' else ''}</div>
            <div class="crd-kpi-value">{segment_at_risk_count:,}</div>
            <div class="crd-kpi-badge down">{_risk_badge_text}</div>
            {make_sparkline_svg(risk_hist, "#FF5D8F") if risk_hist is not None and len(risk_hist) > 1 else ''}
        </div>
        <div class="crd-kpi">
            <div class="crd-kpi-top">
                <div class="crd-kpi-icon">💰</div>
            </div>
            <div class="crd-kpi-label">Riskteki Tahmini CLV{' — ' + selected_segment if selected_segment != 'Tümü' else ''}</div>
            <div class="crd-kpi-value">${segment_at_risk_clv:,.0f}</div>
            <div class="crd-kpi-badge">Ort. ${segment_avg_at_risk_clv:,.0f}/müşteri</div>
            {make_sparkline_svg(atrisk_clv_hist, "#22D3EE") if atrisk_clv_hist is not None and len(atrisk_clv_hist) > 1 else ''}
        </div>
        <div class="crd-kpi">
            <div class="crd-kpi-top">
                <div class="crd-kpi-icon">🎯</div>
            </div>
            <div class="crd-kpi-label">Filtrelenen Sonuç</div>
            <div class="crd-kpi-value">{len(filtered):,}</div>
            <div class="crd-kpi-badge">{selected_segment}</div>
            {make_sparkline_svg(filtered_risk_hist, "#7C5CFF") if len(filtered) > 1 else ''}
        </div>
    </div>
    """
)

if "alert_pool" not in st.session_state:
    pool = df[df["ChurnRiskScore"] > 0.5]["customerID"].tolist()
    random.seed(7)
    random.shuffle(pool)
    st.session_state["alert_pool"] = pool
if "alert_feed" not in st.session_state:
    st.session_state["alert_feed"] = []
if "selected_customer" not in st.session_state:
    st.session_state["selected_customer"] = None
if "generated_sms" not in st.session_state:
    st.session_state["generated_sms"] = {}


def risk_badge_html(x):
    if x > 0.6:
        return f'<span class="risk-badge risk-high">🔴 {x*100:.0f}%</span>'
    elif x > 0.3:
        return f'<span class="risk-badge risk-mid">🟡 {x*100:.0f}%</span>'
    return f'<span class="risk-badge risk-low">🟢 {x*100:.0f}%</span>'


ALL_TABS = {
    "🤖 AI Copilot": "copilot",
    "🔔 Canlı Uyarılar": "alerts",
    "📋 Müşteri Listesi": "list",
    "💰 ROI Simülasyonu": "roi",
}

ROLE_TAB_MAP = {
    "executive": ["🤖 AI Copilot", "💰 ROI Simülasyonu"],
    "marketing": ["📋 Müşteri Listesi", "🔔 Canlı Uyarılar", "💰 ROI Simülasyonu", "🤖 AI Copilot"],
    "retention": ["🔔 Canlı Uyarılar", "🤖 AI Copilot"],
}

visible_tab_labels = ROLE_TAB_MAP[user_role]
role_names = {"executive": "Yönetici", "marketing": "Pazarlama Ekibi", "retention": "Retention Manager"}
st.caption(f"📍 Şu an **{role_names[user_role]}** görünümündesin — bu role özel {len(visible_tab_labels)} ekran gösteriliyor.")

# ---------- AI Executive Briefing (sadece Yonetici rolunde) ----------
if user_role == "executive":
    seg_summary_exec = get_segment_stats(df)

    # Tum uygulamada TUTARLI tek bir oneri kaynagi (net dolar etkisine gore secilir)
    rec = BEST_RECOMMENDATION
    top_segment_clv = rec["top_clv_segment"]
    rec_segment = rec["segment"]
    rec_n = rec["n"]
    rec_retained = rec["retained"]
    rec_revenue = rec["revenue"]
    rec_total_cost = rec["cost"]
    rec_roi_mult = rec["roi_mult"]

    fallback_summary = (
        f"<span style='color:#FF93AF; font-weight:700;'>%{at_risk_pct:.1f}</span> müşteri tabanı "
        f"(<span style='font-family:\"IBM Plex Mono\",monospace;'>{at_risk_count:,}</span> müşteri) "
        f"şu an yüksek risk taşıyor, toplam "
        f"<span style='color:#5EEAD4; font-weight:700;'>${at_risk_clv:,.0f}</span> tahmini gelir riskte. "
        f"En yoğun segment <b>{top_segment_clv}</b>. Önerimiz <b>{rec_segment}</b> "
        f"segmentine kampanya başlatmak — beklenen net "
        f"<span style='color:#4ADE80; font-weight:700;'>${rec_revenue - rec_total_cost:,.0f}</span> gelir kazancı "
        f"({rec_roi_mult:.1f}x getiri)."
    )

    ai_col1, ai_col2 = st.columns([5, 1])
    with ai_col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        refresh_clicked = st.button("🔄 AI Özeti Üret", key="refresh_exec_summary", use_container_width=True, type="primary")
    ai_col1.caption(
        "Rakamlar (hedef müşteri, ROI vb.) her sayfa yüklemesinde veriden otomatik hesaplanır. "
        "Buton sadece bu rakamları AI ile *doğal dilde anlatan cümleyi* yeniler."
    )

    if refresh_clicked:
        api_key = st.session_state.get("api_key", "")
        if not api_key or not ANTHROPIC_AVAILABLE:
            st.session_state["exec_summary_html"] = fallback_summary
            if not api_key:
                ai_col1.warning("API key girilmedi, şablon özet gösteriliyor. Sol panelden key gir.")
        else:
            with st.spinner("AI özet oluşturuyor..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    prompt = f"""Sen bir telekom sirketinde CEO/CMO'ya sunum yapan bir veri analistisin.
Asagidaki GERCEK verilere dayanarak, yoneticiye 2-3 cumlelik kisa bir Turkce ozet yaz.

Toplam musteri: {len(df):,}
Yuksek riskli musteri (>%50): {at_risk_count:,} (%{at_risk_pct:.1f})
Riskteki toplam tahmini CLV: ${at_risk_clv:,.0f}
En yuksek CLV riski tasiyan segment: {top_segment_clv}
Onerilen kampanya segmenti (net dolar etkisine gore en iyisi): {rec_segment}
Onerilen kampanya hedef kitlesi: {rec_n} musteri
Beklenen kurtarilan musteri: {rec_retained:.0f}
Beklenen gelir: ${rec_revenue:,.0f}
Kampanya maliyeti: ${rec_total_cost:,.0f}
Net kazanc: ${rec_revenue - rec_total_cost:,.0f}
ROI carpani: {rec_roi_mult:.1f}x

Kurallar:
- SADECE yukaridaki sayilari kullan, uydurma sayi ekleme.
- Onerilen segmenti MUTLAKA acikca ismiyle belirt (belirsiz birakma).
- Yonetici diline uygun, kisa, net, aksiyon odakli yaz.
- 2-3 cumle, HTML/markdown formatlamasi kullanma, duz metin yaz.
- "Onerimiz" gibi bir ifadeyle kampanya onerisini vurgula."""
                    response = client.messages.create(
                        model="claude-sonnet-5", max_tokens=300,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    ai_text = "".join(b.text for b in response.content if b.type == "text").strip()
                    st.session_state["exec_summary_html"] = ai_text
                except Exception as e:
                    st.session_state["exec_summary_html"] = fallback_summary
                    ai_col1.error(f"AI özet üretilemedi, şablon gösteriliyor: {e}")

    if "exec_summary_html" not in st.session_state:
        st.session_state["exec_summary_html"] = fallback_summary

    _exec_html = (
        '<div class="crd-ai-card">'
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">'
        + SINYO_IMG_TAG.replace("width:52px", "width:38px") +
        '<div class="crd-ai-eyebrow" style="margin:0;">Sinyo\'nun Kampanya Önerisi</div>'
        '</div>'
        '<div style="font-size:19px; line-height:1.7; color:#F5F6FD; font-weight:500; margin-bottom:20px; white-space:pre-wrap;">'
        + st.session_state['exec_summary_html'] +
        '</div>'
        '<div class="crd-ai-metrics">'
        f'<div><div class="crd-ai-metric-label">Hedef Müşteri ({rec_segment})</div><div class="crd-ai-metric-value">{rec_n}</div></div>'
        f'<div><div class="crd-ai-metric-label">Beklenen Kurtarılan</div><div class="crd-ai-metric-value pos">{rec_retained:,.0f}</div></div>'
        f'<div><div class="crd-ai-metric-label">Beklenen Gelir</div><div class="crd-ai-metric-value pos">${rec_revenue:,.0f}</div></div>'
        f'<div><div class="crd-ai-metric-label">Kampanya Maliyeti</div><div class="crd-ai-metric-value">${rec_total_cost:,.0f}</div></div>'
        '</div>'
        '</div>'
    )
    st.markdown(_exec_html, unsafe_allow_html=True)

    st.markdown("##### Segmentlere Göre Riskteki Gelir")
    st.caption(
        "Bu grafik **toplam riskteki gelire (CLV)** göre sıralıdır. Bir üstteki AI önerisi ise "
        "**net dolar kazancına** göre seçilir — bu ikisi bazen farklı segmentleri işaret edebilir, "
        "bu normal: biri 'nerede risk yoğun' sorusuna, diğeri 'nereye kampanya en kârlı' sorusuna cevap verir."
    )
    seg_chart_df = seg_summary_exec.reset_index().sort_values("clv_at_risk", ascending=True)
    fig = go.Figure(go.Bar(
        x=seg_chart_df["clv_at_risk"], y=seg_chart_df["ChurnReasonSegment"],
        orientation="h",
        marker=dict(color=["#7C5CFF", "#22D3EE", "#4ADE80", "#FF5D8F", "#F59E0B", "#6B7299"][:len(seg_chart_df)]),
        text=[f"${v:,.0f}" for v in seg_chart_df["clv_at_risk"]],
        textposition="outside",
        textfont=dict(color="#A8AEC7", size=11),
    ))
    fig.update_layout(
        margin=dict(l=0, r=60, t=10, b=10), height=260,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(tickfont=dict(color="#A8AEC7", size=12)),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(
        "* Bu özet gerçek segment/risk verilerinden hesaplanmıştır (zaman serisi değildir, "
        "statik anlık görüntüdür). Kampanya maliyeti/dönüşüm oranları varsayımsaldır."
    )
    st.markdown("---")

if "active_tab" not in st.session_state or st.session_state["active_tab"] not in visible_tab_labels:
    st.session_state["active_tab"] = visible_tab_labels[0]

_tab_cols = st.columns(len(visible_tab_labels))
for _tcol, _label in zip(_tab_cols, visible_tab_labels):
    with _tcol:
        _is_active_tab = st.session_state["active_tab"] == _label
        if st.button(
            _label, key=f"tabbtn_{_label}", use_container_width=True,
            type="primary" if _is_active_tab else "secondary",
        ):
            st.session_state["active_tab"] = _label
            st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

active_tab = st.session_state["active_tab"]

if active_tab == "🤖 AI Copilot":
    render_html(
        f"""<div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
        {SINYO_IMG_TAG}
        <div>
            <div style="font-size:17px; font-weight:700; color:#F5F6FD;">Sinyo ile konuş</div>
            <div style="font-size:13px; color:#8B93C7;">Akıllı asistanın — veri hakkında ne merak ediyorsan sor.</div>
        </div>
        </div>"""
    )
    st.caption(
        "Veri hakkında doğal dilde soru sor — cevaplar gerçek veriden (en riskli müşteriler, "
        "segment istatistikleri) türetilir, uydurma değildir."
    )

    example_questions = [
        "Bugün kimi aramalıyız?",
        "Hangi segment en riskli?",
        "En değerli riskli müşteriler kim?",
        "Hangi kampanya en kârlı?",
    ]
    ex_cols = st.columns(len(example_questions))
    for i, q in enumerate(example_questions):
        if ex_cols[i].button(q, key=f"ex_q_{i}", use_container_width=True):
            st.session_state["copilot_input"] = q
            st.rerun()

    user_question = st.text_input(
        "Sorunu yaz",
        placeholder="Örn: Bugün hangi 5 müşteriyi aramalıyız ve neden?",
        key="copilot_input",
    )

    if st.button("🔍 Sor", key="copilot_ask", type="primary"):
        api_key = st.session_state.get("api_key", "")
        if not user_question.strip():
            st.warning("Önce bir soru yaz.")
        elif not api_key:
            st.error("Önce sol taraftaki panelden Anthropic API key'ini gir.")
        elif not ANTHROPIC_AVAILABLE:
            st.error("`anthropic` kütüphanesi kurulu değil.")
        else:
            with st.spinner("Veriler analiz ediliyor..."):
                try:
                    # Gercek veriden bir baglam ozeti olustur (model bu sayilarin disina cikmasin diye)
                    seg_stats = (
                        df.groupby("ChurnReasonSegment")
                        .agg(
                            musteri=("customerID", "count"),
                            ort_risk=("ChurnRiskScore", "mean"),
                            toplam_clv=("EstimatedCLV", "sum"),
                            ort_donusum=("SimulatedConversionRate", "mean"),
                        )
                        .round(3)
                        .to_string()
                    )
                    top10 = (
                        df[df["ChurnRiskScore"] > 0.5]
                        .sort_values("EstimatedCLV", ascending=False)
                        .head(10)[[
                            "customerID", "ChurnRiskScore", "ChurnReasonSegment",
                            "RecommendedCampaign", "EstimatedCLV", "tenure",
                        ]]
                        .round(3)
                        .to_string(index=False)
                    )

                    context = f"""Senin adin Sinyo. Bu telekom sirketinin churn (musteri kaybi)
    onleme sisteminde calisan, akilli, cozum uretebilen, sicak ama profesyonel bir yapay
    zeka asistanisin. Sirket calisanlarina (pazarlama/retention ekibi) yardim ediyorsun.

    Asagida gercek veriden turetilmis ozet tablolar var. SADECE bu
    verilere dayanarak cevap ver, bu verilerin disinda sayi/istatistik uydurma.

    --- SEGMENT ISTATISTIKLERI ---
    {seg_stats}

    --- YUKSEK RISKLI (risk>0.5), EN DEGERLI 10 MUSTERI (CLV'ye gore siralanmis) ---
    {top10}

    --- TOPLAM ---
    Toplam musteri: {len(df)}
    Yuksek riskli musteri (>0.5): {len(df[df['ChurnRiskScore'] > 0.5])}
    Riskteki toplam tahmini CLV: ${df[df['ChurnRiskScore'] > 0.5]['EstimatedCLV'].sum():,.0f}

    --- RESMI SISTEM ONERISI (net dolar etkisine gore hesaplanmis, TUM panellerde kullanilan tek dogru kaynak) ---
    Onerilen kampanya segmenti: {BEST_RECOMMENDATION['segment']}
    Hedef musteri sayisi: {BEST_RECOMMENDATION['n']}
    Beklenen net kazanc: ${BEST_RECOMMENDATION['revenue'] - BEST_RECOMMENDATION['cost']:,.0f}
    ROI carpani: {BEST_RECOMMENDATION['roi_mult']:.1f}x

    Kullanicinin sorusu: {user_question}

    Kurallar:
    - Sinyo olarak, birinci tekil sahisla, samimi ama profesyonel bir tonda cevap ver.
    - Turkce cevap ver, kisa ve net ol (max 5-6 cumle veya kisa madde listesi).
    - Cevabini SADECE yukaridaki tablolardan cikar, tahmin/uydurma yapma.
    - Eger soru "hangi segmente/kampanyaya oncelik verelim" turundeyse, MUTLAKA yukaridaki
      "RESMI SISTEM ONERISI" bolumundeki segmenti belirt (baska panellerle celismesin).
    - Somut musteri ID'leri, segment isimleri, sayilar kullan.
    - Eger soru tablolarda cevaplanamayacak bir sey soruyorsa, bunu acikca belirt.
    - Cevabinin basinda "Ben Sinyo," gibi bir tekrar yapma, dogrudan cevaba gec (persona
      zaten ton ve uslupla hissettirilsin)."""

                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model="claude-sonnet-5",
                        max_tokens=600,
                        messages=[{"role": "user", "content": context}],
                    )
                    answer = "".join(b.text for b in response.content if b.type == "text").strip()
                    st.session_state["copilot_answer"] = answer
                except Exception as e:
                    st.error(f"Cevap üretilirken hata oluştu: {e}")

    if st.session_state.get("copilot_answer"):
        _copilot_html = (
            '<div class="crd-ai-card"><div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">'
            + SINYO_IMG_TAG.replace("width:52px", "width:36px")
            + '<div class="crd-ai-eyebrow" style="margin:0;">Sinyo diyor ki</div></div>'
            + '<div style="color:#E4E7F5; font-size:15px; line-height:1.7; white-space:pre-wrap;">'
            + st.session_state['copilot_answer'] + '</div></div>'
        )
        st.markdown(_copilot_html, unsafe_allow_html=True)

elif active_tab == "🔔 Canlı Uyarılar":
    st.caption(
        "Gerçek zamanlı bir CRM entegrasyonunda bu akış otomatik dolar. MVP'de yeni "
        "uyarıyı simüle etmek için butona tıkla."
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🆕 Yeni Uyarı Simüle Et", use_container_width=True, type="primary"):
            already_alerted = {a["customerID"] for a in st.session_state["alert_feed"]}
            candidates = df[df["ChurnRiskScore"] > 0.5]
            if selected_segment != "Tümü":
                candidates = candidates[candidates["ChurnReasonSegment"] == selected_segment]
            candidates = candidates[~candidates["customerID"].isin(already_alerted)]

            if len(candidates) > 0:
                new_id = candidates.sample(1)["customerID"].iloc[0]
                st.session_state["alert_feed"].insert(
                    0, {"customerID": new_id, "time": datetime.datetime.now().strftime("%H:%M:%S")}
                )
                st.session_state["selected_customer"] = new_id  # yeni uyarı otomatik acilsin
            else:
                st.info(
                    f"'{selected_segment}' segmentinde daha önce gösterilmemiş yüksek riskli "
                    "müşteri kalmadı. Sol panelden segmenti değiştirebilirsin."
                )
    with c2:
        st.caption(f"Şu an seçili segment: **{selected_segment}** (sol panelden değiştirebilirsin)")

    if not st.session_state["alert_feed"]:
        st.info("Henüz uyarı yok. 'Yeni Uyarı Simüle Et' butonuna tıkla.")
    elif len(st.session_state["alert_feed"]) > 1:
        with st.expander(f"📜 Geçmiş uyarılar ({len(st.session_state['alert_feed']) - 1})"):
            for alert in st.session_state["alert_feed"][1:8]:
                cust = df[df["customerID"] == alert["customerID"]].iloc[0]
                risk_pct = cust["ChurnRiskScore"] * 100
                icon = "🔴" if risk_pct > 60 else "🟡"
                label = f"{icon} [{alert['time']}] {cust['customerID']} — {cust['ChurnReasonSegment']} — Risk %{risk_pct:.0f}"
                if st.button(label, key=f"alert_{alert['customerID']}_{alert['time']}"):
                    st.session_state["selected_customer"] = cust["customerID"]

    if st.session_state["selected_customer"]:
        cust = df[df["customerID"] == st.session_state["selected_customer"]].iloc[0]
        st.markdown("<br>", unsafe_allow_html=True)
        card_col1, card_col2 = st.columns([1, 1])
        with card_col1:
            render_html(
                f"""<div class="crd-card"><h4>👤 Müşteri Profili</h4>
                <div class="crd-field"><b>ID:</b> {cust['customerID']}</div>
                <div class="crd-field"><b>Risk:</b> {risk_badge_html(cust['ChurnRiskScore'])}</div>
                <div class="crd-field"><b>Segment:</b> {cust['ChurnReasonSegment']}</div>
                <div class="crd-field"><b>Tenure:</b> {cust['tenure']} ay</div>
                <div class="crd-field"><b>Aylık Ücret:</b> ${cust['MonthlyCharges']:.2f}</div>
                <div class="crd-field"><b>Sözleşme:</b> {cust['Contract']}</div>
                <div class="crd-field"><b>İnternet:</b> {cust['InternetService']}</div>
                <div class="crd-field"><b>Tahmini CLV:</b> ${cust['EstimatedCLV']:,.0f}</div>
                </div>"""
            )
        with card_col2:
            render_html(
                f"""<div class="crd-card"><h4>🎯 Önerilen Aksiyon</h4>
                <div class="crd-field"><b>Kampanya:</b> {cust['RecommendedCampaign']}</div>
                <div class="crd-field"><b>Varsayılan Dönüşüm:</b> ~%{cust['SimulatedConversionRate']*100:.0f}</div>
                <div class="crd-field"><b>Maliyet:</b> ${cust['CampaignCostPerCustomer']:.0f}/müşteri</div>
                </div>"""
            )
            st.markdown("<br>", unsafe_allow_html=True)
            render_html(
                f"""<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                {SINYO_IMG_TAG.replace("width:52px", "width:34px")}
                <div style="font-size:13px; color:#8B93C7;">Sinyo bu müşteriye nasıl ulaşmak istersin?</div>
                </div>"""
            )

            if "generated_whatsapp" not in st.session_state:
                st.session_state["generated_whatsapp"] = {}
            if "generated_email" not in st.session_state:
                st.session_state["generated_email"] = {}
            if "call_queue" not in st.session_state:
                st.session_state["call_queue"] = set()

            def _sinyo_channel_prompt(channel):
                base_info = f"""Musteri verisi:
    - Segment: {cust['ChurnReasonSegment']}
    - Onerilen kampanya: {cust['RecommendedCampaign']}
    - Musterilik suresi: {cust['tenure']} ay
    - Aylik odeme: {cust['MonthlyCharges']:.0f} TL
    - Sozlesme tipi: {cust['Contract']}"""

                persona = """Senin adin Sinyo. Bir telekom sirketi icin calisan, musterilere ozel
    kampanyalar ureten akilli bir robotsun. Kisiligin: Sicak, enerjik, cozum odakli,
    samimi ama saygili. Robot kimligini gizleme, bunu sevimli bir ozellik gibi kullan."""

                common_rules = """Kurallar:
    - SADECE nihai, temiz metni yaz. Taslak, aciklama, dipnot, kendi kendini
      duzeltme YOK.
    - Onerilen kampanyayi SOMUT bir rakamla anlat.
    - Musterilik suresini dogru say (yil degil, ay - eger 12'den kucukse).
    - Eylem cagrisi ile bitir, KESINLIKLE soru cumlesi kurma (soru isareti yok),
      emir kipiyle net bir yonlendirme yap."""

                if channel == "whatsapp":
                    return f"""{persona}

    {base_info}

    Musteriye WhatsApp'tan gonderilecek bir mesaj yaz. WhatsApp SMS'ten daha
    rahat/samimi olabilir, 1-2 emoji kullanabilirsin (abartmadan), 2-4 cumle
    olabilir (SMS'ten biraz daha uzun olabilir).

    {common_rules}

    Cikti SADECE mesaj metni olsun, baska hicbir sey yazma (JSON degil, duz metin)."""

                elif channel == "email":
                    return f"""{persona}

    {base_info}

    Musteriye e-posta gonderilecek. Once konu satirini, sonra bos satir, sonra
    e-posta govdesini yaz. E-posta SMS'ten daha resmi/detayli olabilir (4-6 cumle),
    ama hala Sinyo'nun sicak tonunu koru.

    {common_rules}

    Cikti TAM OLARAK su formatta olsun:
    KONU: [konu satiri]

    [e-posta govdesi]

    Baska hicbir aciklama ekleme."""

                return None  # sms zaten ayri yonetiliyor

            ch_col1, ch_col2, ch_col3, ch_col4 = st.columns(4)

            with ch_col1:
                sms_clicked = st.button("💬 SMS", key=f"sms_btn_{cust['customerID']}", use_container_width=True, type="primary")
            with ch_col2:
                wa_clicked = st.button("🟢 WhatsApp", key=f"wa_btn_{cust['customerID']}", use_container_width=True, type="primary")
            with ch_col3:
                email_clicked = st.button("📧 E-posta", key=f"email_btn_{cust['customerID']}", use_container_width=True, type="primary")
            with ch_col4:
                call_clicked = st.button("📞 Arama Planla", key=f"call_btn_{cust['customerID']}", use_container_width=True, type="primary")

            api_key = st.session_state.get("api_key", "")

            if call_clicked:
                st.session_state["call_queue"].add(cust["customerID"])
                st.success(
                    f"📞 Sinyo, {cust['customerID']} numaralı müşteriyi arama listesine ekledi. "
                    "(Gerçek entegrasyonda bu, çağrı merkezi kuyruğuna otomatik düşer.)"
                )

            if sms_clicked:
                if not api_key:
                    st.error("Önce sol taraftaki panelden Anthropic API key'ini gir.")
                elif not ANTHROPIC_AVAILABLE:
                    st.error("`anthropic` kütüphanesi kurulu değil.")
                else:
                    with st.spinner("Sinyo SMS hazırlıyor..."):
                        try:
                            client = anthropic.Anthropic(api_key=api_key)
                            prompt = f"""Senin adin Sinyo. Bir telekom sirketi icin calisan, musterilere
    ozel kampanyalar ureten akilli bir robotsun. Musteriye gonderilecek SMS'i SEN
    yaziyorsun - bu mesaj senin agzindan, senin kisiligini yansitan bir mesaj.

    Kisiligin: Sicak, enerjik, cozum odakli, samimi ama saygili. Musteriye "senin
    icin ozel bir sey buldum/hazirladim" hissi veren, robot ama sevimli bir asistan.

    Asagidaki musteri bilgisine gore, churn (musteri kaybi) riskini azaltmayi
    hedefleyen, SMS ile gonderilecek TEK bir mesaj yaz.

    Musteri verisi:
    - Segment: {cust['ChurnReasonSegment']}
    - Onerilen kampanya: {cust['RecommendedCampaign']}
    - Musterilik suresi: {cust['tenure']} ay
    - Aylik odeme: {cust['MonthlyCharges']:.0f} TL
    - Sozlesme tipi: {cust['Contract']}

    Kurallar (kesinlikle uy):
    1. SADECE nihai, temiz SMS metnini yaz. Ilk taslak, aciklama, alternatif,
       dipnot, yildizli not (*), kendi kendini duzeltme YOK. Tek seferde dogru
       ve son halini yaz.
    2. Mesaj Sinyo'nun agzindan gitmeli - "Ben Sinyo," ile ya da dogrudan
       "Senin icin [kampanya] hazirladim/buldum" gibi ilk tekil sahisla baslayabilirsin.
       Robot kimligini gizleme, bunu bir ozellik gibi kullan (sicak ve akilli bir
       asistan hissi).
    3. Turkce yaz, abartili unlemden kacin ama enerjik ve kisisel bir dil kullan.
    4. En fazla 2-3 cumle, toplamda 200 karakteri gecme.
    5. Onerilen kampanyayi SOMUT bir rakamla anlat (yuzde indirim, ay sayisi gibi -
       {cust['RecommendedCampaign']} icindeki bilgiyi kullan).
    6. Musterilik suresini dogru say: {cust['tenure']} ay (yil degil, ay olarak
       ifade et eger 12'den kucukse).
    7. Bir eylem cagrisi (CTA) ile bitir, ama KESINLIKLE soru cumlesi kurma
       (soru isareti "?" kullanma). Emir kipiyle, net ve aciliyet hissi veren bir
       yonlendirme yap: "Hemen aktif et.", "Vakit kaybetmeden uygulamayi ac.",
       "Bu firsati kacirma, hemen basvur." gibi.

    Ornek stil (bunu birebir kopyalama, sadece tonu ve yapiyi anla):
    "Ben Sinyo! Senin icin ozel bir firsat buldum: [kampanya] ile %15 indirim
    tanimladim. Vakit kaybetmeden hemen uygulamaya gir ve firsati kacirma."

    Cikti SADECE SMS metni olsun, baska hicbir sey yazma."""
                            response = client.messages.create(
                                model="claude-sonnet-5", max_tokens=300,
                                messages=[{"role": "user", "content": prompt}],
                            )
                            sms_text = "".join(b.text for b in response.content if b.type == "text").strip()
                            if not sms_text:
                                st.warning(
                                    "API cevap verdi ama SMS metni boş geldi. "
                                    f"Ham cevap: {response.content}"
                                )
                            st.session_state["generated_sms"][cust["customerID"]] = sms_text
                        except Exception as e:
                            st.error(f"SMS oluşturulurken hata oluştu: {type(e).__name__}: {e}")

            if wa_clicked:
                if not api_key:
                    st.error("Önce sol taraftaki panelden Anthropic API key'ini gir.")
                elif not ANTHROPIC_AVAILABLE:
                    st.error("`anthropic` kütüphanesi kurulu değil.")
                else:
                    with st.spinner("Sinyo WhatsApp mesajı hazırlıyor..."):
                        try:
                            client = anthropic.Anthropic(api_key=api_key)
                            response = client.messages.create(
                                model="claude-sonnet-5", max_tokens=400,
                                messages=[{"role": "user", "content": _sinyo_channel_prompt("whatsapp")}],
                            )
                            wa_text = "".join(b.text for b in response.content if b.type == "text").strip()
                            st.session_state["generated_whatsapp"][cust["customerID"]] = wa_text
                        except Exception as e:
                            st.error(f"WhatsApp mesajı oluşturulurken hata: {type(e).__name__}: {e}")

            if email_clicked:
                if not api_key:
                    st.error("Önce sol taraftaki panelden Anthropic API key'ini gir.")
                elif not ANTHROPIC_AVAILABLE:
                    st.error("`anthropic` kütüphanesi kurulu değil.")
                else:
                    with st.spinner("Sinyo e-posta hazırlıyor..."):
                        try:
                            client = anthropic.Anthropic(api_key=api_key)
                            response = client.messages.create(
                                model="claude-sonnet-5", max_tokens=500,
                                messages=[{"role": "user", "content": _sinyo_channel_prompt("email")}],
                            )
                            email_text = "".join(b.text for b in response.content if b.type == "text").strip()
                            st.session_state["generated_email"][cust["customerID"]] = email_text
                        except Exception as e:
                            st.error(f"E-posta oluşturulurken hata: {type(e).__name__}: {e}")

            if cust["customerID"] in st.session_state["generated_sms"]:
                st.text_area(
                    "💬 Oluşturulan SMS", value=st.session_state["generated_sms"][cust["customerID"]],
                    height=120, key=f"sms_text_{cust['customerID']}",
                )
            if cust["customerID"] in st.session_state["generated_whatsapp"]:
                st.text_area(
                    "🟢 Oluşturulan WhatsApp Mesajı", value=st.session_state["generated_whatsapp"][cust["customerID"]],
                    height=140, key=f"wa_text_{cust['customerID']}",
                )
            if cust["customerID"] in st.session_state["generated_email"]:
                st.text_area(
                    "📧 Oluşturulan E-posta", value=st.session_state["generated_email"][cust["customerID"]],
                    height=180, key=f"email_text_{cust['customerID']}",
                )
            if cust["customerID"] in st.session_state["call_queue"]:
                st.caption("📞 Bu müşteri arama listesinde.")

elif active_tab == "📋 Müşteri Listesi":
    seg_summary = (
        get_segment_stats(df)
        .reset_index().sort_values("musteri_sayisi", ascending=False)
    )

    def _dark_bar_chart(x_col, y_col, color, title, y_is_pct=False):
        fig = go.Figure(go.Bar(
            x=seg_summary[x_col], y=seg_summary[y_col], marker=dict(color=color),
            text=[f"%{v*100:.0f}" if y_is_pct else f"{v:,.0f}" for v in seg_summary[y_col]],
            textposition="outside", textfont=dict(color="#E4E7F5", size=11),
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=60), height=260,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#C7CCE8", size=11), tickangle=-30),
            yaxis=dict(visible=False),
            showlegend=False,
        )
        return fig

    g1, g2 = st.columns([1, 1])
    with g1:
        st.caption("Segment Dağılımı (müşteri sayısı)")
        st.plotly_chart(
            _dark_bar_chart("ChurnReasonSegment", "musteri_sayisi", "#7C5CFF", "Segment Dağılımı"),
            use_container_width=True, config={"displayModeBar": False},
        )
    with g2:
        st.caption("Segment Bazlı Ortalama Risk")
        st.plotly_chart(
            _dark_bar_chart("ChurnReasonSegment", "ortalama_risk", "#FF5D8F", "Ortalama Risk", y_is_pct=True),
            use_container_width=True, config={"displayModeBar": False},
        )

    st.markdown("##### Müşteri Akışı: Segment → Risk Seviyesi → Kampanya Sonucu")
    st.caption(
        "İlk iki aşama (Segment, Risk Seviyesi) doğrudan gerçek veriden. Üçüncü aşama "
        "(Kampanya Sonucu) sadece **Yüksek Risk** grubu için, varsayımsal dönüşüm "
        "oranlarına göre **beklenen** bir dağılımdır — gerçek kampanya sonucu değildir."
    )

    @st.cache_data
    def build_sankey_data(df):
        def _risk_level(r):
            if r > 0.6:
                return "🔴 Yüksek Risk"
            elif r > 0.3:
                return "🟡 Orta Risk"
            return "🟢 Düşük Risk"

        _sk = df.copy()
        _sk["RiskLevel"] = _sk["ChurnRiskScore"].apply(_risk_level)

        segments = sorted(_sk["ChurnReasonSegment"].unique().tolist())
        risk_levels = ["🟢 Düşük Risk", "🟡 Orta Risk", "🔴 Yüksek Risk"]
        outcomes = ["✅ Beklenen Kurtarılan", "⚠️ Beklenen Kayıp", "➖ Kampanya Gerekmiyor"]

        all_nodes = segments + risk_levels + outcomes
        node_idx = {name: i for i, name in enumerate(all_nodes)}

        sources, targets, values, link_colors = [], [], [], []
        seg_colors = ["#7C5CFF", "#22D3EE", "#4ADE80", "#FF5D8F", "#F59E0B", "#A78BFA"]
        seg_color_map = {s: seg_colors[i % len(seg_colors)] for i, s in enumerate(segments)}

        # Asama 1: Segment -> Risk Seviyesi
        for seg in segments:
            for rl in risk_levels:
                cnt = len(_sk[(_sk["ChurnReasonSegment"] == seg) & (_sk["RiskLevel"] == rl)])
                if cnt > 0:
                    sources.append(node_idx[seg])
                    targets.append(node_idx[rl])
                    values.append(cnt)
                    link_colors.append(seg_color_map[seg] + "55")

        # Asama 2: Risk Seviyesi -> Kampanya Sonucu
        # Dusuk/Orta risk -> "Kampanya Gerekmiyor" (kampanya hedeflenmiyor)
        for rl in ["🟢 Düşük Risk", "🟡 Orta Risk"]:
            cnt = len(_sk[_sk["RiskLevel"] == rl])
            if cnt > 0:
                sources.append(node_idx[rl])
                targets.append(node_idx["➖ Kampanya Gerekmiyor"])
                values.append(cnt)
                link_colors.append("#6B729955")

        # Yuksek risk -> Beklenen Kurtarilan / Beklenen Kayip (segment ortalama donusum oranina gore)
        high_risk_df = _sk[_sk["RiskLevel"] == "🔴 Yüksek Risk"]
        total_high = len(high_risk_df)
        avg_conv = high_risk_df["SimulatedConversionRate"].mean() if total_high > 0 else 0
        expected_retained = int(round(total_high * avg_conv))
        expected_lost = total_high - expected_retained

        if expected_retained > 0:
            sources.append(node_idx["🔴 Yüksek Risk"])
            targets.append(node_idx["✅ Beklenen Kurtarılan"])
            values.append(expected_retained)
            link_colors.append("#4ADE8055")
        if expected_lost > 0:
            sources.append(node_idx["🔴 Yüksek Risk"])
            targets.append(node_idx["⚠️ Beklenen Kayıp"])
            values.append(expected_lost)
            link_colors.append("#FF5D8F55")

        node_colors = (
            [seg_color_map[s] for s in segments]
            + ["#4ADE80", "#F59E0B", "#EF4444"]
            + ["#4ADE80", "#FF5D8F", "#6B7299"]
        )

        return all_nodes, node_colors, sources, targets, values, link_colors

    _sk_nodes, _sk_node_colors, _sk_src, _sk_tgt, _sk_val, _sk_link_colors = build_sankey_data(df)

    sankey_fig = go.Figure(go.Sankey(
        node=dict(
            pad=18, thickness=18,
            line=dict(color="rgba(255,255,255,.15)", width=0.5),
            label=_sk_nodes, color=_sk_node_colors,
        ),
        link=dict(source=_sk_src, target=_sk_tgt, value=_sk_val, color=_sk_link_colors),
    ))
    sankey_fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=10), height=420,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E4E7F5", size=12),
    )
    st.plotly_chart(sankey_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"#### Müşteri Listesi — {selected_segment}")
    display_df = filtered.head(200).copy()
    display_df["Risk"] = display_df["ChurnRiskScore"].apply(lambda x: f"{x*100:.0f}%")
    display_df["Tahmini CLV"] = display_df["EstimatedCLV"].apply(lambda x: f"${x:,.0f}")
    display_df["Varsayılan Dönüşüm"] = display_df["SimulatedConversionRate"].apply(lambda x: f"~{x*100:.0f}%")
    st.dataframe(
        display_df[[
            "customerID", "Risk", "ChurnReasonSegment", "RecommendedCampaign",
            "Varsayılan Dönüşüm", "Tahmini CLV", "tenure", "MonthlyCharges",
        ]].rename(columns={
            "customerID": "Müşteri ID", "ChurnReasonSegment": "Segment",
            "RecommendedCampaign": "Önerilen Kampanya", "tenure": "Tenure (ay)",
            "MonthlyCharges": "Aylık Ücret",
        }),
        use_container_width=True, height=460,
    )
    st.caption("* Dönüşüm oranları varsayımsaldır. Risk skoru Random Forest modeliyle üretilmiştir (AUC 0.84).")
    st.download_button(
        "⬇ Filtrelenen Listeyi CSV Olarak İndir",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"churn_segment_{selected_segment.replace(' ', '_')}.csv", mime="text/csv",
    )

elif active_tab == "💰 ROI Simülasyonu":
    st.caption(
        "Seçtiğin segmentteki riskli müşterilere kampanyayı uygularsak ne kazanırız? "
        "Varsayılan maliyet/dönüşüm oranlarını değiştirip senaryoyu test edebilirsin."
    )
    roi_col1, roi_col2 = st.columns([1, 2])
    with roi_col1:
        roi_segment = st.selectbox(
            "Simülasyon için segment", sorted(df["ChurnReasonSegment"].unique().tolist()), key="roi_segment"
        )
        roi_risk_threshold = st.slider("Hedef kitle: minimum risk skoru", 0.0, 1.0, 0.5, 0.05, key="roi_risk")
        seg_df = df[(df["ChurnReasonSegment"] == roi_segment) & (df["ChurnRiskScore"] >= roi_risk_threshold)]
        default_cost = float(seg_df["CampaignCostPerCustomer"].iloc[0]) if len(seg_df) > 0 else 10.0
        default_conv = float(seg_df["SimulatedConversionRate"].iloc[0]) if len(seg_df) > 0 else 0.2
        campaign_cost = st.slider("Müşteri başı kampanya maliyeti ($)", 0.0, 50.0, default_cost, 1.0, key="roi_cost")
        conversion_rate = st.slider(
            "Varsayılan dönüşüm oranı (%)", 0, 100, int(default_conv * 100), 1, key="roi_conv"
        ) / 100
    with roi_col2:
        n_targeted = len(seg_df)
        if n_targeted == 0:
            st.info(
                f"'{roi_segment}' segmentinde, %{roi_risk_threshold*100:.0f} risk eşiğinin üzerinde "
                "müşteri bulunmuyor (bu segmentin ortalama riski düşük olabilir). "
                "Soldaki 'Hedef kitle: minimum risk skoru' değerini düşürerek tekrar dene."
            )
        else:
            avg_clv = seg_df["EstimatedCLV"].mean()
            expected_retained = n_targeted * conversion_rate
            revenue_saved = expected_retained * avg_clv
            total_cost = n_targeted * campaign_cost
            net_roi = revenue_saved - total_cost
            roi_multiplier = (revenue_saved / total_cost) if total_cost > 0 else 0
            m1, m2, m3 = st.columns(3)
            m1.metric("Hedeflenen Müşteri", f"{n_targeted:,}")
            m2.metric("Beklenen Kurtarılan Müşteri", f"{expected_retained:,.0f}")
            m3.metric("Ortalama CLV", f"${avg_clv:,.0f}")
            m4, m5, m6 = st.columns(3)
            m4.metric("Toplam Kampanya Maliyeti", f"${total_cost:,.0f}")
            m5.metric("Kurtarılan Gelir", f"${revenue_saved:,.0f}")
            m6.metric("Net ROI", f"${net_roi:,.0f}", delta=f"{roi_multiplier:.1f}x" if total_cost > 0 else None)
            if total_cost > 0:
                if net_roi > 0:
                    st.success(f"Bu senaryoda kampanya kârlı: her 1$ maliyete karşılık ~{roi_multiplier:.1f}$ gelir kurtarılıyor.")
                else:
                    st.warning("Bu senaryoda kampanya maliyeti, kurtarılan gelirden fazla.")
    st.caption(
        "* Bu simülasyon varsayımsal maliyet ve dönüşüm oranlarına dayanır. Gerçek kampanya "
        "sonuçları geldiğinde bu değerler güncellenmeli."
    )
