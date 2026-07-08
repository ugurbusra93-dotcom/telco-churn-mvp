# HeyGen hesabindaki mevcut avatarlari/talking photo'lari listeler.
# Once HeyGen web sitesinden (app.heygen.com) Sinyo'nun fotografini
# "Avatars" / "Talking Photo" bolumunden yukle, SONRA bu scripti calistir.
#
# Calistirmak icin: python list_heygen_avatars.py

import os
import sys
import requests
from dotenv import load_dotenv

print("Script basladi...", flush=True)

load_dotenv()

HEYGEN_API_KEY = os.environ.get("HEYGEN_API_KEY", "")

if not HEYGEN_API_KEY:
    print("HATA: .env dosyanda HEYGEN_API_KEY tanimli degil.")
    sys.exit(1)

print("API key bulundu, HeyGen'e istek gonderiliyor...", flush=True)

try:
    response = requests.get(
        "https://api.heygen.com/v2/avatars",
        headers={"X-Api-Key": HEYGEN_API_KEY},
        timeout=20,
    )
except requests.exceptions.Timeout:
    print("HATA: Istek 20 saniyede zaman asimina ugradi. Internet baglantini")
    print("veya guvenlik duvari/antivirus ayarlarini kontrol et.")
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print("HATA: Istek gonderilemedi:", e)
    sys.exit(1)

print("Cevap alindi.", flush=True)
print("Durum kodu:", response.status_code)
print("")

if response.status_code != 200:
    print("Avatarlar alinamadi:", response.text)
    sys.exit(1)

data = response.json()
avatars = data.get("data", {}).get("avatars", []) or data.get("avatars", [])
talking_photos = data.get("data", {}).get("talking_photos", []) or data.get("talking_photos", [])

print(f"Toplam {len(avatars)} avatar, {len(talking_photos)} talking photo bulundu.\n")

if talking_photos:
    print("=== TALKING PHOTOS ===")
    for tp in talking_photos:
        print(f"- isim: {tp.get('name') or tp.get('talking_photo_name')} | id: {tp.get('talking_photo_id')}")

if avatars:
    print("\n=== AVATARLAR (ilk 10) ===")
    for a in avatars[:10]:
        print(f"- isim: {a.get('avatar_name')} | id: {a.get('avatar_id')}")

print("\nSinyo'yu yukledikten sonra listede ismiyle gorunmesi lazim.")
print("Bulunan ID'yi .env dosyana ekle:")
print("HEYGEN_TALKING_PHOTO_ID=bulunan_id")
print("\nScript tamamlandi.")
