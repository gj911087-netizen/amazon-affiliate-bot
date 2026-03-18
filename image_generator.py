"""
image_generator.py
Flyer animado profesional para productos de hogar y cocina.
Producto GRANDE y centrado, diseño llamativo, layout tipo e-commerce.
Solo Pillow + numpy — sin ffmpeg, funciona en Render plan gratuito.
"""
import os
import tempfile
import requests
import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

WIDTH  = 1080
HEIGHT = 1080

# ── Paletas vibrantes y profesionales ────────────────────────────────────────
PALETAS = [
    {"bg1": (8,12,35),   "bg2": (20,40,80),  "accent": (0,180,255),  "accent2": (0,255,200),  "text": (255,255,255)},
    {"bg1": (25,5,5),    "bg2": (60,10,10),  "accent": (255,60,60),  "accent2": (255,180,0),  "text": (255,255,255)},
    {"bg1": (5,20,15),   "bg2": (10,50,35),  "accent": (0,220,120),  "accent2": (0,200,255),  "text": (255,255,255)},
    {"bg1": (15,5,30),   "bg2": (40,10,70),  "accent": (180,80,255), "accent2": (255,80,180), "text": (255,255,255)},
    {"bg1": (20,10,5),   "bg2": (50,25,5),   "accent": (255,130,0),  "accent2": (255,220,0),  "text": (255,255,255)},
]
PALETA = random.choice(PALETAS)

BENEFICIOS = [
    "✅  Alta calidad garantizada",
    "✅  Fácil de usar",
    "✅  Diseño moderno y práctico",
    "✅  Ideal para tu hogar",
]
TAGS  = ["⚡ Innovador", "👌 Práctico", "🔄 Versátil", "🏆 Top Ventas"]
HOOKS = [
    "¡Esto te va a encantar! 🔥",
    "¡Descubre lo nuevo! ✨",
    "¡No te lo pierdas! 👀",
    "¡Lo más vendido! 🏆",
    "¡Tremenda oferta! 💥",
]

# ── Fuentes ───────────────────────────────────────────────────────────────────
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

def _font_r(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return _font(size)

def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print("⚠️ Error imagen: " + str(e), flush=True)
        return None

# ── Fondo con degradado + halo central ───────────────────────────────────────
def _make_bg():
    bg   = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(bg)
    bg1  = PALETA["bg1"]
    bg2  = PALETA["bg2"]
    acc  = PALETA["accent"]

    # Degradado vertical
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = int(bg1[0] + (bg2[0]-bg1[0])*t)
        g = int(bg1[1] + (bg2[1]-bg1[1])*t)
        b = int(bg1[2] + (bg2[2]-bg1[2])*t)
        draw.line([(0,i),(WIDTH,i)], fill=(r,g,b,255))

    # Halo luminoso detrás del producto
    cx, cy = WIDTH//2, HEIGHT//2 - 20
    for radius in range(360, 30, -12):
        t     = radius / 360
        alpha = int(28 * (1-t))
        cr    = min(255, int(bg2[0] + (acc[0]-bg2[0])*(1-t)*0.6))
        cg    = min(255, int(bg2[1] + (acc[1]-bg2[1])*(1-t)*0.6))
        cb    = min(255, int(bg2[2] + (acc[2]-bg2[2])*(1-t)*0.6))
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=(cr,cg,cb,alpha))

    return bg

# ── Marco y esquinas decorativas ─────────────────────────────────────────────
def _draw_frame(draw):
    acc  = PALETA["accent"]
    acc2 = PALETA["accent2"]
    draw.rectangle([0, 0, WIDTH, 8],              fill=(*acc,  255))
    draw.rectangle([0, 8, WIDTH, 14],             fill=(*acc2, 150))
    draw.rectangle([0, HEIGHT-14, WIDTH, HEIGHT-8], fill=(*acc2, 150))
    draw.rectangle([0, HEIGHT-8,  WIDTH, HEIGHT],   fill=(*acc,  255))
    sz, tk = 55, 6
    for cx, cy, dx, dy in [(0,0,1,1),(WIDTH,0,-1,1),(0,HEIGHT,1,-1),(WIDTH,HEIGHT,-1,-1)]:
        x1,x2 = sorted([cx, cx+dx*sz])
        y1,y2 = sorted([cy, cy+dy*tk])
        draw.rectangle([x1,y1,x2,y2], fill=(*acc,220))
        x1,x2 = sorted([cx, cx+dx*tk])
        y1,y2 = sorted([cy, cy+dy*sz])
        draw.rectangle([x1,y1,x2,y2], fill=(*acc,220))

# ── Badge HOGAR & COCINA ──────────────────────────────────────────────────────
def _draw_badge(draw, alpha=255):
    acc  = PALETA["accent"]
    text = "🏠  HOGAR & COCINA  •  AMAZON"
    font = _font(24)
    bbox = draw.textbbox((0,0), text, font=font)
    tw   = bbox[2]-bbox[0]
    pad  = 32
    bw, bh = tw+pad*2, 48
    bx = (WIDTH-bw)//2
    by = 20
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=24,
                            fill=(*acc, min(alpha,240)))
    draw.text((WIDTH//2, by+bh//2), text, font=font,
              fill=(10,10,20,255), anchor="mm")

# ── Hook ──────────────────────────────────────────────────────────────────────
def _draw_hook(draw, text, alpha, scale=1.0):
    acc  = PALETA["accent"]
    size = max(24, int(74*scale))
    font = _font(size)
    y    = 116
    draw.text((WIDTH//2+4, y+4), text, font=font, fill=(0,0,0,min(alpha,150)), anchor="mm")
    draw.text((WIDTH//2,   y),   text, font=font, fill=(255,255,255,min(alpha,255)), anchor="mm")
    bbox = draw.textbbox((0,0), text, font=font)
    tw   = bbox[2]-bbox[0]
    lw   = int(tw * min(alpha/255, 1.0))
    lx   = WIDTH//2 - lw//2
    draw.rectangle([lx, y+size//2+4, lx+lw, y+size//2+10], fill=(*acc, min(alpha,230)))

# ── Producto GRANDE con glow ───────────────────────────────────────────────────
def _paste_product(canvas, prod_img, scale=1.0, float_y=0, glow=True):
    max_size = int(720 * scale)
    prod = prod_img.copy()
    prod.thumbnail((max_size, max_size), Image.LANCZOS)
    pw, ph = prod.size
    px = (WIDTH  - pw) // 2
    py = (HEIGHT - ph) // 2 - 20 + float_y

    if glow:
        acc = PALETA["accent"]
        gl  = Image.new("RGBA", (pw+140, ph+140), (0,0,0,0))
        gd  = ImageDraw.Draw(gl)
        for r in range(70, 0, -5):
            a = int(35*(1-r/70))
            gd.ellipse([70-r, 70-r+ph//5, pw+70+r, ph+70-ph//5+r], fill=(*acc,a))
        gl = gl.filter(ImageFilter.GaussianBlur(20))
        canvas.paste(gl, (px-70, py-70), gl)

        sh = Image.new("RGBA", (pw+80, 60), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.ellipse([10, 8, pw+70, 52], fill=(0,0,0,90))
        sh = sh.filter(ImageFilter.GaussianBlur(16))
        canvas.paste(sh, (px-40, py+ph-10), sh)

    canvas.paste(prod, (px, py), prod)

# ── Beneficios ────────────────────────────────────────────────────────────────
def _draw_beneficios(draw, visible=4, alpha=255):
    acc  = PALETA["accent"]
    acc2 = PALETA["accent2"]
    font = _font(29)
    pad  = 55
    bh   = 54
    gap  = 10
    visible = min(visible, len(BENEFICIOS))  # nunca superar el total
    total_h = visible*(bh+gap)
    y_start = HEIGHT - total_h - 185

    for i in range(visible):
        y   = y_start + i*(bh+gap)
        a   = min(alpha, 255)
        col = acc if i%2==0 else acc2
        # Pill fondo
        draw.rounded_rectangle([pad, y, WIDTH-pad, y+bh], radius=27,
                                fill=(col[0],col[1],col[2], int(35*a/255)))
        # Borde izquierdo
        draw.rounded_rectangle([pad, y, pad+7, y+bh], radius=4,
                                fill=(*col, a))
        draw.text((pad+28, y+bh//2), BENEFICIOS[i], font=font,
                  fill=(255,255,255,a), anchor="lm")

# ── Tags ──────────────────────────────────────────────────────────────────────
def _draw_tags(draw, alpha=255):
    acc  = PALETA["accent"]
    acc2 = PALETA["accent2"]
    font = _font(26)
    y    = HEIGHT - 295
    tag_w = (WIDTH-80)//4
    x0    = 40

    for i, tag in enumerate(TAGS):
        a   = min(alpha, 255)
        col = acc if i%2==0 else acc2
        cx  = x0 + i*tag_w + tag_w//2
        tw  = tag_w - 14
        draw.rounded_rectangle([cx-tw//2, y-22, cx+tw//2, y+26],
                                radius=15, fill=(*col, int(215*a/255)))
        draw.text((cx, y+2), tag, font=font, fill=(10,10,20,a), anchor="mm")

# ── Nombre del producto ───────────────────────────────────────────────────────
def _draw_product_name(draw, name, alpha=255):
    font  = _font_r(27)
    max_w = WIDTH - 100
    words = name.split()
    lines, line = [], ""
    for w in words:
        test = (line+" "+w).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    lines = lines[:2]
    y = HEIGHT - 265
    for ln in lines:
        draw.text((WIDTH//2, y), ln, font=font,
                  fill=(210,210,210,min(alpha,180)), anchor="mm")
        y += 36

# ── CTA ───────────────────────────────────────────────────────────────────────
def _draw_cta(draw, pulse=1.0, alpha=255):
    acc  = PALETA["accent"]
    bw   = int(620*pulse)
    bh   = 78
    bx   = (WIDTH-bw)//2
    by   = HEIGHT - 135
    a    = min(alpha, 255)
    draw.rounded_rectangle([bx-12, by-12, bx+bw+12, by+bh+12],
                            radius=50, fill=(*acc, int(45*a/255)))
    draw.rounded_rectangle([bx, by, bx+bw, by+bh],
                            radius=39, fill=(*acc, a))
    draw.rounded_rectangle([bx+20, by+5, bx+bw-20, by+16],
                            radius=8,  fill=(255,255,255, int(45*a/255)))
    font = _font(37)
    draw.text((WIDTH//2, by+bh//2), "🛒  Compra Ahora en Amazon",
              font=font, fill=(10,10,20,255), anchor="mm")

# ── Watermark ─────────────────────────────────────────────────────────────────
def _draw_watermark(draw):
    font = _font_r(22)
    draw.text((WIDTH//2, HEIGHT-18), "To-do en Uno  •  @impulso_dijital",
              font=font, fill=(255,255,255,60), anchor="mm")

# ── Ease ──────────────────────────────────────────────────────────────────────
def _ease_out(t):      return 1-(1-t)**3
def _ease_in_out(t):   return t*t*(3-2*t)

# ── GENERADOR PRINCIPAL ───────────────────────────────────────────────────────
def create_animated_gif(product_name, image_url):
    print("🎬 Generando GIF animado profesional...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        print("❌ No se pudo descargar imagen", flush=True)
        return None

    prod_img  = prod_img.convert("RGBA")
    hook_text = random.choice(HOOKS)

    gif_frames = []
    FPS  = 10
    FASES = [
        ("hook",       int(1.5*FPS)),
        ("producto",   int(2.0*FPS)),
        ("beneficios", int(2.5*FPS)),
        ("tags",       int(1.5*FPS)),
        ("cta",        int(2.0*FPS)),
    ]
    total_frames = sum(n for _,n in FASES)

    for fase_name, n_frames in FASES:
        for fi in range(n_frames):
            t  = fi / max(n_frames-1, 1)
            et = _ease_out(t)
            ei = _ease_in_out(t)

            canvas = _make_bg()
            draw   = ImageDraw.Draw(canvas)
            _draw_frame(draw)
            _draw_watermark(draw)

            if fase_name == "hook":
                ha = int(255*et)
                _draw_badge(draw, alpha=ha)
                _draw_hook(draw, hook_text, ha, scale=0.65+0.35*et)
                _paste_product(canvas, prod_img, scale=0.55+0.25*et,
                               float_y=int(18*(1-et)), glow=False)

            elif fase_name == "producto":
                fy = int(-14*math.sin(t*math.pi*2))
                _draw_badge(draw, alpha=255)
                _draw_hook(draw, hook_text, alpha=55)
                _paste_product(canvas, prod_img, scale=0.94, float_y=fy, glow=True)

            elif fase_name == "beneficios":
                ps  = 0.94 - 0.27*ei
                fy  = int(-10*math.sin(t*math.pi*2)) - int(85*ei)
                vis = max(1, int(ei*4)+1)
                ba  = int(255*min(t*2.5, 1.0))
                _draw_badge(draw, alpha=255)
                _paste_product(canvas, prod_img, scale=ps, float_y=fy, glow=True)
                _draw_beneficios(draw, visible=vis, alpha=ba)

            elif fase_name == "tags":
                fy = int(-8*math.sin(t*math.pi*2)) - 85
                ta = int(255*et)
                _draw_badge(draw, alpha=255)
                _paste_product(canvas, prod_img, scale=0.67, float_y=fy, glow=True)
                _draw_beneficios(draw, visible=4, alpha=155)
                _draw_tags(draw, alpha=ta)

            elif fase_name == "cta":
                fy    = int(-6*math.sin(t*math.pi*2)) - 85
                pulse = 1.0 + 0.03*math.sin(t*math.pi*4)
                ca    = int(255*min(t*2, 1.0))
                _draw_badge(draw, alpha=255)
                _paste_product(canvas, prod_img, scale=0.60, float_y=fy, glow=True)
                _draw_beneficios(draw, visible=4, alpha=90)
                _draw_product_name(draw, product_name, alpha=ca)
                _draw_cta(draw, pulse=pulse, alpha=ca)

            frame_p = canvas.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=128)
            gif_frames.append(frame_p)

        print(f"  ✅ Fase '{fase_name}' ({n_frames} frames)", flush=True)

    out_path    = tempfile.mktemp(suffix=".gif")
    duration_ms = int(1000/FPS)

    gif_frames[0].save(
        out_path,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )
    gif_frames.clear()

    size_kb = os.path.getsize(out_path)//1024
    print(f"✅ GIF listo: {size_kb}KB | {total_frames} frames | ~{total_frames//FPS}s", flush=True)
    return out_path


def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print("🎨 Generando flyer animado: " + product_name[:60], flush=True)
    path = create_animated_gif(product_name, image_url)
    if path:
        return "gif", path
    return None, None
