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

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SOURCE_PHOTO = os.path.join(PROJECT_ROOT, "source-photo.png")
DEFAULT_INPUT = SOURCE_PHOTO if os.path.exists(SOURCE_PHOTO) else os.path.join(PROJECT_ROOT, "avatar.png")
OUT_PATH = os.path.join(PROJECT_ROOT, "source-prepped.png")


def prep_image(input_path):
    if not os.path.exists(input_path):
        print(f"Error: input image '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing image: {input_path}")
    try:
        import cv2
        import numpy as np
        img = cv2.imread(input_path)
        h, w = img.shape[:2]

        # If it's a selfie landscape/wide (like 1024x768), crop around subject (face & phone)
        if w > h:
            crop_x1 = int(w * 0.05)
            crop_x2 = int(w * 0.76)
            img = img[:, crop_x1:crop_x2]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered = cv2.bilateralFilter(gray, 7, 50, 50)
        clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(filtered)
        cv2.imwrite(OUT_PATH, enhanced)
        print(f"Successfully wrote CLAHE enhanced image to: {OUT_PATH}")
    except Exception as e:
        print(f"OpenCV processing fallback to PIL: {e}")
        from PIL import Image, ImageEnhance, ImageOps
        img = Image.open(input_path).convert("L")
        w, h = img.size
        if w > h:
            img = img.crop((int(w * 0.05), 0, int(w * 0.76), h))
        equalized = ImageOps.autocontrast(img, cutoff=2)
        enhancer = ImageEnhance.Contrast(equalized)
        boosted = enhancer.enhance(1.8)
        sharp = ImageEnhance.Sharpness(boosted).enhance(1.5)
        sharp.save(OUT_PATH)
        print(f"Successfully wrote PIL enhanced image to: {OUT_PATH}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    prep_image(target)


if __name__ == "__main__":
    main()
