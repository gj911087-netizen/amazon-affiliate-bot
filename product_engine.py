import requests
import random
import re
import time
from config import PRODUCT_LIMIT

# ── Categorías: Hogar y Cocina ────────────────────────────────────────────────
BESTSELLER_URLS = [
    # Kitchen & Dining
    "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/",
    "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289857",     # Cookware
    "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/284507",     # Gadgets
    "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741421",    # Coffee
    "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/679248011",  # Storage
    # Home & Garden
    "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/",
    "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063498",        # Bedding
    "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063306",        # Bath
    "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732961",        # Cleaning
    "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733781",        # Organization
    # Small Appliances
    "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/",
    "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/3736281",
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
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        time.sleep(random.uniform(2, 4))
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code != 200:
            return None, None

        html = response.text

        # Titulo
        title_match = re.search(r'id="productTitle"[^>]*>\s*([^<]{10,})\s*<', html)
        if not title_match:
            title_match = re.search(r'"title"\s*:\s*"([^"]{10,})"', html)
        title = title_match.group(1).strip() if title_match else None

        # Imagen
        image_match = re.search(r'"hiRes"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        if not image_match:
            image_match = re.search(r'"large"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        if not image_match:
            image_match = re.search(r'id="landingImage"[^>]*src="(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        image = image_match.group(1) if image_match else None

        return title, image

    except Exception as e:
        print(f"Error detalles {asin}: {e}", flush=True)
        return None, None


def get_asins_from_bestsellers(url):
    try:
        delay = random.uniform(3, 6)
        print(f"⏳ Esperando {delay:.1f}s...", flush=True)
        time.sleep(delay)
        print(f"📡 Scraping: {url}", flush=True)
        response = requests.get(url, headers=get_headers(), timeout=20)

        if response.status_code == 200:
            asins = re.findall(r'data-asin="([A-Z0-9]{10})"', response.text)
            seen = set()
            unique = []
            for a in asins:
                if a not in seen:
                    seen.add(a)
                    unique.append(a)
            return unique
        else:
            print(f"⚠️ Status {response.status_code}", flush=True)
    except Exception as e:
        print(f"Error scraping: {e}", flush=True)
    return []


def find_products():
    while True:
        # Mezclar categorías para variedad: cocina + hogar
        kitchen_urls = [u for u in BESTSELLER_URLS if "kitchen" in u.lower() or "appliances" in u.lower()]
        home_urls    = [u for u in BESTSELLER_URLS if "garden" in u.lower()]

        urls = []
        if kitchen_urls:
            urls.append(random.choice(kitchen_urls))
        if home_urls:
            urls.append(random.choice(home_urls))

        clean_products = []
        seen_asins = set()

        for url in urls:
            if len(clean_products) >= PRODUCT_LIMIT:
                break

            asins = get_asins_from_bestsellers(url)
            if not asins:
                continue

            print(f"📦 ASINs encontrados: {len(asins)}", flush=True)
            random.shuffle(asins)

            for asin in asins[:10]:
                if len(clean_products) >= PRODUCT_LIMIT:
                    break
                if asin in seen_asins:
                    continue

                print(f"🔍 Obteniendo detalles: {asin}", flush=True)
                title, image = get_product_details(asin)

                if not title or not image:
                    print(f"⚠️ Sin datos para {asin}, saltando...", flush=True)
                    continue

                clean_products.append({
                    "asin":          asin,
                    "product_title": title,
                    "product_photo": image
                })
                seen_asins.add(asin)
                print(f"✅ {asin} | {title[:50]}", flush=True)

        if clean_products:
            print(f"✅ Total productos hogar/cocina: {len(clean_products)}", flush=True)
            return clean_products

        print("⚠️ Sin productos, reintentando en 5 min...", flush=True)
        time.sleep(300)
