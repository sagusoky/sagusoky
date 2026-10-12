#!/usr/bin/env python3
"""
Preprocess a source photo or avatar for clean ASCII art generation.
- Converts to grayscale
- Auto-contrasts / normalizes dynamic range
- Sharpens edge details
- Writes source-prepped.png
Usage:
  python scripts/prep_photo.py [optional_path_to_photo]
"""
import os
import sys
from PIL import Image, ImageEnhance, ImageOps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DEFAULT_INPUT = os.path.join(PROJECT_ROOT, "avatar.png")
OUT_PATH = os.path.join(PROJECT_ROOT, "source-prepped.png")


def prep_image(input_path):
    if not os.path.exists(input_path):
        print(f"Error: input image '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Opening image: {input_path}")
    img = Image.open(input_path).convert("RGBA")

    # If image has transparency, composite over solid background
    # (black or white depending on source)
    bg = Image.new("RGBA", img.size, (20, 20, 20, 255))
    composite = Image.alpha_composite(bg, img).convert("L")

    # Boost contrast and equalize
    equalized = ImageOps.autocontrast(composite, cutoff=2)
    enhancer = ImageEnhance.Contrast(equalized)
    boosted = enhancer.enhance(1.8)

    # Mild sharpness boost
    sharp = ImageEnhance.Sharpness(boosted).enhance(1.5)

    sharp.save(OUT_PATH)
    print(f"Successfully wrote preprocessed image to: {OUT_PATH}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    prep_image(target)


if __name__ == "__main__":
    main()
