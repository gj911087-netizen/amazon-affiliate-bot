import requests
from config import FACEBOOK_TOKEN, PAGE_ID, INSTAGRAM_TOKEN, INSTAGRAM_ACCOUNT_ID


def post_to_facebook(text, image_url=None):
    # Si hay imagen se publica como foto
    if image_url:
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        payload = {
            "caption": text,
            "url": image_url,
            "access_token": FACEBOOK_TOKEN
        }
    else:
        # Si no hay imagen solo publica texto
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


def post_to_instagram(text, image_url):
    if not image_url:
        print("⚠️ Instagram requiere imagen, publicación omitida")
        return

    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"

    payload = {
        "image_url": image_url,
        "caption": text,
        "access_token": INSTAGRAM_TOKEN
    }

    response = requests.post(url, data=payload)
    result = response.json()

    media_id = result.get("id")

    if media_id:
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"

        requests.post(
            publish_url,
            data={
                "creation_id": media_id,
                "access_token": INSTAGRAM_TOKEN
            }
        )

        print("✅ Publicado en Instagram:", media_id)

    else:
        print("❌ Error Instagram:", result)


def post_to_social(text, image=None):
    print("📤 Publicando en redes sociales...")

    # Facebook
    post_to_facebook(text, image)

    # Instagram
    post_to_instagram(text, image)
