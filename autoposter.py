import requests
import os
import time
from config import (
    FACEBOOK_TOKEN, PAGE_ID,
    INSTAGRAM_TOKEN, INSTAGRAM_ACCOUNT_ID
)

# ── Facebook ──────────────────────────────────────────────────────────────────
def post_image_to_facebook(text, image_path):
    """Publica imagen/GIF en Facebook subiendo el archivo directamente."""
    try:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        with open(image_path, "rb") as f:
            response = requests.post(url, data={
                "caption":      text,
                "access_token": FACEBOOK_TOKEN
            }, files={"source": f})
        result = response.json()
        if "id" in result:
            print("✅ Publicado en Facebook: " + result["id"], flush=True)
        else:
            print("❌ Error Facebook: " + str(result), flush=True)
    except Exception as e:
        print("❌ Error Facebook: " + str(e), flush=True)

# ── Instagram ─────────────────────────────────────────────────────────────────
def post_image_to_instagram(text, image_url):
    """
    Publica imagen en Instagram usando la URL publica de Amazon.
    Instagram requiere URL publica https:// — la imagen de Amazon ya lo es.
    NOTA: Instagram no acepta GIFs directamente, usamos la imagen original de Amazon.
    """
    if not image_url or not image_url.startswith("https://"):
        print("⚠️ Instagram: sin URL publica de imagen", flush=True)
        return
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
            print("❌ Error Instagram (crear): " + str(result), flush=True)
            return
        time.sleep(3600)
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        response = requests.post(publish_url, data={
            "creation_id":  media_id,
            "access_token": INSTAGRAM_TOKEN
        })
        result = response.json()
        if "id" in result:
            print("✅ Publicado en Instagram: " + result["id"], flush=True)
        else:
            print("❌ Error Instagram publicar: " + str(result), flush=True)
    except Exception as e:
        print("❌ Error Instagram: " + str(e), flush=True)

# ── Punto de entrada ──────────────────────────────────────────────────────────
def post_to_social(text, media=None, amazon_image_url=None):
    """
    media            = ("gif", "/tmp/archivo.gif")  ← nuevo tipo GIF
    amazon_image_url = URL publica de Amazon para Instagram (no acepta GIFs)

    Facebook: recibe el GIF animado directamente → se ve animado en el feed ✅
    Instagram: recibe la URL de Amazon como imagen estática (limitación de la API) ✅
    """
    print("📤 Publicando en redes sociales...", flush=True)

    if not media or not isinstance(media, tuple):
        print("⚠️ Sin media para publicar", flush=True)
        return

    media_type, media_path = media

    if not media_path or not os.path.exists(media_path):
        print("⚠️ Archivo no encontrado: " + str(media_path), flush=True)
        return

    # GIF → Facebook lo muestra animado, Instagram recibe imagen original de Amazon
    if media_type in ("image", "gif"):
        post_image_to_facebook(text, media_path)
        if amazon_image_url:
            post_image_to_instagram(text, amazon_image_url)
        else:
            print("⚠️ Sin URL de Amazon para Instagram", flush=True)

    # Limpiar archivo temporal
    try:
        os.remove(media_path)
        print("🗑️ Archivo temporal eliminado", flush=True)
    except Exception:
        pass
