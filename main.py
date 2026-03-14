import time
import os
import sys

sys.stderr = sys.stdout

print("🔍 Verificando configuración...")

from product_engine import find_products
from affiliate_links import generate_affiliate_link
from marketing_ai import generate_marketing_text
from image_generator import generate_image
from autoposter import post_to_social
from analytics import log_post
from config import POST_INTERVAL

print("🤖 Bot de afiliados iniciado...")

while True:
    try:
        products = find_products()
        if not products:
            print("⚠️ No se encontraron productos, reintentando en 5 min...")
            time.sleep(300)
            continue

        for product in products:
            try:
                asin = product.get("asin")
                name = product.get("product_title", "Producto Amazon")
                image_url = product.get("product_photo")

                if not asin:
                    print("⚠️ Producto sin ASIN, saltando...")
                    continue

                print(f"🔎 Procesando: {name}")
                print(f"🖼️ Imagen URL: {image_url}")

                link = generate_affiliate_link(asin)
                text = generate_marketing_text(name, link)
                image = generate_image(name, image_url)
                post_to_social(text, image)
                log_post(name, link)

                print(f"✅ Publicado: {name}")
                print(f"⏳ Esperando {POST_INTERVAL} segundos...")
                time.sleep(POST_INTERVAL)

            except Exception as e:
                print(f"❌ Error en producto: {e}")
                import traceback
                traceback.print_exc()  # ← muestra el error completo
                time.sleep(60)

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(300)
