import time
import os
import sys
import random
import json

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
except Exception as e:
    print(f"❌ ERROR AL IMPORTAR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ── Historial persistente en disco ────────────────────────────────────────────
# Se guarda en /opt/render/project/src/posted_asins.json
# Este archivo persiste entre reinicios del bot en Render
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "posted_asins.json")
MAX_HISTORY  = 300   # maximo de ASINs a recordar

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("asins", []))
    except Exception as e:
        print("Advertencia historial: " + str(e), flush=True)
    return set()

def save_history(posted):
    try:
        # Si supera el maximo, eliminar los mas antiguos (lista FIFO)
        asins_list = list(posted)
        if len(asins_list) > MAX_HISTORY:
            asins_list = asins_list[-MAX_HISTORY:]
        with open(HISTORY_FILE, "w") as f:
            json.dump({"asins": asins_list}, f)
        print("📋 Historial guardado: " + str(len(asins_list)) + " productos", flush=True)
    except Exception as e:
        print("Advertencia guardar historial: " + str(e), flush=True)

# ── Bot ───────────────────────────────────────────────────────────────────────
print("🤖 Bot ejecutándose...", flush=True)

try:
    # Cargar historial de productos ya publicados
    posted_asins = load_history()
    print("📋 Historial cargado: " + str(len(posted_asins)) + " productos ya publicados", flush=True)

    # Buscar productos
    products = find_products()
    if not products:
        print("⚠️ Sin productos disponibles", flush=True)
        sys.exit(0)

    # Filtrar los que ya se publicaron
    nuevos = [p for p in products if p.get("asin") not in posted_asins]
    print("🆕 Productos nuevos disponibles: " + str(len(nuevos)) + " de " + str(len(products)), flush=True)

    # Si todos ya fueron publicados, limpiar historial y usar todos
    if not nuevos:
        print("🔄 Todos publicados, reiniciando historial...", flush=True)
        posted_asins = set()
        nuevos = products

    # Elegir producto aleatorio de los nuevos
    product   = random.choice(nuevos)
    asin      = product.get("asin")
    name      = product.get("product_title", "Producto Amazon")
    image_url = product.get("product_photo")

    if not asin or not image_url:
        print("⚠️ Producto sin ASIN o imagen", flush=True)
        sys.exit(0)

    print(f"🔎 Procesando: {name}", flush=True)
    print(f"🖼️ Imagen: {image_url}", flush=True)

    link  = generate_affiliate_link(asin)
    text  = generate_marketing_text(name, link)
    media = generate_image(name, image_url)

    post_to_social(text, media)
    log_post(name, link)

    # Guardar en historial
    posted_asins.add(asin)
    save_history(posted_asins)

    media_type = media[0] if media else "unknown"
    print(f"✅ Publicado ({media_type}): {name}", flush=True)

except Exception as e:
    print(f"❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
