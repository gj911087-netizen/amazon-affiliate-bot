import requests
import os
import time
from config import FACEBOOK_TOKEN, PAGE_ID, INSTAGRAM_TOKEN, INSTAGRAM_ACCOUNT_ID


def post_image_to_facebook(text, image_path):
    """Publica imagen en Facebook"""
    try:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        with open(image_path, "rb") as f:
            response = requests.post(url, data={
                "caption": text,
                "access_token": FACEBOOK_TOKEN
            }, files={"source": f})
        result = response.json()
        if "id" in result:
            print(f"✅ Imagen publicada en Facebook: {result['id']}", flush=True)
        else:
            print(f"❌ Error Facebook imagen: {result}", flush=True)
    except Exception as e:
        print(f"❌ Error Facebook: {e}", flush=True)


def post_video_to_facebook(text, video_path):
    """Publica video/reel en Facebook"""
    try:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/videos"
        with open(video_path, "rb") as f:
            response = requests.post(url, data={
                "description": text,
                "access_token": FACEBOOK_TOKEN
            }, files={"source": f})
        result = response.json()
        if "id" in result:
            print(f"✅ Video publicado en Facebook: {result['id']}", flush=True)
        else:
            print(f"❌ Error Facebook video: {result}", flush=True)
    except Exception as e:
        print(f"❌ Error Facebook video: {e}", flush=True)


def post_image_to_instagram(text, image_path):
    """Publica imagen en Instagram subiendo archivo directamente"""
    try:
        # Subir imagen a un host temporal usando imgbb o similar
        # Usamos la URL pública de Facebook después de publicar
        # Por ahora usamos el endpoint de contenedor con archivo
        upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"

        with open(image_path, "rb") as f:
            response = requests.post(upload_url, data={
                "caption": text,
                "access_token": INSTAGRAM_TOKEN
            }, files={"image": f})

        result = response.json()
        media_id = result.get("id")

        if not media_id:
            print(f"❌ Error Instagram (crear contenedor): {result}", flush=True)
            return

        # Publicar
        time.sleep(3)
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        response = requests.post(publish_url, data={
            "creation_id": media_id,
            "access_token": INSTAGRAM_TOKEN
        })
        result = response.json()
        if "id" in result:
            print(f"✅ Imagen publicada en Instagram: {result['id']}", flush=True)
        else:
            print(f"❌ Error Instagram publicar: {result}", flush=True)

    except Exception as e:
        print(f"❌ Error Instagram imagen: {e}", flush=True)


def post_video_to_instagram(text, video_path):
    """Publica reel en Instagram"""
    try:
        # Paso 1 - crear contenedor de reel
        upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"

        with open(video_path, "rb") as f:
            response = requests.post(upload_url, data={
                "media_type": "REELS",
                "caption": text,
                "access_token": INSTAGRAM_TOKEN
            }, files={"video": f})

        result = response.json()
        media_id = result.get("id")

        if not media_id:
            print(f"❌ Error Instagram reel (crear): {result}", flush=True)
            return

        # Esperar a que procese el video
        print("⏳ Esperando que Instagram procese el video...", flush=True)
        time.sleep(15)

        # Paso 2 - publicar
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        response = requests.post(publish_url, data={
            "creation_id": media_id,
            "access_token": INSTAGRAM_TOKEN
        })
        result = response.json()
        if "id" in result:
            print(f"✅ Reel publicado en Instagram: {result['id']}", flush=True)
        else:
            print(f"❌ Error Instagram publicar reel: {result}", flush=True)

    except Exception as e:
        print(f"❌ Error Instagram video: {e}", flush=True)


def post_to_social(text, media=None):
    """
    Publica en Facebook e Instagram
    media puede ser (tipo, ruta) donde tipo es 'image' o 'video'
    """
    print("📤 Publicando en redes sociales...", flush=True)

    if not media or not isinstance(media, tuple):
        print("⚠️ Sin media para publicar", flush=True)
        return

    media_type, media_path = media

    if not media_path or not os.path.exists(media_path):
        print("⚠️ Archivo de media no encontrado", flush=True)
        return

    print(f"📌 Publicando {media_type}: {media_path}", flush=True)

    if media_type == "image":
        post_image_to_facebook(text, media_path)
        post_image_to_instagram(text, media_path)
    elif media_type == "video":
        post_video_to_facebook(text, media_path)
        post_video_to_instagram(text, media_path)

    # Limpiar archivo temporal
    try:
        os.remove(media_path)
        print(f"🗑️ Archivo temporal eliminado", flush=True)
    except:
        pass
