import time
import os
import sys
import json
import random
import redis

sys.stderr = sys.stdout
print("INICIO", flush=True)

try:
    from product_engine import find_products
    print("OK product_engine", flush=True)
    from affiliate_links import generate_affiliate_link
    print("OK affiliate_links", flush=True)
    from marketing_ai import generate_marketing_text
    print("OK marketing_ai", flush=True)
    from image_generator import generate_image
    print("OK image_generator", flush=True)
    from autoposter import post_to_social
    print("OK autoposter", flush=True)
    from analytics import log_post
    print("OK analytics", flush=True)
    from config import POST_INTERVAL
    print("OK config", flush=True)
except Exception as e:
    print(f"❌ ERROR AL IMPORTAR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    time.sleep(99999)

# ── Redis para historial permanente ─────────────────────
REDIS_URL = os.getenv("REDIS_URL")
r = redis.from_url(REDIS_URL) if REDIS_URL and REDIS_URL.startswith(("redis://", "rediss://", "unix://")) else None

def already_posted(asin):
    if r:
        return r.sismember("posted_asins", asin)
    return False

def mark_posted(asin):
    if r:
        r.sadd("posted_asins", asin)
        total = r.scard("posted_asins")
        print(f"📦 Total publicados historial: {total}", flush=True)
        # Si llega a 2000 reinicia para no llenarse
        if total >= 2000:
            r.delete("posted_asins")
            print("🔄 Historial reiniciado", flush=True)
# ────────────────────────────────────────────────────────

print("🤖 Bot iniciado", flush=True)

while True:
    try:
        products = find_products()
        if not products:
            print("⚠️ Sin productos, reintentando en 5 min...", flush=True)
            time.sleep(300)
            continue

        # Filtrar ya publicados
        nuevos = [p for p in products if not already_posted(p.get("asin", ""))]

        if not nuevos:
            print("🔄 Todos estos publicados, buscando más...", flush=True)
            time.sleep(30)
            continue

        # Elegir producto aleatorio
        product = random.choice(nuevos)
        asin = product.get("asin")
        name = product.get("product_title", "Producto Amazon")
        image_url = product.get("product_photo")

        if not asin or not image_url:
            print("⚠️ Producto sin ASIN o imagen, saltando...", flush=True)
            time.sleep(30)
            continue

        print(f"🔎 Procesando: {name}", flush=True)
        print(f"🖼️ Imagen: {image_url}", flush=True)

        link = generate_affiliate_link(asin)
        text = generate_marketing_text(name, link)
        image = generate_image(name, image_url)
        post_to_social(text, image)
        log_post(name, link)
        mark_posted(asin)

        print(f"✅ Publicado: {name}", flush=True)
        print(f"⏰ Próxima en {POST_INTERVAL//60} minutos", flush=True)
        time.sleep(POST_INTERVAL)

    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        time.sleep(60)
