#!/usr/bin/env python3
"""Build the animated terminal SVG used as the profile README hero.

The portrait in `portrait.txt` is shaded ASCII art derived from the avatar
(density-mapped luminance, not hand-drawn). Two themes are emitted from one
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

THEMES = {
    "dark": {
        "bg": "#12100B", "bar": "#1D1912", "edge": "#332C20",
        "fg": "#CFC7B0", "dim": "#7A7160", "rule": "#332C20",
        "rust": "#DB6B34", "amber": "#E8A33D", "olive": "#8A9A5B",
        "ink0": "#E4DCC6", "ink1": "#D6CDB4", "ink2": "#BFB49A",
    },
    "light": {
        "bg": "#F6F1E4", "bar": "#EAE2CF", "edge": "#D2C8AE",
        "fg": "#2E2A20", "dim": "#6E6653", "rule": "#D2C8AE",
        "rust": "#B4551F", "amber": "#8A5E10", "olive": "#5A6838",
        "rust_": "", "ink0": "#8A5E10", "ink1": "#B4551F", "ink2": "#5C4326",
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


def build_lines():
    art = (ROOT / "tools" / "portrait.txt").read_text(encoding="utf-8")
    art_rows = [r.rstrip("\n") for r in art.split("\n")]
    while art_rows and not art_rows[-1].strip():
        art_rows.pop()
    art_w = max(len(r) for r in art_rows)

    lines = []
    lines.append(PROMPT + [("neofetch", "fg")])
    lines.append([("", "fg")])

    label_w = max(len(k) for k, _ in INFO if k and k != "RULE")
    info_start = 2                      # vertical offset of info block

    for i, row in enumerate(art_rows):
        # portrait shading: three bands so the ink reads with depth
        band = "ink0" if i < len(art_rows) * 0.34 else (
            "ink1" if i < len(art_rows) * 0.7 else "ink2")
        segs = [(row.ljust(art_w + GAP), band)]

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
    body("sajha-auction     second-hand marketplace + live auctions", "amber")
    body("                  proxy bids, anti-sniping, real-time (reverb)", "dim")
    body("connectx          social media app", "amber")
    body("multivendor-ecom  multi-vendor e-commerce store", "amber")
    body("scms-module       livewire module with role permissions", "amber")
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

    for idx, segs in enumerate(lines):
        y = TOP + idx * LH
        delay = round(idx * step, 3)
        runs = []
        col = 0
        for t, key in segs:
            if t:
                runs.append(
                    f'<text x="{PAD_X + col*CW:.1f}" y="{y:.1f}" '
                    f'fill="{C.get(key, C["fg"])}" xml:space="preserve">'
                    f'{esc(t)}</text>')
            col += len(t)
        if runs:
            out.append("<g>" + "".join(runs) + "</g>")

    cur_col = sum(len(t) for t, _ in lines[-1])
    out.append(
        f'<rect class="cur" x="{PAD_X + cur_col*CW:.1f}" '
        f'y="{TOP + (len(lines)-1)*LH - FS + 2.5:.1f}" width="{CW:.1f}" '
        f'height="{FS}" fill="{C["rust"]}" '
        f'style="animation-delay:{round(len(lines)*step,3)}s"/>')

    out.append("</svg>")
    return "\n".join(out)


def main():
    for theme, fname in (("dark", "dark_mode.svg"), ("light", "light_mode.svg")):
        p = ROOT / fname
        p.write_text(render(theme), encoding="utf-8")
        print(f"wrote {p.name}  ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
