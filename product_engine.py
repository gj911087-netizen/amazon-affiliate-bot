import requests
import random
from config import PRODUCT_LIMIT, RAPIDAPI_KEY

QUERIES = [
    "tech gadgets best sellers",
    "amazon gadgets trending",
    "cool tech gifts",
    "smart home devices",
    "wireless earbuds best sellers",
    "portable charger amazon",
    "phone accessories trending",
    "laptop accessories best sellers",
    "bluetooth speakers amazon",
    "usb gadgets trending",
    "smart watch best sellers",
    "gaming accessories amazon",
    "home office gadgets",
    "led lights smart home",
    "mini projector amazon"
]

def find_products():
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": random.choice(QUERIES),
        "page": str(random.randint(1, 5)),
        "country": "US",
        "sort_by": "RELEVANCE"
    }
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        data = response.json()
        products = data.get("data", {}).get("products", [])
        clean_products = []
        seen_asins = set()
        for p in products:
            if not isinstance(p, dict):
                continue
            asin = p.get("asin")
            if not asin or asin in seen_asins:
                continue
            photo = (
                p.get("product_photo") or
                p.get("product_main_image_url") or
                p.get("thumbnail") or
                p.get("image")
            )
            if not photo or not photo.startswith("https://"):
                continue
            title = p.get("product_title", "")
            if not title or len(title) < 10:
                continue
            clean_products.append({
                "asin": asin,
                "product_title": title,
                "product_photo": photo
            })
            seen_asins.add(asin)
            if len(clean_products) >= PRODUCT_LIMIT:
                break
        print(f"✅ Productos encontrados: {len(clean_products)}", flush=True)
        return clean_products if clean_products else _fallback_products()
    except Exception as e:
        print(f"❌ Error RapidAPI: {e}", flush=True)
        return _fallback_products()

def _fallback_products():
    return [
        {
            "asin": "B09G9FPHY6",
            "product_title": "Echo Dot 5ta Generación",
            "product_photo": "https://m.media-amazon.com/images/I/71JB6hM6Z6L._AC_SL1000_.jpg"
        },
        {
            "asin": "B08N5WRWNW",
            "product_title": "Fire TV Stick 4K",
            "product_photo": "https://m.media-amazon.com/images/I/61l9ppRbHlL._AC_SL1000_.jpg"
        },
        {
            "asin": "B07
