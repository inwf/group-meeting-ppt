import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CN_FONTS = [
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/truetype/arphic/uming.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/System/Library/Fonts/Supplemental/Songti.ttc',
    'C:/Windows/Fonts/msyh.ttc',
]
EN_FONTS = [
    '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',
    'C:/Windows/Fonts/timesbd.ttf',
]

INK = (26, 58, 102)
WHITE = (255, 255, 255)
PALE = (235, 243, 252)
NAVY_TOP = (1, 65, 129)
NAVY_BOTTOM = (46, 127, 208)

EMBLEM_BOX = (60, 26, 116, 86)
SCHOOL_CN_BOX = (129, 27, 278, 60)
SCHOOL_EN_BOX = (129, 60, 278, 77)
DIVIDER = (282, 35, 284, 73)
LAB_CN_BOX = (293, 34, 588, 57)
LAB_EN_BOX = (293, 64, 588, 78)


def pick_font(candidates):
    from pathlib import Path
    for path in candidates:
        if Path(path).exists():
            return path
    raise FileNotFoundError(f'找不到可用字体，尝试过 {candidates}')


def cn_font(size):
    return ImageFont.truetype(pick_font(CN_FONTS), size)


def en_font(size):
    return ImageFont.truetype(pick_font(EN_FONTS), size)


def draw_emblem(canvas, scale):
    x0, y0, x1, y1 = [v * scale for v in EMBLEM_BOX]
    d = ImageDraw.Draw(canvas)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(x1 - x0, y1 - y0) / 2 - scale
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=int(2.4 * scale))
    r2 = r * 0.78
    d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=INK,
              width=int(1.1 * scale))
    book = r * 0.52
    d.polygon([(cx - book, cy - book * 0.15), (cx, cy - book * 0.55),
               (cx + book, cy - book * 0.15), (cx + book, cy + book * 0.42),
               (cx, cy + book * 0.05), (cx - book, cy + book * 0.42)],
              outline=INK, width=int(1.6 * scale))
    d.line((cx, cy - book * 0.55, cx, cy + book * 0.05), fill=INK,
           width=int(1.2 * scale))


def centered(canvas, box, text, fnt, fill, scale):
    x0, y0, x1, y1 = [v * scale for v in box]
    d = ImageDraw.Draw(canvas)
    left, top, right, bottom = d.textbbox((0, 0), text, font=fnt)
    x = (x0 + x1) / 2 - (right - left) / 2 - left
    y = (y0 + y1) / 2 - (bottom - top) / 2 - top
    d.text((x, y), text, font=fnt, fill=fill)


def header_png(school_cn, school_en, lab_cn, lab_en, size=(960, 720), scale=6):
    w, h = size
    band = 90
    canvas = Image.new('RGB', (w * scale, h * scale), WHITE)
    d = ImageDraw.Draw(canvas)
    stripe_rows = [(2, 7), (21, 26), (38, 45), (59, 64), (77, 83)]
    for y0, y1 in stripe_rows:
        d.rectangle((0, y0 * scale, 40 * scale, (y1 + 1) * scale), fill=NAVY_TOP)
    d.rectangle((592 * scale, 0, w * scale, 75 * scale), fill=NAVY_TOP)
    d.rectangle((592 * scale, 75 * scale, w * scale, 86 * scale),
                fill=(196, 196, 196))
    draw_emblem(canvas, scale)
    centered(canvas, SCHOOL_CN_BOX, school_cn, cn_font(30 * scale), INK, scale)
    centered(canvas, SCHOOL_EN_BOX, school_en, en_font(15 * scale), INK, scale)
    x0, y0, x1, y1 = [v * scale for v in DIVIDER]
    d.rectangle((x0, y0, x1, y1), fill=(150, 165, 185))
    centered(canvas, LAB_CN_BOX, lab_cn, cn_font(21 * scale), INK, scale)
    centered(canvas, LAB_EN_BOX, lab_en, en_font(11 * scale), INK, scale)
    d.rectangle((0, band * scale, w * scale, h * scale), fill=WHITE)
    out = canvas.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, format='PNG')
    return buf.getvalue()


def gradient(width, height):
    top = np.array(NAVY_TOP, dtype=float)
    bottom = np.array(NAVY_BOTTOM, dtype=float)
    ramp = np.linspace(0.0, 1.0, height)[:, None]
    rows = top[None, :] * (1 - ramp) + bottom[None, :] * ramp
    return np.clip(np.repeat(rows[:, None, :], width, axis=1), 0, 255).astype(np.uint8)


def cover_jpeg(school_cn, lab_cn, lab_en, size=(1000, 184), scale=3):
    w, h = size
    canvas = Image.fromarray(gradient(w * scale, h * scale))
    d = ImageDraw.Draw(canvas)
    d.ellipse([(36 * scale, 22 * scale), (168 * scale, 154 * scale)],
              outline=WHITE, width=int(2.5 * scale))
    d.ellipse([(50 * scale, 36 * scale), (154 * scale, 140 * scale)],
              outline=WHITE, width=int(1.2 * scale))
    centered(canvas, (30, 34, 174, 142), school_cn, cn_font(30 * scale), WHITE, scale)
    centered(canvas, (200, 40, 960, 88), lab_cn, cn_font(40 * scale), WHITE, scale)
    centered(canvas, (200, 96, 960, 140), lab_en, en_font(26 * scale), PALE, scale)
    out = canvas.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, format='JPEG', quality=92)
    return buf.getvalue()


def thumb_jpeg(width, height, strip_ratio=0.23):
    strip = int(height * strip_ratio)
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)
    canvas[:strip] = gradient(width, strip)
    buf = io.BytesIO()
    Image.fromarray(canvas).save(buf, format='JPEG', quality=90)
    return buf.getvalue()
