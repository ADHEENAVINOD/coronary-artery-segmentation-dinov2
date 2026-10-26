"""
Quick inspection of your training data.
Run this to understand what you have before training.
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

Image.MAX_IMAGE_PIXELS = None

BASE = Path(__file__).resolve().parent
IMAGES_DIR = BASE / "output" / "coronary-data-2" / "train_data" / "images"
LABELS_DIR = BASE / "output" / "coronary-data-2" / "train_data" / "labels"

print("=" * 60)
print("DATASET INSPECTION")
print("=" * 60)

# Find all samples
image_files = sorted(IMAGES_DIR.glob("*.png"))
print(f"\nFound {len(image_files)} training samples\n")

# Analyze each
for img_path in image_files:
    name = img_path.stem
    label_path = LABELS_DIR / f"{name}.npy"
    
    if not label_path.exists():
        print(f"[!] {name}: Missing label file")
        continue
    
    # Load
    img = Image.open(img_path)
    label = np.load(label_path)
    
    # Stats
    classes, counts = np.unique(label, return_counts=True)
    total_pixels = label.size
    
    print(f"[DATA] {name}")
    print(f"   Image size: {img.size[0]} × {img.size[1]} = {img.size[0] * img.size[1]:,} pixels")
    print(f"   Label shape: {label.shape}")
    print(f"   Classes found: {classes.tolist()}")
    print(f"   Class distribution:")
    
    class_names = {0: "Background", 1: "Media", 2: "Intima", 3: "Lumen"}
    for c, count in zip(classes, counts):
        pct = 100 * count / total_pixels
        print(f"      {c} ({class_names.get(c, 'Unknown'):10s}): {count:12,} pixels ({pct:5.2f}%)")
    print()

print("=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)
print()

if len(image_files) < 10:
    print("[WARNING] You have very few samples (< 10).")
    print("   Consider:")
    print("   1. Process more slides from data/coronary-data-2/")
    print("   2. Use data augmentation during training")
    print("   3. Start with simple linear head (less overfitting)")
    print()

print("[OK] Data looks good! Next steps:")
print("   1. Read topology papers (see PROJECT_SUMMARY.md)")
print("   2. Train baseline: python scripts/train_segmentation.py \\")
print("      --image_dir output/coronary-data-2/train_data/images \\")
print("      --label_dir output/coronary-data-2/train_data/labels \\")
print("      --batch_size 1 \\")
print("      --epochs 20")
print()
print("   3. After baseline works, add topology constraints")
print()
