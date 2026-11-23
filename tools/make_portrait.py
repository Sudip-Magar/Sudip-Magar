#!/usr/bin/env python3
"""Turn a cut-out photo into the pixel-art grid in tools/portrait.txt.

Each character is one pixel: "." is empty, "1".."5" are tone levels from
darkest to lightest. build_terminal_svg.py draws them as emerald squares.

    python tools/make_portrait.py [assets/photo.png]

The photo should have its background removed (transparent or pure black).
Needs Pillow:  pip install pillow
"""

import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
CROP = (430, 530, 1110, 1290)    # head + shoulders in the source photo
COLS = 36
# brightness cut-offs for tones 2..5, tuned so skin lands on the lightest
# tone, the jacket in the middle and hair / t-shirt in the darkest
THRESHOLDS = (38, 62, 92, 118)


def tone(px):
    """Brightness, re-weighted so skin is the focal point.

    Warm pixels (red well above green) are skin: pushed brighter. Neutral
    ones are the olive jacket, whose highlights would otherwise outshine the
    face: pulled down into the mid tones.
    """
    r, g, b = px
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if r - g > 22 and lum > 45:          # skin (dark red hair tips excluded)
        return 45 + lum * 0.62
    return lum * 0.55


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "photo.png"
    im = Image.open(src).convert("RGBA").crop(CROP)

    # subject mask: alpha, and anything that isn't the pure-black backdrop
    rgb = im.convert("RGB")
    mask = Image.eval(rgb.convert("L"), lambda v: 255 if v > 6 else 0)
    mask = Image.composite(mask, Image.new("L", im.size, 0), im.getchannel("A"))
    mask = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))

    rows = round(COLS * im.height / im.width)
    small = rgb.resize((COLS, rows), Image.LANCZOS)
    m = mask.resize((COLS, rows), Image.LANCZOS)

    out = []
    for y in range(rows):
        row = ""
        for x in range(COLS):
            if m.getpixel((x, y)) < 128:
                row += "."
            else:
                v = tone(small.getpixel((x, y)))
                row += str(1 + sum(v >= t for t in THRESHOLDS))
        out.append(row)
    (ROOT / "tools" / "portrait.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"\n{COLS}x{rows} -> tools/portrait.txt")


if __name__ == "__main__":
    main()
