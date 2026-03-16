import os
import random
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import subprocess
import tempfile

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
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))

    product_img = download_image(image_url)
    if product_img:
        img_ratio = product_img.width / product_img.height
        canvas_ratio = WIDTH / HEIGHT
        if img_ratio > canvas_ratio:
            new_height = HEIGHT
            new_width = int(HEIGHT * img_ratio)
        else:
            new_width = WIDTH
            new_height = int(WIDTH / img_ratio)
        product_img = product_img.resize((new_width, new_height), Image.LANCZOS)
        x = (WIDTH - new_width) // 2
        y = (HEIGHT - new_height) // 2
        canvas.paste(product_img, (x, y), product_img)
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 120))
        canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # Barra superior
    draw.rectangle([0, 0, WIDTH, 160], fill=(0, 0, 0, 180))
    draw.rectangle([0, 0, WIDTH, 8], fill=(255, 153, 0, 255))
    font_top = get_font(48)
    wrapped = textwrap.wrap(product_name[:60], width=24)
    y_top = 30
    for line in wrapped[:2]:
        draw.text((WIDTH//2, y_top), line, font=font_top, fill=(255,255,255,255), anchor="mm")
        y_top += 58

    # Marca de agua central semitransparente
    wm_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    wm_draw = ImageDraw.Draw(wm_layer)
    font_wm = get_font(40)
    wm_text = "🛍 To-do en Uno  |  @impulso_dijital"
    box_w, box_h = 860, 75
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2
    wm_draw.rounded_rectangle([box_x, box_y, box_x+box_w, box_y+box_h], radius=20, fill=(0,0,0,70))
    wm_draw.text((WIDTH//2, box_y+box_h//2), wm_text, font=font_wm, fill=(255,255,255,100), anchor="mm")
    canvas = Image.alpha_composite(canvas.convert("RGBA"), wm_layer)

    draw = ImageDraw.Draw(canvas)

    # Barra inferior CTA
    draw.rectangle([0, HEIGHT-200, WIDTH, HEIGHT], fill=(0,0,0,200))
    draw.rectangle([0, HEIGHT-8, WIDTH, HEIGHT], fill=(255,153,0,255))
    draw.rounded_rectangle([100, HEIGHT-180, WIDTH-100, HEIGHT-80], radius=30, fill=(255,153,0,255))
    draw.text((WIDTH//2, HEIGHT-130), "🛒 COMPRAR EN AMAZON", font=get_font(52), fill=(0,0,0,255), anchor="mm")
    draw.text((WIDTH//2, HEIGHT-50), "👆 Link en descripción", font=get_font(38), fill=(255,255,255,200), anchor="mm")

    return canvas

def create_marketing_video(product_name, image_url):
    print("🎬 Creando reel 9:16...", flush=True)

    canvas = create_reel_frame(product_name, image_url)
    img_path = tempfile.mktemp(suffix=".jpg")
    canvas.convert("RGB").save(img_path, "JPEG", quality=90)

    output_path = tempfile.mktemp(suffix=".mp4")

    try:
        # Video simple sin zoompan para que sea rápido
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-vf", f"scale={WIDTH}:{HEIGHT},fade=t=in:st=0:d=0.5,fade=t=out:st=4:d=0.5",
            "-t", "5",
            "-r", "25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-crf", "28",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode != 0:
            print(f"❌ ffmpeg error: {result.stderr.decode()}", flush=True)
            os.remove(img_path)
            return None
        os.remove(img_path)
        print(f"✅ Reel creado: {output_path}", flush=True)
        return output_path
    except subprocess.TimeoutExpired:
        print("❌ ffmpeg tardó demasiado, saltando video", flush=True)
        return None
    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        return None

def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print(f"📌 Generando reel para: {product_name[:50]}", flush=True)
    path = create_marketing_video(product_name, image_url)
    if path:
        return "video", path
    return None, None
