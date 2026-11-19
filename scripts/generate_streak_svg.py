#!/usr/bin/env python3
"""
scripts/generate_streak_svg.py
Generates the animated GitHub contribution heatmap SVG (Avi Vashishta's exact implementation).
Each square pops in and flashes at 2.4x brightness for a vivid glowing green neon effect.
Reads data/contributions.json and writes contrib-heatmap.svg.
"""
import sys
import json
import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SNAP = os.path.join(ROOT, "data", "contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "contrib-heatmap.svg")

def main():
    if not os.path.exists(SNAP):
        print(f"Error: {SNAP} not found.", file=sys.stderr)
        sys.exit(1)

    with open(SNAP) as f:
        data = json.load(f)

    contribs = data["days"]
    total = data["total_contributions"]

    CELL, GAP, RAD, LEFT, TOP = 13, 3, 2.5, 34, 24
    COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    GRAY = "#7d8590"
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    n = len(contribs)
    NW = (n + 6) // 7
    W = LEFT + NW * (CELL + GAP) + 6
    H = TOP + 7 * (CELL + GAP) + 24

    REVEAL, DUR = 3.6, 0.55
    maxorder = (NW - 1) + 6 * 0.55

    rects, labels = [], []
    sd = datetime.date.fromisoformat(contribs[0]["date"])
    last_m = None

    for wk in range(NW):
        d = sd + datetime.timedelta(days=wk * 7)
        if d.month != last_m:
            last_m = d.month
            labels.append(f'<text class="lbl" x="{LEFT + wk*(CELL+GAP)}" y="{TOP - 8}">{MONTHS[d.month-1]}</text>')

    for name, r in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        labels.append(f'<text class="lbl" x="2" y="{TOP + r*(CELL+GAP) + CELL - 2}">{name}</text>')

    for i, c in enumerate(contribs):
        wk, row = i // 7, i % 7
        lvl = min(c.get("level", 0), len(COLORS) - 1)
        x = LEFT + wk * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        delay = round((wk + row * 0.55) / maxorder * REVEAL, 3)
        cls = "c g" if lvl >= 1 else "c e"
        count = c.get("count", 0)
        date_s = c.get("date", "")
        plural = "s" if count != 1 else ""

        rects.append(
            f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
            f'fill="{COLORS[lvl]}" style="animation-delay:{delay}s">'
            f'<title>{date_s}: {count} contribution{plural}</title></rect>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif">
<style>
  text.lbl {{ fill:{GRAY}; font-size:12px; font-weight:600; }}
  text.total {{ fill:#e6edf3; font-size:14px; font-weight:700; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:0; animation:pop {DUR}s ease-out both; }}
  .g {{ animation:pop {DUR}s ease-out both, flash {DUR+0.18}s ease-out both; }}
  @keyframes pop {{ 0%{{opacity:0;transform:scale(.2)}} 60%{{opacity:1;transform:scale(1.15)}} 100%{{opacity:1;transform:scale(1)}} }}
  @keyframes flash {{ 0%{{filter:brightness(2.8)}} 45%{{filter:brightness(2.8)}} 100%{{filter:brightness(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .c, .g {{ opacity:1 !important; animation:none !important; }} }}
</style>
<rect width="{W}" height="{H}" fill="none"/>
{''.join(labels)}
{''.join(rects)}
<text class="total" x="{LEFT}" y="{H - 6}">{total:,} contributions in the last year</text>
</svg>"""

    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT}: {n} days, {total:,} contributions, flashing neon green.")

if __name__ == "__main__":
    main()
