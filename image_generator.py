"""
image_generator.py
Flyer animado estilo agencia latina — fondo oscuro + esferas de color vibrantes,
emojis flotantes, producto GRANDE al centro, badge HOT DEAL, CTA naranja.
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

# ── Paletas estilo agencia vibrante ──────────────────────────────────────────
PALETAS = [
    {"bg": (26,5,51),    "orb1": (255,107,0),  "orb2": (0,198,255),  "acc": (255,107,0),  "acc2": (255,224,0)},
    {"bg": (5,15,40),    "orb1": (255,0,128),  "orb2": (0,255,136),  "acc": (255,0,128),  "acc2": (0,255,200)},
    {"bg": (10,30,10),   "orb1": (0,200,80),   "orb2": (255,200,0),  "acc": (0,220,80),   "acc2": (255,220,0)},
    {"bg": (40,5,5),     "orb1": (255,50,50),  "orb2": (255,150,0),  "acc": (255,60,60),  "acc2": (255,200,0)},
    {"bg": (5,5,40),     "orb1": (100,80,255), "orb2": (255,80,200), "acc": (120,100,255),"acc2": (255,100,220)},
]
PALETA = random.choice(PALETAS)

HOOKS = [
    ("Lo mas vendido", "esta semana!"),
    ("No te lo", "pierdas!"),
    ("Esto te va", "a encantar!"),
    ("Tremenda", "oferta!"),
    ("Descubre", "lo nuevo!"),
]

BENEFICIOS = ["+ Calidad", "+ Facil uso", "+ Moderno", "Top ventas"]
EMOJIS_FLOAT = ["❤️", "😍", "👍", "💥", "⭐", "🔥", "😮", "💯"]

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

def _remove_white_bg(img, threshold=240):
    """Elimina fondo blanco/claro de la imagen del producto."""
    img = img.convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    # Pixels blancos/casi blancos → transparente
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    data[white_mask, 3] = 0
    # Suavizar bordes — pixels grises claros semi-transparentes
    near_white = (r > 200) & (g > 200) & (b > 200) & ~white_mask
    data[near_white, 3] = (data[near_white, 3] * 0.4).astype(np.uint8)
    return Image.fromarray(data)

def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        # img = _remove_white_bg(img)  # desactivado — imagen original de Amazon
        return img
    except Exception as e:
        print("⚠️ Error imagen: " + str(e), flush=True)
        return None

# ── Fondo oscuro con esferas de color ────────────────────────────────────────
def _make_bg():
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (*PALETA["bg"], 255))
    draw   = ImageDraw.Draw(canvas)
    bg     = PALETA["bg"]
    orb1   = PALETA["orb1"]
    orb2   = PALETA["orb2"]

    # Degradado base
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = max(0, min(255, int(bg[0] + 15 * (1-t))))
        g = max(0, min(255, int(bg[1] + 10 * (1-t))))
        b = max(0, min(255, int(bg[2] + 20 * (1-t))))
        draw.line([(0,i),(WIDTH,i)], fill=(r,g,b,255))

    # Esfera naranja/color1 arriba derecha
    orb_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    od = ImageDraw.Draw(orb_layer)
    cx1, cy1, r1 = WIDTH - 120, -80, 280
    for r in range(r1, 0, -8):
        t = r / r1
        a = int(200 * (1-t))
        cr = min(255, int(orb1[0] * (1-t*0.3)))
        cg = min(255, int(orb1[1] * (1-t*0.3)))
        cb = min(255, int(orb1[2] * (1-t*0.3)))
        od.ellipse([cx1-r, cy1-r, cx1+r, cy1+r], fill=(cr,cg,cb,a))
    canvas = Image.alpha_composite(canvas, orb_layer)

    # Esfera azul/color2 abajo izquierda
    orb_layer2 = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    od2 = ImageDraw.Draw(orb_layer2)
    cx2, cy2, r2 = -80, HEIGHT + 60, 260
    for r in range(r2, 0, -8):
        t = r / r2
        a = int(180 * (1-t))
        cr = min(255, int(orb2[0] * (1-t*0.3)))
        cg = min(255, int(orb2[1] * (1-t*0.3)))
        cb = min(255, int(orb2[2] * (1-t*0.3)))
        od2.ellipse([cx2-r, cy2-r, cx2+r, cy2+r], fill=(cr,cg,cb,a))
    canvas = Image.alpha_composite(canvas, orb_layer2)

    # Esfera pequeña izquierda media
    orb_layer3 = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    od3 = ImageDraw.Draw(orb_layer3)
    for r in range(130, 0, -6):
        t = r / 130
        a = int(80 * (1-t))
        od3.ellipse([-30-r, 380-r, -30+r, 380+r], fill=(*orb1, a))
    canvas = Image.alpha_composite(canvas, orb_layer3)

    return canvas

# ── Puntos decorativos ────────────────────────────────────────────────────────
def _draw_dots(draw, alpha=255):
    positions = [(120,180,16),(60,320,10),(80,540,14),(160,700,8),
                 (WIDTH-100,300,12),(WIDTH-60,480,8),(WIDTH-140,620,14)]
    for x,y,s in positions:
        a = min(alpha, 120)
        draw.ellipse([x-s,y-s,x+s,y+s], fill=(255,255,255,a))

# ── Brand logo arriba izquierda ───────────────────────────────────────────────
def _draw_brand(draw, alpha=255):
    acc = PALETA["acc"]
    # Caja blanca redondeada
    draw.rounded_rectangle([24, 24, 200, 90], radius=16,
                            fill=(255,255,255,min(alpha,240)))
    # Cuadro de color (logo)
    draw.rounded_rectangle([34, 32, 80, 82], radius=10,
                            fill=(*acc, min(alpha,255)))
    font_logo = _font(28)
    draw.text((57, 57), "T", font=font_logo, fill=(255,255,255,255), anchor="mm")    # Texto marca
    font_b = _font(18)
    font_s = _font_r(14)
    draw.text((92, 47), "Todo en", font=font_s, fill=(30,30,30,min(alpha,255)), anchor="lm")
    draw.text((92, 68), "Uno", font=font_b, fill=(30,30,30,min(alpha,255)), anchor="lm")

# ── Tagline arriba derecha ────────────────────────────────────────────────────
def _draw_tagline(draw, alpha=255):
    f1 = _font_r(20)
    f2 = _font(24)
    a  = min(alpha, 255)
    draw.text((WIDTH-30, 36), "Impulsa tus ventas con", font=f1,
              fill=(255,255,255,int(a*0.7)), anchor="rm")
    draw.text((WIDTH-30, 62), "Posts Publicitarios", font=f2,
              fill=(255,255,255,a), anchor="rm")
# ── Badge HOT DEAL rotado ─────────────────────────────────────────────────────
def _draw_hot_badge(canvas, alpha=255):
    acc  = PALETA["acc"]
    acc2 = PALETA["acc2"]
    # Crear badge circular
    size = 160
    badge = Image.new("RGBA", (size, size), (0,0,0,0))
    bd    = ImageDraw.Draw(badge)

    # Círculo exterior sombra
    bd.ellipse([4,4,size-4,size-4], fill=(0,0,0,int(alpha*0.4)))
    # Círculo principal
    for r in range(size//2-4, 0, -4):
        t = r / (size//2)
        cr = min(255, int(acc[0]*(1-t*0.2) + 255*t*0.1))
        cg = min(255, int(acc[1]*(1-t*0.2)))
        cb = min(255, int(acc[2]*(1-t*0.2)))
        bd.ellipse([size//2-r, size//2-r, size//2+r, size//2+r],
                   fill=(cr,cg,cb,min(alpha,230)))

    # Texto badge
    f1 = _font(22)
    f2 = _font(36)
    bd.text((size//2, 52), "* HOT *", font=f1, fill=(255,255,255,255), anchor="mm")
    bd.text((size//2, 92), "DEAL", font=f2, fill=(*acc2, 255), anchor="mm")
    bd.text((size//2, 122), "* * *", font=_font(18), fill=(255,255,255,200), anchor="mm")

    # Rotar y pegar
    badge_rot = badge.rotate(-20, expand=False, resample=Image.BICUBIC)
    bx = WIDTH - 200
    by = 80
    canvas.paste(badge_rot, (bx, by), badge_rot)

# ── Emojis flotantes ──────────────────────────────────────────────────────────
EMOJI_POSITIONS = [
    (70, 200), (45, 330), (90, 460), (160, 160),
    (WIDTH-80, 380), (WIDTH-55, 260), (WIDTH-110, 500),
]

def _draw_emojis(draw, alpha=255, frame=0):
    """Formas decorativas flotantes en lugar de emojis (Pillow no renderiza emojis)."""
    acc  = PALETA["acc"]
    acc2 = PALETA["acc2"]
    shapes = ["circle", "star4", "circle", "diamond", "circle", "star4", "diamond"]

    for i, (ex, ey) in enumerate(EMOJI_POSITIONS):
        fy = ey + int(8 * math.sin((frame * 0.15) + i * 1.2))
        a  = min(alpha, 180)
        col = acc if i % 2 == 0 else acc2
        s   = 22 + (i % 3) * 6  # tamaño variable

        if shapes[i] == "circle":
            draw.ellipse([ex-s, fy-s, ex+s, fy+s], fill=(*col, a))
            draw.ellipse([ex-s+4, fy-s+4, ex+s-4, fy+s-4],
                         fill=(*col, int(a*0.4)))
        elif shapes[i] == "diamond":
            pts = [(ex, fy-s), (ex+s, fy), (ex, fy+s), (ex-s, fy)]
            draw.polygon(pts, fill=(*col, a))
        elif shapes[i] == "star4":
            inner = s // 2
            pts = []
            for k in range(8):
                angle = math.pi/4 * k - math.pi/2
                r_k   = s if k % 2 == 0 else inner
                pts.append((ex + r_k*math.cos(angle), fy + r_k*math.sin(angle)))
            draw.polygon(pts, fill=(*col, a))

# ── Texto hook lado izquierdo ─────────────────────────────────────────────────
def _draw_hook_text(draw, hook, alpha=255):
    acc  = PALETA["acc"]
    acc2 = PALETA["acc2"]
    line1, line2 = hook

    # "Amazon Top Pick" pequeño
    f_small = _font(22)
    draw.text((52, 130), "* Amazon Top Pick *", font=f_small,
              fill=(*acc2, min(alpha,220)), anchor="lm")

    # Líneas grandes
    f_big = _font(72)
    draw.text((52, 210), line1, font=f_big,
              fill=(255,255,255,min(alpha,255)), anchor="lm")

    # Segunda línea con color
    draw.text((52, 300), line2, font=f_big,
              fill=(*acc, min(alpha,255)), anchor="lm")

    # Línea decorativa
    bbox1 = draw.textbbox((0,0), line1, font=f_big)
    lw = bbox1[2]-bbox1[0]
    draw.rectangle([52, 320, 52+min(lw,400), 328],
                   fill=(*acc, min(alpha,200)))

    # Subtítulo
    f_sub = _font_r(24)
    draw.text((52, 355), "Lo mas vendido esta semana", font=f_sub,
              fill=(255,255,255,min(alpha,160)), anchor="lm")

# ── Producto GRANDE al centro-derecha ────────────────────────────────────────
def _paste_product(canvas, prod_img, scale=1.0, float_y=0, glow=True):
    max_size = int(950 * scale)  # producto grande  # producto MÁS GRANDE
    prod     = prod_img.copy()
    prod.thumbnail((max_size, max_size), Image.LANCZOS)
    pw, ph   = prod.size

    # Centrar en el canvas
    px = (WIDTH  - pw) // 2
    py = (HEIGHT - ph) // 2 + float_y

    if glow:
        acc = PALETA["acc"]
        gl  = Image.new("RGBA", (pw+200, ph+200), (0,0,0,0))
        gd  = ImageDraw.Draw(gl)
        for r in range(100, 0, -5):
            a = int(50*(1-r/100))
            gd.ellipse([100-r, 100-r+ph//8, pw+100+r, ph+100-ph//8+r],
                       fill=(*acc, a))
        gl = gl.filter(ImageFilter.GaussianBlur(25))
        canvas.paste(gl, (px-100, py-100), gl)

        # Sombra inferior
        sh = Image.new("RGBA", (pw+120, 80), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.ellipse([10,10,pw+110,70], fill=(0,0,0,120))
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        canvas.paste(sh, (px-60, py+ph-15), sh)

    canvas.paste(prod, (px, py), prod)

# ── Beneficios en fila ────────────────────────────────────────────────────────
def _draw_beneficios(draw, alpha=255):
    acc    = PALETA["acc"]
    acc2   = PALETA["acc2"]
    font   = _font(26)
    n      = len(BENEFICIOS)
    pad    = 30
    total  = WIDTH - pad*2
    bw     = (total - (n-1)*12) // n
    bh     = 70
    y      = HEIGHT - 185

    for i, txt in enumerate(BENEFICIOS):
        x   = pad + i*(bw+12)
        col = acc if i%2==0 else acc2
        a   = min(alpha, 255)
        # Fondo pill semitransparente
        draw.rounded_rectangle([x, y, x+bw, y+bh], radius=18,
                                fill=(col[0],col[1],col[2],int(40*a/255)))
        draw.rounded_rectangle([x, y, x+bw, y+4], radius=4,
                                fill=(*col, a))
        # Texto centrado
        draw.text((x+bw//2, y+bh//2), txt, font=font,
                  fill=(255,255,255,a), anchor="mm")

# ── CTA naranja ───────────────────────────────────────────────────────────────
def _draw_cta(draw, pulse=1.0, alpha=255):
    acc  = PALETA["acc"]
    bw   = int(700*pulse)
    bh   = 82
    bx   = (WIDTH-bw)//2
    by   = HEIGHT - 105
    a    = min(alpha, 255)

    # Glow
    draw.rounded_rectangle([bx-14, by-14, bx+bw+14, by+bh+14],
                            radius=55, fill=(*acc, int(40*a/255)))
    # Botón
    draw.rounded_rectangle([bx, by, bx+bw, by+bh],
                            radius=41, fill=(*acc, a))
    # Brillo
    draw.rounded_rectangle([bx+25, by+6, bx+bw-25, by+20],
                            radius=10, fill=(255,255,255,int(50*a/255)))
    font = _font(40)
    draw.text((WIDTH//2, by+bh//2), "COMPRA AHORA EN AMAZON",
              font=font, fill=(255,255,255,255), anchor="mm")

# ── Nombre del producto ───────────────────────────────────────────────────────
def _draw_product_name(draw, name, alpha=255):
    font  = _font_r(24)
    max_w = WIDTH - 80
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
    y = HEIGHT - 195
    for ln in lines[:2]:
        draw.text((WIDTH//2, y), ln, font=font,
                  fill=(255,255,255,min(alpha,150)), anchor="mm")
        y += 32

# ── Watermark ─────────────────────────────────────────────────────────────────
def _draw_watermark(draw):
    font = _font_r(22)
    draw.text((WIDTH-24, HEIGHT-16), "@impulso_dijital",
              font=font, fill=(255,255,255,50), anchor="rm")

# ── Línea de contacto abajo izquierda ─────────────────────────────────────────
def _draw_contact(draw, alpha=255):
    acc  = PALETA["acc"]
    font = _font(24)
    draw.text((36, HEIGHT-16), "To-do en Uno",
              font=font, fill=(*acc, min(alpha,180)), anchor="lm")

# ── Ease ──────────────────────────────────────────────────────────────────────
def _ease_out(t):    return 1-(1-t)**3
def _ease_in_out(t): return t*t*(3-2*t)

# ── GENERADOR PRINCIPAL ───────────────────────────────────────────────────────
def create_animated_gif(product_name, image_url):
    print("🎬 Generando GIF animado estilo agencia...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        print("❌ No se pudo descargar imagen", flush=True)
        return None

    prod_img = prod_img.convert("RGBA")
    hook     = random.choice(HOOKS)

    gif_frames = []
    FPS   = 10
    FASES = [
        ("intro",      int(1.5*FPS)),   # brand + tagline entran
        ("producto",   int(2.0*FPS)),   # producto zoom in
        ("beneficios", int(2.5*FPS)),   # beneficios aparecen
        ("cta",        int(2.0*FPS)),   # CTA pulsante
        ("loop",       int(1.5*FPS)),   # loop final
    ]
    total_frames = sum(n for _,n in FASES)
    frame_idx    = 0

    for fase_name, n_frames in FASES:
        for fi in range(n_frames):
            t  = fi / max(n_frames-1, 1)
            et = _ease_out(t)
            ei = _ease_in_out(t)

            canvas = _make_bg()
            draw   = ImageDraw.Draw(canvas)

            _draw_dots(draw, alpha=int(180*et) if fase_name=="intro" else 180)
            _draw_watermark(draw)
            _draw_contact(draw, alpha=255)

            if fase_name == "intro":
                a = int(255*et)
                _draw_brand(draw, alpha=a)
                _draw_tagline(draw, alpha=a)
                _draw_hook_text(draw, hook, alpha=a)
                _draw_emojis(draw, alpha=int(180*et), frame=frame_idx)
                _draw_hot_badge(canvas, alpha=a)
                _paste_product(canvas, prod_img, scale=0.5+0.2*et,
                               float_y=int(30*(1-et)), glow=False)

            elif fase_name == "producto":
                fy = int(-12*math.sin(t*math.pi*2))
                _draw_brand(draw, alpha=255)
                _draw_tagline(draw, alpha=200)
                _draw_hook_text(draw, hook, alpha=255)
                _draw_emojis(draw, alpha=180, frame=frame_idx)
                _draw_hot_badge(canvas, alpha=255)
                _paste_product(canvas, prod_img, scale=0.7+0.3*et,
                               float_y=fy, glow=True)

            elif fase_name == "beneficios":
                fy  = int(-10*math.sin(t*math.pi*2))
                ba  = int(255*min(t*2, 1.0))
                ps  = 1.0 - 0.18*ei
                _draw_brand(draw, alpha=255)
                _draw_tagline(draw, alpha=150)
                _draw_hook_text(draw, hook, alpha=int(255*(1-ei*0.4)))
                _draw_emojis(draw, alpha=int(180*(1-ei*0.3)), frame=frame_idx)
                _draw_hot_badge(canvas, alpha=255)
                _paste_product(canvas, prod_img, scale=ps,
                               float_y=fy-int(60*ei), glow=True)
                _draw_beneficios(draw, alpha=ba)

            elif fase_name == "cta":
                fy    = int(-8*math.sin(t*math.pi*2)) - 60
                pulse = 1.0 + 0.025*math.sin(t*math.pi*4)
                ca    = int(255*min(t*2, 1.0))
                _draw_brand(draw, alpha=255)
                _draw_hot_badge(canvas, alpha=255)
                _paste_product(canvas, prod_img, scale=0.72,
                               float_y=fy, glow=True)
                _draw_beneficios(draw, alpha=180)
                _draw_product_name(draw, product_name, alpha=ca)
                _draw_cta(draw, pulse=pulse, alpha=ca)

            elif fase_name == "loop":
                fy    = int(-8*math.sin(t*math.pi*2)) - 60
                pulse = 1.0 + 0.03*math.sin(t*math.pi*3)
                _draw_brand(draw, alpha=255)
                _draw_hot_badge(canvas, alpha=255)
                _draw_emojis(draw, alpha=int(180*et), frame=frame_idx)
                _paste_product(canvas, prod_img, scale=0.72,
                               float_y=fy, glow=True)
                _draw_beneficios(draw, alpha=180)
                _draw_product_name(draw, product_name, alpha=255)
                _draw_cta(draw, pulse=pulse, alpha=255)

            frame_p = canvas.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=128)
            gif_frames.append(frame_p)
            frame_idx += 1

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
