"""
image_generator.py
Reel 9:16  |  12 segundos  |  1080x1920  |  25 fps
- Producto en card blanca centrada (no ocupa toda la pantalla)
- Animacion 3D: entrada slide-up  ->  tilt perspectiva  ->  fade out
- Sombra pre-calculada (no blur por frame) para velocidad en Render gratis
- Marca de agua solo texto, semitransparente, sin ningun fondo ni caja
- Musica corporativa suave con acorde Do mayor
- Tiempo de render estimado en Render free: ~80s (seguro)
"""

import os, math, textwrap, time, subprocess, tempfile
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from io import BytesIO

# ── Constantes ────────────────────────────────────────────────────────────────
WIDTH    = 1080
HEIGHT   = 1920
FPS      = 25
DUR      = 12          # segundos — seguro para Render gratuito
TOTAL    = FPS * DUR   # 300 frames

PROD_MAX = 750         # lado maximo del producto (bien enmarcado, no fullscreen)
CARD_PAD = 38
SB       = 22          # radio del blur de sombra

# ── Tipografia ────────────────────────────────────────────────────────────────
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

# ── Curvas ────────────────────────────────────────────────────────────────────
def _eo(t):   return 1 - (1 - t) ** 3          # ease-out cubico
def _eio(t):  return t * t * (3 - 2 * t)       # ease-in-out cuadratico

# ── Descarga imagen producto ──────────────────────────────────────────────────
def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print(f"Advertencia imagen: {e}", flush=True)
        return None

# ── Recursos pre-calculados (se crean UNA vez antes de renderizar) ────────────
def _build_resources(prod_img):
    # Fondo: blur oscuro del producto
    bg = prod_img.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.14).convert("RGBA")
    # Gradiente oscuro encima para elegancia
    grad = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(HEIGHT):
        bl = max(0, int(26 - 18 * y / HEIGHT))
        al = int(90 + 40 * y / HEIGHT)
        gd.line([(0, y), (WIDTH, y)], fill=(4, 6, bl, al))
    bg = Image.alpha_composite(bg, grad)

    # Sombra de card: calculada UNA sola vez, se resizea por frame (mucho mas rapido)
    _sw = PROD_MAX + CARD_PAD * 2
    sh  = Image.new("RGBA", (_sw + SB * 2, _sw + SB * 2), (0, 0, 0, 0))
    sd  = ImageDraw.Draw(sh)
    sd.rounded_rectangle(
        [SB + 5, SB + 10, SB + _sw - 5, SB + _sw - 10],
        radius=38, fill=(0, 0, 0, 125)
    )
    shadow_base = sh.filter(ImageFilter.GaussianBlur(SB))

    # Fonts
    fonts = {s: _font(s) for s in [54, 33, 35, 44]}

    # Marca de agua pre-renderizada como RGBA
    # Alpha=65 sobre blanco puro -> muy suave, no molesta, pero se lee
    WM_W, WM_H = 760, 54
    wm = Image.new("RGBA", (WM_W, WM_H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.text((WM_W // 2 + 1, WM_H // 2 + 1),
            "To-do en Uno  |  @impulso_dijital",
            font=fonts[35], fill=(0, 0, 0, 28), anchor="mm")
    wd.text((WM_W // 2, WM_H // 2),
            "To-do en Uno  |  @impulso_dijital",
            font=fonts[35], fill=(255, 255, 255, 65), anchor="mm")

    return bg, shadow_base, fonts, wm, (WM_W, WM_H)

# ── Genera un frame ───────────────────────────────────────────────────────────
def _frame(prod_img, bg, shadow_base, fonts, wm_img, wm_size, frame_n, name):
    t = frame_n / TOTAL
    canvas = bg.copy()
    WM_W, WM_H = wm_size

    # Fases de animacion
    if t < 0.12:
        p       = _eo(t / 0.12)
        slide_y = int((1 - p) * 180)
        g       = p
        scale   = 0.87 + 0.13 * p
        tilt    = 0.0
    elif t < 0.88:
        p       = (t - 0.12) / 0.76
        slide_y = 0
        g       = 1.0
        scale   = 1.0 + math.sin(p * math.pi * 3) * 0.013
        tilt    = math.sin(p * math.pi * 2.5) * 0.048
    else:
        p       = (t - 0.88) / 0.12
        slide_y = 0
        g       = 1.0 - _eio(p)
        scale   = 1.0
        tilt    = 0.0

    pw = int(PROD_MAX * scale)
    cw = pw + CARD_PAD * 2
    ch = cw

    # Sombra: resize desde base (sin blur por frame)
    shadow = shadow_base.resize((cw + SB * 2, ch + SB * 2), Image.BILINEAR)

    # Card blanca con producto
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd   = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw, ch], radius=38, fill=(255, 255, 255, 250))
    pc = prod_img.copy()
    pc.thumbnail((pw, pw), Image.LANCZOS)
    card.paste(pc, ((cw - pc.width) // 2, (ch - pc.height) // 2), pc)

    # Tilt 3D
    if abs(tilt) > 0.003:
        skew_x = math.tan(tilt) * ch * 0.30
        card = card.transform(
            (cw, ch), Image.AFFINE,
            (1, tilt * 0.25, -skew_x * 0.12, 0, 1, 0),
            Image.BILINEAR
        )
        compress = max(0.80, 1.0 - abs(tilt) * 0.38)
        nw = int(cw * compress)
        if nw > 200:
            res = card.resize((nw, ch), Image.BILINEAR)
            cc  = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            cc.paste(res, ((cw - nw) // 2, 0), res)
            card = cc

    # Aplicar alpha global (fade in/out)
    def _ap(img, a):
        if a >= 0.999:
            return img
        r2, gg, b2, c2 = img.split()
        c2 = c2.point(lambda x: int(x * a))
        return Image.merge("RGBA", (r2, gg, b2, c2))

    card   = _ap(card,   g)
    shadow = _ap(shadow, g * 0.76)

    cx = (WIDTH - cw)  // 2
    cy = 470 + slide_y
    canvas.paste(shadow, (cx - SB, cy - SB), shadow)
    canvas.paste(card,   (cx, cy),           card)

    # Textos
    draw = ImageDraw.Draw(canvas)
    ta   = int(255 * g)

    lines = textwrap.wrap(name[:50], width=20)[:2]
    ty = 240
    for line in lines:
        draw.text((WIDTH // 2 + 2, ty + 2), line,
                  font=fonts[54], fill=(0, 0, 0, ta // 2), anchor="mm")
        draw.text((WIDTH // 2,     ty    ), line,
                  font=fonts[54], fill=(255, 255, 255, ta), anchor="mm")
        ty += 66

    if g > 0.20:
        draw.text((WIDTH // 2 + 1, ty + 16), "AMAZON BEST SELLER",
                  font=fonts[33], fill=(0, 0, 0, ta // 2), anchor="mm")
        draw.text((WIDTH // 2,     ty + 15), "AMAZON BEST SELLER",
                  font=fonts[33], fill=(255, 190, 30, ta), anchor="mm")

    # Marca de agua — solo letras, semitransparente, sin caja ni fondo
    if 0.14 < t < 0.86:
        wx = (WIDTH  - WM_W) // 2
        wy = (HEIGHT - WM_H) // 2
        canvas.alpha_composite(wm_img, (wx, wy))

    # CTA discreto
    if t > 0.20:
        p2    = min(1.0, (t - 0.20) / 0.10)
        cta_a = int(200 * _eo(p2) * g)
        draw.text((WIDTH // 2, HEIGHT - 112), "Link en descripcion",
                  font=fonts[44], fill=(255, 255, 255, cta_a), anchor="mm")

    return canvas.convert("RGB")

# ── Genera audio corporativo suave ────────────────────────────────────────────
def _make_audio(dur):
    out = tempfile.mktemp(suffix=".aac")
    cmd = [
        "ffmpeg", "-y",
        "-f","lavfi","-i", f"sine=frequency=65.41:duration={dur}",   # C2
        "-f","lavfi","-i", f"sine=frequency=130.81:duration={dur}",  # C3
        "-f","lavfi","-i", f"sine=frequency=261.63:duration={dur}",  # C4
        "-f","lavfi","-i", f"sine=frequency=329.63:duration={dur}",  # E4
        "-f","lavfi","-i", f"sine=frequency=392.00:duration={dur}",  # G4
        "-f","lavfi","-i", f"sine=frequency=523.25:duration={dur}",  # C5
        "-f","lavfi","-i", f"sine=frequency=659.25:duration={dur}",  # E5
        "-f","lavfi","-i", f"sine=frequency=783.99:duration={dur}",  # G5
        "-filter_complex",
        "[0]volume=0.10[sub];"
        "[1]volume=0.17,aecho=0.55:0.25:65:0.28[bas];"
        "[2]volume=0.16[c1];"
        "[3]volume=0.15[c2];"
        "[4]volume=0.14[c3];"
        "[5]volume=0.13,aecho=0.50:0.30:190:0.22[m1];"
        "[6]volume=0.10[m2];"
        "[7]volume=0.05[sh];"
        "[sub][bas][c1][c2][c3][m1][m2][sh]amix=inputs=8:duration=longest,"
        "equalizer=f=80:t=o:w=70:g=7,"
        "equalizer=f=250:t=o:w=200:g=-4,"
        "equalizer=f=3500:t=o:w=1500:g=5,"
        "highpass=f=35,"
        f"afade=t=in:st=0:d=1.8,"
        f"afade=t=out:st={dur-2}:d=1.8,"
        "volume=1.05",
        "-c:a","aac","-b:a","128k",
        out,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=25)
    if r.returncode == 0:
        return out
    print(f"Audio: {r.stderr.decode()[-80:]}", flush=True)
    return None

# ── Pipeline principal ────────────────────────────────────────────────────────
def create_marketing_video(product_name, image_url):
    print(f"Iniciando reel 9:16 {DUR}s...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        prod_img = Image.new("RGBA", (600, 600), (35, 35, 35, 255))

    bg, shadow_base, fonts, wm_img, wm_size = _build_resources(prod_img)
    audio_path = _make_audio(DUR)
    out_path   = tempfile.mktemp(suffix=".mp4")

    cmd = [
        "ffmpeg", "-y",
        "-f","rawvideo", "-vcodec","rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt","rgb24",
        "-r", str(FPS),
        "-i","pipe:0",
    ]
    if audio_path and os.path.exists(audio_path):
        cmd += ["-i", audio_path, "-map","0:v", "-map","1:a",
                "-c:a","aac", "-b:a","128k"]
    else:
        cmd += ["-map","0:v"]

    cmd += [
        "-t", str(DUR),
        "-c:v","libx264",
        "-pix_fmt","yuv420p",
        "-preset","ultrafast",   # mas rapido que 'fast' — seguro en Render gratis
        "-crf","24",
        "-movflags","+faststart",
        out_path,
    ]

    try:
        t0   = time.time()
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        for i in range(TOTAL):
            frm = _frame(prod_img, bg, shadow_base, fonts,
                         wm_img, wm_size, i, product_name)
            proc.stdin.write(frm.tobytes())
            if i % 75 == 0:
                print(f"  {i/TOTAL*100:.0f}% ({time.time()-t0:.0f}s)", flush=True)

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            print(f"Error ffmpeg: {proc.stderr.read().decode()[-200:]}", flush=True)
            return None

        size = os.path.getsize(out_path) / 1024
        print(f"Reel listo: {size:.0f} KB en {time.time()-t0:.0f}s", flush=True)
        return out_path

    except Exception as e:
        print(f"Error render: {e}", flush=True)
        return None
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass

# ── Punto de entrada ──────────────────────────────────────────────────────────
def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print(f"Generando reel: {product_name[:60]}", flush=True)
    path = create_marketing_video(product_name, image_url)
    if path:
        return "video", path
    return None, None
