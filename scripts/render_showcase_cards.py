#!/usr/bin/env python3
"""
scripts/render_showcase_cards.py
Renders 3 custom terminal-style project cards for xCodeWraith's top weapons:
  1. GoogleMapAIagent (382 ⭐)
  2. Crypto-Alpha-Scanner (48 ⭐)
  3. XCodeWraith-AI-Arbitrage-Hunter (Autonomous Trading & n8n)
Width: 280px each. (280 + 10 + 280 + 10 + 280 = 860px).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CARDS_DIR = os.path.join(ROOT, "cards")

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#c9d1d9"
TITLE = "#58a6ff"
GOLD = "#f2cc60"
GREEN = "#39d353"

PROJECTS = [
    {
        "filename": "repo-googlemap.svg",
        "title": "GoogleMapAIagent",
        "desc": "Autonomous Google Maps AI agent for automated lead gen & B2B data extraction.",
        "stars": "382 ⭐",
        "lang": "Python / n8n",
        "badge": "FEATURED WEAPON",
    },
    {
        "filename": "repo-crypto-scanner.svg",
        "title": "Crypto-Alpha-Scanner",
        "desc": "On-chain alpha scanner & real-time crypto anomaly detector with insider tools.",
        "stars": "48 ⭐",
        "lang": "Python / Web3",
        "badge": "ALPHA BOT",
    },
    {
        "filename": "repo-arbitrage.svg",
        "title": "AI-Arbitrage-Hunter",
        "desc": "Automated cross-market arbitrage detection & algorithmic trading pipelines.",
        "stars": "18 ⭐",
        "lang": "Python / Docker",
        "badge": "ARBITRAGE",
    },
]

def render_card(p):
    w, h = 280, 136
    css = """
@keyframes floatIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.card { animation: floatIn 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
""".strip()

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<style>{css}</style>
<defs>
  <linearGradient id="cbg_{p['filename']}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG2}"/>
    <stop offset="1" stop-color="{BG}"/>
  </linearGradient>
</defs>
<rect class="card" width="{w}" height="{h}" rx="8" fill="url(#cbg_{p['filename']})"/>
<rect class="card" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" fill="none" stroke="{FRAME}" stroke-width="1"/>

<!-- Top Bar -->
<circle cx="14" cy="16" r="3.5" fill="#ff5f56"/>
<circle cx="25" cy="16" r="3.5" fill="#ffbd2e"/>
<circle cx="36" cy="16" r="3.5" fill="#27c93f"/>
<text x="{w - 12}" y="19" font-size="9" fill="{GREEN}" text-anchor="end" font-weight="bold">[{p['badge']}]</text>

<!-- Title -->
<text x="14" y="44" font-size="13" font-weight="bold" fill="{TITLE}">{p['title']}</text>

<!-- Description (2 lines) -->
<text x="14" y="66" font-size="10.5" fill="{TEXT}">
  <tspan x="14" dy="0">{p['desc'][:40]}</tspan>
  <tspan x="14" dy="16">{p['desc'][40:80]}...</tspan>
</text>

<!-- Bottom info -->
<line x1="0" y1="106" x2="{w}" y2="106" stroke="{FRAME}" stroke-opacity="0.5"/>
<circle cx="18" cy="121" r="3.5" fill="{GREEN}"/>
<text x="28" y="124" font-size="10" fill="{MUTED}">{p['lang']}</text>
<text x="{w - 14}" y="124" font-size="10.5" font-weight="bold" fill="{GOLD}" text-anchor="end">{p['stars']}</text>
</svg>"""
    return svg

def main():
    os.makedirs(CARDS_DIR, exist_ok=True)
    for p in PROJECTS:
        path = os.path.join(CARDS_DIR, p["filename"])
        content = render_card(p)
        with open(path, "w") as f:
            f.write(content)
        print(f"Wrote {path}")

if __name__ == "__main__":
    main()
