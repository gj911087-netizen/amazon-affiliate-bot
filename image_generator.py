import os, math, textwrap, time, subprocess, tempfile
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from io import BytesIO
 
WIDTH  = 1080
HEIGHT = 1920
FPS    = 25
DUR    = 15
TOTAL  = FPS * DUR
 
PROD_SIZE = 750
CARD_PAD  = 38
 
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
 
def _ease_out(t):
    return 1 - (1 - t) ** 3
 
def _ease_in_out(t):
    return t * t * (3 - 2 * t)
 
def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        return img
    except Exception as e:
        print(f"Advertencia imagen: {e}", flush=True)
        return None
 
def _make_bg(prod_img):
    bg = prod_img.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(55))
    bg = ImageEnhance.Brightness(bg).enhance(0.14)
    canvas = bg.convert("RGBA")
    grad = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(HEIGHT):
        r  = y / HEIGHT
        bl = max(0, int(28 - 20 * r))
        al = int(95 + 45 * r)
        gd.line([(0, y), (WIDTH, y)], fill=(4, 7, bl, al))
    return Image.alpha_composite(canvas, grad)
 
def _frame(prod_img, bg, frame_n, product_name):
    t = frame_n / TOTAL
    canvas = bg.copy()
 
    if t < 0.12:
        p       = _ease_out(t / 0.12)
        slide_y = int((1 - p) * 190)
        g_alpha = p
        scale   = 0.86 + 0.14 * p
        tilt    = 0.0
    elif t < 0.88:
        p       = (t - 0.12) / 0.76
        slide_y = 0
        g_alpha = 1.0
        pulse   = 1.0 + math.sin(p * math.pi * 3) * 0.014
        scale   = pulse
        tilt    = math.sin(p * math.pi * 2.5) * 0.052
    else:
        p       = (t - 0.88) / 0.12
        slide_y = 0
        g_alpha = 1.0 - _ease_in_out(p)
        scale   = 1.0
        tilt    = 0.0
 
    pw = int(PROD_SIZE * scale)
    ph = int(PROD_SIZE * scale)
    cw = pw + CARD_PAD * 2
    ch = ph + CARD_PAD * 2
 
    SB = 30
    shadow = Image.new("RGBA", (cw + SB * 2, ch + SB * 2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [SB + 6, SB + 12, SB + cw - 6, SB + ch - 6],
        radius=44, fill=(0, 0, 0, 145)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(SB))
 
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw, ch], radius=44, fill=(255, 255, 255, 252))
 
    pc = prod_img.copy()
    pc.thumbnail((pw, ph), Image.LANCZOS)
    px = (cw - pc.width)  // 2
    py = (ch - pc.height) // 2
    if pc.mode == "RGBA":
        card.paste(pc, (px, py), pc)
    else:
        card.paste(pc, (px, py))
 
    if abs(tilt) > 0.003:
        skew_x = math.tan(tilt) * ch * 0.32
        card = card.transform(
            (cw, ch), Image.AFFINE,
            (1, tilt * 0.28, -skew_x * 0.14, 0, 1, 0),
            Image.BILINEAR
        )
        compress = max(0.75, 1.0 - abs(tilt) * 0.45)
        new_cw = int(cw * compress)
        if new_cw > 200:
            resized = card.resize((new_cw, ch), Image.LANCZOS)
            card_c  = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            card_c.paste(resized, ((cw - new_cw) // 2, 0), resized)
            card = card_c
 
    def _alpha(img, a):
        if a >= 0.999:
            return img
        r, g, b, c = img.split()
        c = c.point(lambda x: int(x * a))
        return Image.merge("RGBA", (r, g, b, c))
 
    card   = _alpha(card,   g_alpha)
    shadow = _alpha(shadow, g_alpha * 0.82)
 
    cx = (WIDTH  - cw)  // 2
    cy = 470 + slide_y
 
    canvas.paste(shadow, (cx - SB, cy - SB), shadow)
    canvas.paste(card,   (cx, cy),           card)
 
    draw = ImageDraw.Draw(canvas)
    ta   = int(255 * g_alpha)
 
    lines = textwrap.wrap(product_name[:55], width=20)[:2]
    ty = 240
    fn = _font(54)
    for line in lines:
        draw.text((WIDTH // 2 + 2, ty + 2), line, font=fn,
                  fill=(0, 0, 0, ta // 2), anchor="mm")
        draw.text((WIDTH // 2,     ty    ), line, font=fn,
                  fill=(255, 255, 255, ta), anchor="mm")
        ty += 68
 
    if g_alpha > 0.25:
        fb = _font(33)
        draw.text((WIDTH // 2 + 1, ty + 17), "AMAZON BEST SELLER",
                  font=fb, fill=(0, 0, 0, ta // 2), anchor="mm")
        draw.text((WIDTH // 2,     ty + 16), "AMAZON BEST SELLER",
                  font=fb, fill=(255, 190, 30, ta), anchor="mm")
 
    if 0.15 < t < 0.85:
        fw  = _font(35)
        wma = int(90 * g_alpha)
        wm  = "To-do en Uno  |  @impulso_dijital"
        draw.text((WIDTH // 2 + 1, HEIGHT // 2 + 1), wm,
                  font=fw, fill=(0, 0, 0, wma // 2), anchor="mm")
        draw.text((WIDTH // 2,     HEIGHT // 2    ), wm,
                  font=fw, fill=(255, 255, 255, wma), anchor="mm")
 
    if t > 0.20:
        p2    = min(1.0, (t - 0.20) / 0.10)
        cta_y = HEIGHT - 115 + int((1 - _ease_out(p2)) * 50)
        cta_a = int(215 * _ease_out(p2) * g_alpha)
        fc    = _font(44)
        draw.text((WIDTH // 2, cta_y), "Link en descripcion",
                  font=fc, fill=(255, 255, 255, cta_a), anchor="mm")
 
    return canvas.convert("RGB")
 
def _make_audio(dur):
    out = tempfile.mktemp(suffix=".aac")
    cmd = [
        "ffmpeg", "-y",
        "-f","lavfi","-i", f"sine=frequency=65.41:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=130.81:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=261.63:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=329.63:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=392.00:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=523.25:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=659.25:duration={dur}",
        "-f","lavfi","-i", f"sine=frequency=783.99:duration={dur}",
        "-filter_complex",
        "[0]volume=0.10[sub];"
        "[1]volume=0.18,aecho=0.55:0.25:65:0.28[bas];"
        "[2]volume=0.17[c1];"
        "[3]volume=0.16[c2];"
        "[4]volume=0.15[c3];"
        "[5]volume=0.14,aecho=0.50:0.30:190:0.22[m1];"
        "[6]volume=0.11[m2];"
        "[7]volume=0.06[sh];"
        "[sub][bas][c1][c2][c3][m1][m2][sh]amix=inputs=8:duration=longest,"
        "equalizer=f=80:t=o:w=70:g=7,"
        "equalizer=f=250:t=o:w=200:g=-4,"
        "equalizer=f=3500:t=o:w=1500:g=5,"
        "highpass=f=35,"
        f"afade=t=in:st=0:d=2.0,"
        f"afade=t=out:st={dur-2}:d=1.8,"
        "volume=1.05",
        "-c:a","aac","-b:a","192k",
        out,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=30)
    if r.returncode == 0:
        return out
    print(f"Audio sin musica: {r.stderr.decode()[-100:]}", flush=True)
    return None
 
def create_marketing_video(product_name, image_url):
    print("Iniciando reel 9:16 15s...", flush=True)
 
    prod_img = _download(image_url)
    if prod_img is None:
        prod_img = Image.new("RGBA", (600, 600), (40, 40, 40, 255))
 
    bg         = _make_bg(prod_img)
    audio_path = _make_audio(DUR)
    out_path   = tempfile.mktemp(suffix=".mp4")
 
    cmd = [
        "ffmpeg", "-y",
        "-f","rawvideo","-vcodec","rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt","rgb24",
        "-r", str(FPS),
        "-i","pipe:0",
    ]
    if audio_path and os.path.exists(audio_path):
        cmd += ["-i", audio_path, "-map","0:v","-map","1:a",
                "-c:a","aac","-b:a","192k"]
    else:
        cmd += ["-map","0:v"]
 
    cmd += [
        "-t", str(DUR),
        "-c:v","libx264",
        "-pix_fmt","yuv420p",
        "-preset","fast",
        "-crf","22",
        "-movflags","+faststart",
        out_path,
    ]
 
    try:
        t0   = time.time()
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
 
        for i in range(TOTAL):
            frm = _frame(prod_img, bg, i, product_name)
            proc.stdin.write(frm.tobytes())
            if i % 75 == 0:
                print(f"  {i/TOTAL*100:.0f}% ({time.time()-t0:.0f}s)", flush=True)
 
        proc.stdin.close()
        proc.wait()
 
        if proc.returncode != 0:
            print(f"Error ffmpeg: {proc.stderr.read().decode()[-300:]}", flush=True)
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
 
def generate_image(product_name, image_url=None):
    if not image_url:
        return None, None
    print(f"Generando reel: {product_name[:60]}", flush=True)
    path = create_marketing_video(product_name, image_url)
    if path:
        return "video", path
    return None, None
