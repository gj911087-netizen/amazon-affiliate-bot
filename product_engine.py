import requests
import random
import re
import time
from config import PRODUCT_LIMIT

# ── Categorías SEPARADAS para máxima variedad ────────────────────────────────
CATEGORIAS = {
    "Utensilios cocina":  "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289857",
    "Gadgets cocina":     "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/284507",
    "Café y bebidas":     "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741421",
    "Organización":       "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733781",
    "Ropa de cama":       "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063498",
    "Baño":               "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063306",
    "Limpieza":           "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732961",
    "Electrodomésticos":  "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

BLACKLIST_KEYWORDS = [
    "sneaker", "shoe", "shoes", "boot", "sandal", "apparel", "shirt", "pants",
    "dress", "jacket", "clothing", "converse", "nike", "adidas", "kids",
    "baby", "diaper", "formula", "toy", "game", "book", "vitamin", "supplement",
    "laptop", "phone", "tablet", "cable", "charger", "battery", "paper towel",
    "napkin", "tissue", "toilet paper", "disposable", "glove", "mask",
]

# Palabras similares — evitar repetir misma SUBCATEGORÍA
SIMILAR_GROUPS = [
    ["paper towel", "napkin", "tissue", "toilet"],
    ["coffee pod", "k-cup", "nespresso", "coffee capsule"],
    ["knife", "blade", "cutter"],
    ["ice maker", "ice machine"],
    ["air fryer", "fryer"],
    ["vacuum", "cleaner", "mop"],
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

def _is_valid_product(title):
    if not title:
        return False
    title_lower = title.lower()
    for kw in BLACKLIST_KEYWORDS:
        if kw in title_lower:
            return False
    return True

def _is_similar_to_existing(title, existing_titles):
    """Evita productos de la misma subcategoría."""
    title_lower = title.lower()
    for group in SIMILAR_GROUPS:
        # Si el nuevo producto pertenece a este grupo
        if any(kw in title_lower for kw in group):
            # Verificar si ya hay uno de ese grupo en los existentes
            for existing in existing_titles:
                existing_lower = existing.lower()
                if any(kw in existing_lower for kw in group):
                    return True
    return False

def get_product_details(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    try:
        time.sleep(random.uniform(2, 4))
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code != 200:
            return None, None

        html = response.text

        title_match = re.search(r'id="productTitle"[^>]*>\s*([^<]{10,})\s*<', html)
        if not title_match:
            title_match = re.search(r'"title"\s*:\s*"([^"]{10,})"', html)
        title = title_match.group(1).strip() if title_match else None

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
        clean_products  = []
        seen_asins      = set()
        existing_titles = []

        # Tomar categorías aleatorias SIN repetir
        cats = list(CATEGORIAS.items())
        random.shuffle(cats)

        for cat_name, url in cats:
            if len(clean_products) >= PRODUCT_LIMIT:
                break

            print(f"🏷️ Categoría: {cat_name}", flush=True)
            asins = get_asins_from_bestsellers(url)
            if not asins:
                continue

            random.shuffle(asins)
            encontrado = False

            for asin in asins[:15]:
                if len(clean_products) >= PRODUCT_LIMIT:
                    break
                if asin in seen_asins:
                    continue

                print(f"🔍 Obteniendo detalles: {asin}", flush=True)
                title, image = get_product_details(asin)

                if not title or not image:
                    print(f"⚠️ Sin datos para {asin}, saltando...", flush=True)
                    continue

                if not _is_valid_product(title):
                    print(f"⛔ Fuera de categoría: {title[:50]}", flush=True)
                    continue

                if _is_similar_to_existing(title, existing_titles):
                    print(f"🔁 Similar a uno existente, saltando: {title[:50]}", flush=True)
                    continue

                clean_products.append({
                    "asin":          asin,
                    "product_title": title,
                    "product_photo": image,
                    "categoria":     cat_name,
                })
                seen_asins.add(asin)
                existing_titles.append(title)
                print(f"✅ [{cat_name}] {asin} | {title[:45]}", flush=True)
                encontrado = True
                break  # 1 producto por categoría — máxima variedad

        if clean_products:
            print(f"✅ Total productos variados: {len(clean_products)}", flush=True)
            return clean_products

        print("⚠️ Sin productos, reintentando en 5 min...", flush=True)
        time.sleep(300)
