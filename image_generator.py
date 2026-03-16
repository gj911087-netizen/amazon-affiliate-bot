"""
image_generator.py
Reel profesional 9:16 - showcase limpio
- Solo producto en card blanca + marca de agua sin fondo
- Animaciones: float + breathe + spotlight
- Musica: acordes con armonicos + doble eco (suena a instrumento real, no pitido)
- Seguro en Render gratis: ~65s render
"""

import os, math, time, subprocess, tempfile
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from io import BytesIO

WIDTH    = 1080
HEIGHT   = 1920
FPS      = 25
DUR      = 12
TOTAL    = FPS * DUR

PROD_MAX = 820
CARD_PAD = 40
SB       = 24


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


def _eoq(t):  return 1 - (1 - t) ** 4
def _eio(t):  return t * t * (3 - 2 * t)


def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print("Advertencia imagen: " + str(e), flush=True)
        return None


def _make_bg(prod_img, style):
    """6 estilos de fondo que rotan en cada video."""
    if style == 1:
        bg = prod_img.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(45))
        bg = ImageEnhance.Brightness(bg).enhance(0.12).convert("RGBA")
        grad = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
        gd = ImageDraw.Draw(grad)
        for y in range(HEIGHT):
            a = int(105 + 45*(y/HEIGHT))
            gd.line([(0,y),(WIDTH,y)], fill=(4,4,14,a))
        return Image.alpha_composite(bg, grad)
    elif style == 2:
        bg = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r=int(15+20*(y/HEIGHT)); g=int(5+10*(y/HEIGHT)); b=int(45+30*(y/HEIGHT))
            draw.line([(0,y),(WIDTH,y)],fill=(r,g,b,255))
        glow = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
        gd = ImageDraw.Draw(glow)
        for r in range(600,0,-15):
            alpha=int(18*(1-r/600))
            gd.ellipse([WIDTH//2-r,HEIGHT//2-r,WIDTH//2+r,HEIGHT//2+r],fill=(80,50,180,alpha))
        return Image.alpha_composite(bg, glow)
    elif style == 3:
        bg = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r=int(25+15*(y/HEIGHT)); g=int(12+8*(y/HEIGHT)); b=int(5+3*(y/HEIGHT))
            draw.line([(0,y),(WIDTH,y)],fill=(r,g,b,255))
        glow = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
        gd = ImageDraw.Draw(glow)
        for r in range(700,0,-15):
            alpha=int(15*(1-r/700))
            gd.ellipse([WIDTH//2-r,HEIGHT//3-r,WIDTH//2+r,HEIGHT//3+r],fill=(200,80,10,alpha))
        return Image.alpha_composite(bg, glow)
    elif style == 4:
        bg = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r=int(5+5*(y/HEIGHT)); g=int(20+20*(y/HEIGHT)); b=int(35+25*(y/HEIGHT))
            draw.line([(0,y),(WIDTH,y)],fill=(r,g,b,255))
        glow = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
        gd = ImageDraw.Draw(glow)
        for r in range(650,0,-15):
            alpha=int(20*(1-r/650))
            gd.ellipse([WIDTH//2-r,HEIGHT//2-r,WIDTH//2+r,HEIGHT//2+r],fill=(0,180,160,alpha))
        return Image.alpha_composite(bg, glow)
    elif style == 5:
        bg = prod_img.convert("RGB").resize((WIDTH,HEIGHT),Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(35))
        bg = ImageEnhance.Brightness(bg).enhance(0.20)
        bg = ImageEnhance.Color(bg).enhance(2.5).convert("RGBA")
        overlay = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,140))
        return Image.alpha_composite(bg, overlay)
    else:
        bg = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r=int(35+20*(y/HEIGHT)); g=int(5+3*(y/HEIGHT)); b=int(5+3*(y/HEIGHT))
            draw.line([(0,y),(WIDTH,y)],fill=(r,g,b,255))
        glow = Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,0))
        gd = ImageDraw.Draw(glow)
        for r in range(600,0,-15):
            alpha=int(18*(1-r/600))
            gd.ellipse([WIDTH//2-r,HEIGHT//2-r,WIDTH//2+r,HEIGHT//2+r],fill=(180,20,20,alpha))
        return Image.alpha_composite(bg, glow)


def _build_resources(prod_img, style):
    bg = _make_bg(prod_img, style)

    # Sombra pre-calculada (una vez)
    _sw = PROD_MAX + CARD_PAD * 2
    sh  = Image.new("RGBA", (_sw + SB * 2, _sw + SB * 2), (0, 0, 0, 0))
    sd  = ImageDraw.Draw(sh)
    sd.rounded_rectangle(
        [SB + 4, SB + 10, SB + _sw - 4, SB + _sw - 10],
        radius=48, fill=(0, 0, 0, 115)
    )
    shadow_base = sh.filter(ImageFilter.GaussianBlur(SB))

    # Marca de agua: SOLO letras blancas semitransparentes, cero fondo
    fw   = _font(36)
    WM_W = 780
    WM_H = 52
    wm   = Image.new("RGBA", (WM_W, WM_H), (0, 0, 0, 0))
    wd   = ImageDraw.Draw(wm)
    wd.text((WM_W // 2 + 1, WM_H // 2 + 1),
            "To-do en Uno  |  @impulso_dijital",
            font=fw, fill=(0, 0, 0, 25), anchor="mm")
    wd.text((WM_W // 2, WM_H // 2),
            "To-do en Uno  |  @impulso_dijital",
            font=fw, fill=(255, 255, 255, 68), anchor="mm")

    # Cache de overlays spotlight (evita crear imagenes por frame)
    spotlight_cache = {}
    for alpha in range(0, 30, 5):
        spotlight_cache[alpha] = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, alpha))

    return bg, shadow_base, wm, (WM_W, WM_H), spotlight_cache


def _ap(img, a):
    if a >= 0.999:
        return img
    r2, g2, b2, c2 = img.split()
    c2 = c2.point(lambda x: int(x * a))
    return Image.merge("RGBA", (r2, g2, b2, c2))


def _frame(prod_img, bg, shadow_base, wm_img, wm_size, spotlight_cache, frame_n):
    t       = frame_n / TOTAL
    WM_W, _ = wm_size
    WM_H    = 52
    canvas  = bg.copy()

    if t < 0.15:
        p        = _eoq(t / 0.15)
        g_alpha  = p
        scale    = 0.88 + 0.12 * p
        float_y  = int((1 - p) * 100)
        spotlight = 0

    elif t < 0.88:
        p        = (t - 0.15) / 0.73
        g_alpha  = 1.0
        # BREATHE: 2 ciclos suaves
        scale    = 1.0 + math.sin(p * math.pi * 2) * 0.018
        # FLOAT: sincronizado con breathe
        float_y  = int(math.sin(p * math.pi * 2) * 16)
        # SPOTLIGHT: oscurece fondo en peak
        spotlight = round(abs(math.sin(p * math.pi)) * 25 / 5) * 5

    else:
        p        = (t - 0.88) / 0.12
        g_alpha  = 1.0 - _eio(p)
        scale    = 1.0
        float_y  = 0
        spotlight = 0

    if spotlight > 0 and spotlight in spotlight_cache:
        canvas = Image.alpha_composite(canvas, spotlight_cache[spotlight])

    pw     = int(PROD_MAX * scale)
    cw     = pw + CARD_PAD * 2
    shadow = shadow_base.resize((cw + SB * 2, cw + SB * 2), Image.BILINEAR)

    card = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    cd   = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw, cw], radius=48, fill=(255, 255, 255, 252))
    pc   = prod_img.copy()
    pc.thumbnail((pw, pw), Image.LANCZOS)
    card.paste(pc, ((cw - pc.width) // 2, (cw - pc.height) // 2), pc)

    card   = _ap(card,   g_alpha)
    shadow = _ap(shadow, g_alpha * 0.74)

    cx = (WIDTH  - cw) // 2
    cy = (HEIGHT - cw) // 2 - 70 + float_y
    canvas.paste(shadow, (cx - SB, cy - SB), shadow)
    canvas.paste(card,   (cx, cy),           card)

    # Solo marca de agua, nada mas
    if 0.12 < t < 0.88:
        canvas.alpha_composite(wm_img, ((WIDTH - WM_W) // 2, HEIGHT - 145))

    return canvas.convert("RGB")


def _make_audio(dur):
    """
    Musica con armonicos reales + doble eco.
    6 voces, formula estable en Render.
    """
    out = tempfile.mktemp(suffix=".aac")

    freqs  = [65.41, 130.81, 164.81, 196.00, 261.63, 329.63]
    vols   = [0.30,  0.20,   0.17,   0.15,   0.18,   0.15  ]
    labels = list("abcdef")

    inp = []
    for f in freqs:
        inp += ["-f", "lavfi", "-i",
                "sine=frequency=" + str(f) + ":duration=" + str(dur)]

    parts = ["[" + str(i) + "]volume=" + str(v) + "[" + l + "]"
             for i, (l, v) in enumerate(zip(labels, vols))]
    mix   = "".join("[" + l + "]" for l in labels) + "amix=inputs=6:duration=longest"

    fc = (
        ";".join(parts) + ";" + mix
        + ",aecho=0.65:0.45:60:0.40"
        + ",aecho=0.55:0.35:180:0.28"
        + ",bass=g=11"
        + ",treble=g=6"
        + ",highpass=f=38"
        # CRITICO: convertir a estereo 44100Hz
        # Facebook e Instagram silencian audio mono o de baja calidad
        + ",aformat=channel_layouts=stereo"
        + ",afade=t=in:st=0:d=1.8"
        + ",afade=t=out:st=" + str(dur - 2) + ":d=2.0"
        + ",volume=0.92"
    )

    cmd = ["ffmpeg", "-y"] + inp + ["-filter_complex", fc,
                                     "-c:a", "aac", "-b:a", "192k",
                                     "-ar", "44100",
                                     "-ac", "2",
                                     out]
    r = subprocess.run(cmd, capture_output=True, timeout=25)

    if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 5000:
        print("Audio generado: " + str(os.path.getsize(out) // 1024) + "KB", flush=True)
        return out

    print("Audio fallo rc=" + str(r.returncode), flush=True)
    if r.returncode != 0:
        print(r.stderr.decode()[-150:], flush=True)

    # Fallback: audio mas simple (3 voces, sin EQ complejo)
    out2 = tempfile.mktemp(suffix=".aac")
    cmd2 = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=261.63:duration=" + str(dur),
        "-f", "lavfi", "-i", "sine=frequency=329.63:duration=" + str(dur),
        "-f", "lavfi", "-i", "sine=frequency=196.00:duration=" + str(dur),
        "-filter_complex",
        "[0]volume=0.35[a];[1]volume=0.28[b];[2]volume=0.22[c];"
        "[a][b][c]amix=inputs=3:duration=longest"
        ",bass=g=10,treble=g=5"
        ",afade=t=in:st=0:d=1.5"
        ",afade=t=out:st=" + str(dur - 2) + ":d=1.8"
        ",volume=0.9",
        "-c:a", "aac", "-b:a", "192k",
        "-ar", "44100", "-ac", "2", out2
    ]
    r2 = subprocess.run(cmd2, capture_output=True, timeout=20)
    if r2.returncode == 0 and os.path.exists(out2) and os.path.getsize(out2) > 1000:
        print("Audio fallback OK: " + str(os.path.getsize(out2) // 1024) + "KB", flush=True)
        return out2

    print("Audio fallback tambien fallo", flush=True)
    return None


def create_marketing_video(product_name, image_url):
    print("Iniciando reel " + str(DUR) + "s...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        prod_img = Image.new("RGBA", (600, 600), (35, 35, 35, 255))

    import random as _rand
    style = _rand.randint(1, 6)
    print("Estilo de fondo: " + str(style), flush=True)
    bg, shadow_base, wm_img, wm_size, spotlight_cache = _build_resources(prod_img, style)
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
        cmd += ["-i", audio_path,
                "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k",
                "-ar", "44100", "-ac", "2"]
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
            frm = _frame(prod_img, bg, shadow_base,
                         wm_img, wm_size, spotlight_cache, i)
            proc.stdin.write(frm.tobytes())
            if i % 75 == 0:
                print("  " + str(round(i / TOTAL * 100)) + "% ("
                      + str(round(time.time() - t0)) + "s)", flush=True)

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            print("Error ffmpeg: " + proc.stderr.read().decode()[-200:], flush=True)
            return None

        size = os.path.getsize(out_path) / 1024
        print("Reel listo: " + str(round(size)) + "KB en "
              + str(round(time.time() - t0)) + "s", flush=True)
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


def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print("Generando reel: " + product_name[:60], flush=True)
    path = create_marketing_video(product_name, image_url)
    if path:
        return "video", path
    return None, None
