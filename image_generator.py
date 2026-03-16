"""
image_generator.py
Reel profesional 9:16 - estilo marketing limpio
- Producto centrado en card blanca con sombra - protagonista total
- Fondo borroso oscuro elegante (del mismo producto)
- Animacion: fade-in suave + zoom gentil + fade-out
- SOLO marca de agua semitransparente, ningun texto encima del producto
- Musica estilo soul jazz original (sin derechos)
- 12 segundos - seguro para Render plan gratuito (~67s render)
"""

import os, math, time, subprocess, tempfile
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from io import BytesIO

WIDTH    = 1080
HEIGHT   = 1920
FPS      = 25
DUR      = 12
TOTAL    = FPS * DUR   # 300 frames

PROD_SIZE = 800   # producto grande pero con espacio alrededor
CARD_PAD  = 40
SB        = 24    # blur radio de sombra


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


# ── Curvas de animacion ───────────────────────────────────────────────────────
def _eoq(t):  return 1 - (1 - t) ** 4    # ease-out quartic (suave)
def _eio(t):  return t * t * (3 - 2 * t) # ease-in-out cuadratico


# ── Descarga imagen ───────────────────────────────────────────────────────────
def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print(f"Advertencia imagen: {e}", flush=True)
        return None


# ── Recursos pre-calculados (una sola vez antes del loop) ────────────────────
def _build_resources(prod_img):
    # Fondo: producto muy borroso y oscuro
    bg = prod_img.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(45))
    bg = ImageEnhance.Brightness(bg).enhance(0.12)
    bg = bg.convert("RGBA")

    # Gradiente oscuro encima para profundidad
    grad = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(HEIGHT):
        a = int(110 + 40 * (y / HEIGHT))
        gd.line([(0, y), (WIDTH, y)], fill=(5, 5, 15, a))
    bg = Image.alpha_composite(bg, grad)

    # Sombra de card (se calcula UNA vez, se resizea por frame)
    _sw = PROD_SIZE + CARD_PAD * 2
    sh  = Image.new("RGBA", (_sw + SB * 2, _sw + SB * 2), (0, 0, 0, 0))
    sd  = ImageDraw.Draw(sh)
    sd.rounded_rectangle(
        [SB + 4, SB + 10, SB + _sw - 4, SB + _sw - 10],
        radius=44, fill=(0, 0, 0, 120)
    )
    shadow_base = sh.filter(ImageFilter.GaussianBlur(SB))

    # Marca de agua: SOLO texto, sin caja, muy transparente
    # Alpha=70 sobre 255 → se ve pero no molesta para nada
    fw  = _font(36)
    WM_W, WM_H = 780, 52
    wm  = Image.new("RGBA", (WM_W, WM_H), (0, 0, 0, 0))
    wd  = ImageDraw.Draw(wm)
    wd.text((WM_W // 2 + 1, WM_H // 2 + 1),
            "To-do en Uno  |  @impulso_dijital",
            font=fw, fill=(0, 0, 0, 25), anchor="mm")
    wd.text((WM_W // 2, WM_H // 2),
            "To-do en Uno  |  @impulso_dijital",
            font=fw, fill=(255, 255, 255, 70), anchor="mm")

    return bg, shadow_base, wm, (WM_W, WM_H)


# ── Genera un frame ───────────────────────────────────────────────────────────
def _frame(prod_img, bg, shadow_base, wm_img, wm_size, frame_n):
    t      = frame_n / TOTAL
    canvas = bg.copy()
    WM_W, WM_H = wm_size

    # Fases de animacion
    if t < 0.15:                         # ENTRADA: fade + slide suave
        p       = _eoq(t / 0.15)
        g_alpha = p
        slide_y = int((1 - p) * 120)
        scale   = 0.92 + 0.08 * p

    elif t < 0.88:                       # SHOWCASE: zoom arco suave (sin rebotes)
        p       = (t - 0.15) / 0.73
        g_alpha = 1.0
        slide_y = 0
        # Arco sinusoidal unico: sube 2.2% y vuelve — se ve vivo, no robotico
        scale   = 1.0 + math.sin(p * math.pi) * 0.022

    else:                                # SALIDA: fade out limpio
        p       = (t - 0.88) / 0.12
        g_alpha = 1.0 - _eio(p)
        slide_y = 0
        scale   = 1.0

    pw = int(PROD_SIZE * scale)
    cw = pw + CARD_PAD * 2
    ch = cw

    # Sombra (resize sin recalcular blur — rapido)
    shadow = shadow_base.resize((cw + SB * 2, ch + SB * 2), Image.BILINEAR)

    # Card blanca con producto — sin ningun texto encima
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd   = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw, ch], radius=44, fill=(255, 255, 255, 252))
    pc = prod_img.copy()
    pc.thumbnail((pw, pw), Image.LANCZOS)
    card.paste(pc, ((cw - pc.width) // 2, (ch - pc.height) // 2), pc)

    # Aplicar alpha global
    def _ap(img, a):
        if a >= 0.999:
            return img
        r2, g2, b2, c2 = img.split()
        c2 = c2.point(lambda x: int(x * a))
        return Image.merge("RGBA", (r2, g2, b2, c2))

    card   = _ap(card,   g_alpha)
    shadow = _ap(shadow, g_alpha * 0.75)

    # Posicion: centrado, ligeramente por encima del centro (balance visual)
    cx = (WIDTH  - cw) // 2
    cy = (HEIGHT - ch) // 2 - 80 + slide_y

    canvas.paste(shadow, (cx - SB, cy - SB), shadow)
    canvas.paste(card,   (cx, cy),           card)

    # UNICO elemento de texto: marca de agua discreta abajo
    if 0.12 < t < 0.88:
        wx = (WIDTH  - WM_W) // 2
        wy = HEIGHT - 140
        canvas.alpha_composite(wm_img, (wx, wy))

    return canvas.convert("RGB")


# ── Audio estilo soul jazz original ──────────────────────────────────────────
def _make_audio(dur):
    """
    Acorde Cmaj7 con walking bass y shimmer.
    8 voces, max 2 filtros EQ (limite seguro con ffmpeg en Render).
    """
    out    = tempfile.mktemp(suffix=".aac")
    freqs  = [65.41, 130.81, 196.00, 261.63, 329.63, 392.00, 523.25, 659.25]
    vols   = [0.18,  0.24,   0.14,   0.20,   0.18,   0.16,   0.13,   0.07 ]
    labels = list("abcdefgh")

    inp = []
    for f in freqs:
        inp += ["-f", "lavfi", "-i", "sine=frequency=" + str(f) + ":duration=" + str(dur)]

    parts = [f"[{i}]volume={v}[{l}]" for i, (l, v) in enumerate(zip(labels, vols))]
    mix   = "".join(f"[{l}]" for l in labels) + "amix=inputs=8:duration=longest"
    chain = (
        ";" .join(parts) + ";" + mix
        + ",bass=g=8"
        + ",treble=g=5"
        + ",highpass=f=40"
        + ",afade=t=in:st=0:d=1.5"
        + ",afade=t=out:st=" + str(dur - 2) + ":d=1.8"
        + ",volume=1.1"
    )

    cmd = ["ffmpeg", "-y"] + inp + ["-filter_complex", chain,
                                     "-c:a", "aac", "-b:a", "192k", out]
    r = subprocess.run(cmd, capture_output=True, timeout=25)
    if r.returncode == 0:
        return out
    print("Audio sin musica:", r.stderr.decode()[-80:], flush=True)
    return None


# ── Pipeline principal ────────────────────────────────────────────────────────
def create_marketing_video(product_name, image_url):
    print("Iniciando reel 9:16 " + str(DUR) + "s...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        prod_img = Image.new("RGBA", (600, 600), (35, 35, 35, 255))

    bg, shadow_base, wm_img, wm_size = _build_resources(prod_img)
    audio_path = _make_audio(DUR)
    out_path   = tempfile.mktemp(suffix=".mp4")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", str(WIDTH) + "x" + str(HEIGHT),
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
    ]
    if audio_path and os.path.exists(audio_path):
        cmd += ["-i", audio_path, "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-map", "0:v"]

    cmd += [
        "-t", str(DUR),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "ultrafast",
        "-crf", "22",
        "-movflags", "+faststart",
        out_path,
    ]

    try:
        t0   = time.time()
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        for i in range(TOTAL):
            frm = _frame(prod_img, bg, shadow_base, wm_img, wm_size, i)
            proc.stdin.write(frm.tobytes())
            if i % 75 == 0:
                print("  " + str(round(i / TOTAL * 100)) + "% (" + str(round(time.time() - t0)) + "s)", flush=True)

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            print("Error ffmpeg: " + proc.stderr.read().decode()[-200:], flush=True)
            return None

        size = os.path.getsize(out_path) / 1024
        print("Reel listo: " + str(round(size)) + "KB en " + str(round(time.time() - t0)) + "s", flush=True)
        return out_path

    except Exception as e:
        print("Error render: " + str(e), flush=True)
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
    print("Generando reel: " + product_name[:60], flush=True)
    path = create_marketing_video(product_name, image_url)
    if path:
        return "video", path
    return None, None
