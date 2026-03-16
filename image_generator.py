import os
import random
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import subprocess
import tempfile

# Formato 9:16 para Reels
WIDTH = 1080
HEIGHT = 1920

def download_image(url):
    try:
        response = requests.get(url, timeout=15)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        return img
    except Exception as e:
        print(f"Error descargando imagen: {e}", flush=True)
        return None

def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def create_reel_frame(product_name, image_url):
    """
    Crea frame 9:16 con:
    - Imagen del producto como fondo (sin degradado)
    - Texto del producto arriba y abajo
    - Marca de agua semitransparente en el centro
    """
    # Canvas 9:16
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))

    # Descargar y colocar imagen del producto como fondo completo
    product_img = download_image(image_url)
    if product_img:
        # Escalar imagen para cubrir todo el canvas manteniendo proporciones
        img_ratio = product_img.width / product_img.height
        canvas_ratio = WIDTH / HEIGHT

        if img_ratio > canvas_ratio:
            new_height = HEIGHT
            new_width = int(HEIGHT * img_ratio)
        else:
            new_width = WIDTH
            new_height = int(WIDTH / img_ratio)

        product_img = product_img.resize((new_width, new_height), Image.LANCZOS)

        # Centrar imagen en canvas
        x = (WIDTH - new_width) // 2
        y = (HEIGHT - new_height) // 2
        canvas.paste(product_img, (x, y), product_img)

        # Overlay oscuro suave para legibilidad del texto
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 120))
        canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # === BARRA SUPERIOR con nombre del producto ===
    draw.rectangle([0, 0, WIDTH, 160], fill=(0, 0, 0, 180))
    draw.rectangle([0, 0, WIDTH, 8], fill=(255, 153, 0, 255))  # Línea naranja arriba

    font_top = get_font(48)
    wrapped = textwrap.wrap(product_name[:60], width=24)
    y_top = 30
    for line in wrapped[:2]:
        draw.text((WIDTH // 2, y_top), line, font=font_top, fill=(255, 255, 255, 255), anchor="mm")
        y_top += 58

    # === MARCA DE AGUA CENTRAL SEMITRANSPARENTE ===
    wm_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm_layer)

    font_wm = get_font(44)
    wm_text = "🛍 To-do en Uno  |  @impulso_dijital"
    box_w, box_h = 860, 80
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2

    # Fondo muy transparente
    wm_draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=20,
        fill=(0, 0, 0, 70)
    )
    # Texto semitransparente
    wm_draw.text(
        (WIDTH // 2, box_y + box_h // 2),
        wm_text,
        font=font_wm,
        fill=(255, 255, 255, 100),
        anchor="mm"
    )
    canvas = Image.alpha_composite(canvas.convert("RGBA"), wm_layer)

    draw = ImageDraw.Draw(canvas)

    # === BARRA INFERIOR con CTA ===
    draw.rectangle([0, HEIGHT - 200, WIDTH, HEIGHT], fill=(0, 0, 0, 200))
    draw.rectangle([0, HEIGHT - 8, WIDTH, HEIGHT], fill=(255, 153, 0, 255))  # Línea naranja abajo

    # Botón CTA naranja
    draw.rounded_rectangle([100, HEIGHT - 180, WIDTH - 100, HEIGHT - 80], radius=30, fill=(255, 153, 0, 255))
    draw.text((WIDTH // 2, HEIGHT - 130), "🛒 COMPRAR EN AMAZON", font=get_font(52), fill=(0, 0, 0, 255), anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 50), "👆 Link en descripción", font=get_font(38), fill=(255, 255, 255, 200), anchor="mm")

    return canvas

# Efectos de zoom variados
ZOOM_EFFECTS = [
    "zoompan=z='min(zoom+0.002,1.3)':d=250:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "zoompan=z='min(zoom+0.003,1.4)':d=250:x='0':y='0'",
    "zoompan=z='min(zoom+0.002,1.3)':d=250:x='iw-(iw/zoom)':y='ih-(ih/zoom)'",
    "zoompan=z='if(lte(zoom,1.0),1.4,max(1.001,zoom-0.003))':d=250:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "zoompan=z='min(zoom+0.002,1.3)':d=250:x='iw/2-(iw/zoom/2)':y='0'",
]

def create_marketing_video(product_name, image_url):
    print("🎬 Creando reel 9:16...", flush=True)

    canvas = create_reel_frame(product_name, image_url)
    img_path = tempfile.mktemp(suffix=".jpg")
    canvas.convert("RGB").save(img_path, "JPEG", quality=95)

    output_path = tempfile.mktemp(suffix=".mp4")
    zoom_effect = random.choice(ZOOM_EFFECTS)

    try:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-vf", (
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"{zoom_effect}:s={WIDTH}x{HEIGHT},"
                f"fade=t=in:st=0:d=0.5,"
                f"fade=t=out:st=9:d=0.5"
            ),
            "-t", "10",
            "-r", "25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        os.remove(img_path)
        print(f"✅ Reel creado: {output_path}", flush=True)
        return output_path
    except Exception as e:
        print(f"❌ Error creando reel: {e}", flush=True)
        return img_path

def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print(f"📌 Generando reel para: {product_name[:50]}", flush=True)
    path = create_marketing_video(product_name, image_url)
    return "video", path
