import time
import os
import sys
import random
import requests as req_lib
from datetime import datetime
import pytz

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

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal"
}

# ── Horas virales (Colombia UTC-5) ────────────────────────────────────────────
# 7:00 AM  → gente despertando, revisa el cel
# 12:00 PM → hora de almuerzo, máximo scroll
# 7:00 PM  → llegaron a casa, tiempo libre
# 9:00 PM  → pico máximo de engagement nocturno
HORAS_VIRALES = [7, 12, 19, 21]
ZONA_COLOMBIA = pytz.timezone("America/Bogota")

def hora_actual_colombia():
    return datetime.now(ZONA_COLOMBIA).hour

def minuto_actual_colombia():
    return datetime.now(ZONA_COLOMBIA).minute

def es_hora_viral():
    """Retorna True si estamos en una hora viral (en punto)."""
    hora   = hora_actual_colombia()
    minuto = minuto_actual_colombia()
    return hora in HORAS_VIRALES and minuto == 0

def segundos_para_proxima_hora_viral():
    """Calcula cuántos segundos faltan para la siguiente hora viral."""
    ahora      = datetime.now(ZONA_COLOMBIA)
    hora_actual = ahora.hour
    minuto_actual = ahora.minute
    segundo_actual = ahora.second

    # Buscar la próxima hora viral
    for h in sorted(HORAS_VIRALES):
        if h > hora_actual or (h == hora_actual and minuto_actual == 0):
            if h > hora_actual:
                segundos = (h - hora_actual) * 3600 - minuto_actual * 60 - segundo_actual
                return max(segundos, 1)

    # Si ya pasaron todas las horas virales de hoy, esperar a las 7am del día siguiente
    proxima = (24 - hora_actual + HORAS_VIRALES[0]) * 3600 - minuto_actual * 60 - segundo_actual
    return max(proxima, 1)

# ── Supabase helpers ──────────────────────────────────────────────────────────
def load_history():
    try:
        url  = f"{SUPABASE_URL}/rest/v1/posted_products?select=asin"
        r    = req_lib.get(url, headers=HEADERS_SB, timeout=10)
        data = r.json()
        asins = set(row["asin"] for row in data if "asin" in row)
        print(f"📋 Historial Supabase: {len(asins)} productos publicados", flush=True)
        return asins
    except Exception as e:
        print(f"⚠️ Error cargando historial Supabase: {e}", flush=True)
        return set()

def save_to_history(asin, product_name):
    try:
        url  = f"{SUPABASE_URL}/rest/v1/posted_products"
        body = {"asin": asin, "product_name": product_name[:200]}
        r    = req_lib.post(url, headers=HEADERS_SB, json=body, timeout=10)
        if r.status_code in (200, 201):
            print(f"✅ ASIN guardado en Supabase: {asin}", flush=True)
        else:
            print(f"⚠️ Supabase respuesta: {r.status_code} {r.text}", flush=True)
    except Exception as e:
        print(f"⚠️ Error guardando en Supabase: {e}", flush=True)

def clear_history():
    try:
        url = f"{SUPABASE_URL}/rest/v1/posted_products?asin=neq.null"
        r   = req_lib.delete(url, headers=HEADERS_SB, timeout=10)
        print(f"🔄 Historial Supabase borrado: {r.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Error borrando historial: {e}", flush=True)

# ── Publicar un producto ──────────────────────────────────────────────────────
def publicar():
    print(f"\n🚀 Publicando a las {hora_actual_colombia()}:00 hora Colombia", flush=True)
    try:
        posted_asins = load_history()
        products     = find_products()

        if not products:
            print("⚠️ Sin productos disponibles", flush=True)
            return

        nuevos = [p for p in products if p.get("asin") not in posted_asins]
        print(f"🆕 Productos nuevos: {len(nuevos)} de {len(products)}", flush=True)

        if not nuevos:
            print("🔄 Todos publicados, reiniciando historial...", flush=True)
            clear_history()
            nuevos = products

        product   = random.choice(nuevos)
        asin      = product.get("asin")
        name      = product.get("product_title", "Producto Amazon")
        image_url = product.get("product_photo")

        if not asin or not image_url:
            print("⚠️ Producto sin ASIN o imagen", flush=True)
            return

        print(f"🔎 Procesando: {name}", flush=True)
        print(f"🖼️ Imagen: {image_url}", flush=True)

        link  = generate_affiliate_link(asin)
        text  = generate_marketing_text(name, link)
        media = generate_image(name, image_url)

        post_to_social(text, media, amazon_image_url=image_url)
        log_post(name, link)
        save_to_history(asin, name)

        media_type = media[0] if media else "unknown"
        print(f"✅ Publicado ({media_type}): {name}", flush=True)

    except Exception as e:
        print(f"❌ Error publicando: {e}", flush=True)
        import traceback
        traceback.print_exc()

# ── Loop principal ────────────────────────────────────────────────────────────
print("🤖 Bot ejecutándose con horario viral...", flush=True)
print(f"⏰ Horas programadas (Colombia): {HORAS_VIRALES}", flush=True)

while True:
    if es_hora_viral():
        publicar()
        # Esperar 61 segundos para no publicar dos veces en el mismo minuto
        time.sleep(61)
    else:
        espera = segundos_para_proxima_hora_viral()
        hora   = hora_actual_colombia()
        print(f"⏳ Son las {hora}h Colombia. Próxima publicación en {espera//3600}h {(espera%3600)//60}m", flush=True)
        # Revisar cada 30 segundos
        time.sleep(30)
