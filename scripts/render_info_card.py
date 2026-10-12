#!/usr/bin/env python3
"""
Generate an animated neofetch-style info card SVG (info-card.svg) for Shloka Shetty (@sagusoky).
Features:
- macOS Terminal window bar with colored dots.
- Staggered line-by-line slide-in & fade-in animation (CSS keyframes).
- Content grounded in Shloka's real resume, achievements, and tech stack.
- Terminal ANSI color blocks footer.
- Static mode supported via STATIC=1 env var for headless previews.
"""
import html
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "..", "info-card.svg")
IS_STATIC = os.environ.get("STATIC", "0") == "1"


def esc(s):
    return html.escape(s, quote=True)


def build_svg():
    width = 540
    height = 570

    # Line items: (Icon/Label, Value, Label Color, Value Color)
    lines = [
        ("user", "shloka@mit-wpu", "#58a6ff", "#58a6ff"),
        ("separator", "─────────────────────────────────────────────────", "#30363d", "#30363d"),
        ("OS", "macOS Sonoma (Darwin arm64)", "#bc8cff", "#c9d1d9"),
        ("Host", "MacBook Air (Apple Silicon)", "#bc8cff", "#c9d1d9"),
        ("Role", "Software Engineer · iOS Dev · AI & Data Builder", "#3fb950", "#f0f6fc"),
        ("Education", "B.Tech CSE @ MIT World Peace Univ (8.82 CGPA)", "#e3b341", "#c9d1d9"),
        ("🏆 Honors", "Apple Swift Challenge '26 Distinguished Top 50", "#f0883e", "#58a6ff"),
        ("🏛️ Key Event", "Invited to Apple Park, Cupertino · ZS Top 100", "#f0883e", "#c9d1d9"),
        ("Experience", "Omnevu Systems (App & Risk) · Infosys (Retail)", "#58a6ff", "#c9d1d9"),
        ("⚡ Big Data", "Zomato AI Pipeline (33M+ rows, Snowflake, dbt)", "#3fb950", "#7ee787"),
        ("📊 Analytics", "PharmaPulse (2.1k+ sales records, Tableau, SQL)", "#3fb950", "#7ee787"),
        ("Stack", "Python · Swift · Snowflake · dbt · Airflow · C++", "#ff7b72", "#c9d1d9"),
        ("Tools", "Figma · Adobe Suite · Jira · Git · Docker · Linux", "#ff7b72", "#c9d1d9"),
        ("Currently", "Building Storeasy (iOS) · LLM Decision Analytics", "#79c0ff", "#f0f6fc"),
        ("Vibe", "Powered by coffee & pizza ☕🍕 · \"a geek\"", "#d2a8ff", "#e6edf3"),
    ]

    rendered_lines = []
    line_start_y = 72
    line_height = 27

    for idx, (label, val, l_color, v_color) in enumerate(lines):
        y = line_start_y + idx * line_height
        delay = round(0.08 * (idx + 1), 3) if not IS_STATIC else 0
        anim_attr = f'style="animation-delay: {delay}s;"' if not IS_STATIC else ''

        if label == "user":
            line_content = f'<text x="32" y="{y}" class="code-title">{esc(val)}</text>'
        elif label == "separator":
            line_content = f'<text x="32" y="{y}" class="code-sep">{esc(val)}</text>'
        else:
            line_content = (
                f'<text x="32" y="{y}" class="code-label" fill="{l_color}">{esc(label)}: '
                f'<tspan fill="{v_color}" font-weight="400">{esc(val)}</tspan></text>'
            )

        rendered_lines.append(f'<g class="term-line" {anim_attr}>{line_content}</g>')

    # ANSI color palette dots/bars at bottom
    ansi_colors_1 = ["#0d1117", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4"]
    ansi_colors_2 = ["#484f58", "#ffa198", "#56d364", "#e3b341", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"]

    palette_y = height - 42
    swatch_w = 26
    swatch_h = 10
    swatch_gap = 5
    start_swatch_x = 32

    swatches_1 = []
    swatches_2 = []
    for i in range(8):
        sx = start_swatch_x + i * (swatch_w + swatch_gap)
        swatches_1.append(f'<rect x="{sx}" y="{palette_y}" width="{swatch_w}" height="{swatch_h}" rx="2.5" fill="{ansi_colors_1[i]}" />')
        swatches_2.append(f'<rect x="{sx}" y="{palette_y + 14}" width="{swatch_w}" height="{swatch_h}" rx="2.5" fill="{ansi_colors_2[i]}" />')

    palette_delay = round(0.08 * (len(lines) + 2), 3) if not IS_STATIC else 0
    anim_palette_attr = f'style="animation-delay: {palette_delay}s;"' if not IS_STATIC else ''

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      @keyframes lineFadeIn {{
        0% {{
          opacity: 0;
          transform: translateX(-14px);
        }}
        100% {{
          opacity: 1;
          transform: translateX(0);
        }}
      }}
      .term-card {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1.2;
        rx: 12px;
      }}
      .term-topbar {{
        fill: #161b22;
      }}
      .term-heading {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 12px;
        fill: #8b949e;
        font-weight: 500;
      }}
      .code-title {{
        font-family: "SF Mono", "Fira Code", Menlo, Monaco, Consolas, monospace;
        font-size: 15px;
        fill: #58a6ff;
        font-weight: 700;
        letter-spacing: 0.5px;
      }}
      .code-sep {{
        font-family: "SF Mono", "Fira Code", Menlo, monospace;
        font-size: 11px;
        fill: #30363d;
      }}
      .code-label {{
        font-family: "SF Mono", "Fira Code", Menlo, Monaco, Consolas, monospace;
        font-size: 12.5px;
        font-weight: 600;
      }}
      .term-line {{
        opacity: {"1" if IS_STATIC else "0"};
        animation: {"none" if IS_STATIC else "lineFadeIn 0.35s ease-out forwards"};
      }}
      .term-palette {{
        opacity: {"1" if IS_STATIC else "0"};
        animation: {"none" if IS_STATIC else "lineFadeIn 0.35s ease-out forwards"};
      }}
    </style>
  </defs>

  <!-- Card Background -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" class="term-card" />

  <!-- Window Header -->
  <path d="M 1 13 Q 1 1 13 1 L {width - 13} 1 Q {width - 1} 1 {width - 1} 13 L {width - 1} 36 L 1 36 Z" class="term-topbar" />
  <line x1="1" y1="36" x2="{width - 1}" y2="36" stroke="#30363d" stroke-width="1" />

  <!-- Window Buttons -->
  <circle cx="20" cy="19" r="5.5" fill="#ff5f56" />
  <circle cx="36" cy="19" r="5.5" fill="#ffbd2e" />
  <circle cx="52" cy="19" r="5.5" fill="#27c93f" />

  <!-- Terminal Window Title -->
  <text x="{width / 2}" y="23" text-anchor="middle" class="term-heading">shloka@macbook-air: ~ (fastfetch)</text>

  <!-- Output Lines -->
  {''.join(rendered_lines)}

  <!-- Terminal Color Blocks -->
  <g class="term-palette" {anim_palette_attr}>
    {''.join(swatches_1)}
    {''.join(swatches_2)}
  </g>
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
