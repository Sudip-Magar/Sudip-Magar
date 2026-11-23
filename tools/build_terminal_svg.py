#!/usr/bin/env python3
"""Build the animated terminal SVG used as the profile README hero.

The left panel is a pixel-art portrait (see make_portrait.py). Two themes are emitted from one
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


# ── pixel portrait (left panel) ─────────────────────────────────────────────
# tools/portrait.txt is a pixel grid made by make_portrait.py: "." = empty,
# "1".."5" = tone, dark to light. Drawn as squares on a dark emerald screen
# (same in both themes, so the portrait keeps its contrast in light mode).
CARD_COLS = 33                    # text columns reserved for the panel
CARD_ROWS = 16                    # text rows reserved for the panel
CARD_W = 206                      # px; fits CARD_COLS even on narrow fonts
SCREEN = "#04140F"
TONES = {"1": "#155A41", "2": "#1F8058", "3": "#2BB57D",
         "4": "#5BE3A6", "5": "#D1FAE5"}


def portrait_svg(C, x, y):
    grid = [r for r in (ROOT / "tools" / "portrait.txt")
            .read_text(encoding="utf-8").splitlines() if r]
    w, h = CARD_W, CARD_ROWS * LH - 8
    pad = 8
    cell = min((w - 2 * pad) / len(grid[0]), (h - 2 * pad) / len(grid))
    ox = x + (w - cell * len(grid[0])) / 2
    oy = y + h - pad - cell * len(grid)          # sit on the bottom edge
    gap = max(0.6, cell * 0.12)
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
         f'fill="{SCREEN}" stroke="{C["edge"]}" stroke-width="1"/>']
    # faint grid behind the subject, like the dots of an LED panel
    o.append(f'<g fill="#0A1F18">' + "".join(
        f'<rect x="{ox + c*cell:.1f}" y="{oy + r*cell:.1f}" width="{cell-gap:.1f}" '
        f'height="{cell-gap:.1f}"/>'
        for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == ".")
        + "</g>")
    for tone, col in TONES.items():
        cells = "".join(
            f'<rect x="{ox + c*cell:.1f}" y="{oy + r*cell:.1f}" '
            f'width="{cell-gap:.1f}" height="{cell-gap:.1f}"/>'
            for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == tone)
        o.append(f'<g fill="{col}">{cells}</g>')
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

    out += portrait_svg(C, PAD_X, TOP + 2 * LH - FS - 2)

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
