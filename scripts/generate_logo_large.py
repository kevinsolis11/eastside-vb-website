"""Generate a 600x150 PNG placeholder logo at
volleyball_site/team/static/team/img/logo.png

Usage: python3 scripts/generate_logo_large.py
"""
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    raise SystemExit("Pillow is required: run 'pip install Pillow' and re-run this script")

OUT = Path(__file__).resolve().parents[1] / 'volleyball_site' / 'team' / 'static' / 'team' / 'img' / 'logo.png'
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 600, 150
bg = (11, 97, 255)  # #0b61ff
fg = (255, 255, 255)

img = Image.new('RGBA', (W, H), bg)
draw = ImageDraw.Draw(img)

# Try to load a common system font; fall back to default if not available
font = None
for fname in [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/Library/Fonts/Arial.ttf',
    '/System/Library/Fonts/SFNS.ttf',
]:
    try:
        font = ImageFont.truetype(fname, 48)
        break
    except Exception:
        font = None

if font is None:
    font = ImageFont.load_default()

text = "Eastside VB"
try:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
except Exception:
    tw, th = draw.textsize(text, font=font)
draw.text(((W - tw) / 2, (H - th) / 2), text, font=font, fill=fg)

img.save(OUT)
print('Wrote', OUT)
