import time
from product_engine import find_products
from affiliate_links import generate_affiliate_link
from marketing_ai import generate_marketing_text
from image_generator import generate_image
from autoposter import post_to_social
from analytics import log_post
from config import POST_INTERVAL

products = find_products()
for product in products:
    try:
        asin = product["asin"]
        name = product["product_title"]
        image_url = product.get("product_photo")
        link = generate_affiliate_link(asin)
        text = generate_marketing_text(name, link)
        image = generate_image(name, image_url)
        post_to_social(text, image)
        log_post(name, link)
        print(f"⏳ Esperando {POST_INTERVAL} segundos...")
        time.sleep(POST_INTERVAL)
    except Exception as e:
        print("Error:", e)
