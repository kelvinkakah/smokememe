# 🔥 SmokeMeme – Crypto Meme & Quote Generator

> *The most degen crypto meme generator on the internet. Built for web3 degens, by degens.*

![SmokeMeme Banner](https://via.placeholder.com/1200x400/050510/39ff14?text=SMOKEMEME+%F0%9F%94%A5+Crypto+Meme+Generator)

## ✨ Features

- 🖼 **6 Built-in Crypto Templates** — Pepe, Rocket, Diamond Hands, Laser Eyes, Ape In, Moon Math
- 📤 **Upload Your Own Image** — JPG, PNG, GIF, WEBP (up to 10MB)
- ✍️ **Full Text Control** — Top & bottom text, font size slider, 4 neon color options
- 🖊 **Black outline toggle** for maximum readability
- ⚡ **Instant Preview** — Meme rendered server-side with Pillow, returned as base64
- ⬇️ **One-click PNG Download**
- 📋 **Copy to clipboard** support
- 💬 **24+ Crypto Quotes** — Random quote generator with "Turn Into Meme" shortcut
- 🖼 **Session Gallery** — Browse all memes you generated this session
- 🌙 **Cyberpunk Dark UI** — Neon green/plasma accents, CRT scanlines, Orbitron font
- 📱 **Fully Responsive** — Mobile-first design

## 🗂 Project Structure

```
smokememe/
├── app.py                    # Main Flask app + Pillow meme generation
├── generate_templates.py     # One-time script to generate template PNGs
├── templates/
│   ├── base.html             # Cyberpunk navbar, footer, global styles
│   ├── index.html            # Hero page with quote + template grid
│   ├── generator.html        # Full meme generator with live preview
│   ├── quotes.html           # All 24+ crypto quotes with meme shortcuts
│   ├── gallery.html          # Session gallery with lightbox
│   └── 404.html              # Rugged 404 page
├── static/
│   ├── images/templates/     # 6 generated template PNGs
│   └── uploads/              # Temp upload dir (gitignored)
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Local Setup

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/smokememe.git
cd smokememe

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

### 3. Generate Template Images

```bash
python generate_templates.py
```

This creates the 6 crypto template PNGs in `static/images/templates/`.

### 4. Run

```bash
flask run
# or
python app.py
```

Visit `http://localhost:5000` 🎉

## ☁️ Vercel Deployment

### Prerequisites
- [Vercel CLI](https://vercel.com/cli): `npm i -g vercel`
- Python 3.11+ on Vercel

### Steps

```bash
# 1. Login to Vercel
vercel login

# 2. Set your secret key as a Vercel environment variable
vercel env add SECRET_KEY
# Paste a long random string when prompted

# 3. Deploy
vercel --prod
```

That's it. Vercel auto-detects Python and uses `vercel.json` for routing.

> **Note:** Vercel serverless functions are stateless — the session gallery works per-request but isn't persistent across function instances. For a persistent gallery, add a database like PlanetScale or Supabase.

### Environment Variables on Vercel

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session secret — use a long random string |

Set via Vercel Dashboard → Project → Settings → Environment Variables.

## 🎨 Add More Templates

1. Add your image to `static/images/templates/yourname.png`
2. Add an entry to the `TEMPLATES` list in `app.py`:

```python
{
    "id": "yourname",
    "name": "Your Template Name",
    "emoji": "🔥",
    "file": "yourname.png",
    "description": "A short description shown in the UI.",
},
```

3. Optionally add placeholder colors to `TEMPLATE_COLORS` in `app.py`:

```python
"yourname": ("#darkcolor", "#accentcolor"),
```

## 💬 Add More Quotes

In `app.py`, add to the `CRYPTO_QUOTES` list:

```python
CRYPTO_QUOTES = [
    ...
    ("Your amazing quote here.", "The Author"),
]
```

Each quote is a `(quote, author)` tuple.

## 🛠 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Flask 3.x (Python) |
| Image Processing | Pillow (PIL) |
| Frontend | Jinja2 + Tailwind CSS (CDN) |
| Fonts | Orbitron + Share Tech Mono (Google Fonts) |
| Deployment | Vercel (serverless Python) |

## 📸 Screenshots

| Page | Description |
|---|---|
| **Home** | Hero with animated neon title, quote of the day, 6 template cards |
| **Generator** | Split-panel: controls left, live preview right |
| **Quotes** | Grid of 24+ crypto quotes with hover-reveal Meme/Copy buttons |
| **Gallery** | Session gallery with lightbox viewer |

## 🔐 Security Notes

- Uploaded files are validated by extension and MIME type
- Images are processed in-memory (no disk writes for generated memes)
- File upload size capped at 10 MB
- Secret key loaded from environment variable — never hardcode it

## 🤝 Contributing

PRs welcome! Some ideas:
- [ ] Add more templates (Wojak, Chad, This Is Fine, etc.)
- [ ] Watermark option
- [ ] Twitter/Discord direct share
- [ ] Persistent gallery with database
- [ ] Font style selector
- [ ] Sticker/overlay support

## 📜 License

MIT — Do whatever you want. WAGMI. 🤝

---

*Not financial advice. Past memes are not indicative of future gains. DYOR.*

**WAGMI 🤝 | Diamond Hands 💎 | NGMI → 🚀**
