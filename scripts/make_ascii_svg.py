#!/usr/bin/env python3
"""
Convert preprocessed photo/avatar into an animated self-typing SVG (shloka-ascii.svg).
Features:
- Downsamples image to character grid preserving aspect ratio.
- Density ramp mapping with high contrast monochrome aesthetic.
- Staggered line typing animation (pure SVG CSS keyframes, plays once and freezes).
- Terminal window layout with macOS window controls matching info-card.svg.
"""
import html
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SOURCE_PREPPED = os.path.join(PROJECT_ROOT, "source-prepped.png")
SOURCE_RAW = os.path.join(PROJECT_ROOT, "avatar.png")
OUT_PATH = os.path.join(PROJECT_ROOT, "shloka-ascii.svg")

# Density ramp: sparse (blank/dark background) to dense (bright highlights)
RAMP = "   ..::-=+*cs#%@"


def get_image():
    from PIL import Image, ImageOps
    if os.path.exists(SOURCE_PREPPED):
        return Image.open(SOURCE_PREPPED).convert("L")
    elif os.path.exists(SOURCE_RAW):
        import subprocess
        prep_script = os.path.join(SCRIPT_DIR, "prep_photo.py")
        subprocess.run([sys.executable, prep_script, SOURCE_RAW], check=True)
        return Image.open(SOURCE_PREPPED).convert("L")
    else:
        print("Error: No source image found.", file=sys.stderr)
        sys.exit(1)


def generate_ascii_grid(img, cols=62, rows=34):
    from PIL import Image, ImageOps

    # Detect bounding box to focus on the emblem/subject
    bbox = img.getbbox()
    if bbox:
        # Add slight margin
        w, h = img.size
        pad_x = int((bbox[2] - bbox[0]) * 0.05)
        pad_y = int((bbox[3] - bbox[1]) * 0.05)
        x0 = max(0, bbox[0] - pad_x)
        y0 = max(0, bbox[1] - pad_y)
        x1 = min(w, bbox[2] + pad_x)
        y1 = min(h, bbox[3] + pad_y)
        cropped = img.crop((x0, y0, x1, y1))
    else:
        cropped = img

    resized = cropped.resize((cols, rows), Image.Resampling.LANCZOS)

    # Determine if background is dark or light
    corner_pixels = [
        resized.getpixel((0, 0)),
        resized.getpixel((cols - 1, 0)),
        resized.getpixel((0, rows - 1)),
        resized.getpixel((cols - 1, rows - 1)),
    ]
    avg_corner = sum(corner_pixels) / len(corner_pixels)
    is_dark_bg = avg_corner < 128

    grid = []
    ramp_len = len(RAMP)
    for y in range(rows):
        line_chars = []
        for x in range(cols):
            val = resized.getpixel((x, y))
            # If dark bg, bright is dense; if light bg, dark is dense
            score = val if is_dark_bg else (255 - val)
            idx = int(score / 256.0 * ramp_len)
            idx = max(0, min(ramp_len - 1, idx))
            line_chars.append(RAMP[idx])
        grid.append("".join(line_chars))

    return grid


def render_svg(grid):
    width = 540
    height = 570

    line_start_y = 96
    line_spacing = 12.2
    char_size = 10.2

    row_elements = []
    for idx, row in enumerate(grid):
        delay = round(0.045 * (idx + 1), 3)
        y_pos = line_start_y + idx * line_spacing
        escaped_row = html.escape(row)
        # Wrap each line with staggered reveal
        el = (
            f'<g class="ascii-line" style="animation-delay: {delay}s;">'
            f'<text x="24" y="{y_pos:.1f}" class="ascii-text">{escaped_row}</text>'
            f'</g>'
        )
        row_elements.append(el)

    cursor_delay = round(0.045 * (len(grid) + 1), 3)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      @keyframes rowReveal {{
        0% {{
          opacity: 0;
          transform: translateY(-2px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
      @keyframes cursorBlink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
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
      .prompt-text {{
        font-family: "SF Mono", "Fira Code", Menlo, Monaco, Consolas, monospace;
        font-size: 12px;
        fill: #58a6ff;
        font-weight: 600;
      }}
      .prompt-cmd {{
        fill: #7ee787;
        font-weight: 400;
      }}
      .ascii-text {{
        font-family: "SF Mono", "Fira Code", "Courier New", monospace;
        font-size: {char_size}px;
        fill: #79c0ff;
        letter-spacing: 0px;
        white-space: pre;
      }}
      .ascii-line {{
        opacity: 0;
        animation: rowReveal 0.05s ease-out forwards;
      }}
      .status-text {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
        font-size: 10.5px;
        fill: #8b949e;
      }}
      .cursor-blink {{
        animation: cursorBlink 1s infinite;
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
  <text x="{width / 2}" y="23" text-anchor="middle" class="term-heading">shloka@macbook-air: ~ (ascii-portrait)</text>

  <!-- Prompt Command -->
  <text x="24" y="62" class="prompt-text">shloka@github:~$ <tspan class="prompt-cmd">./render_ascii.sh --animate</tspan></text>

  <!-- Animated ASCII Art Rows -->
  {''.join(row_elements)}

  <!-- Footer Status Bar -->
  <g transform="translate(24, {height - 18})">
    <circle cx="4" cy="-4" r="3" fill="#39d353" />
    <text x="14" y="0" class="status-text">MONOCHROME VECTOR ART · AUTO-TYPING ENGINE</text>
    <rect x="{width - 60}" y="-10" width="8" height="12" fill="#58a6ff" class="cursor-blink" />
  </g>
</svg>
"""
    return svg


def main():
    img = get_image()
    grid = generate_ascii_grid(img)
    svg_content = render_svg(grid)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {OUT_PATH} ({len(svg_content)} bytes)")


if __name__ == "__main__":
    main()
