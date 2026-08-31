#!/usr/bin/env python3
"""Generate the Open Graph image and favicons.

Requires Pillow:  pip install Pillow
Run from the repo root:  python _build/gen_images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
IMG.mkdir(parents=True, exist_ok=True)

FONTS = Path("C:/Windows/Fonts")

# Brand palette (matches --paper / --ink / --teal / --clay / --ink-soft in CSS)
PAPER = (251, 250, 247)
MIST = (242, 239, 232)
INK = (22, 33, 28)
INK_SOFT = (71, 83, 76)
TEAL = (14, 107, 92)
CLAY = (180, 83, 42)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


# --------------------------------------------------------------------------
# Open Graph image — 1200x630
# --------------------------------------------------------------------------

def og_image():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # Warm wash in the top-right corner
    wash = Image.new("RGB", (W, H), MIST)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([W - 620, -330, W + 260, 470], fill=70)
    img.paste(wash, (0, 0), mask)

    # Concentric arcs bottom-right — a loose "lost / searching" motif
    for i, (radius, width, alpha) in enumerate([(210, 26, 26), (280, 26, 18), (350, 26, 11)]):
        box = [W - 130 - radius * 2, H - 60 - radius * 2, W - 130, H - 60]
        d.arc(box, start=180, end=320, fill=TEAL + (alpha,), width=width)

    # Thin rule between headline and sub-headline
    d.rectangle([96, 348, 96 + 60, 351], fill=CLAY)

    # Headline
    f_h1 = font("georgia.ttf", 78)
    f_h1b = font("georgiab.ttf", 78)
    d.text((96, 150), "Confused about", font=f_h1, fill=INK)
    d.text((96, 238), "life?", font=f_h1b, fill=TEAL)

    # Sub-headline
    f_sub = font("segoeui.ttf", 33)
    d.text((96, 380), "Practical clarity for when life stops", font=f_sub, fill=INK_SOFT)
    d.text((96, 424), "making sense. No pep talks.", font=f_sub, fill=INK_SOFT)

    # Brand mark + wordmark
    d.ellipse([98, 530, 122, 554], fill=CLAY)
    d.text((136, 526), "confusedlife.online", font=font("segoeuib.ttf", 28), fill=INK)

    img.save(IMG / "og-default.png", "PNG", optimize=True)
    print("  wrote assets/img/og-default.png (1200x630)")


# --------------------------------------------------------------------------
# Favicons
# --------------------------------------------------------------------------

def favicon_png(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded-square teal field
    r = int(size * 0.22)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=TEAL + (255,))

    # Off-centre clay dot — the "lost" mark
    cx, cy = size * 0.5, size * 0.5
    dot = max(2, int(size * 0.17))
    d.ellipse([cx - dot - size * 0.055, cy - dot, cx + dot - size * 0.055, cy + dot],
              fill=CLAY + (255,))

    # Faint arc suggesting a path not yet taken
    if size >= 48:
        d.arc([size * 0.18, size * 0.18, size * 0.82, size * 0.82],
              start=195, end=345, fill=(255, 255, 255, 90), width=max(1, int(size * 0.045)))

    return img


def favicons():
    favicon_png(180).save(IMG / "apple-touch-icon.png", "PNG", optimize=True)
    favicon_png(32).save(IMG / "favicon.png", "PNG", optimize=True)
    print("  wrote assets/img/favicon.png + apple-touch-icon.png")


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="ConfusedLife">
  <rect width="64" height="64" rx="14" fill="#0E6B5C"/>
  <path d="M10 44a22 22 0 0 1 44 0" fill="none" stroke="#FFFFFF" stroke-opacity=".22" stroke-width="4" stroke-linecap="round"/>
  <circle cx="26" cy="32" r="11" fill="#B4532A"/>
</svg>
"""


def favicon_svg():
    (IMG / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    print("  wrote assets/img/favicon.svg")


if __name__ == "__main__":
    og_image()
    favicons()
    favicon_svg()
