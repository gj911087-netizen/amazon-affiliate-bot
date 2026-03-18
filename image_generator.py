"""
image_generator.py
Genera un GIF animado profesional tipo flyer para productos de hogar y cocina.
Usa solo Pillow + imageio — sin ffmpeg, funciona en Render plan gratuito.
"""
import os
import tempfile
import requests
import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

WIDTH  = 1080
HEIGHT = 1080

# ── Paleta de colores para hogar/cocina ───────────────────────────────────────
PALETAS = [
    {"bg": (15, 15, 25),     "accent": (255, 180, 0),   "accent2": (255, 100, 30)},   # dorado/naranja
    {"bg": (10, 25, 20),     "accent": (0, 220, 140),   "accent2": (0, 180, 255)},    # verde menta
    {"bg": (25, 10, 35),     "accent": (200, 80, 255),  "accent2": (255, 60, 120)},   # púrpura
    {"bg": (25, 15, 10),     "accent": (255, 120, 50),  "accent2": (255, 200, 80)},   # naranja cálido
    {"bg": (10, 20, 35),     "accent": (50, 150, 255),  "accent2": (0, 220, 200)},    # azul marino
]

import random
PALETA = random.choice(PALETAS)

# ── Fuentes ────────────────────────────────────────────────────────────────────
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

# ── Descarga imagen producto ───────────────────────────────────────────────────
def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print("⚠️ Advertencia imagen: " + str(e), flush=True)
        return None

# ── Texto con wrap automático ──────────────────────────────────────────────────
def _wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ── Fondo con degradado ────────────────────────────────────────────────────────
def _make_bg(alpha=255):
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (*PALETA["bg"], alpha))
    draw = ImageDraw.Draw(bg)
    # Degradado circular desde el centro
    cx, cy = WIDTH // 2, HEIGHT // 2
    for r in range(max(WIDTH, HEIGHT), 0, -20):
        t = r / max(WIDTH, HEIGHT)
        c = tuple(int(PALETA["bg"][i] + (PALETA["accent"][i] - PALETA["bg"][i]) * (1 - t) * 0.3) for i in range(3))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*c, alpha))
    return bg

# ── Líneas decorativas ─────────────────────────────────────────────────────────
def _draw_deco(draw, progress=1.0):
    acc = PALETA["accent"]
    acc2 = PALETA["accent2"]
    # Línea superior
    w = int(WIDTH * 0.7 * progress)
    x0 = (WIDTH - w) // 2
    draw.rectangle([x0, 28, x0 + w, 34], fill=(*acc, 200))
    draw.rectangle([x0 + 10, 38, x0 + w - 10, 41], fill=(*acc2, 120))
    # Línea inferior
    draw.rectangle([x0, HEIGHT - 34, x0 + w, HEIGHT - 28], fill=(*acc, 200))
    draw.rectangle([x0 + 10, HEIGHT - 41, x0 + w - 10, HEIGHT - 38], fill=(*acc2, 120))
    # Esquinas — coordenadas siempre ordenadas (min, max)
    corner = 60
    thick = 6
    for x, y, dx, dy in [(30, 30, 1, 1), (WIDTH - 30, 30, -1, 1),
                          (30, HEIGHT - 30, 1, -1), (WIDTH - 30, HEIGHT - 30, -1, -1)]:
        x1a, x2a = sorted([x, x + dx * corner])
        y1a, y2a = sorted([y, y + dy * thick])
        draw.rectangle([x1a, y1a, x2a, y2a], fill=(*acc, 180))
        x1b, x2b = sorted([x, x + dx * thick])
        y1b, y2b = sorted([y, y + dy * corner])
        draw.rectangle([x1b, y1b, x2b, y2b], fill=(*acc, 180))

# ── Badge "HOGAR & COCINA" ─────────────────────────────────────────────────────
def _draw_badge(draw, alpha=255):
    acc = PALETA["accent"]
    bw, bh = 340, 48
    bx = (WIDTH - bw) // 2
    by = 60
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24,
                            fill=(*acc, min(alpha, 230)))
    font = _font(22)
    draw.text((WIDTH // 2, by + bh // 2), "🏠 HOGAR & COCINA  •  AMAZON",
              font=font, fill=(20, 20, 20, 255), anchor="mm")

# ── Hook text animado ──────────────────────────────────────────────────────────
def _draw_hook(draw, text, alpha):
    font = _font(68)
    shadow_color = (0, 0, 0, min(alpha, 180))
    text_color = (255, 255, 255, min(alpha, 255))
    acc = PALETA["accent"]
    y = 168
    # Sombra
    draw.text((WIDTH // 2 + 3, y + 3), text, font=font, fill=shadow_color, anchor="mm")
    draw.text((WIDTH // 2, y), text, font=font, fill=text_color, anchor="mm")
    # Subrayado accent
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.rectangle([WIDTH // 2 - tw // 2, y + 38,
                    WIDTH // 2 + tw // 2, y + 44], fill=(*acc, min(alpha, 220)))

# ── Beneficios ────────────────────────────────────────────────────────────────
BENEFICIOS = [
    ("✔", "Alta calidad garantizada"),
    ("✔", "Fácil de usar"),
    ("✔", "Diseño moderno"),
    ("✔", "Ideal para tu hogar"),
]

def _draw_beneficios(draw, visible=4, alpha=255):
    acc = PALETA["accent"]
    acc2 = PALETA["accent2"]
    font_icon = _font(32)
    font_txt  = _font(30)
    y_start = HEIGHT - 310
    for i, (icon, txt) in enumerate(BENEFICIOS[:visible]):
        y = y_start + i * 58
        a = min(alpha, 255)
        # Pill de fondo
        draw.rounded_rectangle([80, y - 18, WIDTH - 80, y + 34],
                                radius=20, fill=(255, 255, 255, int(18 * a / 255)))
        # Icono
        draw.text((130, y + 8), icon, font=font_icon, fill=(*acc, a), anchor="mm")
        # Texto
        draw.text((160, y + 8), txt, font=font_txt, fill=(255, 255, 255, a), anchor="lm")

# ── Etiquetas pop ─────────────────────────────────────────────────────────────
TAGS = ["Innovador", "Práctico", "Versátil", "Top Ventas"]

def _draw_tags(draw, alpha=255):
    acc = PALETA["accent"]
    acc2 = PALETA["accent2"]
    font = _font(28)
    x_positions = [140, 360, 580, 800]
    y = HEIGHT // 2 + 240
    for i, (tag, xc) in enumerate(zip(TAGS, x_positions)):
        a = min(alpha, 255)
        col = acc if i % 2 == 0 else acc2
        tw_half = 70
        draw.rounded_rectangle([xc - tw_half, y - 20, xc + tw_half, y + 28],
                                radius=16, fill=(*col, int(200 * a / 255)))
        draw.text((xc, y + 4), tag, font=font, fill=(15, 15, 15, a), anchor="mm")

# ── CTA ───────────────────────────────────────────────────────────────────────
def _draw_cta(draw, pulse=1.0, alpha=255):
    acc = PALETA["accent"]
    acc2 = PALETA["accent2"]
    bw = int(500 * pulse)
    bh = 72
    bx = (WIDTH - bw) // 2
    by = HEIGHT - 160
    a = min(alpha, 255)
    # Sombra glow
    draw.rounded_rectangle([bx - 8, by - 8, bx + bw + 8, by + bh + 8],
                            radius=42, fill=(*acc, int(60 * a / 255)))
    # Botón principal
    draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                            radius=36, fill=(*acc, a))
    font = _font(34)
    draw.text((WIDTH // 2, by + bh // 2), "👉  Compra Ahora en Amazon",
              font=font, fill=(15, 15, 15, 255), anchor="mm")
    # Watermarks
    fw = _font(26)
    draw.text((WIDTH // 2, HEIGHT - 60), "To-do en Uno  •  @impulso_dijital",
              font=fw, fill=(255, 255, 255, 70), anchor="mm")

# ── Producto centrado con zoom/float ─────────────────────────────────────────
def _paste_product(canvas, prod_img, scale=1.0, float_y=0):
    """Pega el producto centrado con escala y desplazamiento vertical."""
    size = int(420 * scale)
    prod = prod_img.copy()
    prod.thumbnail((size, size), Image.LANCZOS)
    pw, ph = prod.size
    px = (WIDTH - pw) // 2
    py = (HEIGHT - ph) // 2 - 60 + float_y  # centro visual ligeramente arriba
    # Sombra suave
    shadow = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([10, ph - 10, pw + 30, ph + 35], fill=(0, 0, 0, 60))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(shadow, (px - 20, py - 20), shadow)
    # Producto
    canvas.paste(prod, (px, py), prod)

# ── GENERADOR PRINCIPAL DE FRAMES ────────────────────────────────────────────
def _ease_in_out(t):
    return t * t * (3 - 2 * t)

def create_animated_gif(product_name, image_url):
    print("🎬 Generando GIF animado...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        print("❌ No se pudo descargar imagen", flush=True)
        return None

    # Preparar imagen del producto con fondo transparente
    prod_img = prod_img.convert("RGBA")

    frames = []
    FPS = 12  # frames por segundo
    # Fases: hook(1.5s) | producto(2s) | beneficios(2.5s) | tags(1.5s) | cta(2s) = ~10s
    FASE = [
        ("hook",        int(1.5 * FPS)),
        ("producto",    int(2.0 * FPS)),
        ("beneficios",  int(2.5 * FPS)),
        ("tags",        int(1.5 * FPS)),
        ("cta",         int(2.0 * FPS)),
    ]

    total_frames = sum(n for _, n in FASE)
    frame_idx = 0

    # Hooks rotativos para variedad
    hooks = ["¡Esto te va a encantar! 🔥", "¡Descubre lo nuevo! ✨", "¡No te lo pierdas! 👀"]
    hook_text = random.choice(hooks)

    for fase_name, n_frames in FASE:
        for fi in range(n_frames):
            t = fi / max(n_frames - 1, 1)  # 0.0 → 1.0
            et = _ease_in_out(t)

            canvas = _make_bg()
            draw = ImageDraw.Draw(canvas)

            # Decoraciones siempre visibles
            _draw_deco(draw, progress=1.0)
            _draw_badge(draw, alpha=255)

            if fase_name == "hook":
                alpha = int(255 * et) if t < 0.5 else 255
                _draw_hook(draw, hook_text, alpha)
                # Producto ya aparece de fondo suave
                _paste_product(canvas, prod_img, scale=0.6 + 0.1 * et, float_y=0)

            elif fase_name == "producto":
                _draw_hook(draw, hook_text, alpha=80)
                # Zoom in elegante
                scale = 0.7 + 0.3 * et
                float_y = int(-15 * np.sin(t * np.pi))
                _paste_product(canvas, prod_img, scale=scale, float_y=float_y)

            elif fase_name == "beneficios":
                # Producto flotando
                float_y = int(-10 * np.sin(t * 2 * np.pi))
                _paste_product(canvas, prod_img, scale=0.72, float_y=float_y - 60)
                # Beneficios aparecen uno a uno
                visible = max(1, int(et * 4) + 1)
                alpha = int(255 * min(t * 3, 1.0))
                _draw_beneficios(draw, visible=visible, alpha=alpha)

            elif fase_name == "tags":
                _paste_product(canvas, prod_img, scale=0.65, float_y=-70)
                alpha = int(255 * et)
                _draw_tags(draw, alpha=alpha)
                _draw_beneficios(draw, visible=4, alpha=120)

            elif fase_name == "cta":
                _paste_product(canvas, prod_img, scale=0.60, float_y=-80)
                _draw_beneficios(draw, visible=4, alpha=80)
                # Pulso del botón
                pulse = 1.0 + 0.04 * np.sin(t * 4 * np.pi)
                alpha = int(255 * min(t * 2, 1.0))
                _draw_cta(draw, pulse=pulse, alpha=alpha)
                # Nombre del producto
                font_name = _font(26)
                name_short = product_name[:55] + ("..." if len(product_name) > 55 else "")
                draw.text((WIDTH // 2, HEIGHT - 195), name_short,
                          font=font_name, fill=(220, 220, 220, 180), anchor="mm")

            # Convertir a RGB para imageio
            rgb = canvas.convert("RGB")
            frames.append(np.array(rgb))
            frame_idx += 1

        print(f"  ✅ Fase '{fase_name}' completada ({n_frames} frames)", flush=True)

    # Guardar GIF
    out_path = tempfile.mktemp(suffix=".gif")
    duration = 1.0 / FPS  # segundos por frame

    imageio.mimsave(
        out_path,
        frames,
        format="GIF",
        duration=duration,
        loop=0,          # loop infinito
        palettesize=256,
        subrectangles=True,  # compresión inteligente
    )

    size_kb = os.path.getsize(out_path) // 1024
    print(f"✅ GIF listo: {size_kb}KB | {total_frames} frames | ~{total_frames // FPS}s", flush=True)
    return out_path


# ── Punto de entrada ──────────────────────────────────────────────────────────
def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print("🎨 Generando flyer animado: " + product_name[:60], flush=True)
    path = create_animated_gif(product_name, image_url)
    if path:
        return "gif", path
    return None, None
