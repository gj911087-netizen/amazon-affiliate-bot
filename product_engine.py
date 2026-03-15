import requests
import random
import xml.etree.ElementTree as ET
import re
import time
from config import PRODUCT_LIMIT

# Feeds RSS de Amazon por categoría
RSS_FEEDS = [
    # Electrónica y gadgets
    "https://www.amazon.com/gp/rss/bestsellers/electronics/",
    "https://www.amazon.com/gp/rss/bestsellers/computers/",
    "https://www.amazon.com/gp/rss/bestsellers/wireless/",
    "https://www.amazon.com/gp/rss/bestsellers/photo/",
    # Videojuegos
    "https://www.amazon.com/gp/rss/bestsellers/videogames/",
    "https://www.amazon.com/gp/rss/bestsellers/pc/",
    # Cocina y hogar
    "https://www.amazon.com/gp/rss/bestsellers/kitchen/",
    "https://www.amazon.com/gp/rss/bestsellers/garden/",
    "https://www.amazon.com/gp/rss/bestsellers/tools/",
    "https://www.amazon.com/gp/rss/bestsellers/appliances/",
    # Belleza y salud
    "https://www.amazon.com/gp/rss/bestsellers/beauty/",
    "https://www.amazon.com/gp/rss/bestsellers/health-personal-care/",
    "https://www.amazon.com/gp/rss/bestsellers/luxury-beauty/",
    # Deportes
    "https://www.amazon.com/gp/rss/bestsellers/sports/",
    "https://www.amazon.com/gp/rss/bestsellers/outdoor/",
    # Bebés y niños
    "https://www.amazon.com/gp/rss/bestsellers/baby-products/",
    "https://www.amazon.com/gp/rss/bestsellers/toys-and-games/",
    "https://www.amazon.com/gp/rss/bestsellers/kids/",
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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
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
    for attempt in range(retries):
        try:
            delay = random.uniform(2, 5)
            print(f"⏳ Esperando {delay:.1f}s...", flush=True)
            time.sleep(delay)

            print(f"📡 RSS: {feed_url} (intento {attempt+1})", flush=True)
            response = requests.get(feed_url, headers=get_headers(), timeout=15)

            if response.status_code == 200:
                return response.content
            elif response.status_code == 404:
                print(f"⚠️ Feed no existe (404), saltando...", flush=True)
                return None
            elif response.status_code == 429:
                wait = (attempt + 1) * 30
                print(f"🚫 Bloqueado, esperando {wait}s...", flush=True)
                time.sleep(wait)
            else:
                print(f"⚠️ Status {response.status_code}, reintentando...", flush=True)
                time.sleep(10)

        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            time.sleep(10)

    return None

def find_products():
    while True:
        feeds = random.sample(RSS_FEEDS, min(4, len(RSS_FEEDS)))
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
                    asin = extract_asin(link_el.text.strip())
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
