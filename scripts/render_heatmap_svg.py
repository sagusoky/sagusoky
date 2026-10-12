#!/usr/bin/env python3
"""
Render data/contributions.json as an animated, terminal-themed SVG (contrib-heatmap.svg).
Features:
- 53-week x 7-day contribution grid with rounded cells.
- Diagonal cascading entrance animation (CSS keyframes, plays once and freezes).
- Terminal window title bar with colored dots.
- Month header and weekday labels.
- Live stats footer: total contributions, current & longest streak, best day, and legend.
"""
import datetime
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "contributions.json")
OUT_PATH = os.path.join(SCRIPT_DIR, "..", "contrib-heatmap.svg")

# GitHub dark theme green palette (0 to 5)
PALETTE = [
    "#161b22",  # 0: None
    "#0e4429",  # 1: Low
    "#006d32",  # 2: Medium
    "#26a641",  # 3: High
    "#39d353",  # 4: Very High
    "#69f0a0",  # 5: Peak neon
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"Data file not found at {DATA_PATH}. Please run fetch_contributions.py first.", file=sys.stderr)
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_color(count, level):
    if count == 0:
        return PALETTE[0]
    if level >= 4:
        return PALETTE[5] if count >= 20 else PALETTE[4]
    if level == 3:
        return PALETTE[3]
    if level == 2:
        return PALETTE[2]
    return PALETTE[1]


def render_svg(data):
    days = data.get("days", [])
    if not days:
        return ""

    total = data.get("total_contributions", 0)
    cur_streak = data.get("current_streak", {}).get("length", 0)
    long_streak = data.get("longest_streak", {}).get("length", 0)
    best_day = data.get("best_day", {})
    username = data.get("username", "sagusoky")

    # Layout constants
    width = 860
    height = 220
    cell_size = 11
    cell_gap = 3.2
    step = cell_size + cell_gap

    start_x = 42
    start_y = 66

    # Organize days into columns (weeks)
    # Parse first day to find day-of-week (0=Sunday in GitHub calendar convention)
    first_date_str = days[0]["date"]
    first_dt = datetime.datetime.strptime(first_date_str, "%Y-%m-%d")
    # Python weekday(): Monday is 0, Sunday is 6. In GitHub, Sunday is 0.
    first_dow = (first_dt.weekday() + 1) % 7

    # Group into weeks
    weeks = []
    current_week = [None] * first_dow

    month_labels = []
    last_month = None

    for d in days:
        dt = datetime.datetime.strptime(d["date"], "%Y-%m-%d")
        if dt.month != last_month and len(current_week) == 0:
            month_labels.append((len(weeks), MONTH_NAMES[dt.month - 1]))
            last_month = dt.month
        elif dt.month != last_month and last_month is None:
            month_labels.append((0, MONTH_NAMES[dt.month - 1]))
            last_month = dt.month

        current_week.append(d)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []

    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    # Build cell elements
    cells_svg = []
    for col_idx, week in enumerate(weeks):
        for row_idx, day_info in enumerate(week):
            if not day_info:
                continue
            cx = start_x + col_idx * step
            cy = start_y + row_idx * step
            count = day_info.get("count", 0)
            level = day_info.get("level", 0)
            color = get_color(count, level)
            delay = round((col_idx * 1.1 + row_idx * 0.8) * 0.007, 3)
            date_str = day_info.get("date", "")

            cell_el = (
                f'<rect class="cell" x="{cx:.1f}" y="{cy:.1f}" width="{cell_size}" height="{cell_size}" '
                f'rx="2.5" fill="{color}" style="animation-delay: {delay}s;" '
                f'data-date="{date_str}" data-count="{count}">'
                f'<title>{date_str}: {count} contributions</title>'
                f'</rect>'
            )
            cells_svg.append(cell_el)

    # Build month labels
    month_svg = []
    for col, m_name in month_labels:
        mx = start_x + col * step
        month_svg.append(f'<text x="{mx:.1f}" y="{start_y - 8}" class="cal-label">{m_name}</text>')

    # Build weekday labels (Mon, Wed, Fri)
    weekday_svg = []
    for row, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        wy = start_y + row * step + 9
        weekday_svg.append(f'<text x="{start_x - 10}" y="{wy:.1f}" text-anchor="end" class="cal-label">{name}</text>')

    # Legend at bottom right
    legend_start_x = width - 150
    legend_y = height - 22
    legend_svg = [
        f'<text x="{legend_start_x - 8}" y="{legend_y + 8}" text-anchor="end" class="cal-legend-label">Less</text>'
    ]
    for idx, c in enumerate(PALETTE):
        lx = legend_start_x + idx * (cell_size + 3)
        legend_svg.append(
            f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{c}"/>'
        )
    legend_svg.append(
        f'<text x="{legend_start_x + len(PALETTE) * (cell_size + 3) + 6}" y="{legend_y + 8}" class="cal-legend-label">More</text>'
    )

    best_count = best_day.get("count", 0)
    best_date = best_day.get("date", "N/A")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      @keyframes cellFade {{
        0% {{
          opacity: 0;
          transform: scale(0.2);
        }}
        70% {{
          opacity: 0.9;
          transform: scale(1.1);
        }}
        100% {{
          opacity: 1;
          transform: scale(1);
        }}
      }}
      @keyframes termGlow {{
        0%, 100% {{ opacity: 0.8; }}
        50% {{ opacity: 1; }}
      }}
      .terminal-bg {{
        fill: #0d1117;
        stroke: #30363d;
        stroke-width: 1.2;
        rx: 12px;
      }}
      .term-header {{
        fill: #161b22;
      }}
      .term-title {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 12px;
        fill: #8b949e;
        font-weight: 500;
      }}
      .cal-label {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 10px;
        fill: #7d8590;
      }}
      .cal-legend-label {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 10px;
        fill: #7d8590;
      }}
      .stats-text {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 11px;
        fill: #c9d1d9;
      }}
      .stats-highlight {{
        fill: #39d353;
        font-weight: 600;
      }}
      .stats-sub {{
        fill: #8b949e;
      }}
      .cell {{
        transform-origin: center;
        transform-box: fill-box;
        animation: cellFade 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      }}
    </style>
  </defs>

  <!-- Background Card -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" class="terminal-bg" />

  <!-- Window Header Bar -->
  <path d="M 1 13 Q 1 1 13 1 L {width - 13} 1 Q {width - 1} 1 {width - 1} 13 L {width - 1} 34 L 1 34 Z" class="term-header" />
  <line x1="1" y1="34" x2="{width - 1}" y2="34" stroke="#30363d" stroke-width="1" />

  <!-- macOS Window Dots -->
  <circle cx="20" cy="18" r="5.5" fill="#ff5f56" />
  <circle cx="36" cy="18" r="5.5" fill="#ffbd2e" />
  <circle cx="52" cy="18" r="5.5" fill="#27c93f" />

  <!-- Terminal Title -->
  <text x="{width / 2}" y="22" text-anchor="middle" class="term-title">⚡ {username}@github: ~/contributions.sh</text>

  <!-- Months -->
  {''.join(month_svg)}

  <!-- Weekdays -->
  {''.join(weekday_svg)}

  <!-- Heatmap Grid Cells -->
  {''.join(cells_svg)}

  <!-- Stats Footer -->
  <g transform="translate(42, {height - 18})">
    <text class="stats-text" y="0">
      <tspan class="stats-highlight">{total:,}</tspan><tspan class="stats-sub"> contributions in last year  ·  Streak: </tspan><tspan class="stats-highlight">{cur_streak}d</tspan><tspan class="stats-sub"> (max: {long_streak}d)  ·  Peak: </tspan><tspan class="stats-highlight">{best_count}</tspan><tspan class="stats-sub"> on {best_date}</tspan>
    </text>
  </g>

  <!-- Legend -->
  {''.join(legend_svg)}
</svg>
"""
    return svg


def main():
    data = load_data()
    svg_content = render_svg(data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {OUT_PATH} ({len(svg_content)} bytes)")


if __name__ == "__main__":
    main()
