#!/usr/bin/env python3
"""
scripts/make_ascii_svg.py
Converts prepped photo into a clean, monochrome animated ASCII SVG (Avi Vashishta / Andrew6rant style).
Single ink color (#c9d1d9), dark GitHub background (#0d1117), SMIL left-to-right typewriter wipe,
and an active blinking cursor.
Width: 370px, Height: 415px (matches info-card.svg 490px to total 860px).
"""
import os
import sys
import html
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "dev-ascii.svg")

# Target dimensions to exactly pair with info-card.svg (370px + 490px = 860px)
CANVAS_W = 370
CANVAS_H = 415
PAD = 16
TITLEBAR_H = 30
STATUS_H = 32

ART_W = CANVAS_W - PAD * 2  # 338px
COLS = int(os.environ.get("COLS", 96))
CELL_W = ART_W / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round((CANVAS_H - TITLEBAR_H - STATUS_H - PAD * 1.2) / CELL_H)
ART_H = ROWS * CELL_H

RAMP = " .`:-=+*cs#%@"  # Bright (sparse) -> Dark (dense)

# Precise tuning for facial/subject detail
CONTRAST = 1.08
BRIGHTNESS = 1.0
GAMMA = 1.15
WHITE_FLOOR = 0.82

# Exact Avi Vashishta Palette
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 4.8 / ROWS
STAGGER = ROW_DUR

def main():
    if not os.path.exists(SRC):
        print(f"Error: {SRC} does not exist. Run prep_photo.py first.", file=sys.stderr)
        sys.exit(1)

    im = Image.open(SRC).convert("L")
    im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    im = im.resize((COLS, ROWS), Image.LANCZOS)
    px = im.load()

    rows_txt = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = px[x, y] / 255.0
            lum = pow(lum, GAMMA)
            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows_txt.append("".join(chars))

    art_top = TITLEBAR_H + 10

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="bg_ascii" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="10" fill="url(#bg_ascii)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="10" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    # Traffic light dots
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*14}" cy="{TITLEBAR_H/2}" r="4.5" fill="{dotcol}"/>')

    parts.append(
        f'<text x="{CANVAS_W/2 + 15}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="11" text-anchor="middle">'
        f'dev@xCodeWraith: ~$ ./portrait.sh</text>'
    )

    font_size = CELL_H * 0.86
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER
        safe = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>'
        )

        parts.append(
            f'<clipPath id="ar{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.2f}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#ar{ry})">{text}</g>')
        parts.append(
            f'<rect y="{row_y+0.5:.1f}" width="{CELL_W:.2f}" height="{CELL_H-1:.2f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
        )

    # Status bar with blinking terminal cursor
    status_line_y = CANVAS_H - STATUS_H
    status_y = status_line_y + 20
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="12">'
        f'dev@xCodeWraith:~$ whoami <tspan fill="{INK}" font-weight="bold">DEV</tspan></text>'
    )
    cursor_x = PAD + len("dev@xCodeWraith:~$ whoami DEV ") * 7.2
    parts.append(
        f'<rect x="{cursor_x:.1f}" y="{status_y-11:.1f}" width="7" height="13" fill="{INK}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>'
    )

    parts.append("</svg>")
    svg = "".join(parts)

    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Successfully generated {OUT} ({CANVAS_W}x{CANVAS_H}, {len(svg)} bytes)")

if __name__ == "__main__":
    main()
