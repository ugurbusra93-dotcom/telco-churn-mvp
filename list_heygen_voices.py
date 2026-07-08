# HeyGen'deki mevcut sesleri (voice) listeler, Turkce olanlari filtreler.
# Calistirmak icin: python list_heygen_voices.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

HEYGEN_API_KEY = os.environ.get("HEYGEN_API_KEY", "")

if not HEYGEN_API_KEY:
    print("HATA: .env dosyanda HEYGEN_API_KEY tanimli degil.")
    exit(1)

response = requests.get(
    "https://api.heygen.com/v2/voices",
    headers={"X-Api-Key": HEYGEN_API_KEY},
)

print("Durum kodu:", response.status_code)

if response.status_code != 200:
    print("Sesler alinamadi:", response.text)
    exit(1)

data = response.json()
voices = data.get("data", {}).get("voices", []) or data.get("voices", [])

print(f"\nToplam {len(voices)} ses bulundu.\n")

turkish_voices = [v for v in voices if "turk" in str(v.get("language", "")).lower() or v.get("language") == "Turkish"]

if turkish_voices:
    print("=== TURKCE SESLER ===")
    for v in turkish_voices[:15]:
        print(f"- {v.get('name')} | voice_id: {v.get('voice_id')} | dil: {v.get('language')} | cinsiyet: {v.get('gender')}")
else:
    print("Turkce ses bulunamadi. Ilk 15 sesi gosteriyorum (herhangi bir dil):")
    for v in voices[:15]:
        print(f"- {v.get('name')} | voice_id: {v.get('voice_id')} | dil: {v.get('language')} | cinsiyet: {v.get('gender')}")

print("\nBegendigin bir voice_id'yi kopyala, .env dosyana ekle:")
print("HEYGEN_VOICE_ID=secilen_voice_id")
