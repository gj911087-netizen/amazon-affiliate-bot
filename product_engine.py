import requests
from config import PRODUCT_LIMIT, AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AFFILIATE_TAG
import bottlenose
from amazonscraper import AmazonScraper

def find_products():
    try:
        amazon = bottlenose.Amazon(
            AMAZON_ACCESS_KEY,
            AMAZON_SECRET_KEY,
            AFFILIATE_TAG,
            Region="US",
            Parser=lambda text: text
        )
        # Buscar productos más vendidos
        response = amazon.BrowseNodeLookup(
            BrowseNodeId="bestsellers",
            ResponseGroup="TopSellers"
        )
        # Extraer ASINs
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response)
        asins = [item.text for item in root.iter("ASIN")]
        return asins[:PRODUCT_LIMIT]
    except Exception as e:
        print("Error Amazon API:", e)
        # Productos de respaldo reales
        return [
            "B09G9FPHY6",  # Echo Dot
            "B08N5WRWNW",  # Fire TV Stick
            "B07XJ8C8F5"   # Kindle
        ][:PRODUCT_LIMIT]
