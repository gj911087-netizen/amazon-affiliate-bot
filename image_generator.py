"""
image_generator.py
Descarga la imagen original de Amazon, la pone en 1080x1080
y agrega solo la marca de agua. Sin diseño extra, sin GIF.
"""
import os
import tempfile
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
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def create_marketing_image(product_name, image_url):
    print("📸 Descargando imagen de Amazon...", flush=True)
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(r.content)).convert("RGB")
    except Exception as e:
        print("❌ Error descargando imagen: " + str(e), flush=True)
        return None

    # Redimensionar a 1080x1080 manteniendo proporción (cover)
    iw, ih = img.size
    scale  = max(WIDTH / iw, HEIGHT / ih)
    new_w  = int(iw * scale)
    new_h  = int(ih * scale)
    img    = img.resize((new_w, new_h), Image.LANCZOS)

    # Recortar al centro
    left = (new_w - WIDTH)  // 2
    top  = (new_h - HEIGHT) // 2
    img  = img.crop((left, top, left + WIDTH, top + HEIGHT))

    # Agregar solo marca de agua semitransparente
    canvas = img.convert("RGBA")
    draw   = ImageDraw.Draw(canvas)
    fw     = _font(32)

    y1 = HEIGHT - 70
    y2 = HEIGHT - 32

    # Sombra
    draw.text((WIDTH // 2 + 2, y1 + 2), "To-do en Uno",
              font=fw, fill=(0, 0, 0, 60), anchor="mm")
    draw.text((WIDTH // 2 + 2, y2 + 2), "@impulso_dijital",
              font=fw, fill=(0, 0, 0, 60), anchor="mm")

    # Texto blanco semitransparente
    draw.text((WIDTH // 2, y1), "To-do en Uno",
              font=fw, fill=(255, 255, 255, 90), anchor="mm")
    draw.text((WIDTH // 2, y2), "@impulso_dijital",
              font=fw, fill=(255, 255, 255, 90), anchor="mm")

    out_path = tempfile.mktemp(suffix=".jpg")
    canvas.convert("RGB").save(out_path, "JPEG", quality=95)
    print("✅ Imagen lista: " + str(os.path.getsize(out_path) // 1024) + "KB", flush=True)
    return out_path


def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print("🖼️ Procesando imagen: " + product_name[:60], flush=True)
    path = create_marketing_image(product_name, image_url)
    if path:
        return "image", path
    return None, None
