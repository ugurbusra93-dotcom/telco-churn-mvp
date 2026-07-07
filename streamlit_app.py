"""
Churn Simulator AI — Telco Kampanya Hedefleme MVP (Streamlit)

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F6F7FB; }

    /* Marka paleti: Churn Simulator AI logosundan - mor -> teal gradient, lacivert ikon rengi */
    .crd-header {
        background: linear-gradient(120deg, #0B1130 0%, #171A45 45%, #0E2A44 100%);
        margin: -1rem -1rem 1.2rem -1rem;
        padding: 30px 40px 24px 40px; border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #7B5CF5, #17B8A0) 1;
        position: relative; overflow: hidden;
    }
    .crd-brand-row { display:flex; align-items:center; gap:12px; }
    .crd-brand-badge {
        width:36px; height:36px; border-radius:10px;
        background: linear-gradient(135deg, #7B5CF5, #17B8A0);
        display:flex; align-items:center; justify-content:center;
        font-size:18px; flex-shrink:0;
    }
    .crd-eyebrow {
        font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: .14em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #A78BFA, #5EEAD4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0 0 4px 0; font-weight:600;
    }
    .crd-title { color: #F6F7FB; font-size: 27px; font-weight: 800; margin: 0; }
    .crd-tagline {
        color: #8B93C7; font-size: 13px; margin-top: 6px; font-weight:600; letter-spacing:.03em;
    }
    .crd-sub { color: #6C7399; font-size: 12px; margin-top: 8px; font-family: 'IBM Plex Mono', monospace;}

    .crd-kpi-row { display:flex; gap:14px; margin: 0 0 22px 0; flex-wrap: wrap; }
    .crd-kpi {
        flex:1; min-width:160px; background:#0E1230; border-radius:12px;
        padding:16px 20px; border-top: 3px solid #17B8A0;
    }
    .crd-kpi.accent { border-top-color: #7B5CF5; }
    .crd-kpi.warn { border-top-color: #E8577A; }
    .crd-kpi-label {
        font-family:'IBM Plex Mono', monospace; font-size:10.5px; letter-spacing:.08em;
        text-transform:uppercase; color:#7076A3; margin-bottom:6px;
    }
    .crd-kpi-value { font-family:'IBM Plex Mono', monospace; font-size:26px; font-weight:600; color:#F6F7FB; }
    .crd-kpi.warn .crd-kpi-value { color:#F492A8; }
    .crd-kpi.accent .crd-kpi-value { color:#C4B5FD; }

    /* Sekme grubu - segmented control gorunumu */
    div[data-baseweb="tab-list"] {
        display:flex; justify-content:center; gap:8px; border-bottom:none;
        background:#EDEEF6; padding:6px; border-radius:12px; margin:0 auto 24px auto;
        max-width:640px;
    }
    button[data-baseweb="tab"] {
        font-family:'Inter', sans-serif; font-weight:600; font-size:14.5px; color:#5A5F8C;
        border-radius:8px; padding:10px 18px !important; border:none !important;
        transition: all .15s ease;
    }
    button[data-baseweb="tab"]:hover { background: rgba(123,92,245,.08); }
    button[aria-selected="true"] {
        background: white !important;
        box-shadow: 0 1px 4px rgba(23,20,80,.12);
        background: linear-gradient(90deg, #7B5CF5, #17B8A0) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    }
    div[data-baseweb="tab-highlight"] { display:none; }
    div[data-baseweb="tab-border"] { display:none; }

    .risk-badge {
        display:inline-block; padding:3px 10px; border-radius:20px;
        font-family:'IBM Plex Mono', monospace; font-size:12px; font-weight:600;
    }
    .risk-high { background: rgba(232,87,122,.12); color:#C23A5A; }
    .risk-mid  { background: rgba(226,160,63,.16); color:#9C6A16; }
    .risk-low  { background: rgba(23,184,160,.12); color:#0E8C7A; }

    .crd-card {
        background:white; border-radius:14px; padding:22px 26px;
        border:1px solid #E2E4F0; box-shadow: 0 2px 8px rgba(23,20,80,.05);
    }
    .crd-card h4 {
        margin-top:0; font-size:15px; color:#171A45;
        display:flex; align-items:center; gap:8px;
    }
    .crd-field { font-size:14px; margin-bottom:6px; color:#3A3F6B; }
    .crd-field b { color:#171A45; }

    .stButton button {
        border-radius:8px; font-weight:600; font-family:'Inter',sans-serif;
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #7B5CF5, #17B8A0); border:none;
    }

    /* Sidebar markalama */
    section[data-testid="stSidebar"] {
        background: #0E1230; border-right: 1px solid #232A5C;
    }
    section[data-testid="stSidebar"] * { color: #D7DAF5; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #F6F7FB !important;
        font-family: 'Inter', sans-serif; font-weight:700;
    }
    section[data-testid="stSidebar"] .stAlert {
        background: rgba(23,184,160,.12); border: 1px solid rgba(23,184,160,.3);
    }
    section[data-testid="stSidebar"] label { color: #A8AFDA !important; font-size:13px; }
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background:#171A45; border-color:#2E3570; color:#F6F7FB;
    }
    section[data-testid="stSidebar"] hr { border-color:#232A5C; }
    </style>
    """,
    unsafe_allow_html=True,
)


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
            <div class="crd-brand-badge">📡</div>
            <div>
                <div class="crd-eyebrow">Churn Simulator AI</div>
                <div class="crd-title">Kampanya Hedefleme Panosu</div>
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
    st.sidebar.success("✅ API key .env dosyasından yüklendi.")
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
at_risk_clv = df[df['ChurnRiskScore'] > 0.5]['EstimatedCLV'].sum()

st.markdown(
    f"""
    <div class="crd-kpi-row">
        <div class="crd-kpi accent"><div class="crd-kpi-label">Toplam Müşteri</div><div class="crd-kpi-value">{len(df):,}</div></div>
        <div class="crd-kpi warn"><div class="crd-kpi-label">Yüksek Risk (&gt;%50)</div><div class="crd-kpi-value">{at_risk_count:,}</div></div>
        <div class="crd-kpi"><div class="crd-kpi-label">Riskteki Tahmini CLV</div><div class="crd-kpi-value">${at_risk_clv:,.0f}</div></div>
        <div class="crd-kpi accent"><div class="crd-kpi-label">Filtrelenen Sonuç</div><div class="crd-kpi-value">{len(filtered):,}</div></div>
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
                st.session_state["selected_customer"] = new_id
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