import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, abort

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("LABEL_PRINTER_DATA_DIR", ".")
IMAGE = os.path.join(DATA_DIR, "serial_qr.png")

app = Flask(__name__)


def _print_image():
    subprocess.run(
        ["brother_ql", "print", "-l", "62", "--600dpi", IMAGE],
        check=False,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/printlabel", methods=["GET", "POST"])
def print_label():
    subprocess.run(["python3", os.path.join(APP_DIR, "generator.py")], check=False)
    _print_image()
    return redirect(url_for("index", message="Label gedruckt"))


@app.route("/printlabelWithDate", methods=["GET", "POST"])
def print_label_with_date():
    subprocess.run(["python3", os.path.join(APP_DIR, "generator_with_date.py")], check=False)
    _print_image()
    return redirect(url_for("index", message="Label gedruckt"))


@app.route("/printlabelHistory", methods=["GET", "POST"])
def print_label_history():
    _print_image()
    return redirect(url_for("index", message="Label gedruckt"))


@app.route("/printlabelAsset", methods=["GET", "POST"])
def print_label_asset():
    asset_id = request.args.get("id")
    if not asset_id or asset_id == "0":
        abort(500, description="(id) query parameter must be provided and non-zero")

    subprocess.run(
        ["python3", os.path.join(APP_DIR, "generator_asset.py"), str(int(asset_id))],
        check=False,
    )
    _print_image()
    return redirect(url_for("index", message="Label gedruckt"))


if __name__ == "__main__":
    host = os.environ.get("LABEL_PRINTER_HOST", "0.0.0.0")
    port = int(os.environ.get("LABEL_PRINTER_PORT", "3333"))
    app.run(host=host, port=port)
