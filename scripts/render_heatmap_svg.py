#!/usr/bin/env python3
"""
scripts/render_heatmap_svg.py
Renders data/contributions.json as an animated GitHub-style contribution heatmap SVG.
Uses Avi Vashishta's exact palette, diagonal cascade animation (CSS keyframes),
macOS window header, Less->More legend, and detailed metrics footer.
Target Width: 860px (Exact alignment with portrait 370px + info card 490px).
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
IN_PATH = os.path.join(ROOT, "data", "contributions.json")
OUT_PATH = os.path.join(ROOT, "contrib-heatmap.svg")

# Exact Avi Vashishta Green Ramp & Theme
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 20
LEFT_LABEL_W = 28
TOP_LABEL_H = 18
TITLEBAR_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

COL_T = 0.016
ROW_T = 0.040
CELL_DUR = 0.38

def level_for(count):
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5

def build_grid(days):
    if not days:
        # Fallback: Generate 53 weeks of empty days up to today
        today = datetime.date.today()
        start = today - datetime.timedelta(days=364)
        days = []
        cur = start
        while cur <= today:
            days.append({"date": cur.isoformat(), "count": 0, "level": 0})
            cur += datetime.timedelta(days=1)

    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # Sunday = 0
    grid = []
    col = [None] * lead_pad

    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d.get("count", 0), d.get("level", level_for(d.get("count", 0)))))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid

def render(data):
    days = data.get("days", [])
    grid = build_grid(days)
    n_cols = len(grid)
    art_w = n_cols * STEP
    art_h = 7 * STEP

    month_labels = []
    seen_months = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    canvas_w = 860  # Fixed 860px to match exactly
    grid_left = PAD + LEFT_LABEL_W
    # Center grid horizontally inside 860px
    available_w = canvas_w - grid_left - PAD
    if art_w < available_w:
        grid_left += (available_w - art_w) // 2

    stats_h = 76
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    css = f"""
@keyframes cell {{
  0%   {{ opacity: 0; transform: translateY(-5px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
.c {{ opacity: 0; animation: cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>',
        '</defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="10" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="10" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    # Traffic light dots
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*14}" cy="{TITLEBAR_H/2}" r="4.5" fill="{dotcol}"/>')

    parts.append(
        f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="11" text-anchor="middle">'
        f'xCodeWraith@github: ~/contributions --graph</text>'
    )

    grid_top = TITLEBAR_H + TOP_LABEL_H

    # Month headers
    for ci, label in month_labels:
        x = grid_left + ci * STEP
        parts.append(f'<text x="{x}" y="{TITLEBAR_H + 13}" fill="{MUTED}" font-size="10">{label}</text>')

    # Day labels
    for wi, wname in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + wi * STEP + CELL * 0.78
        parts.append(f'<text x="{grid_left - 24}" y="{y:.1f}" fill="{MUTED}" font-size="9">{wname}</text>')

    # Contribution cells
    for ci, column in enumerate(grid):
        gx = grid_left + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            gy = grid_top + ri * STEP
            delay = ci * COL_T + ri * ROW_T
            plural = "s" if count != 1 else ""
            fill_color = PALETTE[lvl] if lvl < len(PALETTE) else PALETTE[-1]
            parts.append(
                f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{fill_color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_s}: {count} contribution{plural}</title></rect>'
            )

    # Legend (Less [][][][][] More)
    leg_y = grid_top + art_h + 8
    leg_x = grid_left + art_w - (len(PALETTE) * (CELL - 1) + 65)
    parts.append(f'<text x="{leg_x}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    lx = leg_x + 8
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2" fill="{color}"/>')
        lx += CELL
    parts.append(f'<text x="{lx + 4}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')

    sep_y = leg_y + CELL + 12
    parts.append(f'<line x1="0" y1="{sep_y}" x2="{canvas_w}" y2="{sep_y}" stroke="{FRAME}" stroke-opacity="0.6"/>')

    cs = data.get("current_streak", {}).get("length", 0)
    ls = data.get("longest_streak", {}).get("length", 0)
    total = data.get("total_contributions", 0)
    best = data.get("best_day", {"count": 0, "date": "N/A"})
    rng = data.get("range", {"start": "2025", "end": "2026"})

    ly = sep_y + 22
    parts.append(
        f'<text x="{PAD}" y="{ly}" font-size="12.5" fill="{GREEN}">'
        f'<tspan font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_w - PAD}" y="{ly}" font-size="11.5" fill="{MUTED}" text-anchor="end">'
        f'{rng.get("start")} &#8594; {rng.get("end")}</text>'
    )

    ly += 20
    parts.append(
        f'<text x="{PAD}" y="{ly}" font-size="12" fill="{MUTED}">current streak '
        f'<tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan>'
        f'<tspan fill="{MUTED}">   &#183;   longest </tspan>'
        f'<tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_w - PAD}" y="{ly}" font-size="11.5" fill="{MUTED}" text-anchor="end">'
        f'best day <tspan fill="{GOLD}" font-weight="700">{best.get("count", 0)}</tspan> on {best.get("date", "N/A")}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)

def main():
    if not os.path.exists(IN_PATH):
        print(f"Error: {IN_PATH} not found. Run fetch_contributions.py first.", file=sys.stderr)
        sys.exit(1)

    with open(IN_PATH) as f:
        data = json.load(f)

    svg = render(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Successfully rendered {OUT_PATH} ({len(svg)} bytes)")

if __name__ == "__main__":
    main()
