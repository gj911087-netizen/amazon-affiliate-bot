import requests
import random
import re
import time
from config import PRODUCT_LIMIT

# ── Categorías EXPANDIDAS con múltiples URLs por categoría ───────────────────
CATEGORIAS = {
    "Utensilios cocina": [
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289857",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289913",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289914",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289905",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289906",
    ],
    "Gadgets cocina": [
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/284507",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741451",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741461",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/372791011",
    ],
    "Café y bebidas": [
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741421",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/678508011",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741431",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/16225927011",
    ],
    "Organización hogar": [
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733781",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3734001",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733911",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733901",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733971",
    ],
    "Ropa de cama": [
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063498",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3031022011",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/404276011",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063506",
    ],
    "Baño": [
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063306",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/13887101",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063308",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3031042011",
    ],
    "Limpieza": [
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732961",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733041",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3733071",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732981",
    ],
    "Electrodomésticos": [
        "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/",
        "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/510938",
        "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/510946",
        "https://www.amazon.com/Best-Sellers-Home-Kitchen-Small-Appliances/zgbs/appliances/510942",
    ],
    "Almacenamiento cocina": [
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289887",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/289888",
        "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/3741381",
    ],
    "Iluminación": [
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063338",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/1063340",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/526676",
    ],
    "Decoración hogar": [
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732871",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732881",
        "https://www.amazon.com/Best-Sellers-Home-Garden/zgbs/garden/3732891",
    ],
    "Jardín y exterior": [
        "https://www.amazon.com/Best-Sellers-Patio-Lawn-Garden/zgbs/lawn-garden/",
        "https://www.amazon.com/Best-Sellers-Patio-Lawn-Garden/zgbs/lawn-garden/3238155011",
        "https://www.amazon.com/Best-Sellers-Patio-Lawn-Garden/zgbs/lawn-garden/2972638011",
    ],
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
    title_lower = title.lower()
    for group in SIMILAR_GROUPS:
        if any(kw in title_lower for kw in group):
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


def find_products(seen_asins_global=None):
    """
    seen_asins_global: set de ASINs ya usados (vendrían de Supabase).
    Si no se pasa, se crea uno vacío.
    """
    if seen_asins_global is None:
        seen_asins_global = set()

    while True:
        clean_products  = []
        seen_asins_session = set()
        existing_titles = []

        # Expandir: por cada categoría, elegir una URL aleatoria distinta
        # y además intentar con MÚLTIPLES URLs si la primera no da variedad
        cats = list(CATEGORIAS.items())
        random.shuffle(cats)

        for cat_name, urls in cats:
            if len(clean_products) >= PRODUCT_LIMIT:
                break

            print(f"🏷️ Categoría: {cat_name}", flush=True)

            # Mezclar las URLs de esta categoría para no repetir siempre la primera
            urls_shuffled = urls.copy()
            random.shuffle(urls_shuffled)

            encontrado = False
            for url in urls_shuffled:
                if encontrado:
                    break

                asins = get_asins_from_bestsellers(url)
                if not asins:
                    continue

                # Mezclar para no tomar siempre el top-1
                random.shuffle(asins)

                # Saltar los que ya están en Supabase o en esta sesión
                asins_filtrados = [
                    a for a in asins
                    if a not in seen_asins_global and a not in seen_asins_session
                ]

                if not asins_filtrados:
                    print(f"🔁 Todos los ASINs de esta URL ya fueron usados, probando otra URL...", flush=True)
                    continue

                # Intentar hasta 25 ASINs antes de rendirse con esta URL
                for asin in asins_filtrados[:25]:
                    if len(clean_products) >= PRODUCT_LIMIT:
                        break

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
                    seen_asins_session.add(asin)
                    existing_titles.append(title)
                    print(f"✅ [{cat_name}] {asin} | {title[:45]}", flush=True)
                    encontrado = True
                    break  # 1 producto por categoría — máxima variedad

        if clean_products:
            print(f"✅ Total productos variados: {len(clean_products)}", flush=True)
            return clean_products

        print("⚠️ Sin productos, reintentando en 5 min...", flush=True)
        time.sleep(300)
