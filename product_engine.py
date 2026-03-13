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
        print("RapidAPI respuesta:", data)  # para ver qué devuelve
        products = data.get("data", {}).get("products", [])
        if not products:
            raise Exception("Sin productos")
        asins = [p["asin"] for p in products if "asin" in p]
        return asins[:PRODUCT_LIMIT]
    except Exception as e:
        print("Error RapidAPI:", e)
        return [
            "B09G9FPHY6",
            "B08N5WRWNW",
            "B07XJ8C8F5"
        ][:PRODUCT_LIMIT]
