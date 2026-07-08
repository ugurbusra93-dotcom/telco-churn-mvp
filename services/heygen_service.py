# services/heygen_service.py
#
# HeyGen entegrasyonunun TUM mantigi burada toplanmistir.
#
# ONEMLI NOT: Bu kod, HeyGen'in "v3" API'sine sahip oldugu varsayimiyla
# yazilmistir (/v3/avatars/looks, /v3/videos, /v3/videos/{id}). Bu endpoint'lerin
# GERCEKTEN var olup olmadigini dogrulayamadim (web erisimim yok). Eger bu
# endpoint'ler 404 donduruyorsa, HeyGen'in guncel API surumu hala v2 olabilir -
# bu durumda docs.heygen.com'dan kontrol edip bu dosyayi guncellememiz gerekir.
#
# Bu dosyanin amaci: tum HeyGen API cagrilarini TEK YERDE toplamak, boylece
# API surumu/endpoint'i degisirse sadece bu dosyayi guncellemek yeterli olsun,
# streamlit_app.py'a dokunmaya gerek kalmasin.

import os
import time
import requests

HEYGEN_API_BASE = "https://api.heygen.com"


class HeyGenError(Exception):
    """HeyGen API ile ilgili tum hatalar icin ozel exception sinifi.
    Boylece Streamlit tarafinda kullanici dostu mesaj gostermek kolaylasir."""
    pass


def _get_api_key():
    api_key = os.environ.get("HEYGEN_API_KEY", "")
    if not api_key:
        raise HeyGenError(
            "HEYGEN_API_KEY tanimli degil. .env dosyana veya Render "
            "Environment Variables kismina ekle."
        )
    return api_key


def find_sinyo_look_id(avatar_name="Sinyo"):
    """GET /v3/avatars/looks ile hesaptaki private avatarlari ceker,
    ismi 'Sinyo' olani bulup Look ID'sini dondurur."""
    api_key = _get_api_key()
    headers = {"X-Api-Key": api_key}

    try:
        resp = requests.get(
            f"{HEYGEN_API_BASE}/v3/avatars/looks",
            headers=headers,
            params={"ownership": "private"},
            timeout=20,
        )
    except requests.exceptions.RequestException as e:
        raise HeyGenError(f"Avatar listesi alinirken baglanti hatasi: {e}")

    if resp.status_code == 404:
        raise HeyGenError(
            "404: /v3/avatars/looks bulunamadi. HeyGen'in v3 API'si mevcut "
            "olmayabilir - docs.heygen.com'dan guncel endpoint'i kontrol et."
        )
    if resp.status_code != 200:
        raise HeyGenError(f"Avatar listesi alinamadi ({resp.status_code}): {resp.text}")

    data = resp.json()

    # HeyGen'in cevap yapisi degisebiliyor - hem {"data": {"looks": [...]}} hem
    # {"data": [...]} hem dogrudan [...] gibi farkli sekiller olabilir. Hepsini
    # güvenli sekilde ele aliyoruz.
    inner = data.get("data", data) if isinstance(data, dict) else data

    if isinstance(inner, list):
        looks = inner
    elif isinstance(inner, dict):
        looks = inner.get("looks", []) or inner.get("avatars", []) or []
    else:
        looks = []

    if not looks:
        raise HeyGenError(
            f"Avatar listesi bos geldi ya da beklenmeyen bir formatta. "
            f"Ham cevap (ilk 500 karakter): {str(data)[:500]}"
        )

    for look in looks:
        if not isinstance(look, dict):
            continue
        name = look.get("name") or look.get("look_name") or look.get("avatar_name") or ""
        if avatar_name.lower() in str(name).lower():
            look_id = look.get("look_id") or look.get("id") or look.get("avatar_id")
            if look_id:
                return look_id

    available_names = [
        look.get("name") or look.get("look_name") or look.get("avatar_name") or "?"
        for look in looks if isinstance(look, dict)
    ]
    raise HeyGenError(
        f"'{avatar_name}' isimli bir avatar bulunamadi. "
        f"Hesaptaki mevcut avatar isimleri: {available_names}"
    )


def get_sinyo_look_id_cached(session_state, avatar_name="Sinyo"):
    """Look ID'yi session_state icinde onbellekler - her seferinde API'ye
    sormaya gerek kalmasin."""
    cache_key = "heygen_sinyo_look_id"
    if cache_key not in session_state:
        session_state[cache_key] = find_sinyo_look_id(avatar_name)
    return session_state[cache_key]


def create_video(text, look_id, voice_id=None, width=720, height=720):
    """POST /v3/videos ile video olusturma istegi baslatir, video_id dondurur
    (video henuz hazir degildir, ayrica polling ile beklenmesi gerekir)."""
    api_key = _get_api_key()
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    voice_config = {"type": "text", "input_text": text}
    if voice_id:
        voice_config["voice_id"] = voice_id

    payload = {
        "video_inputs": [
            {
                "character": {"type": "avatar", "look_id": look_id},
                "voice": voice_config,
            }
        ],
        "dimension": {"width": width, "height": height},
    }

    try:
        resp = requests.post(f"{HEYGEN_API_BASE}/v3/videos", headers=headers, json=payload, timeout=30)
    except requests.exceptions.RequestException as e:
        raise HeyGenError(f"Video olusturma istegi gonderilirken baglanti hatasi: {e}")

    if resp.status_code == 404:
        raise HeyGenError(
            "404: /v3/videos bulunamadi. HeyGen'in v3 API'si mevcut olmayabilir - "
            "docs.heygen.com'dan guncel endpoint'i kontrol et."
        )
    if resp.status_code != 200:
        raise HeyGenError(f"Video olusturma istegi basarisiz ({resp.status_code}): {resp.text}")

    data = resp.json()
    video_id = data.get("data", {}).get("video_id") or data.get("video_id")
    if not video_id:
        raise HeyGenError(f"video_id alinamadi, cevap: {data}")
    return video_id


def check_video_status(video_id):
    """GET /v3/videos/{video_id} ile video durumunu kontrol eder.
    Dondurur: (status, video_url_veya_None, hata_mesaji_veya_None)"""
    api_key = _get_api_key()
    headers = {"X-Api-Key": api_key}

    try:
        resp = requests.get(f"{HEYGEN_API_BASE}/v3/videos/{video_id}", headers=headers, timeout=20)
    except requests.exceptions.RequestException as e:
        raise HeyGenError(f"Video durumu sorgulanirken baglanti hatasi: {e}")

    if resp.status_code != 200:
        raise HeyGenError(f"Video durumu alinamadi ({resp.status_code}): {resp.text}")

    data = resp.json().get("data", {})
    status = data.get("status")
    video_url = data.get("video_url")
    error_msg = data.get("error")
    return status, video_url, error_msg


def generate_video_and_wait(text, look_id, voice_id=None, max_wait_seconds=120, poll_interval=5):
    """Video olusturur ve tamamlanana kadar bekler (polling). Video URL dondurur."""
    video_id = create_video(text, look_id, voice_id=voice_id)

    waited = 0
    while waited < max_wait_seconds:
        time.sleep(poll_interval)
        waited += poll_interval
        status, video_url, error_msg = check_video_status(video_id)

        if status == "completed" and video_url:
            return video_url
        if status == "failed":
            raise HeyGenError(f"Video uretimi basarisiz oldu: {error_msg or 'bilinmeyen hata'}")

    raise HeyGenError(
        f"Video {max_wait_seconds} saniyede tamamlanmadi (video_id: {video_id}). "
        "HeyGen tarafinda hala isleniyor olabilir, birkac dakika sonra tekrar dene."
    )
