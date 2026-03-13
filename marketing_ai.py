import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_marketing_text(product_name, link):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en marketing de afiliados. Crea textos cortos, atractivos y con emojis para publicar en Facebook e Instagram."},
                {"role": "user", "content": f"Crea un post de marketing para este producto: {product_name}. Link de compra: {link}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error GPT:", e)
        return f"🔥 Producto recomendado\n{product_name}\nDescúbrelo aquí: {link}"
