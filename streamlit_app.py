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

    .stButton button {
        border-radius:12px; font-weight:600; font-family:'Inter',sans-serif;
        background: linear-gradient(90deg, #7C5CFF, #22D3EE) !important;
        color:#070B1F !important; border:none !important;
        transition: box-shadow .2s ease, transform .15s ease;
    }
    .stButton button:hover {
        box-shadow: 0 0 24px rgba(124,92,255,.5);
        transform: translateY(-1px);
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
        background: rgba(17,24,45,.8); border-color: rgba(255,255,255,.1); border-radius:10px;
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.08); }

    /* Tablo */
    [data-testid="stDataFrame"] { border-radius:16px; overflow:hidden; }

    /* Expander / info / success / warning kutulari */
    [data-testid="stExpander"], .stAlert {
        background: rgba(17,24,45,.7) !important; border:1px solid rgba(255,255,255,.08) !important;
        border-radius:14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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

st.markdown(
    """
    <div class="crd-header">
        <div class="crd-brand-row">
            <div class="crd-brand-badge">◈</div>
            <div>
                <div class="crd-eyebrow">Churn Simulator AI</div>
                <div class="crd-title">Campaign Intelligence Dashboard</div>
            </div>
        </div>
        <div class="crd-tagline">Predict. Personalize. Retain.</div>
        <div class="crd-sub">Telco Churn Dataset · 7.043 müşteri · Model AUC 0.84</div>
    </div>
    """,
    unsafe_allow_html=True,
)

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

# Sparkline verileri - gercek dagilimlardan turetilmis (histogram bin sayimlari)
tenure_hist, _ = np.histogram(df["tenure"], bins=16)
risk_hist, _ = np.histogram(df["ChurnRiskScore"], bins=16)
atrisk_clv_hist, _ = np.histogram(df[df['ChurnRiskScore'] > 0.5]['EstimatedCLV'], bins=16)
filtered_risk_hist, _ = np.histogram(filtered["ChurnRiskScore"], bins=16) if len(filtered) > 1 else (np.array([0, 0]), None)

st.markdown(
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
            <div class="crd-kpi-label">Yüksek Risk (&gt;%50)</div>
            <div class="crd-kpi-value">{at_risk_count:,}</div>
            <div class="crd-kpi-badge down">%{at_risk_pct:.1f} of total</div>
            {make_sparkline_svg(risk_hist, "#FF5D8F")}
        </div>
        <div class="crd-kpi">
            <div class="crd-kpi-top">
                <div class="crd-kpi-icon">💰</div>
            </div>
            <div class="crd-kpi-label">Riskteki Tahmini CLV</div>
            <div class="crd-kpi-value">${at_risk_clv:,.0f}</div>
            <div class="crd-kpi-badge">Ort. ${avg_at_risk_clv:,.0f}/müşteri</div>
            {make_sparkline_svg(atrisk_clv_hist, "#22D3EE")}
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
    """,
    unsafe_allow_html=True,
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


tab_alerts, tab_list, tab_roi = st.tabs(["🔔 Canlı Uyarılar", "📋 Müşteri Listesi", "💰 ROI Simülasyonu"])

with tab_alerts:
    st.caption(
        "Gerçek zamanlı bir CRM entegrasyonunda bu akış otomatik dolar. MVP'de yeni "
        "uyarıyı simüle etmek için butona tıkla."
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🆕 Yeni Uyarı Simüle Et", use_container_width=True):
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
            st.markdown(
                f"""<div class="crd-card"><h4>👤 Müşteri Profili</h4>
                <div class="crd-field"><b>ID:</b> {cust['customerID']}</div>
                <div class="crd-field"><b>Risk:</b> {risk_badge_html(cust['ChurnRiskScore'])}</div>
                <div class="crd-field"><b>Segment:</b> {cust['ChurnReasonSegment']}</div>
                <div class="crd-field"><b>Tenure:</b> {cust['tenure']} ay</div>
                <div class="crd-field"><b>Aylık Ücret:</b> ${cust['MonthlyCharges']:.2f}</div>
                <div class="crd-field"><b>Sözleşme:</b> {cust['Contract']}</div>
                <div class="crd-field"><b>İnternet:</b> {cust['InternetService']}</div>
                <div class="crd-field"><b>Tahmini CLV:</b> ${cust['EstimatedCLV']:,.0f}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with card_col2:
            st.markdown(
                f"""<div class="crd-card"><h4>🎯 Önerilen Aksiyon</h4>
                <div class="crd-field"><b>Kampanya:</b> {cust['RecommendedCampaign']}</div>
                <div class="crd-field"><b>Varsayılan Dönüşüm:</b> ~%{cust['SimulatedConversionRate']*100:.0f}</div>
                <div class="crd-field"><b>Maliyet:</b> ${cust['CampaignCostPerCustomer']:.0f}/müşteri</div>
                </div>""",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✉️ Kişiselleştirilmiş SMS Oluştur", key=f"sms_btn_{cust['customerID']}"):
                api_key = st.session_state.get("api_key", "")
                if not api_key:
                    st.error("Önce sol taraftaki panelden Anthropic API key'ini gir.")
                elif not ANTHROPIC_AVAILABLE:
                    st.error("`anthropic` kütüphanesi kurulu değil.")
                else:
                    with st.spinner("SMS oluşturuluyor..."):
                        try:
                            client = anthropic.Anthropic(api_key=api_key)
                            prompt = f"""Sen bir telekom sirketinde deneyimli bir pazarlama metin yazarisin.
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
2. Turkce, sicak ama profesyonel bir ton kullan; abartili unlemlerden kacin.
3. En fazla 2 cumle, toplamda 160 karakteri gecme.
4. "Degerli musterimiz" ile basla, musteri adini kullanma.
5. Musterilik suresini dogru say: {cust['tenure']} ay (yil degil, ay olarak
   ifade et eger 12'den kucukse; 12 veya uzeriyse yil olarak da belirtebilirsin
   ama sayiyi yanlis hesaplama).
6. Kampanyayi somut ve net anlat, genel gecer laf kalabaligi yapma.
7. Bir eylem cagrisi (CTA) ile bitir, ama KESINLIKLE soru cumlesi kurma
   (soru isareti "?" kullanma). Emir kipiyle, net bir yonlendirme yap:
   "Hemen aktif edin.", "Detaylar icin 444'u arayin.", "Kampanyadan
   yararlanmak icin uygulamayi acin." gibi. Gercek bir telekom firmasinin
   musteriye soru sorarak degil, yonlendirerek konustugunu unutma.

Cikti SADECE SMS metni olsun, baska hicbir sey yazma."""
                            response = client.messages.create(
                                model="claude-sonnet-5", max_tokens=300,
                                messages=[{"role": "user", "content": prompt}],
                            )
                            sms_text = "".join(b.text for b in response.content if b.type == "text").strip()
                            st.session_state["generated_sms"][cust["customerID"]] = sms_text
                        except Exception as e:
                            st.error(f"SMS oluşturulurken hata oluştu: {e}")

            if cust["customerID"] in st.session_state["generated_sms"]:
                st.text_area(
                    "Oluşturulan SMS", value=st.session_state["generated_sms"][cust["customerID"]],
                    height=140, key=f"sms_text_{cust['customerID']}",
                )

with tab_list:
    seg_summary = (
        df.groupby("ChurnReasonSegment")
        .agg(musteri_sayisi=("customerID", "count"), ortalama_risk=("ChurnRiskScore", "mean"))
        .reset_index().sort_values("musteri_sayisi", ascending=False)
    )
    g1, g2 = st.columns([1, 1])
    with g1:
        st.caption("Segment Dağılımı")
        st.bar_chart(seg_summary.set_index("ChurnReasonSegment")["musteri_sayisi"], color="#7B5CF5")
    with g2:
        st.caption("Segment Bazlı Ortalama Risk")
        st.bar_chart(seg_summary.set_index("ChurnReasonSegment")["ortalama_risk"], color="#E8577A")

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

with tab_roi:
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
        avg_clv = seg_df["EstimatedCLV"].mean() if n_targeted > 0 else 0
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
