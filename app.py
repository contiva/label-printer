import os
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/printlabel", methods=["GET", "POST"])
def print_label():
    os.system("python3 generator.py")
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
    os.system("brother_ql print -l 62 --600dpi serial_qr.png")
    return redirect(url_for("index", message="Label gedruckt"))


@app.route("/printlabelWithDate", methods=["GET", "POST"])
def print_label_with_date():
    os.system("python3 generator_with_date.py")
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
    os.system("brother_ql print -l 62 --600dpi serial_qr.png")
    return redirect(url_for("index", message="Label gedruckt"))


@app.route("/printlabelHistory", methods=["GET", "POST"])
def print_label_history():
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
    os.system("brother_ql print -l 62 --600dpi serial_qr.png")
    return redirect(url_for("index", message="Label gedruckt"))


@app.route("/printlabelAsset", methods=["GET", "POST"])
def print_label_asset():
    asset_id = request.args.get("id")
    if not asset_id or asset_id == "0":
        abort(500, description="(id) query parameter must be provided and non-zero")

    os.system(f"python3 generator_asset.py {int(asset_id)}")
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
    os.system("brother_ql print -l 62 --600dpi serial_qr.png")
    return redirect(url_for("index", message="Label gedruckt"))


if __name__ == "__main__":
    host = os.environ.get("LABEL_PRINTER_HOST", "0.0.0.0")
    port = int(os.environ.get("LABEL_PRINTER_PORT", "3333"))
    app.run(host=host, port=port)
