import requests
from config import PRODUCT_LIMIT, RAPIDAPI_KEY

def find_products():
    url = "https://real-time-amazon-data.p.rapidapi.com/search"

    querystring = {
        "query": "tech gadgets",
        "page": "1",
        "country": "US"
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        products = data["data"]["products"]
        asins = [product["asin"] for product in products]

        return asins[:PRODUCT_LIMIT]

    except Exception as e:
        print("Error RapidAPI:", e)

        # productos de respaldo
        return [
            "B09G9FPHY6",
            "B08N5WRWNW",
            "B07XJ8C8F5"
        ][:PRODUCT_LIMIT]
