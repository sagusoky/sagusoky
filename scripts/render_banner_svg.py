#!/usr/bin/env python3
"""
Generate an animated cyber-terminal hero banner SVG (terminal-header.svg).
Features:
- macOS terminal styling.
- Typing cursor and glowing title.
- Dynamic subtitle cycling or typewriter effect.
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "..", "terminal-header.svg")


def build_svg():
    width = 860
    height = 140

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
      }}
      @keyframes typeLine1 {{
        0% {{ width: 0; }}
        100% {{ width: 100%; }}
      }}
      @keyframes pulseGlow {{
        0%, 100% {{ filter: drop-shadow(0 0 4px rgba(88, 166, 255, 0.4)); }}
        50% {{ filter: drop-shadow(0 0 12px rgba(88, 166, 255, 0.8)); }}
      }}
      .banner-card {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1.2;
        rx: 12px;
      }}
      .banner-bar {{
        fill: #161b22;
      }}
      .term-title {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 12px;
        fill: #8b949e;
        font-weight: 500;
      }}
      .banner-hero {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 26px;
        font-weight: 800;
        fill: #58a6ff;
        animation: pulseGlow 4s infinite ease-in-out;
      }}
      .banner-sub {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 13.5px;
        fill: #7ee787;
        font-weight: 500;
      }}
      .banner-accent {{
        fill: #d2a8ff;
      }}
      .cursor {{
        animation: blink 0.9s infinite;
      }}
    </style>
  </defs>

  <!-- Window Container -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" class="banner-card" />

  <!-- Window Header -->
  <path d="M 1 13 Q 1 1 13 1 L {width - 13} 1 Q {width - 1} 1 {width - 1} 13 L {width - 1} 34 L 1 34 Z" class="banner-bar" />
  <line x1="1" y1="34" x2="{width - 1}" y2="34" stroke="#30363d" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="20" cy="18" r="5.5" fill="#ff5f56" />
  <circle cx="36" cy="18" r="5.5" fill="#ffbd2e" />
  <circle cx="52" cy="18" r="5.5" fill="#27c93f" />
  <text x="{width / 2}" y="22" text-anchor="middle" class="term-title">shloka@macbook-air: ~ (welcome.sh)</text>

  <!-- Hero Text -->
  <text x="36" y="74" class="banner-hero">Hi, I'm Shloka Shetty 👋</text>
  <rect x="360" y="54" width="10" height="24" fill="#58a6ff" class="cursor" />

  <!-- Subtitle Terminal Output -->
  <text x="36" y="106" class="banner-sub">
    ❯ Software Engineer · iOS Developer · Big Data &amp; AI Builder · <tspan class="banner-accent">Apple Swift '26 Distinguished Top 50 🏆</tspan>
  </text>
</svg>
"""
    return svg


def main():
    svg_content = build_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {OUT_PATH} ({len(svg_content)} bytes)")


if __name__ == "__main__":
    main()
