"""Render a Contiva guest-WLAN password label as 62mm endless / 600 dpi.

Intended to be called from app.py as a short-lived subprocess, same pattern
as generator.py and generator_with_date.py. The PIL image is written to the
shared OUTPUT_FILE that `brother_ql print` consumes.
"""

import argparse
import os

from PIL import Image, ImageDraw, ImageFont

DATA_DIR = os.environ.get("LABEL_PRINTER_DATA_DIR", ".")
OUTPUT_FILE = os.path.join(DATA_DIR, "serial_qr.png")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Brother QL 62mm endless at 600dpi — print-area width in pixels.
LABEL_WIDTH_PX = 696


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except IOError:
        return ImageFont.load_default()


def _fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int,
              sizes: list[int]) -> ImageFont.ImageFont:
    """Return the largest font from `sizes` whose rendered `text` still fits
    within `max_width`. Falls back to the smallest if none fit."""
    for size in sizes:
        font = _load_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
    return _load_font(sizes[-1])


def generate(pw: str, ssid: str, valid_until: str) -> None:
    # Build once at a large canvas, measure, then redraw at exact height.
    # Simpler: compute heights from font metrics up front.
    tmp = Image.new("RGB", (LABEL_WIDTH_PX, 10), "white")
    d = ImageDraw.Draw(tmp)

    font_header = _load_font(32)
    font_pw = _fit_font(d, pw, LABEL_WIDTH_PX - 40, [72, 64, 56, 48, 40, 32])
    font_meta = _load_font(26)

    line_gap = 10
    header_h = font_header.size
    pw_h = font_pw.size
    meta_h = font_meta.size
    pad = 18
    total_h = pad + header_h + line_gap + pw_h + line_gap + meta_h
    if valid_until:
        total_h += line_gap + meta_h
    total_h += pad

    img = Image.new("RGB", (LABEL_WIDTH_PX, total_h), "white")
    draw = ImageDraw.Draw(img)

    def centre(text: str, y: int, font: ImageFont.ImageFont) -> None:
        w = draw.textlength(text, font=font)
        draw.text(((LABEL_WIDTH_PX - w) / 2, y), text, fill="black", font=font)

    y = pad
    centre("Contiva Gäste-WLAN", y, font_header)
    y += header_h + line_gap

    centre(pw, y, font_pw)
    y += pw_h + line_gap

    centre(f"SSID: {ssid}", y, font_meta)
    y += meta_h

    if valid_until:
        y += line_gap
        centre(f"Gültig bis: {valid_until}", y, font_meta)

    img.save(OUTPUT_FILE, dpi=(600, 600))
    print(
        f"WLAN label rendered: pw={pw!r} ssid={ssid!r} valid_until={valid_until!r} "
        f"({LABEL_WIDTH_PX}×{total_h}px)"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate a Contiva guest-WLAN password label.")
    p.add_argument("--pw", required=True, help="Weekly password to print")
    p.add_argument("--ssid", default="Contiva Guest", help="SSID shown on the label")
    p.add_argument("--valid-until", default="",
                   help="Optional validity string, e.g. '28.04.2026, 00:00 Uhr'")
    args = p.parse_args()
    generate(args.pw, args.ssid, args.valid_until)
