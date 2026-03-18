import time
import os
import sys
import random
import requests as req_lib
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

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal"
}

def load_history():
    """Carga todos los ASINs publicados desde Supabase."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/posted_products?select=asin"
        r   = req_lib.get(url, headers=HEADERS_SB, timeout=10)
        data = r.json()
        asins = set(row["asin"] for row in data if "asin" in row)
        print(f"📋 Historial Supabase: {len(asins)} productos publicados", flush=True)
        return asins
    except Exception as e:
        print(f"⚠️ Error cargando historial Supabase: {e}", flush=True)
        return set()

def save_to_history(asin, product_name):
    """Guarda el ASIN publicado en Supabase."""
    try:
        url  = f"{SUPABASE_URL}/rest/v1/posted_products"
        body = {"asin": asin, "product_name": product_name[:200]}
        r    = req_lib.post(url, headers=HEADERS_SB, json=body, timeout=10)
        if r.status_code in (200, 201):
            print(f"✅ ASIN guardado en Supabase: {asin}", flush=True)
        else:
            print(f"⚠️ Supabase respuesta: {r.status_code} {r.text}", flush=True)
    except Exception as e:
        print(f"⚠️ Error guardando en Supabase: {e}", flush=True)

def clear_history():
    """Borra todo el historial cuando ya se publicaron todos."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/posted_products?asin=neq.null"
        r   = req_lib.delete(url, headers=HEADERS_SB, timeout=10)
        print(f"🔄 Historial Supabase borrado: {r.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Error borrando historial: {e}", flush=True)

# ── Bot ───────────────────────────────────────────────────────────────────────
print("🤖 Bot ejecutándose...", flush=True)
try:
    posted_asins = load_history()

    products = find_products()
    if not products:
        print("⚠️ Sin productos disponibles", flush=True)
        sys.exit(0)

    nuevos = [p for p in products if p.get("asin") not in posted_asins]
    print(f"🆕 Productos nuevos: {len(nuevos)} de {len(products)}", flush=True)

    if not nuevos:
        print("🔄 Todos publicados, reiniciando historial...", flush=True)
        clear_history()
        nuevos = products

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

    post_to_social(text, media, amazon_image_url=image_url)
    log_post(name, link)

    # Guardar en Supabase — persiste aunque Render reinicie
    save_to_history(asin, name)

    media_type = media[0] if media else "unknown"
    print(f"✅ Publicado ({media_type}): {name}", flush=True)

except Exception as e:
    print(f"❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
