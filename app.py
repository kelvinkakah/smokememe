"""
SmokeMeme – Crypto Meme & Quote Generator
Flask + Pillow meme generator, Vercel-compatible
"""

import os
import io
import base64
import random
import textwrap
from pathlib import Path

from flask import (
    Flask, render_template, request, send_file,
    jsonify, session
)
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smokememe-dev-key-change-in-prod")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
TEMPLATE_FOLDER = Path(__file__).parent / "static" / "images" / "templates"

# ── Crypto Quotes ─────────────────────────────────────────────────────────────
CRYPTO_QUOTES = [
    ("NGMI if you sold the bottom.", "Anonymous Degen"),
    ("We're all gonna make it. WAGMI.", "Crypto Twitter"),
    ("Number go up. Touch grass later.", "Diamond Hans"),
    ("This is financial advice: DYOR.", "Not A Financial Advisor"),
    ("Wen moon? When you sell.", "The Market"),
    ("Buy the dip. Every. Single. Dip.", "Every Bull Market"),
    ("I'm not selling. I'm just accumulating losses.", "Paper Hans"),
    ("My portfolio is a performance art piece.", "Rugged Artist"),
    ("Not your keys, not your coins.", "Satoshi's Ghost"),
    ("I told my family we'd retire. I didn't say when.", "Long Term Holder"),
    ("The real alpha was the friends we rekt along the way.", "Discord Mod"),
    ("1 BTC = 1 BTC. Cope.", "Bitcoin Maxi"),
    ("If your bags are heavy, your future is bright.", "Optimistic Degen"),
    ("I didn't lose money. I made a generous donation to whales.", "Hopeful Retail"),
    ("Blockchain technology will revolutionize... eventually.", "VC Partner"),
    ("I'm not addicted. I can stop checking the charts any time.", "Chartoholic"),
    ("Patience is the rarest altcoin.", "Zen Degen"),
    ("The best time to buy was yesterday. Second best? Also yesterday.", "Time Traveler"),
    ("Volatility is just opportunity wearing a scary costume.", "Risk Manager"),
    ("We don't need sleep. We need green candles.", "Insomniac Trader"),
    ("My investment strategy: vibes.", "Strategy Consultant"),
    ("Diversification: holding 47 memecoins.", "Portfolio Manager"),
    ("Diamond hands forged in bear markets.", "OG Hodler"),
    ("The metaverse will be ready right after soon.", "Roadmap Reader"),
]

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {"id": "pepe",    "name": "Feels Good Pepe",  "emoji": "🐸", "file": "pepe.png",    "description": "The OG crypto frog."},
    {"id": "rocket",  "name": "To The Moon",       "emoji": "🚀", "file": "rocket.png",  "description": "When your bags finally pump."},
    {"id": "diamond", "name": "Diamond Hands",     "emoji": "💎", "file": "diamond.png", "description": "Paper hands need not apply."},
    {"id": "laser",   "name": "Laser Eyes",        "emoji": "👀", "file": "laser.png",   "description": "100k incoming."},
    {"id": "ape",     "name": "Ape In",            "emoji": "🦍", "file": "ape.png",     "description": "Apes together strong."},
    {"id": "moon",    "name": "Moon Math",         "emoji": "🌙", "file": "moon.png",    "description": "Zoom out. Always bullish."},
]

TEMPLATE_COLORS = {
    "pepe":    ("#0d2b0d", "#1a4a1a"),
    "rocket":  ("#050520", "#0a0a3e"),
    "diamond": ("#050a14", "#0a1a28"),
    "laser":   ("#140005", "#28000a"),
    "ape":     ("#140a00", "#28140a"),
    "moon":    ("#050510", "#0a0a1e"),
}

# ── Font helper ───────────────────────────────────────────────────────────────
def get_font(size: int):
    """Get best available font at given size."""
    candidates = [
        str(Path(__file__).parent / "static" / "fonts" / "bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Pillow 10+ supports size on default font
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

# ── Helpers ───────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_text_size(font, text):
    """Get text width and height safely across Pillow versions."""
    try:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        try:
            return font.getsize(text)
        except Exception:
            return len(text) * 20, 30

def draw_meme_text(draw, img_w, img_h, text, position, font_size, color, outline):
    if not text:
        return
    font = get_font(font_size)
    margin = 20
    max_chars = max(10, int(img_w / (font_size * 0.55)))
    lines = textwrap.wrap(text.upper(), width=max_chars)

    _, line_h = get_text_size(font, "A")
    line_h = line_h + 10
    total_h = line_h * len(lines)

    y_start = margin if position == "top" else img_h - total_h - margin

    for i, line in enumerate(lines):
        text_w, _ = get_text_size(font, line)
        x = (img_w - text_w) // 2
        y = y_start + i * line_h

        if outline:
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))

        draw.text((x, y), line, font=font, fill=color)

def create_placeholder(emoji, color1, color2, size=(600, 600)):
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    for y in range(size[1]):
        t = y / size[1]
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    # Grid lines for style
    for x in range(0, size[0], 60):
        draw.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 15), width=1)
    for y in range(0, size[1], 60):
        draw.line([(0, y), (size[0], y)], fill=(255, 255, 255, 15), width=1)
    # Center text
    font = get_font(100)
    text_w, text_h = get_text_size(font, emoji)
    x = (size[0] - text_w) // 2
    y = (size[1] - text_h) // 2
    draw.text((x, y), emoji, font=font, fill=(255, 255, 255))
    return img

def get_template_image(template_id):
    t = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not t:
        return create_placeholder("❓", "#111111", "#333333")
    path = TEMPLATE_FOLDER / t["file"]
    if path.exists():
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            pass
    colors = TEMPLATE_COLORS.get(template_id, ("#111111", "#333333"))
    return create_placeholder(t["emoji"], *colors)

def generate_meme(image_source, top_text, bottom_text, font_size, text_color_hex, outline):
    if isinstance(image_source, str):
        img = Image.open(image_source).convert("RGBA")
    else:
        img = image_source.convert("RGBA")
    # Cap size
    if max(img.size) > 1000:
        img.thumbnail((1000, 1000), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    color = hex_to_rgb(text_color_hex)
    draw_meme_text(draw, img.width, img.height, top_text, "top", font_size, color, outline)
    draw_meme_text(draw, img.width, img.height, bottom_text, "bottom", font_size, color, outline)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    quote, author = random.choice(CRYPTO_QUOTES)
    return render_template("index.html", quote=quote, author=author, templates=TEMPLATES)

@app.route("/generator")
def generator():
    template_id = request.args.get("template", "")
    return render_template("generator.html", templates=TEMPLATES, selected_template=template_id)

@app.route("/quotes")
def quotes():
    shuffled = random.sample(CRYPTO_QUOTES, len(CRYPTO_QUOTES))
    return render_template("quotes.html", quotes=shuffled)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", memes=session.get("gallery", []))

@app.route("/api/generate", methods=["POST"])
def api_generate():
    top_text    = request.form.get("top_text", "").strip()
    bottom_text = request.form.get("bottom_text", "").strip()
    font_size   = min(max(int(request.form.get("font_size", 48)), 16), 120)
    text_color  = request.form.get("text_color", "#39ff14")
    outline     = request.form.get("outline", "true").lower() == "true"
    template_id = request.form.get("template_id", "")
    file        = request.files.get("image")

    try:
        if file and file.filename and allowed_file(file.filename):
            img = Image.open(io.BytesIO(file.read()))
        elif template_id:
            img = get_template_image(template_id)
        else:
            img = create_placeholder("🔥", "#0a0a0a", "#1a1a2e")

        buf  = generate_meme(img, top_text, bottom_text, font_size, text_color, outline)
        b64  = base64.b64encode(buf.read()).decode("utf-8")

        gallery = session.get("gallery", [])
        gallery.insert(0, {"data": b64, "top": top_text, "bottom": bottom_text})
        session["gallery"] = gallery[:12]

        return jsonify({"success": True, "image": b64})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json(silent=True) or {}
    b64  = data.get("image", "")
    if not b64:
        return "No image data", 400
    try:
        buf = io.BytesIO(base64.b64decode(b64))
        buf.seek(0)
        return send_file(buf, mimetype="image/png", as_attachment=True, download_name="smokememe.png")
    except Exception as e:
        return str(e), 400

@app.route("/api/random-quote")
def api_random_quote():
    quote, author = random.choice(CRYPTO_QUOTES)
    return jsonify({"quote": quote, "author": author})

@app.route("/api/template-preview/<template_id>")
def api_template_preview(template_id):
    img = get_template_image(template_id)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify({"success": False, "error": "File too large (max 10 MB)"}), 413

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
