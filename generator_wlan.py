"""Render a Contiva guest-WLAN password label as 62mm endless / 600 dpi.

Intended to be called from app.py as a short-lived subprocess, same pattern
as generator.py and generator_with_date.py. The PIL image is written to the
shared OUTPUT_FILE that `brother_ql print` consumes.
"""

import argparse
import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = os.environ.get("LABEL_PRINTER_DATA_DIR", ".")
OUTPUT_FILE = os.path.join(DATA_DIR, "serial_qr.png")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Brother QL 62mm endless at 600dpi — print-area width in pixels.
LABEL_WIDTH_PX = 696


def _load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    path = FONT_PATH if bold else FONT_PATH_REGULAR
    try:
        return ImageFont.truetype(path, size)
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


def _wifi_qr(ssid: str, box_size: int = 8) -> Image.Image:
    # Open network (no password): WIFI:T:nopass;S:<ssid>;;
    # The portal's captive-portal page handles auth after the client joins.
    payload = f"WIFI:T:nopass;S:{ssid};;"
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def generate(pw: str, ssid: str, valid_until: str) -> None:
    tmp = Image.new("RGB", (LABEL_WIDTH_PX, 10), "white")
    d = ImageDraw.Draw(tmp)

    font_header = _load_font(28)
    font_pw_label = _load_font(28)
    # Leave extra margin so the box padding doesn't push the password into the edge.
    font_pw = _fit_font(d, pw, LABEL_WIDTH_PX - 120, [72, 64, 56, 48, 40, 32])
    font_meta = _load_font(26)
    font_step_num = _load_font(24)
    font_step_text = _load_font(24, bold=False)
    font_caption = _load_font(22, bold=False)

    steps = [
        ("1.", f'WLAN "{ssid}" wählen'),
        ("2.", "AGB akzeptieren"),
        ("3.", "Passwort oben eingeben"),
    ]
    session_hint = "Anmeldung gilt bis Tagesende (00:00 Uhr)."

    qr_img = _wifi_qr(ssid, box_size=8)
    qr_w, qr_h = qr_img.size

    pad = 18
    line_gap = 10
    section_gap = 22
    sep_gap = 14

    header_h = font_header.size
    pw_label_h = font_pw_label.size
    pw_h = font_pw.size
    meta_h = font_meta.size
    step_h = max(font_step_num.size, font_step_text.size)
    caption_h = font_caption.size

    pw_box_pad_v = 16
    pw_box_h = pw_h + 2 * pw_box_pad_v

    total_h = pad + header_h + section_gap
    total_h += pw_label_h + 6 + pw_box_h + line_gap + meta_h
    if valid_until:
        total_h += line_gap + meta_h
    total_h += section_gap + sep_gap
    total_h += caption_h + line_gap
    total_h += len(steps) * (step_h + line_gap)
    total_h += section_gap + qr_h + line_gap + caption_h
    total_h += section_gap + caption_h + pad

    img = Image.new("RGB", (LABEL_WIDTH_PX, total_h), "white")
    draw = ImageDraw.Draw(img)

    def centre(text: str, y: int, font: ImageFont.ImageFont) -> None:
        w = draw.textlength(text, font=font)
        draw.text(((LABEL_WIDTH_PX - w) / 2, y), text, fill="black", font=font)

    y = pad
    centre("Contiva Gäste-WLAN", y, font_header)
    y += header_h + section_gap

    centre("Passwort dieser Woche:", y, font_pw_label)
    y += pw_label_h + 6

    box_x0, box_x1 = pad * 2, LABEL_WIDTH_PX - pad * 2
    draw.rectangle([(box_x0, y), (box_x1, y + pw_box_h)], outline="black", width=4)
    centre(pw, y + pw_box_pad_v, font_pw)
    y += pw_box_h + line_gap

    centre(f"SSID: {ssid}", y, font_meta)
    y += meta_h

    if valid_until:
        y += line_gap
        centre(f"Passwort gültig bis: {valid_until}", y, font_meta)
        y += meta_h

    y += section_gap
    draw.line([(pad * 2, y), (LABEL_WIDTH_PX - pad * 2, y)], fill="black", width=2)
    y += sep_gap

    centre("So verbindest du dich:", y, font_caption)
    y += caption_h + line_gap

    step_left = 60
    text_left = step_left + 42
    for num, text in steps:
        draw.text((step_left, y), num, fill="black", font=font_step_num)
        draw.text((text_left, y), text, fill="black", font=font_step_text)
        y += step_h + line_gap

    y += section_gap
    qr_x = (LABEL_WIDTH_PX - qr_w) // 2
    img.paste(qr_img, (qr_x, y))
    y += qr_h + line_gap
    centre("QR scannen = direkt verbinden", y, font_caption)
    y += caption_h

    y += section_gap
    centre(session_hint, y, font_caption)

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
