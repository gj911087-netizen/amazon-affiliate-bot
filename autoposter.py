import requests
from config import FACEBOOK_TOKEN, PAGE_ID, INSTAGRAM_TOKEN, INSTAGRAM_ACCOUNT_ID

def post_to_facebook(text, image_url=None):
    # ✅ Validar que la imagen sea URL pública HTTPS
    valid_image = image_url if (image_url and image_url.startswith("https://")) else None

    if valid_image:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        payload = {
            "caption": text,
            "url": valid_image,
            "access_token": FACEBOOK_TOKEN
        }
    else:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        payload = {
            "message": text,
            "access_token": FACEBOOK_TOKEN
        }

    response = requests.post(url, data=payload)
    result = response.json()

    if "id" in result:
        print("✅ Publicado en Facebook:", result["id"])
    else:
        print("❌ Error Facebook:", result)

def post_to_instagram(text, image_url=None):
    valid_image = image_url if (image_url and image_url.startswith("https://")) else None

    if not valid_image:
        print("⚠️ Instagram requiere imagen HTTPS, publicación omitida")
        return

    # Paso 1 — crear el contenedor
    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "image_url": valid_image,
        "caption": text,
        "access_token": INSTAGRAM_TOKEN
    }
    response = requests.post(url, data=payload)
    result = response.json()
    media_id = result.get("id")

    if not media_id:
        print("❌ Error Instagram (crear contenedor):", result)
        return

    # Paso 2 — publicar
    publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    requests.post(publish_url, data={
        "creation_id": media_id,
        "access_token": INSTAGRAM_TOKEN
    })
    print("✅ Publicado en Instagram:", media_id)

def post_to_social(text, image=None):
    print("📤 Publicando en redes sociales...")
    print("🖼️ Imagen:", image)
    post_to_facebook(text, image)
    post_to_instagram(text, image)
