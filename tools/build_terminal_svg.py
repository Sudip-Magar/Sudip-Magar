#!/usr/bin/env python3
"""Build the animated terminal SVG used as the profile README hero.

The left panel is a vector profile card (hexagon "SM" badge). Two themes are emitted from one
source of truth so layout and timing can never drift apart.

    python3 tools/build_terminal_svg.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── geometry ────────────────────────────────────────────────────────────────
FS = 11             # font size (px)
CW = FS * 0.6       # monospace advance width
LH = 15.5           # line height
PAD_X = 26
BAR_H = 34
TOP = BAR_H + 30    # first baseline
GAP = 4             # columns between portrait and info

MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'DejaVu Sans Mono','Liberation Mono',monospace")

# Emerald palette. Key names are roles, not hues:
#   rust = primary accent, amber = secondary accent, olive = labels/prompt.
THEMES = {
    "dark": {
        "bg": "#04140F", "bar": "#0A2119", "edge": "#14382B",
        "fg": "#D1FAE5", "dim": "#5F8B7A", "rule": "#14382B",
        "rust": "#34D399", "amber": "#FCD34D", "olive": "#6EE7B7",
        "ink0": "#A7F3D0", "ink1": "#6EE7B7", "ink2": "#34D399",
    },
    "light": {
        "bg": "#F0FDF7", "bar": "#D1FAE5", "edge": "#A7F3D0",
        "fg": "#06281D", "dim": "#4D7A69", "rule": "#A7F3D0",
        "rust": "#047857", "amber": "#92400E", "olive": "#065F46",
        "ink0": "#065F46", "ink1": "#047857", "ink2": "#059669",
    },
}

PROMPT = [("sudip@github", "olive"), (":", "dim"), ("~", "rust"), ("$ ", "dim")]

INFO = [
    ("host",     "Sudip-Magar"),
    ("RULE",     ""),
    ("role",     "laravel developer"),
    ("shell",    "php · javascript"),
    ("backend",  "laravel · livewire · mysql"),
    ("frontend", "react · tailwind · bootstrap"),
    ("design",   "figma · photoshop · illustrator"),
    ("degree",   "BCA, tribhuvan university (2026)"),
    ("", ""),
    ("uname",    "php artisan serve, always"),
]


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── profile card (left panel) ───────────────────────────────────────────────
# Drawn as real SVG shapes, not text art: block/box glyphs never tile cleanly
# at this line height. The terminal reserves CARD_ROWS blank rows for it.
CARD_COLS = 33                    # columns of space reserved for the card
CARD_ROWS = 13
CARD_W = 206                      # px; fits CARD_COLS even on narrow fonts
CHIPS = ["laravel", "php", "mysql"]


def card_svg(C, theme, x, y):
    w, h = CARD_W, CARD_ROWS * LH - 6
    cx = x + w / 2
    hy, r = y + 54, 38
    pts = " ".join(f"{cx + r * dx:.1f},{hy + r * dy:.1f}" for dx, dy in
                   ((0, -1), (.866, -.5), (.866, .5), (0, 1), (-.866, .5), (-.866, -.5)))
    inner = " ".join(f"{cx + (r - 7) * dx:.1f},{hy + (r - 7) * dy:.1f}" for dx, dy in
                     ((0, -1), (.866, -.5), (.866, .5), (0, 1), (-.866, .5), (-.866, -.5)))
    glow = .22 if theme == "dark" else .14
    o = [
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{C["olive"]}" stop-opacity="{glow}"/>'
        f'<stop offset="1" stop-color="{C["rust"]}" stop-opacity="{glow/4}"/>'
        f'</linearGradient></defs>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
        f'fill="{C["bar"]}" stroke="{C["edge"]}" stroke-width="1"/>',
        f'<polygon points="{pts}" fill="url(#g)" stroke="{C["rust"]}" stroke-width="1.6"/>',
        f'<polygon points="{inner}" fill="none" stroke="{C["rust"]}" '
        f'stroke-opacity=".35" stroke-width="1" stroke-dasharray="2 3"/>',
        f'<text x="{cx}" y="{hy + 9}" text-anchor="middle" font-size="25" '
        f'font-weight="700" letter-spacing="1" fill="{C["rust"]}">SM</text>',
        f'<text x="{cx}" y="{y + 116}" text-anchor="middle" font-size="14" '
        f'font-weight="700" fill="{C["fg"]}">Sudip Magar</text>',
        f'<text x="{cx}" y="{y + 132}" text-anchor="middle" font-size="9" '
        f'letter-spacing="2.2" fill="{C["dim"]}">LARAVEL DEVELOPER</text>',
    ]
    cw = [len(c) * 6 + 14 for c in CHIPS]
    gap = 6
    cxp = cx - (sum(cw) + gap * (len(CHIPS) - 1)) / 2
    for c, wc in zip(CHIPS, cw):
        o.append(f'<rect x="{cxp:.1f}" y="{y + 143}" width="{wc}" height="16" rx="8" '
                 f'fill="none" stroke="{C["olive"]}" stroke-opacity=".6"/>')
        o.append(f'<text x="{cxp + wc/2:.1f}" y="{y + 154.5}" text-anchor="middle" '
                 f'font-size="9.5" fill="{C["olive"]}">{c}</text>')
        cxp += wc + gap
    o.append(f'<circle cx="{cx - 52}" cy="{y + 179}" r="3.2" fill="{C["rust"]}"/>')
    o.append(f'<circle cx="{cx - 52}" cy="{y + 179}" r="6" fill="none" '
             f'stroke="{C["rust"]}" stroke-opacity=".35"/>')
    o.append(f'<text x="{cx - 42}" y="{y + 182.5}" font-size="10" '
             f'fill="{C["dim"]}">open to freelance work</text>')
    return o


def build_lines():
    art_rows = [[(" " * CARD_COLS, "fg")] for _ in range(CARD_ROWS)]

    lines = []
    lines.append(PROMPT + [("neofetch", "fg")])
    lines.append([("", "fg")])

    label_w = max(len(k) for k, _ in INFO if k and k != "RULE")
    info_start = 2                      # vertical offset of info block

    for i, row in enumerate(art_rows):
        segs = list(row) + [(" " * GAP, "fg")]

        j = i - info_start
        if 0 <= j < len(INFO):
            k, v = INFO[j]
            if k == "RULE":
                segs.append(("─" * 38, "rule"))
            elif k == "host":
                segs.append(("sudip", "rust"))
                segs.append(("@", "dim"))
                segs.append(("github", "amber"))
            elif k:
                segs.append((k.ljust(label_w) + "   ", "olive"))
                segs.append((v, "fg"))
        lines.append(segs)

    def blank():
        lines.append([("", "fg")])

    def cmd(text):
        lines.append(PROMPT + [(text, "fg")])

    def body(text, key="fg"):
        lines.append([("  " + text, key)])

    blank()
    cmd("cat about.txt")
    body("laravel developer from nepal. i build web apps end to end —")
    body("laravel + mysql on the backend, react / tailwind on the front.")
    body("BCA graduate — milton international college, TU (2026).")
    blank()
    body("open to freelance work. say hi: sudeepmagar730@gmail.com")

    blank()
    cmd("ls ~/stack")
    body("php        laravel    livewire   mysql       reverb", "olive")
    body("javascript alpine.js  react      tailwind    bootstrap", "olive")
    body("git        github     figma      photoshop   jquery", "olive")

    blank()
    cmd("ls ~/projects")
    def proj(name, desc, key="fg"):
        lines.append([("  " + name.ljust(18), "rust"), (desc, key)])

    proj("sajha-auction", "second-hand marketplace + live auctions")
    proj("", "proxy bids, anti-sniping, real-time (reverb)", "dim")
    proj("connectx", "social media app")
    proj("multivendor-ecom", "multi-vendor e-commerce store")
    proj("scms-module", "livewire module with role permissions")
    lines.append([("  → ", "dim"), ("github.com/Sudip-Magar", "rust")])

    blank()
    lines.append(list(PROMPT))
    return lines


def render(theme):
    C = THEMES[theme]
    lines = build_lines()
    width_cols = max(sum(len(t) for t, _ in segs) for segs in lines)
    W = int(PAD_X * 2 + width_cols * CW) + 8
    H = int(TOP + LH * len(lines) + 20)

    step = 0.055                       # per-line reveal stagger
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="{FS}">',
        # Content is visible by default. Animation is an enhancement only —
        # never a precondition for the text showing up, because an SVG loaded
        # via <img> is not guaranteed to run its animation clock.
        "<style>"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".cur{animation:blink 1.05s step-end infinite}"
        "@media(prefers-reduced-motion:reduce){.cur{animation:none}}"
        "</style>",
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="11" '
        f'fill="{C["bg"]}" stroke="{C["edge"]}" stroke-width="1.5"/>',
        f'<path d="M1 12 a11 11 0 0 1 11-11 h{W-24} a11 11 0 0 1 11 11 '
        f'v{BAR_H-12} h-{W-2} z" fill="{C["bar"]}"/>',
        f'<line x1="1" y1="{BAR_H}" x2="{W-1}" y2="{BAR_H}" '
        f'stroke="{C["edge"]}" stroke-width="1.5"/>',
    ]
    for i, col in enumerate(("rust", "amber", "olive")):
        out.append(f'<circle cx="{22 + i*17}" cy="{BAR_H/2}" r="4.8" '
                   f'fill="{C[col]}"/>')
    out.append(f'<text x="{W/2}" y="{BAR_H/2 + 4}" text-anchor="middle" '
               f'fill="{C["dim"]}" font-size="11">sudip@github — zsh</text>')

    out += card_svg(C, theme, PAD_X, TOP + 2 * LH - FS - 2)

    # One <text> per line with coloured <tspan>s, so the browser advances each
    # glyph itself. Positioning runs by an assumed char width drifts on fonts
    # whose advance isn't exactly 0.6em (e.g. Consolas), leaving odd gaps.
    for idx, segs in enumerate(lines):
        y = TOP + idx * LH
        last = idx == len(lines) - 1
        spans = "".join(
            f'<tspan fill="{C.get(key, C["fg"])}">{esc(t)}</tspan>'
            for t, key in segs if t)
        if last:
            spans += (f'<tspan class="cur" fill="{C["rust"]}" '
                      f'style="animation-delay:{round(len(lines)*0.055,3)}s">█</tspan>')
        if spans:
            out.append(f'<text x="{PAD_X}" y="{y:.1f}" xml:space="preserve">'
                       f'{spans}</text>')

    out.append("</svg>")
    return "\n".join(out)


def main():
    for theme, fname in (("dark", "dark_mode.svg"), ("light", "light_mode.svg")):
        p = ROOT / fname
        p.write_text(render(theme), encoding="utf-8")
        print(f"wrote {p.name}  ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
