import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_marketing_text(product_name, link):

    text = f"""
🔥 Producto recomendado

{product_name}

Descúbrelo aquí:
{link}
"""

    return text
