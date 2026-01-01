"""Generate a small PNG placeholder for static/team/img/logo.png.

This script writes a tiny 1x1 PNG (transparent) as a placeholder.
Run it from the repo root: `python scripts/generate_logo_png.py`.
"""
import base64
from pathlib import Path

DATA = (
    b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
)

OUT = Path(__file__).resolve().parents[1] / 'volleyball_site' / 'team' / 'static' / 'team' / 'img' / 'logo.png'
OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open('wb') as f:
    f.write(base64.b64decode(DATA))

print('Wrote', OUT)
