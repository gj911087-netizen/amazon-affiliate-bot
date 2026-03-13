import requests
from config import FACEBOOK_TOKEN, PAGE_ID, INSTAGRAM_TOKEN, INSTAGRAM_ACCOUNT_ID

def post_to_facebook(text):
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
    url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": text,
        "access_token": INSTAGRAM_TOKEN
    }
    response = requests.post(url, data=payload)
    media_id = response.json().get("id")
    if media_id:
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        requests.post(publish_url, data={"creation_id": media_id, "access_token": INSTAGRAM_TOKEN})
        print("✅ Publicado en Instagram:", media_id)
    else:
        print("❌ Error Instagram:", response.json())

def post_to_social(text, image=None):
    print("📤 Publicando en redes sociales...")
    post_to_facebook(text)
