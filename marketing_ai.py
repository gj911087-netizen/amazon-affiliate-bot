import requests
from config import GROQ_API_KEY

def generate_marketing_text(product_name, link):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "Eres un experto en marketing de afiliados. Crea textos cortos, atractivos y con emojis para Facebook e Instagram."},
                {"role": "user", "content": f"Crea un post de marketing para: {product_name}. Link: {link}"}
            ]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        print("Groq respuesta:", result)
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error Groq:", e)
        return f"🔥 {product_name}\nDescúbrelo aquí: {link}"
