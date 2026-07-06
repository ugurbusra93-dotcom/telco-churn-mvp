# Churn Radar — Telco Kampanya Hedefleme MVP

Pazarlama ekibinin churn riski yüksek müşterileri segmentlere ayırıp,
her segment için önerilen kampanyayı görebildiği basit bir dashboard.

## Ne yapıyor?

1. **`pipeline.py`** — Ham Telco Churn CSV'sini temizler, yeni sütunlar üretir:
   - `ChurnRiskScore` — Random Forest modelinden churn olasılığı (AUC ≈ 0.84)
   - `ChurnReasonSegment` — kural tabanlı 6 segment (Fiyat Duyarlı, Hizmet
     Memnuniyetsizliği, Güvenlik/Yedekleme Eksikliği, Sözleşme Esnekliği
     Arıyor, Ödeme Sürtünmesi, Genel Risk)
   - `RecommendedCampaign` — segmente özel kampanya önerisi
   - `SimulatedConversionRate` — **varsayımsal** dönüşüm oranı (gerçek A/B
     test verisi geldiğinde değiştirilecek, dashboard'da açıkça etiketli)
   - `EstimatedCLV` — basit varsayımsal yaşam boyu değer

2. **`app.py`** — Flask dashboard. Segment ve risk skoruna göre filtreleme,
   üst kısımda özet metrikler (toplam müşteri, yüksek riskli müşteri sayısı,
   riskteki tahmini CLV).

## Kurulum ve çalıştırma (kendi makinende / sunucunda)

```bash
pip install -r requirements.txt
python3 pipeline.py     # veriyi işler, modeli eğitir, enriched_telco.csv üretir
python3 app.py           # http://localhost:5000 adresinde dashboard açılır
```

> Not: Bu MVP, geliştirme ortamımda (sandbox) network erişimi kapalı olduğu
> için burada sadece dosya seviyesinde test edildi (Flask test client ile).
> Gerçek tarayıcıda görsel kontrolü senin ortamında yapman gerekiyor.

## VS Code'da yerel çalıştırma (Streamlit)

```bash
# 1) Sanal ortam (önerilir)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2) Kütüphaneler
pip install -r requirements.txt

# 3) Veriyi işle + modeli eğit (bir kez, ya da veri değişince)
python3 pipeline.py

# 4) Uygulamayı başlat
streamlit run streamlit_app.py
```

Tarayıcıda otomatik olarak `http://localhost:8501` açılacak.

## Render'a deploy

1. Bu klasörü bir GitHub reposuna push et (CSV, `.py` dosyaları, `render.yaml`
   hepsi dahil — model dosyalarını (`.pkl`) push etmene gerek yok, build
   sırasında `pipeline.py` zaten yeniden üretiyor).
2. render.com → New → Blueprint → repoyu seç. Render, klasördeki
   `render.yaml` dosyasını otomatik algılayıp servisi kuracak
   (build: pip install + pipeline.py, start: streamlit run).
3. Alternatif olarak Blueprint kullanmadan manuel Web Service de
   oluşturabilirsin:
   - Build Command: `pip install -r requirements.txt && python3 pipeline.py`
   - Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
4. Deploy birkaç dakika sürer, sonunda `https://churn-radar.onrender.com`
   gibi bir URL alırsın — bunu pazarlama ekibiyle veya yatırımcıyla
   doğrudan paylaşabilirsin.

Not: Render'ın ücretsiz planında servis 15 dakika kullanılmazsa uykuya
geçer, ilk istek birkaç saniye gecikir — MVP demo için sorun değil, gerçek
kullanıcı trafiği için ücretli plana geçmek gerekir.

## Canlıya alma (production) için diğer öneriler

Şu an Flask'ın development server'ı kullanılıyor — bu sadece test için.
Canlıya çıkarken:

- **Basit/hızlı:** Railway, Render veya Fly.io gibi bir PaaS'a deploy et
  (Gunicorn + `app.py` ile). Küçük bir startup MVP'si için en hızlı yol.
- **Streamlit alternatifi:** Eğer daha hızlı iterasyon istiyorsan, aynı
  `pipeline.py` çıktısını (`enriched_telco.csv`) bir Streamlit uygulamasına
  bağlayabiliriz — kodu isterse ayrıca yazarım, sandbox'ta streamlit kurulu
  olmadığı için burada test edemedim.
- **Gunicorn ile:** `gunicorn -w 4 -b 0.0.0.0:8000 app:app`

## Bilinen sınırlamalar (MVP şeffaflığı için önemli)

- `SimulatedConversionRate` gerçek veri değil, iş mantığına dayalı bir
  varsayım. Pitch'te bunu açıkça belirtmek lazım: "gerçek CRM entegrasyonu
  ile bu oranlar gerçek A/B test sonuçlarıyla değişecek."
- Veri seti statik bir snapshot (zaman serisi yok). Müşteri davranışının
  zaman içindeki değişimi bir sonraki versiyonda eklenebilir.
- Segment kuralları şu an elle yazılmış eşik değerlere dayanıyor;
  ölçeklendirilirken bunlar bir clustering modeliyle (örn. KMeans)
  otomatikleştirilebilir.

## Dosyalar

- `pipeline.py` — veri işleme + model eğitimi
- `app.py` — Flask dashboard
- `templates/index.html` — arayüz
- `enriched_telco.csv` — zenginleştirilmiş çıktı verisi
- `churn_model.pkl`, `encoders.pkl` — eğitilmiş model ve encoder'lar
- `metrics.json` — model performans metrikleri
