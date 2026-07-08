# TEK SEFERLIK KURULUM SCRIPTI
# Sinyo'nun fotografini HeyGen'e yukler, bir "talking photo" kimligi (ID) alir.
# Bu ID'yi bir kere aldiktan sonra .env dosyana kaydedip streamlit_app.py'da
# kullanacagiz - her SMS/video icin tekrar yuklemeye gerek yok.
#
# Calistirmak icin:
#     pip install requests python-dotenv
#     python create_sinyo_avatar.py
#
# NOT: Bu kod HeyGen API'sinin bilinen yapisina gore yazildi. Hata alirsan
# HeyGen'in guncel API dokumantasyonuna (docs.heygen.com) bakip
# endpoint/parametre isimlerini karsilastir.

import os
import requests
from dotenv import load_dotenv

load_dotenv()

HEYGEN_API_KEY = os.environ.get("HEYGEN_API_KEY", "")
PHOTO_PATH = "sinyo.jpeg"

if not HEYGEN_API_KEY:
    print("HATA: .env dosyanda HEYGEN_API_KEY tanimli degil.")
    print("HeyGen dashboard'undan (app.heygen.com) API key alip .env'e ekle:")
    print("HEYGEN_API_KEY=senin_key_in")
    exit(1)

print("1) Fotograf HeyGen'e yukleniyor...")

with open(PHOTO_PATH, "rb") as f:
    upload_response = requests.post(
        "https://upload.heygen.com/v1/asset",
        headers={
            "X-Api-Key": HEYGEN_API_KEY,
            "Content-Type": "image/jpeg",
        },
        data=f.read(),
    )

print("Upload cevabi:", upload_response.status_code, upload_response.text)

if upload_response.status_code != 200:
    print("Yukleme basarisiz. HeyGen API key'ini ve internet baglantini kontrol et.")
    exit(1)

upload_data = upload_response.json()
image_key = upload_data.get("data", {}).get("image_key") or upload_data.get("image_key")

if not image_key:
    print("image_key bulunamadi, cevabin tam yapisina bak:", upload_data)
    exit(1)

print("2) Fotograf yuklendi, image_key:", image_key)
print("")
print("Bu image_key'i dogrudan talking_photo_id olarak kullanabiliriz.")
print("Bu ID'yi .env dosyana ekle:")
print("HEYGEN_TALKING_PHOTO_ID=" + image_key)
print("")
print("Sonra video uretimini streamlit_app.py icinden Video Olustur butonuyla test et.")
print("Video uretimi hata verirse, o hatayi bana getir, birlikte duzeltiriz.")
