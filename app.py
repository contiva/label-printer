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


@app.route("/printwlan", methods=["POST"])
def print_wlan_password():
    # POST-only so the password doesn't end up in access logs / browser
    # history as a query string. Accepted as form data OR JSON body.
    data = request.get_json(silent=True) or request.form
    pw = (data.get("pw") or "").strip()
    ssid = (data.get("ssid") or "Contiva Guest").strip()
    valid_until = (data.get("valid_until") or "").strip()

    if not pw:
        abort(400, description="(pw) body field is required")

    cmd = [
        "python3",
        os.path.join(APP_DIR, "generator_wlan.py"),
        "--pw", pw,
        "--ssid", ssid,
    ]
    if valid_until:
        cmd.extend(["--valid-until", valid_until])
    subprocess.run(cmd, check=False)
    _print_image()
    # Browser clients (the test form below) get redirected back to the index;
    # API clients should look at the HTTP status. 302 is fine for both.
    return redirect(url_for("index", message="WLAN-Passwort gedruckt"))


if __name__ == "__main__":
    host = os.environ.get("LABEL_PRINTER_HOST", "0.0.0.0")
    port = int(os.environ.get("LABEL_PRINTER_PORT", "3333"))
    app.run(host=host, port=port)
