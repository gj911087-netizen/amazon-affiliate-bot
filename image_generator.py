import os
import random
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import subprocess
import tempfile

WIDTH  = 1080
HEIGHT = 1920

# ── Tipografía ────────────────────────────────────────────────────────────────
def get_font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ── Descarga imagen del producto ──────────────────────────────────────────────
def download_image(url):
    try:
        r = requests.get(url, timeout=15,
                         headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        return img
    except Exception as e:
        print(f"⚠️ Error descargando imagen: {e}", flush=True)
        return None

# ── Construye el frame limpio (sin barras amarillas) ─────────────────────────
def build_clean_frame(product_name: str, image_url: str) -> Image.Image:
    """
    Frame 1080×1920:
    • Imagen del producto cubre TODO el canvas (cover crop)
    • Overlay oscuro muy suave solo para legibilidad
    • Nombre del producto en la parte superior (texto blanco, sin caja)
    • Marca de agua centrada semitransparente (solo texto, sin fondo)
    • Nada más — video limpio y profesional
    """
    # ── 1. Fondo negro por si falla la descarga
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 10, 255))

    # ── 2. Imagen del producto como fondo (cover crop)
    product_img = download_image(image_url)
    if product_img:
        # Mejorar nitidez / brillo ligeramente
        enhancer = ImageEnhance.Sharpness(product_img)
        product_img = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Brightness(product_img)
        product_img = enhancer.enhance(1.05)

        # Cover crop: escalar para llenar todo el canvas
        iw, ih = product_img.size
        scale = max(WIDTH / iw, HEIGHT / ih)
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        product_img = product_img.resize((new_w, new_h), Image.LANCZOS)

        # Centrar
        x = (WIDTH  - new_w) // 2
        y = (HEIGHT - new_h) // 2
        canvas.paste(product_img, (x, y), product_img)

        # ── 3. Overlay oscuro suave (solo para que el texto sea legible)
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 100))
        canvas = Image.alpha_composite(canvas, overlay)

        # ── 4. Gradiente suave arriba y abajo para el texto
        grad_top = Image.new("RGBA", (WIDTH, 300), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad_top)
        for i in range(300):
            alpha = int(160 * (1 - i / 300))
            gd.line([(0, i), (WIDTH, i)], fill=(0, 0, 0, alpha))
        canvas.alpha_composite(grad_top, (0, 0))

        grad_bot = Image.new("RGBA", (WIDTH, 250), (0, 0, 0, 0))
        gb = ImageDraw.Draw(grad_bot)
        for i in range(250):
            alpha = int(140 * (i / 250))
            gb.line([(0, i), (WIDTH, i)], fill=(0, 0, 0, alpha))
        canvas.alpha_composite(grad_bot, (0, HEIGHT - 250))

    draw = ImageDraw.Draw(canvas)

    # ── 5. Nombre del producto — parte superior (solo texto, sin caja)
    font_name = get_font(54)
    name_clean = product_name.replace("&amp;", "&").replace("&#39;", "'")
    lines = textwrap.wrap(name_clean, width=22)[:3]  # máx 3 líneas
    y_text = 55
    for line in lines:
        # Sombra sutil para legibilidad
        draw.text((WIDTH // 2 + 2, y_text + 2), line,
                  font=font_name, fill=(0, 0, 0, 160), anchor="mm")
        draw.text((WIDTH // 2, y_text), line,
                  font=font_name, fill=(255, 255, 255, 240), anchor="mm")
        y_text += 68

    # ── 6. Marca de agua centrada — SOLO letras, semitransparente, sin fondo
    font_wm = get_font(38)
    wm_text = "To-do en Uno  ·  @impulso_dijital"
    cx = WIDTH // 2
    cy = HEIGHT // 2

    # Sombra muy ligera para que se lea sobre cualquier fondo
    draw.text((cx + 2, cy + 2), wm_text,
              font=font_wm, fill=(0, 0, 0, 80), anchor="mm")
    # Texto principal — blanco con 45% de opacidad (semitransparente)
    draw.text((cx, cy), wm_text,
              font=font_wm, fill=(255, 255, 255, 115), anchor="mm")

    # ── 7. Pequeño texto "Link en bio" abajo (discreto, sin barra)
    font_bio = get_font(40)
    draw.text((cx + 1, HEIGHT - 75 + 1), "👆 Link en descripción",
              font=font_bio, fill=(0, 0, 0, 100), anchor="mm")
    draw.text((cx, HEIGHT - 75), "👆 Link en descripción",
              font=font_bio, fill=(255, 255, 255, 190), anchor="mm")

    return canvas

# ── Audio: acorde musical agradable generado con ffmpeg ──────────────────────
AUDIO_PRESETS = [
    # (freq1, freq2, freq3, volume) — acordes mayores calmados
    (261.63, 329.63, 392.00, 0.22),   # Do mayor
    (293.66, 369.99, 440.00, 0.22),   # Re mayor
    (329.63, 415.30, 493.88, 0.20),   # Mi mayor
    (349.23, 440.00, 523.25, 0.22),   # Fa mayor
    (392.00, 493.88, 587.33, 0.20),   # Sol mayor
    (440.00, 554.37, 659.25, 0.20),   # La mayor
]

def generate_audio(duration: int) -> str:
    """Genera un archivo AAC con acorde musical suave."""
    f1, f2, f3, vol = random.choice(AUDIO_PRESETS)
    audio_path = tempfile.mktemp(suffix=".aac")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={f1}:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency={f2}:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency={f3}:duration={duration}",
        "-filter_complex",
        f"[0][1][2]amix=inputs=3:duration=longest,"
        f"afade=t=in:st=0:d=1,"
        f"afade=t=out:st={duration-1}:d=1,"
        f"volume={vol}",
        "-c:a", "aac", "-b:a", "128k",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=30)
    if result.returncode == 0:
        return audio_path
    print("⚠️ Audio fallback silencioso", flush=True)
    return None

# ── Generador principal de vídeo ──────────────────────────────────────────────
VIDEO_DURATION = 7   # segundos — tiempo suficiente para que Instagram lo acepte

def create_marketing_video(product_name: str, image_url: str) -> str | None:
    print("🎬 Creando reel profesional 9:16...", flush=True)

    # 1. Frame
    try:
        frame = build_clean_frame(product_name, image_url)
    except Exception as e:
        print(f"❌ Error creando frame: {e}", flush=True)
        return None

    img_path = tempfile.mktemp(suffix=".jpg")
    frame.convert("RGB").save(img_path, "JPEG", quality=95)

    # 2. Audio
    audio_path = generate_audio(VIDEO_DURATION)

    # 3. Video
    output_path = tempfile.mktemp(suffix=".mp4")
    try:
        # Filtro de video: fade in/out suave + zoom Ken Burns muy sutil
        zoom_scale = 1.04  # zoom muy sutil (4%) para dar vida sin distorsionar
        vf = (
            f"scale={int(WIDTH * zoom_scale)}:{int(HEIGHT * zoom_scale)},"
            f"crop={WIDTH}:{HEIGHT}:'(iw-{WIDTH})/2*(1+t/{VIDEO_DURATION})':"
            f"'(ih-{HEIGHT})/2*(1+t/{VIDEO_DURATION})',"
            f"fade=t=in:st=0:d=0.8,"
            f"fade=t=out:st={VIDEO_DURATION - 0.8}:d=0.8"
        )

        if audio_path and os.path.exists(audio_path):
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", img_path,
                "-i", audio_path,
                "-vf", vf,
                "-map", "0:v",
                "-map", "1:a",
                "-t", str(VIDEO_DURATION),
                "-r", "25",
                "-c:v", "libx264",
                "-c:a", "aac", "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                "-preset", "ultrafast",
                "-crf", "24",
                "-movflags", "+faststart",
                output_path
            ]
        else:
            # Sin audio si falló
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", img_path,
                "-vf", vf,
                "-t", str(VIDEO_DURATION),
                "-r", "25",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "ultrafast",
                "-crf", "24",
                "-movflags", "+faststart",
                output_path
            ]

        result = subprocess.run(cmd, capture_output=True, timeout=90)

        if result.returncode != 0:
            print(f"❌ ffmpeg error: {result.stderr.decode()[-400:]}", flush=True)
            return None

        size_kb = os.path.getsize(output_path) / 1024
        print(f"✅ Reel listo: {size_kb:.0f} KB — {VIDEO_DURATION}s con audio", flush=True)
        return output_path

    except subprocess.TimeoutExpired:
        print("❌ ffmpeg tardó demasiado (>90s)", flush=True)
        return None
    except Exception as e:
        print(f"❌ Error video: {e}", flush=True)
        return None
    finally:
        # Limpiar temporales
        for p in [img_path, audio_path]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

# ── Punto de entrada ──────────────────────────────────────────────────────────
def generate_image(product_name: str, image_url: str = None):
    """
    Retorna ("video", path) si el reel se creó correctamente,
    o (None, None) si falló.
    """
    if not image_url:
        print("⚠️ Sin URL de imagen", flush=True)
        return None, None

    print(f"📌 Generando reel para: {product_name[:60]}", flush=True)
    path = create_marketing_video(product_name, image_url)
    if path:
        return "video", path
    return None, None
