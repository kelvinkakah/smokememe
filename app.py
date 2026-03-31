import os, io, base64, random, textwrap
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, session
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smokememe-dev-key")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
TEMPLATE_FOLDER = Path(__file__).parent / "static" / "images" / "templates"

CRYPTO_QUOTES = [
    ("NGMI if you sold the bottom.", "Anonymous Degen"),
    ("We are all gonna make it. WAGMI.", "Crypto Twitter"),
    ("Number go up. Touch grass later.", "Diamond Hans"),
    ("This is financial advice: DYOR.", "Not A Financial Advisor"),
    ("Wen moon? When you sell.", "The Market"),
    ("Buy the dip. Every. Single. Dip.", "Every Bull Market"),
    ("Not your keys, not your coins.", "Satoshi's Ghost"),
    ("I told my family we would retire. I did not say when.", "Long Term Holder"),
    ("1 BTC = 1 BTC. Cope.", "Bitcoin Maxi"),
    ("Patience is the rarest altcoin.", "Zen Degen"),
    ("Volatility is just opportunity in disguise.", "Risk Manager"),
    ("We do not need sleep. We need green candles.", "Insomniac Trader"),
    ("My investment strategy: vibes.", "Strategy Consultant"),
    ("Diamond hands forged in bear markets.", "OG Hodler"),
]

TEMPLATES = [
    {"id": "pepe",    "name": "Feels Good Pepe",  "emoji": "frog",    "file": "pepe.png",    "description": "The OG crypto frog."},
    {"id": "rocket",  "name": "To The Moon",       "emoji": "rocket",  "file": "rocket.png",  "description": "When your bags finally pump."},
    {"id": "diamond", "name": "Diamond Hands",     "emoji": "diamond", "file": "diamond.png", "description": "Paper hands need not apply."},
    {"id": "laser",   "name": "Laser Eyes",        "emoji": "eyes",    "file": "laser.png",   "description": "100k incoming."},
    {"id": "ape",     "name": "Ape In",            "emoji": "ape",     "file": "ape.png",     "description": "Apes together strong."},
    {"id": "moon",    "name": "Moon Math",         "emoji": "moon",    "file": "moon.png",    "description": "Zoom out. Always bullish."},
]

TEMPLATE_COLORS = {
    "pepe": ("#0d2b0d","#1a4a1a"), "rocket": ("#050520","#0a0a3e"),
    "diamond": ("#050a14","#0a1a28"), "laser": ("#140005","#28000a"),
    "ape": ("#140a00","#28140a"), "moon": ("#050510","#0a0a1e"),
}

def get_font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def allowed_file(f):
    return "." in f and f.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def get_text_size(font, text):
    try:
        b = font.getbbox(text)
        return b[2]-b[0], b[3]-b[1]
    except Exception:
        return len(text)*12, 20

def draw_meme_text(draw, iw, ih, text, pos, fsize, color, outline):
    if not text: return
    font = get_font(fsize)
    margin = 20
    max_chars = max(10, int(iw/(fsize*0.6)))
    lines = textwrap.wrap(text.upper(), width=max_chars)
    _, lh = get_text_size(font, "A")
    lh += 8
    total_h = lh * len(lines)
    y0 = margin if pos == "top" else ih - total_h - margin
    for i, line in enumerate(lines):
        tw, _ = get_text_size(font, line)
        x = (iw - tw) // 2
        y = y0 + i * lh
        if outline:
            for dx in range(-2,3):
                for dy in range(-2,3):
                    if dx or dy:
                        draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0))
        draw.text((x, y), line, font=font, fill=color)

def create_placeholder(label, c1, c2, size=(600,600)):
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    r1,g1,b1 = hex_to_rgb(c1)
    r2,g2,b2 = hex_to_rgb(c2)
    for y in range(size[1]):
        t = y/size[1]
        draw.line([(0,y),(size[0],y)], fill=(int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t)))
    for x in range(0,size[0],60):
        draw.line([(x,0),(x,size[1])], fill=(40,40,40))
    for y in range(0,size[1],60):
        draw.line([(0,y),(size[0],y)], fill=(40,40,40))
    font = get_font(60)
    tw, th = get_text_size(font, label.upper())
    draw.text(((size[0]-tw)//2, (size[1]-th)//2), label.upper(), font=font, fill=(255,255,255))
    return img

def get_template_image(tid):
    t = next((t for t in TEMPLATES if t["id"]==tid), None)
    if not t: return create_placeholder("???", "#111","#333")
    path = TEMPLATE_FOLDER / t["file"]
    if path.exists():
        try: return Image.open(path).convert("RGBA")
        except Exception: pass
    return create_placeholder(t["name"], *TEMPLATE_COLORS.get(tid, ("#111","#333")))

def generate_meme(src, top, bottom, fsize, color_hex, outline):
    img = (Image.open(src) if isinstance(src,str) else src).convert("RGBA")
    if max(img.size) > 1000: img.thumbnail((1000,1000), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    color = hex_to_rgb(color_hex)
    draw_meme_text(draw, img.width, img.height, top, "top", fsize, color, outline)
    draw_meme_text(draw, img.width, img.height, bottom, "bottom", fsize, color, outline)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return buf

@app.route("/")
def index():
    q, a = random.choice(CRYPTO_QUOTES)
    return render_template("index.html", quote=q, author=a, templates=TEMPLATES)

@app.route("/generator")
def generator():
    return render_template("generator.html", templates=TEMPLATES, selected_template=request.args.get("template",""))

@app.route("/quotes")
def quotes():
    return render_template("quotes.html", quotes=random.sample(CRYPTO_QUOTES, len(CRYPTO_QUOTES)))

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", memes=session.get("gallery",[]))

@app.route("/api/generate", methods=["POST"])
def api_generate():
    top = request.form.get("top_text","").strip()
    bottom = request.form.get("bottom_text","").strip()
    fsize = min(max(int(request.form.get("font_size",48)),16),120)
    color = request.form.get("text_color","#39ff14")
    outline = request.form.get("outline","true").lower()=="true"
    tid = request.form.get("template_id","")
    file = request.files.get("image")
    try:
        if file and file.filename and allowed_file(file.filename):
            img = Image.open(io.BytesIO(file.read()))
        elif tid:
            img = get_template_image(tid)
        else:
            img = create_placeholder("SMOKEMEME","#0a0a0a","#1a1a2e")
        buf = generate_meme(img, top, bottom, fsize, color, outline)
        b64 = base64.b64encode(buf.read()).decode()
        g = session.get("gallery",[])
        g.insert(0,{"data":b64,"top":top,"bottom":bottom})
        session["gallery"] = g[:12]
        return jsonify({"success":True,"image":b64})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)}), 400

@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json(silent=True) or {}
    b64 = data.get("image","")
    if not b64: return "No image",400
    try:
        buf = io.BytesIO(base64.b64decode(b64))
        buf.seek(0)
        return send_file(buf, mimetype="image/png", as_attachment=True, download_name="smokememe.png")
    except Exception as e:
        return str(e), 400

@app.route("/api/random-quote")
def api_random_quote():
    q, a = random.choice(CRYPTO_QUOTES)
    return jsonify({"quote":q,"author":a})

@app.route("/api/template-preview/<tid>")
def api_template_preview(tid):
    img = get_template_image(tid)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.errorhandler(404)
def not_found(e): return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)