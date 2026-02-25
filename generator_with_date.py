import datetime as dt
import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

from paperless_api import get_next_asn

SERIAL_FILE = "serial_number.txt"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def generate_image_with_optimal_size():
    api_asn = get_next_asn()
    if api_asn is not None:
        serial_number = api_asn
    elif os.path.exists(SERIAL_FILE):
        with open(SERIAL_FILE, "r") as file:
            serial_number = int(file.read().strip())
    else:
        serial_number = 1

    serial_str = f"ASN{serial_number:05}"
    today = dt.date.today()
    date_str = f"EINGANG: {today.day:02d}.{today.month:02d}.{today.year}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=1,
    )
    qr.add_data(serial_str)
    qr.make(fit=True)
    img_qr = qr.make_image(fill="black", back_color="white").convert("RGB")
    img_qr.thumbnail((200, 200), Image.Resampling.LANCZOS)

    font_size = 60
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except IOError:
        font = ImageFont.load_default()

    font_size_date = 29
    try:
        font_date = ImageFont.truetype(FONT_PATH, font_size_date)
    except IOError:
        font_date = ImageFont.load_default()

    total_width = 696
    total_height = max(img_qr.height, font.size)
    img = Image.new("RGB", (total_width, total_height), "white")
    img.paste(img_qr, (0, (total_height - img_qr.height) // 2))

    draw = ImageDraw.Draw(img)
    text_x = img_qr.width + 100
    text_y = (total_height - 40 - font.size) // 2
    draw.text((text_x, text_y), serial_str, fill="black", font=font)

    date_x = text_x
    date_y = text_y + font.size + 10
    draw.text((date_x, date_y), date_str, fill="black", font=font_date)

    img.save("serial_qr.png", dpi=(600, 600))

    with open(SERIAL_FILE, "w") as file:
        file.write(str(serial_number + 1))

    print(f"Image created: {serial_str}, {date_str}, width: {total_width}px, QR size: {img_qr.size}")


generate_image_with_optimal_size()
