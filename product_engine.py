import requests
import random
import re
import time
from config import PRODUCT_LIMIT

BESTSELLER_URLS = [
    "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/",
    "https://www.amazon.com/Best-Sellers-Computers-Accessories/zgbs/pc/",
    "https://www.amazon.com/Best-Sellers-Cell-Phones-Accessories/zgbs/wireless/",
    "https://www.amazon.com/Best-Sellers-Video-Games/zgbs/videogames/",
    "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/garden/",
    "https://www.amazon.com/Best-Sellers-Tools-Home-Improvement/zgbs/hi/",
    "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty/",
    "https://www.amazon.com/Best-Sellers-Health-Household/zgbs/hpc/",
    "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/",
    "https://www.amazon.com/Best-Sellers-Baby-Products/zgbs/baby-products/",
    "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/",
    "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
    "https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/",
    "https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def get_product_details(asin):
    """
    Obtiene título e imagen DIRECTAMENTE de la página del producto en Amazon
    Así garantizamos que imagen y título son del mismo producto
    """
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        delay = random.uniform(2, 4)
        time.sleep(delay)
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code != 200:
            return None, None

        html = response.text

        # Extraer título
        title_match = re.search(r'id="productTitle"[^>]*>\s*([^<]{10,})\s*<', html)
        if not title_match:
            title_match = re.search(r'"title"\s*:\s*"([^"]{10,})"', html)
        title = title_match.group(1).strip() if title_match else None

        # Extraer imagen principal
        image_match = re.search(r'"hiRes"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        if not image_match:
            image_match = re.search(r'"large"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        if not image_match:
            image_match = re.search(r'id="landingImage"[^>]*src="(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        image = image_match.group(1) if image_match else None

        return title, image

    except Exception as e:
        print(f"❌ Error obteniendo detalles de {asin}: {e}", flush=True)
        return None, None


def get_asins_from_bestsellers(url):
    """Extrae solo los ASINs de la página de Best Sellers"""
    try:
        delay = random.uniform(3, 6)
        print(f"⏳ Esperando {delay:.1f}s...", flush=True)
        time.sleep(delay)

        print(f"📡 Scraping: {url}", flush=True)
        response = requests.get(url, headers=get_headers(), timeout=20)

        if response.status_code == 200:
            asins = re.findall(r'data-asin="([A-Z0-9]{10})"', response.text)
            # Eliminar duplicados manteniendo orden
            seen = set()
            unique_asins = []
            for a in asins:
                if a not in seen:
                    seen.add(a)
                    unique_asins.append(a)
            return unique_asins
        elif response.status_code == 404:
            print(f"⚠️ Página no existe (404)", flush=True)
        elif response.status_code in [503, 429]:
            print(f"🚫 Bloqueado temporalmente", flush=True)
        else:
            print(f"⚠️ Status {response.status_code}", flush=True)

    except Exception as e:
        print(f"❌ Error: {e}", flush=True)

    return []


def find_products():
    while True:
        urls = random.sample(BESTSELLER_URLS, min(3, len(BESTSELLER_URLS)))
        clean_products = []
        seen_asins = set()

        for url in urls:
            if len(clean_products) >= PRODUCT_LIMIT:
                break

            asins = get_asins_from_bestsellers(url)
            if not asins:
                continue

            print(f"📦 ASINs encontrados: {len(asins)}", flush=True)

            # Mezclar para variedad
            random.shuffle(asins)

            for asin in asins[:10]:  # Intentar máximo 10 por categoría
                if len(clean_products) >= PRODUCT_LIMIT:
                    break
                if asin in seen_asins:
                    continue

                print(f"🔍 Obteniendo detalles de ASIN: {asin}", flush=True)
                title, image = get_product_details(asin)

                if not title or not image:
                    print(f"⚠️ Sin datos para {asin}, saltando...", flush=True)
                    continue

                clean_products.append({
                    "asin": asin,
                    "product_title": title,
                    "product_photo": image
                })
                seen_asins.add(asin)
                print(f"✅ ASIN:{asin} | {title[:50]}", flush=True)

        if clean_products:
            print(f"✅ Total productos reales de Amazon: {len(clean_products)}", flush=True)
            return clean_products
        else:
            print("⚠️ Sin productos válidos, reintentando en 5 minutos...", flush=True)
            time.sleep(300)
