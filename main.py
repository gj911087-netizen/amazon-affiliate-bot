import time
import os
import sys
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
    time.sleep(99999)  # ← se queda vivo para que veas el error

print("🤖 Bot iniciado", flush=True)

while True:
    try:
        products = find_products()
        if not products:
            time.sleep(300)
            continue
        for product in products:
            try:
                asin = product.get("asin")
                name = product.get("product_title", "Producto Amazon")
                image_url = product.get("product_photo")
                if not asin:
                    continue
                print(f"🔎 {name}", flush=True)
                link = generate_affiliate_link(asin)
                text = generate_marketing_text(name, link)
                image = generate_image(name, image_url)
                post_to_social(text, image)
                log_post(name, link)
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
