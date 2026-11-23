#!/usr/bin/env python3
"""Turn a photo into the shaded ASCII art used in portrait.txt.

    python tools/make_portrait.py photo.jpg [--crop L,T,R,B] [--cols 46] [--invert]

Brighter pixels become denser characters (they render as light ink on the dark
theme). Needs Pillow:  pip install pillow
"""

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

RAMP = " .,:;+*?%S#@"
ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--crop", help="left,top,right,bottom in pixels")
    ap.add_argument("--cols", type=int, default=46)
    ap.add_argument("--contrast", type=float, default=1.6)
    ap.add_argument("--invert", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "tools" / "portrait.txt"))
    a = ap.parse_args()

    im = Image.open(a.image).convert("L")
    if a.crop:
        im = im.crop(tuple(int(v) for v in a.crop.split(",")))
    im = ImageOps.autocontrast(im, cutoff=2)
    im = ImageEnhance.Contrast(im).enhance(a.contrast)
    im = im.filter(ImageFilter.SMOOTH)
    if a.invert:
        im = ImageOps.invert(im)

    # monospace cells are ~0.6 wide : 1.55 tall (see build_terminal_svg.py)
    rows = max(1, round(a.cols * im.height / im.width * (0.6 * 11) / 15.5))
    im = im.resize((a.cols, rows), Image.LANCZOS)

    px = im.load()
    lines = []
    for y in range(rows):
        row = "".join(RAMP[px[x, y] * (len(RAMP) - 1) // 255] for x in range(a.cols))
        lines.append(row.rstrip())
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n{a.cols}x{rows} -> {a.out}")


if __name__ == "__main__":
    main()
