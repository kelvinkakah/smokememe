"""
Generate placeholder crypto template images for SmokeMeme.
Run once: python generate_templates.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

OUTPUT_DIR = Path("static/images/templates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = (600, 600)

TEMPLATES = [
    {
        "id": "pepe",
        "emoji": "🐸",
        "colors": [("#0d2b0d", "#1a4a1a", "#39ff14")],
        "label": "FEELS GOOD",
    },
    {
        "id": "rocket",
        "emoji": "🚀",
        "colors": [("#050520", "#0a0a3e", "#00d4ff")],
        "label": "TO THE MOON",
    },
    {
        "id": "diamond",
        "emoji": "💎",
        "colors": [("#050a14", "#0a1a28", "#b9f2ff")],
        "label": "DIAMOND HANDS",
    },
    {
        "id": "laser",
        "emoji": "👀",
        "colors": [("#140005", "#28000a", "#ff0040")],
        "label": "LASER EYES",
    },
    {
        "id": "ape",
        "emoji": "🦍",
        "colors": [("#140a00", "#28140a", "#ff8c00")],
        "label": "APE IN",
    },
    {
        "id": "moon",
        "emoji": "🌙",
        "colors": [("#050510", "#0a0a1e", "#a855f7")],
        "label": "MOON MATH",
    },
]


def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def make_template(cfg: dict) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img)

    c1, c2, accent = hex_to_rgb(cfg["colors"][0][0]), hex_to_rgb(cfg["colors"][0][1]), hex_to_rgb(cfg["colors"][0][2])

    # Gradient background
    for y in range(SIZE[1]):
        t = y / SIZE[1]
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (SIZE[0], y)], fill=(r, g, b))

    # Grid lines
    for x in range(0, SIZE[0], 60):
        draw.line([(x, 0), (x, SIZE[1])], fill=(*accent, 20), width=1)
    for y in range(0, SIZE[1], 60):
        draw.line([(0, y), (SIZE[0], y)], fill=(*accent, 20), width=1)

    # Center circle
    cx, cy = SIZE[0] // 2, SIZE[1] // 2
    for r in [200, 160, 100]:
        draw.ellipse(
            [(cx - r, cy - r), (cx + r, cy + r)],
            outline=(*accent, 30),
            width=1,
        )

    # Corner accents
    corner_size = 40
    corners = [(0, 0), (SIZE[0] - corner_size, 0), (0, SIZE[1] - corner_size), (SIZE[0] - corner_size, SIZE[1] - corner_size)]
    for cx_c, cy_c in corners:
        draw.rectangle([cx_c, cy_c, cx_c + corner_size, cy_c + corner_size], outline=(*accent, 80), width=1)

    # Label at top
    try:
        from PIL import ImageFont
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        font = None
        for fp in font_paths:
            if Path(fp).exists():
                font = ImageFont.truetype(fp, 28)
                break
        if not font:
            font = ImageFont.load_default()

        label = cfg["label"]
        try:
            bbox = font.getbbox(label)
            lw = bbox[2] - bbox[0]
        except:
            lw = len(label) * 16

        x = (SIZE[0] - lw) // 2
        # Outline
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                draw.text((x + dx, 24 + dy), label, font=font, fill=(0, 0, 0))
        draw.text((x, 24), label, font=font, fill=accent)

        # Big emoji-like text at center
        big_font = ImageFont.truetype(font_paths[0], 120) if Path(font_paths[0]).exists() else font
        emoji_char = cfg["emoji"]
        try:
            bbox2 = big_font.getbbox(emoji_char)
            ew = bbox2[2] - bbox2[0]
            eh = bbox2[3] - bbox2[1]
        except:
            ew, eh = 120, 120
        ex = (SIZE[0] - ew) // 2
        ey = (SIZE[1] - eh) // 2
        draw.text((ex, ey), emoji_char, font=big_font, fill=(255, 255, 255, 200))

    except Exception as e:
        print(f"  Font error for {cfg['id']}: {e}")

    return img


if __name__ == "__main__":
    print("🔥 Generating SmokeMeme templates...")
    for tmpl in TEMPLATES:
        img = make_template(tmpl)
        out = OUTPUT_DIR / f"{tmpl['id']}.png"
        img.save(out, format="PNG")
        print(f"  ✓ {out}")
    print("✅ All templates generated!")
