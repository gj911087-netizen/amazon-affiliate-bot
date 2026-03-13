from product_engine import find_products
from affiliate_links import generate_affiliate_link
from marketing_ai import generate_marketing_text
from image_generator import generate_image
from autoposter import post_to_social
from analytics import log_post


products = find_products()

for asin in products:

    link = generate_affiliate_link(asin)

    text = generate_marketing_text("Producto Amazon", link)

    image = generate_image("Producto Amazon")

    post_to_social(text, image)

    log_post("Producto Amazon", link)
