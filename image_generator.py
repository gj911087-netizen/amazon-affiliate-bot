"""
image_generator.py
Publica la foto original de Amazon en formato 1080x1080.
Solo agrega 2 marcas de agua semitransparentes centradas:
  - "To-do en Uno"     (linea 1)
  - "@impulso_dijital" (linea 2)
Sin fondos, sin badges, sin ningun otro elemento.
"""

import os, tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

WIDTH  = 1080
HEIGHT = 1080


def _font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print("Advertencia imagen: " + str(e), flush=True)
        return None


def create_marketing_image(product_name, image_url):
    print("Procesando imagen del producto...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        print("❌ No se pudo descargar imagen", flush=True)
        return None

    # Redimensionar a 1080x1080 manteniendo proporcion (cover)
    img = prod_img.convert("RGB")
    iw, ih = img.size
    scale  = max(WIDTH / iw, HEIGHT / ih)
    new_w  = int(iw * scale)
    new_h  = int(ih * scale)
    img    = img.resize((new_w, new_h), Image.LANCZOS)

    # Recortar al centro exacto
    left = (new_w - WIDTH)  // 2
    top  = (new_h - HEIGHT) // 2
    img  = img.crop((left, top, left + WIDTH, top + HEIGHT))

    # Agregar marcas de agua semitransparentes
    canvas = img.convert("RGBA")
    draw   = ImageDraw.Draw(canvas)
    fw     = _font(34)

    # Posicion: parte inferior centrada
    # Linea 1 arriba, linea 2 debajo — una encima de la otra
    y1 = HEIGHT - 78   # "To-do en Uno"
    y2 = HEIGHT - 38   # "@impulso_dijital"

    # Sombra sutil para legibilidad sobre cualquier fondo
    draw.text((WIDTH // 2 + 1, y1 + 1), "To-do en Uno",
              font=fw, fill=(0, 0, 0, 55), anchor="mm")
    draw.text((WIDTH // 2 + 1, y2 + 1), "@impulso_dijital",
              font=fw, fill=(0, 0, 0, 55), anchor="mm")

    # Texto blanco semitransparente (85/255 ~ 33% opacidad)
    draw.text((WIDTH // 2, y1), "To-do en Uno",
              font=fw, fill=(255, 255, 255, 85), anchor="mm")
    draw.text((WIDTH // 2, y2), "@impulso_dijital",
              font=fw, fill=(255, 255, 255, 85), anchor="mm")

    # Guardar como JPEG de alta calidad
    out_path = tempfile.mktemp(suffix=".jpg")
    canvas.convert("RGB").save(out_path, "JPEG", quality=95)
    print("Imagen lista: " + str(os.path.getsize(out_path) // 1024) + "KB", flush=True)
    return out_path


def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print("Generando imagen: " + product_name[:60], flush=True)
    path = create_marketing_image(product_name, image_url)
    if path:
        return "image", path
    return None, None
