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
    "laptop accessories best sellers"
]

def find_products():
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": random.choice(QUERIES),        # ← query aleatoria
        "page": str(random.randint(1, 3)),       # ← página aleatoria
        "country": "US",
        "sort_by": "RELEVANCE"
    }
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        products = data.get("data", {}).get("products", [])
        clean_products = []
        for p in products[:PRODUCT_LIMIT]:
            if not isinstance(p, dict):
                continue
            photo = (
                p.get("product_photo") or
                p.get("product_main_image_url") or
                p.get("thumbnail") or
                p.get("image")
            )
            product = {
                "asin": p.get("asin"),
                "product_title": p.get("product_title", "Producto Amazon"),
                "product_photo": photo
            }
            if product["asin"] and product["product_photo"]:  # ← solo con imagen
                clean_products.append(product)
        return clean_products if clean_products else _fallback_products()
    except Exception as e:
        print("Error RapidAPI:", e)
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
        }
    ]
