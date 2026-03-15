import requests
import random
import re
import time
from config import PRODUCT_LIMIT

# URLs nuevas de Amazon Best Sellers (formato /zgbs/)
BESTSELLER_URLS = [
    # Electrónica y gadgets
    "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/",
    "https://www.amazon.com/Best-Sellers-Computers-Accessories/zgbs/pc/",
    "https://www.amazon.com/Best-Sellers-Cell-Phones-Accessories/zgbs/wireless/",
    # Videojuegos
    "https://www.amazon.com/Best-Sellers-Video-Games/zgbs/videogames/",
    # Cocina y hogar
    "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/garden/",
    "https://www.amazon.com/Best-Sellers-Tools-Home-Improvement/zgbs/hi/",
    "https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances/",
    # Belleza y salud
    "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty/",
    "https://www.amazon.com/Best-Sellers-Health-Household/zgbs/hpc/",
    # Deportes
    "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/",
    # Bebés y niños
    "https://www.amazon.com/Best-Sellers-Baby-Products/zgbs/baby-products/",
    "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/",
    # Mascotas
    "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
    # Oficina
    "https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/",
    # Automotriz
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

def extract_products_from_page(html):
    """Extrae productos del HTML de la página de Best Sellers"""
    products = []
    seen_asins = set()

    # Buscar ASINs en el HTML
    asin_pattern = re.findall(r'"asin"\s*:\s*"([A-Z0-9]{10})"', html)
    if not asin_pattern:
        # Patrón alternativo
        asin_pattern = re.findall(r'/dp/([A-Z0-9]{10})/', html)

    # Buscar títulos
    title_pattern = re.findall(r'"product-title"[^>]*>([^<]+)<', html)
    if not title_pattern:
        title_pattern = re.findall(r'class="p13n-sc-truncated[^"]*"[^>]*>([^<]+)<', html)
    if not title_pattern:
        title_pattern = re.findall(r'"title"\s*:\s*"([^"]{10,})"', html)

    for i, asin in enumerate(asin_pattern):
        if asin in seen_asins:
            continue
        if len(products) >= PRODUCT_LIMIT:
            break

        # Imagen usando ASIN
        image = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg"

        # Título
        if i < len(title_pattern):
            title = title_pattern[i].strip()
        else:
            title = f"Amazon Best Seller - {asin}"

        if len(title) < 5:
            continue

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
            elif response.status_code == 503 or response.status_code == 429:
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

            products = extract_products_from_page(html)
            print(f"📦 Productos extraídos: {len(products)}", flush=True)

            for p in products:
                if p["asin"] not in seen_asins and len(clean_products) < PRODUCT_LIMIT:
                    clean_products.append(p)
                    seen_asins.add(p["asin"])

        if clean_products:
            print(f"✅ Total productos reales de Amazon: {len(clean_products)}", flush=True)
            return clean_products
        else:
            print("⚠️ Sin productos, reintentando en 5 minutos...", flush=True)
            time.sleep(300)
