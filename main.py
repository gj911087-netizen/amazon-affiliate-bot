import time
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
            print("⚠️ No se encontraron productos")
            time.sleep(300)
            continue

        for product in products:
            try:
                # Datos del producto
                asin = product.get("asin")
                name = product.get("product_title", "Producto Amazon")
                image_url = product.get("product_photo")

                if not asin:
                    print("⚠️ Producto sin ASIN, saltando...")
                    continue

                print(f"🔎 Procesando producto: {name}")

                # Generar link afiliado
                link = generate_affiliate_link(asin)

                # Generar texto con IA
                text = generate_marketing_text(name, link)

                # Obtener imagen
                image = generate_image(name, image_url)

                # Publicar en redes
                post_to_social(text, image)

                # Guardar analytics
                log_post(name, link)

                print(f"✅ Producto publicado: {name}")
                print(f"🔗 Link afiliado: {link}")

                print(f"⏳ Esperando {POST_INTERVAL} segundos...")
                time.sleep(POST_INTERVAL)

            except Exception as e:
                print("❌ Error procesando producto:", e)

    except Exception as e:
        print("❌ Error general del bot:", e)

        # Espera antes de intentar otra vez
        time.sleep(300)
