import requests
import random
import re
import json
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

def extract_products_from_html(html):
    """Extrae productos con imagen real del HTML de Amazon Best Sellers"""
    products = []
    seen_asins = set()

    # Buscar bloques de productos en el JSON embebido en el HTML
    # Amazon guarda los datos en un objeto JS dentro del HTML
    json_matches = re.findall(r'"asin"\s*:\s*"([A-Z0-9]{10})"[^}]*?"title"\s*:\s*"([^"]{10,})"[^}]*?"image"\s*:\s*"(https://[^"]+)"', html)

    for asin, title, image in json_matches:
        if asin in seen_asins or len(products) >= PRODUCT_LIMIT:
            break
        if not image.startswith("https://m.media-amazon.com") and not image.startswith("https://images-na"):
            continue
        products.append({
            "asin": asin,
            "product_title": title.strip(),
            "product_photo": image
        })
        seen_asins.add(asin)
        print(f"✅ {title[:60]}", flush=True)

    # Si el patrón anterior no funciona, usar patrón alternativo
    if not products:
        # Buscar imágenes reales de media-amazon.com junto con ASINs
        blocks = re.findall(
            r'data-asin="([A-Z0-9]{10})"[^>]*>.*?'
            r'src="(https://m\.media-amazon\.com/images/I/[^"]+)".*?'
            r'(?:alt|title)="([^"]{10,})"',
            html, re.DOTALL
        )
        for asin, image, title in blocks:
            if asin in seen_asins or len(products) >= PRODUCT_LIMIT:
                break
            products.append({
                "asin": asin,
                "product_title": title.strip(),
                "product_photo": image
            })
            seen_asins.add(asin)
            print(f"✅ {title[:60]}", flush=True)

    # Tercer patrón: buscar directamente imágenes media-amazon con ASIN cercano
    if not products:
        img_pattern = re.findall(
            r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+_.-]+\.jpg)',
            html
        )
        asin_pattern = re.findall(r'/dp/([A-Z0-9]{10})/', html)
        title_pattern = re.findall(r'class="[^"]*title[^"]*"[^>]*>\s*<span[^>]*>([^<]{10,})</span>', html)

        for i, asin in enumerate(asin_pattern):
            if asin in seen_asins or len(products) >= PRODUCT_LIMIT:
                break
            if i >= len(img_pattern):
                break

            image = img_pattern[i]
            title = title_pattern[i].strip() if i < len(title_pattern) else f"Amazon Best Seller {asin}"

            products.append({
                "asin": asin,
                "product_title": title,
                "product_photo": image
            })
            seen_asins.add(asin)
            print(f"✅ {title[:60]}", flush=True)

    return products


def scrape_bestsellers(url, retries=3):
    for attempt in range(retries):
        try:
            delay = random.uniform(3, 7)
            print(f"⏳ Esperando {delay:.1f}s...", flush=True)
            time.sleep(delay)

            print(f"📡 Scraping: {url} (intento {attempt+1})", flush=True)
            response = requests.get(url, headers=get_headers(), timeout=20)

            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                print(f"⚠️ Página no existe (404), saltando...", flush=True)
                return None
            elif response.status_code in [503, 429]:
                wait = (attempt + 1) * 30
                print(f"🚫 Bloqueado, esperando {wait}s...", flush=True)
                time.sleep(wait)
            else:
                print(f"⚠️ Status {response.status_code}", flush=True)
                time.sleep(10)

        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            time.sleep(10)

    return None


def find_products():
    while True:
        urls = random.sample(BESTSELLER_URLS, min(3, len(BESTSELLER_URLS)))
        clean_products = []
        seen_asins = set()

        for url in urls:
            if len(clean_products) >= PRODUCT_LIMIT:
                break

            html = scrape_bestsellers(url)
            if html is None:
                continue

            products = extract_products_from_html(html)
            print(f"📦 Productos extraídos: {len(products)}", flush=True)

            for p in products:
                if p["asin"] not in seen_asins and len(clean_products) < PRODUCT_LIMIT:
                    # Validar que la imagen es real de Amazon
                    if "media-amazon.com" in p["product_photo"]:
                        clean_products.append(p)
                        seen_asins.add(p["asin"])

        if clean_products:
            print(f"✅ Total productos reales de Amazon: {len(clean_products)}", flush=True)
            return clean_products
        else:
            print("⚠️ Sin productos con imagen válida, reintentando en 5 minutos...", flush=True)
            time.sleep(300)
