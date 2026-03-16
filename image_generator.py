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
        print(f"❌ Error descargando imagen: {e}", flush=True)
        return None

def create_gradient(width, height, color1, color2):
    img = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return img

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

def add_watermark(canvas):
    font_wm = get_font(36)
    wm_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm_layer)

    # To-do en Uno (izquierda)
    wm_draw.rounded_rectangle([30, HEIGHT-90, 340, HEIGHT-30], radius=20, fill=(0,0,0,150))
    wm_draw.text((50, HEIGHT-75), "🛍 To-do en Uno", font=font_wm, fill=(255,255,255,220))

    # @impulso_dijital (derecha)
    wm_draw.rounded_rectangle([WIDTH-360, HEIGHT-90, WIDTH-30, HEIGHT-30], radius=20, fill=(0,0,0,150))
    wm_draw.text((WIDTH-345, HEIGHT-75), "@impulso_dijital", font=font_wm, fill=(255,153,0,220))

    canvas.alpha_composite(wm_layer)
    return canvas

def create_marketing_image(product_name, image_url):
    print("🎨 Creando imagen de marketing...", flush=True)
    bg_colors = [
        ((10,10,30),(40,10,60)),
        ((20,0,0),(60,10,10)),
        ((0,20,10),(10,50,30)),
        ((10,10,40),(0,30,60)),
    ]
    color1, color2 = random.choice(bg_colors)
    canvas = create_gradient(WIDTH, HEIGHT, color1, color2)
    draw = ImageDraw.Draw(canvas)

    product_img = download_image(image_url)
    if product_img:
        product_size = 900
        product_img = product_img.resize((product_size, product_size), Image.LANCZOS)
        shadow = Image.new("RGBA", (product_size+40, product_size+40), (0,0,0,0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.ellipse([10,10,product_size+30,product_size+30], fill=(0,0,0,80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        img_x = (WIDTH - product_size) // 2
        img_y = 300
        canvas.paste(shadow, (img_x-20, img_y-10), shadow)
        canvas.paste(product_img, (img_x, img_y), product_img)

    draw.rectangle([0,0,WIDTH,120], fill=(255,153,0,230))
    draw.text((WIDTH//2,60), "⭐ AMAZON BEST SELLER ⭐", font=get_font(52), fill=(0,0,0,255), anchor="mm")

    font_title = get_font(50)
    wrapped = textwrap.wrap(product_name[:80], width=22)
    y_title = 1280
    for line in wrapped[:3]:
        draw.text((WIDTH//2, y_title), line, font=font_title, fill=(255,255,255,255), anchor="mm")
        y_title += 65

    draw.rounded_rectangle([80,1560,WIDTH-80,1700], radius=30, fill=(255,153,0,255))
    draw.text((WIDTH//2,1630), "🛒 COMPRAR EN AMAZON", font=get_font(58), fill=(0,0,0,255), anchor="mm")
    draw.text((WIDTH//2,1780), "👆 Link en descripción", font=get_font(38), fill=(255,220,100,255), anchor="mm")

    canvas = add_watermark(canvas)
    output_path = tempfile.mktemp(suffix=".jpg")
    canvas.convert("RGB").save(output_path, "JPEG", quality=95)
    print(f"✅ Imagen creada: {output_path}", flush=True)
    return output_path

def create_marketing_video(product_name, image_url):
    print("🎬 Creando video de marketing...", flush=True)
    img_path = create_marketing_image(product_name, image_url)
    if not img_path:
        return None
    output_path = tempfile.mktemp(suffix=".mp4")
    try:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-vf", (
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"zoompan=z='min(zoom+0.002,1.3)':d=250:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT},"
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
        print(f"✅ Video creado: {output_path}", flush=True)
        return output_path
    except Exception as e:
        print(f"❌ Error creando video: {e}", flush=True)
        return img_path

def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None

    state_file = "/tmp/post_type_state.txt"
    try:
        with open(state_file, "r") as f:
            last = f.read().strip()
        post_type = "video" if last == "image" else "image"
    except:
        post_type = "image"

    with open(state_file, "w") as f:
        f.write(post_type)

    print(f"📌 Tipo de publicación: {post_type}", flush=True)

    if post_type == "video":
        path = create_marketing_video(product_name, image_url)
        return "video", path
    else:
        path = create_marketing_image(product_name, image_url)
        return "image", path
