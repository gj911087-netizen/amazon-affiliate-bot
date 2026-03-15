import requests
import random
import xml.etree.ElementTree as ET
import re
import time
from config import PRODUCT_LIMIT

# Feeds RSS oficiales de Amazon Best Sellers por categoría
RSS_FEEDS = [
    "https://www.amazon.com/gp/rss/bestsellers/electronics/",
    "https://www.amazon.com/gp/rss/bestsellers/computers/",
    "https://www.amazon.com/gp/rss/bestsellers/wireless/",
    "https://www.amazon.com/gp/rss/bestsellers/photo/",
    "https://www.amazon.com/gp/rss/bestsellers/videogames/",
    "https://www.amazon.com/gp/rss/bestsellers/toys-and-games/",
    "https://www.amazon.com/gp/rss/bestsellers/sporting-goods/",
    "https://www.amazon.com/gp/rss/bestsellers/office-products/",
    "https://www.amazon.com/gp/rss/bestsellers/kitchen/",
    "https://www.amazon.com/gp/rss/bestsellers/tools/",
    "https://www.amazon.com/gp/rss/bestsellers/pet-supplies/",
    "https://www.amazon.com/gp/rss/bestsellers/beauty/",
    "https://www.amazon.com/gp/rss/bestsellers/health-personal-care/",
    "https://www.amazon.com/gp/rss/bestsellers/apparel/",
    "https://www.amazon.com/gp/rss/bestsellers/automotive/",
]

# Rotación de User-Agents para parecer humano
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.0.0",
]

def get_headers():
    """Genera headers aleatorios para parecer un navegador real"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    }

def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    return None

def extract_image(description_html):
    match = re.search(r'src="(https://[^"]*amazon[^"]*\.jpg[^"]*)"', description_html)
    if match:
        return match.group(1)
    match = re.search(r'src="(https://m\.media-amazon\.com/images/[^"]+)"', description_html)
    if match:
        return match.group(1)
    return None

def fetch_feed(feed_url, retries=3):
    """Obtiene un feed RSS con reintentos y delays aleatorios"""
    for attempt in range(retries):
        try:
            # Delay aleatorio entre requests para parecer humano
            delay = random.uniform(2, 6)
            print(f"⏳ Esperando {delay:.1f}s antes de consultar...", flush=True)
            time.sleep(delay)

            print(f"📡 Consultando RSS: {feed_url} (intento {attempt+1})", flush=True)
            response = requests.get(
                feed_url,
                headers=get_headers(),
                timeout=15
            )

            if response.status_code == 200:
                return response.content
            elif response.status_code == 429:
                wait = (attempt + 1) * 30  # 30s, 60s, 90s
                print(f"🚫 Amazon bloqueó temporalmente, esperando {wait}s...", flush=True)
                time.sleep(wait)
            elif response.status_code == 503:
                print(f"⚠️ Amazon no disponible (503), reintentando...", flush=True)
                time.sleep(15)
            else:
                print(f"⚠️ Status inesperado: {response.status_code}", flush=True)
                break

        except Exception as e:
            print(f"❌ Error en request: {e}", flush=True)
            time.sleep(10)

    return None

def find_products():
    while True:
        # Tomar 3 feeds aleatorios cada vez
        feeds = random.sample(RSS_FEEDS, min(3, len(RSS_FEEDS)))
        clean_products = []
        seen_asins = set()

        for feed_url in feeds:
            if len(clean_products) >= PRODUCT_LIMIT:
                break

            content = fetch_feed(feed_url)
            if content is None:
                continue

            try:
                root = ET.fromstring(content)
                channel = root.find('channel')
                if channel is None:
                    continue

                items = channel.findall('item')
                print(f"📦 Items en feed: {len(items)}", flush=True)
                random.shuffle(items)

                for item in items:
                    if len(clean_products) >= PRODUCT_LIMIT:
                        break

                    title_el = item.find('title')
                    if title_el is None or not title_el.text:
                        continue
                    title = title_el.text.strip()
                    if len(title) < 10:
                        continue

                    link_el = item.find('link')
                    if link_el is None or not link_el.text:
                        continue
                    link = link_el.text.strip()
                    asin = extract_asin(link)
                    if not asin or asin in seen_asins:
                        continue

                    desc_el = item.find('description')
                    image = None
                    if desc_el is not None and desc_el.text:
                        image = extract_image(desc_el.text)

                    if not image:
                        image = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg"

                    if not image.startswith("https://"):
                        continue

                    clean_products.append({
                        "asin": asin,
                        "product_title": title,
                        "product_photo": image
                    })
                    seen_asins.add(asin)
                    print(f"✅ {title[:60]}", flush=True)

            except Exception as e:
                print(f"❌ Error parseando feed: {e}", flush=True)
                continue

        if clean_products:
            print(f"✅ Total productos reales de Amazon: {len(clean_products)}", flush=True)
            return clean_products
        else:
            print("⚠️ Sin productos, reintentando en 3 minutos...", flush=True)
            time.sleep(180)
