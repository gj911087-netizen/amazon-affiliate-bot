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

def extract_products_from_html(html):
    """
    Extrae ASIN, título e imagen del MISMO bloque HTML
    para garantizar que los tres datos correspondan al mismo producto
    """
    products = []
    seen_asins = set()

    # Dividir el HTML en bloques por producto usando data-asin como ancla
    # Cada bloque contiene toda la info de UN producto
    blocks = re.split(r'(?=data-asin="[A-Z0-9]{10}")', html)

    for block in blocks:
        if len(products) >= PRODUCT_LIMIT:
            break

        # 1. Extraer ASIN del bloque
        asin_match = re.search(r'data-asin="([A-Z0-9]{10})"', block)
        if not asin_match:
            continue
        asin = asin_match.group(1)

        if asin in seen_asins:
            continue

        # 2. Extraer imagen del MISMO bloque
        image_match = re.search(
            r'src="(https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+_.-]+\.(?:jpg|jpeg|png))"',
            block
        )
        if not image_match:
            # Intentar con imagen en atributo data-src
            image_match = re.search(
                r'data-src="(https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+_.-]+\.(?:jpg|jpeg|png))"',
                block
            )
        if not image_match:
            continue
        image = image_match.group(1)

        # Filtrar imágenes demasiado pequeñas (iconos, sprites)
        if any(x in image for x in ['._AC_SR', '._SS', '._SX', '._SY']):
            # Limpiar parámetros de tamaño para obtener imagen grande
            image = re.sub(r'\._[^.]+\.', '.', image)
            if not image.endswith('.jpg'):
                image += '.jpg'

        # 3. Extraer título del MISMO bloque
        title_match = re.search(
            r'class="[^"]*p13n-sc-truncated[^"]*"[^>]*>([^<]{10,})<',
            block
        )
        if not title_match:
            title_match = re.search(r'alt="([^"]{10,})"', block)
        if not title_match:
            title_match = re.search(r'title="([^"]{10,})"', block)
        if not title_match:
            # Usar ASIN como fallback de título
            continue

        title = title_match.group(1).strip()

        # Filtrar títulos que son claramente navegación o UI
        skip_words = ["Best Seller", "Customer Review", "Add to Cart", "See more", "Amazon"]
        if any(w in title for w in skip_words):
            continue

        products.append({
            "asin": asin,
            "product_title": title,
            "product_photo": image
        })
        seen_asins.add(asin)
        print(f"✅ ASIN:{asin} | {title[:50]}", flush=True)

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
            print(f"📦 Productos extraídos del bloque: {len(products)}", flush=True)

            for p in products:
                if p["asin"] not in seen_asins and len(clean_products) < PRODUCT_LIMIT:
                    clean_products.append(p)
                    seen_asins.add(p["asin"])

        if clean_products:
            print(f"✅ Total productos reales de Amazon: {len(clean_products)}", flush=True)
            return clean_products
        else:
            print("⚠️ Sin productos válidos, reintentando en 5 minutos...", flush=True)
            time.sleep(300)
