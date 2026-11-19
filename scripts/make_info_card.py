#!/usr/bin/env python3
"""
scripts/make_info_card.py
Renders a neofetch-style terminal info card SVG tailored for DEV / xCodeWraith.
Uses Avi Vashishta's exact palette (#0d1117, #30363d, #c9d1d9, #7d8590, #39d353, #22d3ee, #f2cc60),
staggered CSS animations, and macOS terminal styling.
Width: 490px, Height: 415px (Pairs with dev-ascii.svg 370px to total 860px).
"""
import os
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "info-card.svg")

CANVAS_W = 490
CANVAS_H = 415
PAD = 22
TITLEBAR_H = 30

# Exact Avi Vashishta Palette
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
MUTED = "#7d8590"
GREEN = "#39d353"
CYAN = "#22d3ee"
GOLD = "#f2cc60"
BLUE = "#58a6ff"

ROWS_DATA = [
    ("header", "xCodeWraith", "alpha-node"),
    ("divider", "---------------------------------------------", None),
    ("item", "OS", "AlphaOS Linux x86_64", CYAN),
    ("item", "Host", "DEV Autonomous Terminal Node", INK),
    ("item", "Role", "AI Agents Architect & Automation Engineer", INK),
    ("item", "Focus", "Crypto Trading Agents, Alpha Scanners & n8n", INK),
    ("item", "Core Stack", "Python, n8n, LangChain, Web3, Docker", INK),
    ("item", "Authority", "550+ Cumulative GitHub Stars", GOLD),
    ("item", "Featured", "GoogleMapAIagent (382 ⭐)", BLUE),
    ("item", "Motto", '"Insider tools > Insider news"', GREEN),
    ("divider", "---------------------------------------------", None),
    ("status", "System Status", "All agent pipelines operational", GREEN),
]

def main():
    css = """
@keyframes rise {
  0% { opacity: 0; transform: translateY(8px); }
  100% { opacity: 1; transform: translateY(0); }
}
.row { opacity: 0; animation: rise 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
.pulse { animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="bg_info" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="10" fill="url(#bg_info)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="10" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    # Traffic lights
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*14}" cy="{TITLEBAR_H/2}" r="4.5" fill="{dotcol}"/>')

    parts.append(
        f'<text x="{CANVAS_W/2 + 15}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="11" text-anchor="middle">'
        f'xCodeWraith@DEV-terminal:~$ neofetch</text>'
    )

    y_start = TITLEBAR_H + 28
    line_step = 28
    delay_base = 0.15

    for idx, item in enumerate(ROWS_DATA):
        y = y_start + idx * line_step
        delay = delay_base + idx * 0.08
        itype = item[0]

        if itype == "header":
            user, host = item[1], item[2]
            parts.append(
                f'<g class="row" style="animation-delay: {delay:.3f}s;">'
                f'<text x="{PAD}" y="{y}" font-size="13" font-weight="bold">'
                f'<tspan fill="{GREEN}">{user}</tspan>'
                f'<tspan fill="{MUTED}">@</tspan>'
                f'<tspan fill="{CYAN}">{host}</tspan></text></g>'
            )
        elif itype == "divider":
            text = item[1]
            parts.append(
                f'<g class="row" style="animation-delay: {delay:.3f}s;">'
                f'<text x="{PAD}" y="{y-4}" font-size="11" fill="{FRAME}">{text}</text></g>'
            )
        elif itype == "item":
            label, val, val_col = item[1], item[2], item[3]
            parts.append(
                f'<g class="row" style="animation-delay: {delay:.3f}s;">'
                f'<text x="{PAD}" y="{y}" font-size="12">'
                f'<tspan fill="{MUTED}" font-weight="600">{label:12}: </tspan>'
                f'<tspan fill="{val_col}" font-weight="500">{escape(val)}</tspan></text></g>'
            )
        elif itype == "status":
            label, val, val_col = item[1], item[2], item[3]
            parts.append(
                f'<g class="row" style="animation-delay: {delay:.3f}s;">'
                f'<circle cx="{PAD + 4}" cy="{y - 4}" r="3.5" fill="{val_col}" class="pulse"/>'
                f'<text x="{PAD + 16}" y="{y}" font-size="11.5" fill="{MUTED}">'
                f'<tspan font-weight="600">{label}: </tspan>'
                f'<tspan fill="{val_col}">{escape(val)}</tspan></text></g>'
            )

    parts.append("</svg>")
    svg = "".join(parts)

    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Successfully generated {OUT} ({CANVAS_W}x{CANVAS_H}, {len(svg)} bytes)")

if __name__ == "__main__":
    main()
