import requests
from config import PRODUCT_LIMIT, RAPIDAPI_KEY

def find_products():
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": "tech gadgets best sellers",
        "page": "1",
        "country": "US",
        "sort_by": "RELEVANCE"
    }
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        print("RapidAPI respuesta:", data)
        products = data.get("data", {}).get("products", [])
        if not products:
            raise Exception("Sin productos")
        return products[:PRODUCT_LIMIT]
    except Exception as e:
        print("Error RapidAPI:", e)
        return [
            {"asin": "B09G9FPHY6", "product_title": "Echo Dot 5ta Generación", "product_photo": None},
            {"asin": "B08N5WRWNW", "product_title": "Fire TV Stick 4K", "product_photo": None},
            {"asin": "B07XJ8C8F5", "product_title": "Kindle Paperwhite", "product_photo": None}
        ][:PRODUCT_LIMIT]
