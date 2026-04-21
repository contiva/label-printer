import os
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = os.environ.get("LABEL_PRINTER_DATA_DIR", ".")
OUTPUT_FILE = os.path.join(DATA_DIR, "serial_qr.png")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def generate_image_with_optimal_size(asset_id):
    serial_str = f"#{asset_id:06}"
    qr_str = f"{asset_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=1,
    )
    qr.add_data(qr_str)
    qr.make(fit=True)
    img_qr = qr.make_image(fill="black", back_color="white").convert("RGB")
    img_qr.thumbnail((200, 200), Image.Resampling.LANCZOS)

    font_size = 60
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except IOError:
        font = ImageFont.load_default()

    total_width = 696
    total_height = max(img_qr.height, font.size)
    img = Image.new("RGB", (total_width, total_height), "white")
    img.paste(img_qr, (0, (total_height - img_qr.height) // 2))

    draw = ImageDraw.Draw(img)
    text_x = img_qr.width + 100
    text_y = (total_height - font.size) // 2
    draw.text((text_x, text_y), serial_str, fill="black", font=font)

    img.save(OUTPUT_FILE, dpi=(600, 600))
    print(f"Image created with AssetID: {serial_str}, width: {total_width}px, QR size: {img_qr.size}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generator_asset.py <AssetID>")
        sys.exit(1)

    try:
        asset_id = int(sys.argv[1])
        generate_image_with_optimal_size(asset_id)
    except ValueError:
        print("AssetID must be an integer.")
        sys.exit(1)
