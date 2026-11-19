#!/usr/bin/env python3
"""
scripts/prep_photo.py
Prepares an input image (photo or avatar) for clean ASCII conversion:
  1. Removes background using rembg (u2netp session for fast, lightweight inference).
  2. Bilateral-smooths textures while keeping edges sharp.
  3. Stretches tones so highlights map to white (sparse ASCII characters / space).
  4. Darkens edge lines via Difference-of-Gaussians (DoG) filter so key facial/silhouette lines pop.
  5. Composites onto pure white and square-crops the subject.

Output: source-prepped.png (grayscale)
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
INP = sys.argv[1] if len(sys.argv) > 1 else "/Users/dev/Desktop/DEV.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "source-prepped.png")

LINE_WEIGHT = 0.65

def main():
    if not os.path.exists(INP):
        print(f"Error: Input file {INP} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {INP}...")
    orig = Image.open(INP).convert("RGBA")

    print("Removing background with rembg (u2netp)...")
    session = new_session("u2netp")
    cut = remove(orig, session=session)

    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    print("Applying bilateral smoothing and edge enhancement...")
    smooth = gray
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

    # Tone stretch over subject area only
    subject_mask = alpha > 120
    if subject_mask.sum() > 0:
        lo, hi = np.percentile(smooth[subject_mask], [2, 92])
        tone = np.clip((smooth.astype(np.float32) - lo) / max(hi - lo, 1e-5), 0, 1)
    else:
        tone = smooth.astype(np.float32) / 255.0

    # Difference of Gaussians (DoG) edge sharpening
    fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 6.0).astype(np.float32)
    lines = np.clip((coarse - fine) / 40.0, 0, 1)
    out_img = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255.0

    # Feather alpha mask slightly and composite onto pure white
    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    out_img = out_img * mask + 255.0 * (1.0 - mask)

    # Square crop around subject with clean margins
    ys, xs = np.where(alpha > 20)
    if len(xs) > 0 and len(ys) > 0:
        side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
        cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
        canvas = np.full((side, side), 255, np.uint8)
        x0, y0 = cx - side // 2, cy - side // 2
        sx0, sy0 = max(x0, 0), max(y0, 0)
        sx1, sy1 = min(x0 + side, out_img.shape[1]), min(y0 + side, out_img.shape[0])
        canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out_img[sy0:sy1, sx0:sx1].astype(np.uint8)
    else:
        canvas = out_img.astype(np.uint8)

    Image.fromarray(canvas, mode="L").save(OUT)
    print(f"Successfully wrote prepped image: {OUT} ({canvas.shape[1]}x{canvas.shape[0]})")

if __name__ == "__main__":
    main()
