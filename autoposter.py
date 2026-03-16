import requests
import os
import time
import hashlib
from config import (
    FACEBOOK_TOKEN, PAGE_ID,
    INSTAGRAM_TOKEN, INSTAGRAM_ACCOUNT_ID,
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
)


# ── Cloudinary: sube video y devuelve URL publica ─────────────────────────────
def _upload_to_cloudinary(file_path):
    """
    Sube un video a Cloudinary sin SDK, solo con requests.
    Devuelve la URL publica o None si falla.
    """
    try:
        timestamp = str(int(time.time()))
        sign_str  = "timestamp=" + timestamp + CLOUDINARY_API_SECRET
        signature = hashlib.sha1(sign_str.encode()).hexdigest()

        url = (
            "https://api.cloudinary.com/v1_1/"
            + CLOUDINARY_CLOUD_NAME
            + "/video/upload"
        )

        print("☁️  Subiendo video a Cloudinary...", flush=True)
        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                data={
                    "api_key":   CLOUDINARY_API_KEY,
                    "timestamp": timestamp,
                    "signature": signature,
                },
                files={"file": f},
                timeout=120
            )

        result = response.json()
        public_url = result.get("secure_url")

        if public_url:
            print("✅ Video en Cloudinary: " + public_url[:60] + "...", flush=True)
            return public_url, result.get("public_id")
        else:
            print("❌ Cloudinary error: " + str(result), flush=True)
            return None, None

    except Exception as e:
        print("❌ Error subiendo a Cloudinary: " + str(e), flush=True)
        return None, None


def _delete_from_cloudinary(public_id):
    """Borra el video de Cloudinary despues de publicar (ahorra espacio)."""
    try:
        timestamp = str(int(time.time()))
        sign_str  = "public_id=" + public_id + "&timestamp=" + timestamp + CLOUDINARY_API_SECRET
        signature = hashlib.sha1(sign_str.encode()).hexdigest()

        url = (
            "https://api.cloudinary.com/v1_1/"
            + CLOUDINARY_CLOUD_NAME
            + "/video/destroy"
        )
        requests.post(url, data={
            "public_id": public_id,
            "api_key":   CLOUDINARY_API_KEY,
            "timestamp": timestamp,
            "signature": signature,
        }, timeout=30)
        print("🗑️  Video borrado de Cloudinary", flush=True)
    except Exception as e:
        print("Advertencia Cloudinary delete: " + str(e), flush=True)


# ── Facebook ──────────────────────────────────────────────────────────────────
def post_image_to_facebook(text, image_path):
    try:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        with open(image_path, "rb") as f:
            response = requests.post(url, data={
                "caption":      text,
                "access_token": FACEBOOK_TOKEN
            }, files={"source": f})
        result = response.json()
        if "id" in result:
            print("✅ Imagen publicada en Facebook: " + result["id"], flush=True)
        else:
            print("❌ Error Facebook imagen: " + str(result), flush=True)
    except Exception as e:
        print("❌ Error Facebook: " + str(e), flush=True)


def post_video_to_facebook(text, video_path):
    """
    Publica como Reel en Facebook.
    Los Reels siempre tienen audio — el endpoint /videos a veces silencia el audio.
    Flujo: start -> upload binario -> finish/publish
    """
    try:
        # Paso 1: iniciar el upload del reel
        start_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
        r1 = requests.post(start_url, data={
            "upload_phase": "start",
            "access_token": FACEBOOK_TOKEN
        })
        r1_json = r1.json()
        video_id = r1_json.get("video_id")

        if not video_id:
            # Fallback al endpoint clasico si falla el reel
            print("⚠️ Reel start fallo (" + str(r1_json) + "), usando /videos...", flush=True)
            url2 = f"https://graph.facebook.com/v18.0/{PAGE_ID}/videos"
            with open(video_path, "rb") as f:
                r2 = requests.post(url2, data={
                    "description":  text,
                    "access_token": FACEBOOK_TOKEN
                }, files={"source": f})
            res2 = r2.json()
            if "id" in res2:
                print("✅ Video publicado en Facebook: " + res2["id"], flush=True)
            else:
                print("❌ Error Facebook video: " + str(res2), flush=True)
            return

        # Paso 2: subir el archivo binario
        file_size = os.path.getsize(video_path)
        upload_url = "https://rupload.facebook.com/video-upload/v18.0/" + video_id
        with open(video_path, "rb") as f:
            r2 = requests.post(
                upload_url,
                headers={
                    "Authorization": "OAuth " + FACEBOOK_TOKEN,
                    "offset":        "0",
                    "file_size":     str(file_size),
                    "Content-Type":  "application/octet-stream",
                },
                data=f,
                timeout=120
            )
        r2_json = r2.json()
        if not r2_json.get("success"):
            print("❌ Error upload binario Facebook: " + str(r2_json), flush=True)
            return

        # Paso 3: publicar el reel
        r3 = requests.post(start_url, data={
            "video_id":         video_id,
            "upload_phase":     "finish",
            "video_state":      "PUBLISHED",
            "description":      text,
            "content_category": "PRODUCT",
            "access_token":     FACEBOOK_TOKEN
        })
        r3_json = r3.json()
        if r3_json.get("success") or "id" in r3_json:
            print("✅ Reel publicado en Facebook con audio: " + video_id, flush=True)
        else:
            print("❌ Error publicando reel Facebook: " + str(r3_json), flush=True)

    except Exception as e:
        print("❌ Error Facebook video: " + str(e), flush=True)


# ── Instagram ─────────────────────────────────────────────────────────────────
def post_image_to_instagram(text, image_url):
    """image_url debe ser URL publica https://"""
    try:
        upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
        response = requests.post(upload_url, data={
            "image_url":    image_url,
            "caption":      text,
            "access_token": INSTAGRAM_TOKEN
        })
        result   = response.json()
        media_id = result.get("id")

        if not media_id:
            print("❌ Error Instagram imagen (crear): " + str(result), flush=True)
            return

        time.sleep(3)
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        response = requests.post(publish_url, data={
            "creation_id":  media_id,
            "access_token": INSTAGRAM_TOKEN
        })
        result = response.json()
        if "id" in result:
            print("✅ Imagen publicada en Instagram: " + result["id"], flush=True)
        else:
            print("❌ Error Instagram publicar imagen: " + str(result), flush=True)

    except Exception as e:
        print("❌ Error Instagram imagen: " + str(e), flush=True)


def post_video_to_instagram(text, video_url, cloudinary_public_id=None):
    """
    video_url debe ser URL publica https:// (de Cloudinary).
    Instagram no acepta archivos locales para reels.
    """
    try:
        # Paso 1: crear contenedor con la URL publica
        upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
        response = requests.post(upload_url, data={
            "media_type":   "REELS",
            "video_url":    video_url,        # URL publica requerida
            "caption":      text,
            "access_token": INSTAGRAM_TOKEN
        })
        result   = response.json()
        media_id = result.get("id")

        if not media_id:
            print("❌ Error Instagram reel (crear): " + str(result), flush=True)
            return

        # Paso 2: esperar que Instagram procese el video
        print("⏳ Instagram procesando reel...", flush=True)
        time.sleep(20)

        # Paso 3: publicar
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        response = requests.post(publish_url, data={
            "creation_id":  media_id,
            "access_token": INSTAGRAM_TOKEN
        })
        result = response.json()
        if "id" in result:
            print("✅ Reel publicado en Instagram: " + result["id"], flush=True)
        else:
            print("❌ Error Instagram publicar reel: " + str(result), flush=True)

    except Exception as e:
        print("❌ Error Instagram video: " + str(e), flush=True)
    finally:
        # Borrar de Cloudinary despues de publicar
        if cloudinary_public_id:
            _delete_from_cloudinary(cloudinary_public_id)


# ── Punto de entrada principal ────────────────────────────────────────────────
def post_to_social(text, media=None):
    """
    media = ("video", "/tmp/archivo.mp4")  o  ("image", "/tmp/archivo.jpg")
    Para videos: sube a Cloudinary primero, luego publica con URL publica.
    """
    print("📤 Publicando en redes sociales...", flush=True)

    if not media or not isinstance(media, tuple):
        print("⚠️ Sin media para publicar", flush=True)
        return

    media_type, media_path = media

    if not media_path or not os.path.exists(media_path):
        print("⚠️ Archivo de media no encontrado: " + str(media_path), flush=True)
        return

    print("📌 Tipo: " + media_type, flush=True)

    if media_type == "video":
        # Subir a Cloudinary para obtener URL publica
        public_url, public_id = _upload_to_cloudinary(media_path)

        if not public_url:
            print("❌ No se pudo subir a Cloudinary, saltando Instagram", flush=True)
            # Al menos publicar en Facebook con archivo local
            post_video_to_facebook(text, media_path)
        else:
            post_video_to_facebook(text, media_path)
            post_video_to_instagram(text, public_url, public_id)

    elif media_type == "image":
        post_image_to_facebook(text, media_path)
        # Para imagen en Instagram usar URL de Amazon directamente
        # (la imagen del producto ya es URL publica)
        print("ℹ️ Instagram imagen: usa URL publica del producto", flush=True)

    # Limpiar archivo local temporal
    try:
        os.remove(media_path)
        print("🗑️ Archivo local eliminado", flush=True)
    except Exception:
        pass
