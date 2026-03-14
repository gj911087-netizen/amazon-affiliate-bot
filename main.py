import time
import os
import sys
import json
import random

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
    print("ERROR AL IMPORTAR:", e, flush=True)
    import traceback
    traceback.print_exc()
    time.sleep(99999)

# ── Control de productos ya publicados ──────────────────
POSTED_FILE = "posted.json"

def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted(asin):
    posted = load_posted()
    posted.append(asin)
    with open(POSTED_FILE, "w") as f:
        json.dump(posted, f)
# ────────────────────────────────────────────────────────

print("🤖 Bot iniciado", flush=True)

while True:
    try:
        products = find_products()
        if not products:
            time.sleep(300)
            continue

        # Filtrar productos ya publicados
        posted = load_posted()
        nuevos = [p for p in products if p.get("asin") not in posted]

        # Si ya se publicaron todos, reiniciar el historial
        if not nuevos:
            print("🔄 Todos publicados, reiniciando historial...", flush=True)
            with open(POSTED_FILE, "w") as f:
                json.dump([], f)
            nuevos = products

        # Elegir UN producto aleatorio
        product = random.choice(nuevos)

        try:
            asin = product.get("asin")
            name = product.get("product_title", "Producto Amazon")
            image_url = product.get("product_photo")

            if not asin:
                time.sleep(60)
                continue

            print(f"🔎 {name}", flush=True)
            link = generate_affiliate_link(asin)
            text = generate_marketing_text(name, link)
            image = generate_image(name, image_url)
            post_to_social(text, image)
            log_post(name, link)
            save_posted(asin)  # ← guardar ASIN como publicado
            print(f"✅ Publicado: {name}", flush=True)
            time.sleep(POST_INTERVAL)

        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            time.sleep(60)

    except Exception as e:
        print(f"❌ Error general: {e}", flush=True)
        time.sleep(300)
