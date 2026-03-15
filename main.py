import time
import os
import sys
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
except Exception as e:
    print(f"❌ ERROR AL IMPORTAR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🤖 Bot ejecutándose...", flush=True)

try:
    products = find_products()
    if not products:
        print("⚠️ Sin productos disponibles", flush=True)
        sys.exit(0)

    product = random.choice(products)
    asin = product.get("asin")
    name = product.get("product_title", "Producto Amazon")
    image_url = product.get("product_photo")

    if not asin or not image_url:
        print("⚠️ Producto sin ASIN o imagen", flush=True)
        sys.exit(0)

    print(f"🔎 Procesando: {name}", flush=True)
    print(f"🖼️ Imagen: {image_url}", flush=True)

    link = generate_affiliate_link(asin)
    text = generate_marketing_text(name, link)
    image = generate_image(name, image_url)
    post_to_social(text, image)
    log_post(name, link)

    print(f"✅ Publicado: {name}", flush=True)

except Exception as e:
    print(f"❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
