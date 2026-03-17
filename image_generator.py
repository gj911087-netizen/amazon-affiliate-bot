"""
image_generator.py
Imagenes de marketing profesionales 1080x1080
- Badge dorado premium "Recomendado" en esquina superior izquierda de la card
- Marca de agua: "To-do en Uno" izquierda | "@impulso_dijital" derecha
- 6 fondos diferentes rotativos
- Solo letras semitransparentes, sin cajas ni fondos en la marca de agua
"""

import os, random
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from io import BytesIO
import tempfile

WIDTH  = 1080
HEIGHT = 1080


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


def _download(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        print("Advertencia imagen: " + str(e), flush=True)
        return None


def _make_bg(prod_img, style):
    """6 fondos rotativos — cada publicacion se ve diferente."""
    if style == 1:
        # Blur del producto oscuro azulado
        bg = prod_img.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg).enhance(0.15).convert("RGBA")
        grad = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for y in range(HEIGHT):
            a = int(80 + 60 * (y / HEIGHT))
            gd.line([(0, y), (WIDTH, y)], fill=(4, 4, 18, a))
        return Image.alpha_composite(bg, grad)

    elif style == 2:
        # Degradado morado-azul elegante con glow central
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r = int(18 + 15 * (y / HEIGHT))
            g = int(8  + 10 * (y / HEIGHT))
            b = int(50 + 25 * (y / HEIGHT))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for r in range(500, 0, -12):
            alpha = int(20 * (1 - r / 500))
            gd.ellipse([WIDTH//2-r, HEIGHT//2-r, WIDTH//2+r, HEIGHT//2+r],
                       fill=(90, 55, 200, alpha))
        return Image.alpha_composite(bg, glow)

    elif style == 3:
        # Degradado naranja-negro premium con glow superior
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r = int(30 + 12 * (y / HEIGHT))
            g = int(14 +  8 * (y / HEIGHT))
            b = int(5  +  2 * (y / HEIGHT))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for r in range(550, 0, -12):
            alpha = int(16 * (1 - r / 550))
            gd.ellipse([WIDTH//2-r, HEIGHT//3-r, WIDTH//2+r, HEIGHT//3+r],
                       fill=(220, 90, 15, alpha))
        return Image.alpha_composite(bg, glow)

    elif style == 4:
        # Degradado teal-verde tech/moderno
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r = int(5  +  4 * (y / HEIGHT))
            g = int(22 + 18 * (y / HEIGHT))
            b = int(38 + 20 * (y / HEIGHT))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for r in range(500, 0, -12):
            alpha = int(22 * (1 - r / 500))
            gd.ellipse([WIDTH//2-r, HEIGHT//2-r, WIDTH//2+r, HEIGHT//2+r],
                       fill=(0, 190, 170, alpha))
        return Image.alpha_composite(bg, glow)

    elif style == 5:
        # Blur vívido saturado y colorido
        bg = prod_img.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(30))
        bg = ImageEnhance.Brightness(bg).enhance(0.22)
        bg = ImageEnhance.Color(bg).enhance(2.8).convert("RGBA")
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 130))
        return Image.alpha_composite(bg, overlay)

    else:  # style == 6
        # Degradado rojo oscuro impactante
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r = int(38 + 18 * (y / HEIGHT))
            g = int(6  +  3 * (y / HEIGHT))
            b = int(6  +  3 * (y / HEIGHT))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for r in range(480, 0, -12):
            alpha = int(20 * (1 - r / 480))
            gd.ellipse([WIDTH//2-r, HEIGHT//2-r, WIDTH//2+r, HEIGHT//2+r],
                       fill=(190, 22, 22, alpha))
        return Image.alpha_composite(bg, glow)


def _draw_badge(canvas, card_x, card_y):
    """
    Badge premium dorado 'Recomendado' con chulito.
    Posicion: esquina superior izquierda de la card, ligeramente superpuesto.
    """
    BADGE_W = 225
    BADGE_H = 54
    RADIUS  = 27

    bx = card_x - 8
    by = card_y - 22

    # Sombra del badge
    shadow = Image.new("RGBA", (BADGE_W + 14, BADGE_H + 14), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([7, 7, BADGE_W + 7, BADGE_H + 7],
                         radius=RADIUS, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    canvas.paste(shadow, (bx - 7, by - 7), shadow)

    # Fondo dorado del badge
    badge = Image.new("RGBA", (BADGE_W, BADGE_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    # Base dorada
    bd.rounded_rectangle([0, 0, BADGE_W, BADGE_H],
                         radius=RADIUS, fill=(212, 175, 55, 255))
    # Highlight sutil en la mitad superior para dar volumen
    bd.rounded_rectangle([0, 0, BADGE_W, BADGE_H // 2],
                         radius=RADIUS, fill=(235, 205, 85, 110))
    canvas.paste(badge, (bx, by), badge)

    # Texto del badge: chulito + Recomendado
    draw = ImageDraw.Draw(canvas)
    font_badge = _font(25)
    text = "✓  Recomendado"
    # Sombra del texto
    draw.text((bx + BADGE_W // 2 + 1, by + BADGE_H // 2 + 1),
              text, font=font_badge, fill=(80, 50, 0, 130), anchor="mm")
    # Texto principal oscuro sobre dorado
    draw.text((bx + BADGE_W // 2, by + BADGE_H // 2),
              text, font=font_badge, fill=(45, 25, 0, 255), anchor="mm")

    return canvas


def _draw_watermark(canvas):
    """
    Marca de agua profesional bien posicionada:
    - 'To-do en Uno'     → esquina inferior izquierda
    - '@impulso_dijital' → esquina inferior derecha
    Solo letras semitransparentes, sin ningun fondo ni caja.
    """
    draw   = ImageDraw.Draw(canvas)
    fw     = _font(30)
    MARGIN = 30
    Y_POS  = HEIGHT - 40

    # Sombras sutiles para legibilidad sobre cualquier fondo
    draw.text((MARGIN + 1, Y_POS + 1), "To-do en Uno",
              font=fw, fill=(0, 0, 0, 32), anchor="lm")
    draw.text((WIDTH - MARGIN - 1, Y_POS + 1), "@impulso_dijital",
              font=fw, fill=(0, 0, 0, 32), anchor="rm")

    # Textos blancos semitransparentes (80/255 = ~31% opacidad)
    draw.text((MARGIN, Y_POS), "To-do en Uno",
              font=fw, fill=(255, 255, 255, 80), anchor="lm")
    draw.text((WIDTH - MARGIN, Y_POS), "@impulso_dijital",
              font=fw, fill=(255, 255, 255, 80), anchor="rm")

    # Separador vertical sutil en el centro
    draw.line([(WIDTH // 2, Y_POS - 10), (WIDTH // 2, Y_POS + 10)],
              fill=(255, 255, 255, 35), width=1)

    return canvas


def create_marketing_image(product_name, image_url):
    print("Creando imagen de marketing...", flush=True)

    prod_img = _download(image_url)
    if prod_img is None:
        prod_img = Image.new("RGBA", (500, 500), (200, 200, 200, 255))

    # Estilo aleatorio cada vez
    style = random.randint(1, 6)
    print("Estilo fondo: " + str(style), flush=True)

    # Fondo
    canvas = _make_bg(prod_img, style)

    # Card del producto
    CARD_SIZE = 800
    CARD_PAD  = 38
    PROD_SIZE = CARD_SIZE - CARD_PAD * 2
    SH        = 22

    # Sombra de la card
    shadow = Image.new("RGBA", (CARD_SIZE + SH * 2, CARD_SIZE + SH * 2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([SH + 5, SH + 8, SH + CARD_SIZE - 5, SH + CARD_SIZE - 8],
                         radius=38, fill=(0, 0, 0, 115))
    shadow = shadow.filter(ImageFilter.GaussianBlur(SH))

    # Card blanca
    card = Image.new("RGBA", (CARD_SIZE, CARD_SIZE), (0, 0, 0, 0))
    cd   = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, CARD_SIZE, CARD_SIZE], radius=38,
                         fill=(255, 255, 255, 252))

    # Producto centrado dentro de la card
    pc = prod_img.copy()
    pc.thumbnail((PROD_SIZE, PROD_SIZE), Image.LANCZOS)
    px = (CARD_SIZE - pc.width)  // 2
    py = (CARD_SIZE - pc.height) // 2
    if pc.mode == "RGBA":
        card.paste(pc, (px, py), pc)
    else:
        card.paste(pc, (px, py))

    # Posicion de la card: centrada, ligeramente arriba
    cx = (WIDTH  - CARD_SIZE) // 2
    cy = (HEIGHT - CARD_SIZE) // 2 - 25

    canvas.paste(shadow, (cx - SH, cy - SH), shadow)
    canvas.paste(card,   (cx, cy),           card)

    # Badge "Recomendado" en esquina superior izquierda de la card
    canvas = _draw_badge(canvas, cx, cy)

    # Marcas de agua: izquierda y derecha abajo
    canvas = _draw_watermark(canvas)

    # Guardar como JPEG
    out_path = tempfile.mktemp(suffix=".jpg")
    canvas.convert("RGB").save(out_path, "JPEG", quality=92)
    print("Imagen lista: " + str(os.path.getsize(out_path) // 1024) + "KB", flush=True)
    return out_path


def generate_image(product_name, image_url=None):
    """Punto de entrada — devuelve ('image', ruta) o (None, None)."""
    if not image_url:
        return None, None
    print("Generando imagen: " + product_name[:60], flush=True)
    path = create_marketing_image(product_name, image_url)
    if path:
        return "image", path
    return None, None
