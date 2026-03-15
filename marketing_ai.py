import requests
import random
from config import GROQ_API_KEY

# Estrategias de marketing que generan más alcance y engagement
ESTRATEGIAS = [
    "urgencia",      # Escasez y tiempo limitado
    "social_proof",  # Prueba social y popularidad
    "problema",      # Problema → solución
    "curiosidad",    # Generar intriga
    "beneficio",     # Beneficio directo y claro
]

INSTRUCCIONES = {
    "urgencia": (
        "Usa la estrategia de URGENCIA y ESCASEZ. "
        "Hazle sentir al lector que debe actuar YA. "
        "Ejemplo: 'Miles lo están comprando', 'No te quedes sin el tuyo', 'Está volando en Amazon'. "
        "Termina con el link de compra."
    ),
    "social_proof": (
        "Usa la estrategia de PRUEBA SOCIAL. "
        "Menciona que es uno de los más vendidos en Amazon, muy popular, miles de reseñas positivas. "
        "Genera confianza y deseo. Termina con el link de compra."
    ),
    "problema": (
        "Usa la estrategia PROBLEMA → SOLUCIÓN. "
        "Empieza describiendo un problema común que resuelve este producto. "
        "Luego preséntalo como LA solución perfecta. Termina con el link de compra."
    ),
    "curiosidad": (
        "Usa la estrategia de CURIOSIDAD. "
        "Empieza con una pregunta intrigante o dato sorprendente relacionado al producto. "
        "Genera que el lector quiera saber más. Termina con el link de compra."
    ),
    "beneficio": (
        "Usa la estrategia de BENEFICIO DIRECTO. "
        "Ve directo al grano: qué gana el comprador, cómo mejora su vida. "
        "Sé específico y concreto. Termina con el link de compra."
    ),
}

HASHTAGS = [
    "#Amazon #Oferta #Recomendado #Compras #Deal",
    "#AmazonFinds #MustHave #Shopping #Tendencia #Top",
    "#ProductoDelDia #Amazon #LoMejor #Recomendacion #Viral",
    "#AmazonDeals #Descuento #Trending #Comprar #Favorito",
    "#TopVentas #Amazon #Increible #Recomiendo #Oferta",
]

def generate_marketing_text(product_name, link):
    try:
        estrategia = random.choice(ESTRATEGIAS)
        instruccion = INSTRUCCIONES[estrategia]
        hashtags = random.choice(HASHTAGS)

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en marketing digital con 10 años de experiencia vendiendo productos en redes sociales. "
                        "Creas posts virales que generan clics y ventas reales. "
                        "REGLAS:\n"
                        "1. Máximo 5 líneas de texto\n"
                        "2. Usa emojis estratégicamente (máximo 5)\n"
                        "3. Escribe en español natural y cercano\n"
                        "4. El link va al final, solo una vez\n"
                        "5. NUNCA inventes precios ni porcentajes de descuento\n"
                        "6. NUNCA menciones que es publicidad o afiliado\n"
                        "7. Después del texto agrega los hashtags exactamente como te los doy\n"
                        f"8. {instruccion}"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Producto: {product_name}\n"
                        f"Link: {link}\n"
                        f"Hashtags a incluir al final: {hashtags}"
                    )
                }
            ],
            "max_tokens": 250,
            "temperature": 0.8
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        result = response.json()
        text = result["choices"][0]["message"]["content"].strip()
        print(f"✅ Texto generado con estrategia '{estrategia}' ({len(text)} chars)", flush=True)
        return text

    except Exception as e:
        print(f"❌ Error Groq: {e}", flush=True)
        return f"🔥 {product_name}\n👉 Cómpralo aquí: {link}"
