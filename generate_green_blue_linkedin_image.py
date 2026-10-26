# -*- coding: utf-8 -*-
"""
Generate a clean Green & Blue LinkedIn Infographic with small embedded thumbnail images.
Removes:
  - "Master Thesis Research"
  - "Healthcare AI"
  - "Adheena Vinod"
  - "University of Verona"
Color scheme: Clean Green and Blue.
"""

import os
import shutil
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Aesthetics
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans', 'Calibri']
plt.rcParams['font.family'] = 'sans-serif'

# 16:9 Canvas (19.2 x 10.8 inches, 200 DPI = 3840 x 2160 ultra HD crisp)
fig = plt.figure(figsize=(19.2, 10.8), dpi=200)
ax = fig.add_subplot(111)
ax.set_xlim(0, 19.2)
ax.set_ylim(0, 10.8)
ax.axis('off')

# Background: Crisp off-white / light slate
BG_COLOR = '#F8FAFC'
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# -----------------------------------------------------------------------------
# 1. TOP HEADER BANNER (Deep Navy & Forest Green gradient feel)
# -----------------------------------------------------------------------------
header_bg = FancyBboxPatch((0.8, 9.0), 17.6, 1.4,
                           boxstyle="round,pad=0.08,rounding_size=0.18",
                           facecolor='#064E3B', edgecolor='#047857', linewidth=2.0, zorder=1)
ax.add_patch(header_bg)

# Decorative subtle accent line
accent_line = FancyBboxPatch((0.8, 8.95), 17.6, 0.08,
                            boxstyle="round,pad=0.02,rounding_size=0.04",
                            facecolor='#10B981', edgecolor='none', zorder=2)
ax.add_patch(accent_line)

# Title & Subtitle (No names, no university, no thesis tags)
ax.text(9.6, 9.90, "Topology-Aware Deep Learning for Coronary Artery Segmentation",
        ha='center', va='center', fontsize=22, fontweight='bold', color='#FFFFFF', zorder=3)

ax.text(9.6, 9.38, "End-to-End Pipeline: Frozen DINOv2 Vision Backbone + Differentiable clDice Loss for Objective Stenosis Profiling",
        ha='center', va='center', fontsize=12.5, color='#A7F3D0', zorder=3)


# -----------------------------------------------------------------------------
# 2. LOAD & RESIZE THUMBNAIL IMAGES
# -----------------------------------------------------------------------------
ppt_dir = r"d:\Project topics\dinov3-main\ppt_images"

def get_thumbnail(filename, crop_box=None, target_size=(320, 180)):
    p = os.path.join(ppt_dir, filename)
    if os.path.exists(p):
        try:
            im = Image.open(p).convert("RGB")
            if crop_box:
                im = im.crop(crop_box)
            im.thumbnail(target_size, Image.Resampling.LANCZOS)
            return im
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    # Return placeholder
    return Image.new("RGB", target_size, (230, 240, 250))

# 1. Histology Thumbnail
thumb_1 = get_thumbnail("Slide_3_Coronary_Artery_Histology.png", target_size=(320, 170))

# 2. DINOv2 Feature Extraction Thumbnail
thumb_2 = get_thumbnail("Slide_7_DINOv2_Feature_Extraction.png", target_size=(320, 170))

# 3. Decoder Architecture Thumbnail
thumb_3 = get_thumbnail("Slide_8_Decoder_Architecture.png", target_size=(320, 170))

# 4. clDice Skeletonization Thumbnail
thumb_4 = get_thumbnail("Slide_9_clDice_Skeletonization.png", target_size=(320, 170))

# 5. Final Prediction Overlay Thumbnail (crop center region)
im_pred = Image.open(os.path.join(ppt_dir, "Slide_15_Final_Results_Prediction.png")).convert("RGB")
W_p, H_p = im_pred.size
# crop central area of prediction
thumb_5 = im_pred.crop((int(W_p * 0.05), int(H_p * 0.05), int(W_p * 0.95), int(H_p * 0.95)))
thumb_5.thumbnail((320, 170), Image.Resampling.LANCZOS)


# -----------------------------------------------------------------------------
# 3. 5 PIPELINE STAGE CARDS (Green & Blue Alternating Theme)
# -----------------------------------------------------------------------------
card_w = 3.16
card_h = 5.50
card_y = 2.80
gap = 0.45
start_x = 0.82

stages = [
    {
        "num": "01",
        "tag": "INPUT DATA",
        "title": "Whole-Slide\nAutopsy WSIs",
        "theme": "blue",
        "badge_bg": "#1D4ED8",
        "border": "#BFDBFE",
        "accent": "#2563EB",
        "thumb": thumb_1,
        "points": [
            ("Clinical Source", "High-res autopsy scans (40×)"),
            ("Tissue Stains", "H&E + Movat's Pentachrome"),
            ("Annotations", "QuPath multi-layer polygons"),
            ("Caching", "Offline .npy cache (<100MB)")
        ]
    },
    {
        "num": "02",
        "tag": "BACKBONE",
        "title": "Frozen DINOv2\nViT Encoder",
        "theme": "green",
        "badge_bg": "#059669",
        "border": "#A7F3D0",
        "accent": "#059669",
        "thumb": thumb_2,
        "points": [
            ("Model", "Pre-trained ViT-S/14"),
            ("Frozen Weights", "Eliminates cohort overfitting"),
            ("Dense Tokens", "384-d semantic embeddings"),
            ("Self-Supervised", "Captures histological boundaries")
        ]
    },
    {
        "num": "03",
        "tag": "DECODER",
        "title": "3-Stage Conv\nUpsampler",
        "theme": "blue",
        "badge_bg": "#1D4ED8",
        "border": "#BFDBFE",
        "accent": "#2563EB",
        "thumb": thumb_3,
        "points": [
            ("Spatial Reshape", "1D token sequence → 2D grid"),
            ("Convolution", "256 → 128 → 64 → 4 classes"),
            ("Normalization", "Batch Normalization + ReLU"),
            ("Interpolation", "Bilinear upsampling to full-res")
        ]
    },
    {
        "num": "04",
        "tag": "TOPOLOGY LOSS",
        "title": "Differentiable\nclDice Supervision",
        "theme": "green",
        "badge_bg": "#059669",
        "border": "#A7F3D0",
        "accent": "#059669",
        "thumb": thumb_4,
        "points": [
            ("Loss Function", "L_total = L_CE + 0.5 × L_clDice"),
            ("Skeletonization", "Differentiable centerline operator"),
            ("Geometry", "Enforces continuous vessel loop"),
            ("Integrity", "Penalizes broken arterial gaps")
        ]
    },
    {
        "num": "05",
        "tag": "CLINICAL METRIC",
        "title": "Automated Stenosis\nQuantification",
        "theme": "blue",
        "badge_bg": "#1D4ED8",
        "border": "#BFDBFE",
        "accent": "#2563EB",
        "thumb": thumb_5,
        "points": [
            ("Target Layers", "Lumen, Intima, Media classes"),
            ("Area Profiling", "[1 - Area(L) / Area(M)] × 100"),
            ("Clinical Cutoff", "> 75% critical stenosis criterion"),
            ("Objective", "Zero inter-observer subjectivity")
        ]
    }
]

for i, stg in enumerate(stages):
    cx = start_x + i * (card_w + gap)
    
    # Shadow
    card_shadow = FancyBboxPatch((cx + 0.05, card_y - 0.05), card_w, card_h,
                                 boxstyle="round,pad=0.08,rounding_size=0.18",
                                 facecolor='#E2E8F0', edgecolor='none', zorder=1)
    ax.add_patch(card_shadow)
    
    # Main Card
    card = FancyBboxPatch((cx, card_y), card_w, card_h,
                          boxstyle="round,pad=0.08,rounding_size=0.18",
                          facecolor='#FFFFFF', edgecolor=stg["border"], linewidth=2.0, zorder=2)
    ax.add_patch(card)
    
    # Header Pill Badge
    badge_circle = FancyBboxPatch((cx + 0.16, card_y + card_h - 0.55), 0.44, 0.44,
                                  boxstyle="round,pad=0.04,rounding_size=0.22",
                                  facecolor=stg["badge_bg"], edgecolor='none', zorder=3)
    ax.add_patch(badge_circle)
    ax.text(cx + 0.38, card_y + card_h - 0.33, stg["num"],
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#FFFFFF', zorder=4)
    
    # Tag
    ax.text(cx + 0.72, card_y + card_h - 0.33, stg["tag"],
            ha='left', va='center', fontsize=8.5, fontweight='bold', color=stg["accent"], zorder=4)
    
    # Title
    ax.text(cx + 0.18, card_y + card_h - 1.15, stg["title"],
            ha='left', va='center', fontsize=13, fontweight='bold', color='#0F172A', linespacing=1.2, zorder=4)
    
    # Small Embedded Image Thumbnail (Inside card)
    im_box = OffsetImage(stg["thumb"], zoom=0.55)
    ab = AnnotationBbox(im_box, (cx + card_w / 2.0, card_y + card_h - 2.25),
                        frameon=True,
                        bboxprops=dict(edgecolor=stg["border"], facecolor='#F8FAFC', linewidth=1.2, boxstyle="round,pad=0.04"),
                        zorder=4)
    ax.add_artist(ab)
    
    # Dividing hairline
    ax.plot([cx + 0.18, cx + card_w - 0.18], [card_y + card_h - 3.25, card_y + card_h - 3.25],
            color='#E2E8F0', linewidth=1.0, zorder=3)
    
    # Bullet points
    point_start_y = card_y + card_h - 3.65
    for j, (k, v) in enumerate(stg["points"]):
        py = point_start_y - j * 0.46
        # Small colored bullet dot
        ax.plot(cx + 0.25, py, marker='o', markersize=4.0, color=stg["accent"], zorder=4)
        ax.text(cx + 0.42, py + 0.07, k, ha='left', va='center', fontsize=8.6, fontweight='bold', color='#1E293B', zorder=4)
        ax.text(cx + 0.42, py - 0.11, v, ha='left', va='center', fontsize=7.8, color='#64748B', zorder=4)

# Connecting Arrows (Clean Green / Blue theme)
for i in range(len(stages) - 1):
    x1 = start_x + i * (card_w + gap) + card_w + 0.05
    x2 = start_x + (i + 1) * (card_w + gap) - 0.05
    ay = card_y + card_h - 2.25
    
    arr_color = '#059669' if (i % 2 == 0) else '#2563EB'
    arrow = FancyArrowPatch((x1, ay), (x2, ay),
                            arrowstyle='->,head_width=5.0,head_length=8.0',
                            color=arr_color, linewidth=2.4, zorder=5)
    ax.add_patch(arrow)


# -----------------------------------------------------------------------------
# 4. BOTTOM PERFORMANCE METRICS (Pure Green & Blue Scheme)
# -----------------------------------------------------------------------------
bottom_y = 0.55
bottom_h = 1.65
bottom_bg = FancyBboxPatch((0.8, bottom_y), 17.6, bottom_h,
                           boxstyle="round,pad=0.08,rounding_size=0.18",
                           facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.8, zorder=2)
ax.add_patch(bottom_bg)

# Left text
ax.text(1.2, bottom_y + 1.18, "VALIDATED BENCHMARK OUTCOMES",
        ha='left', va='center', fontsize=9.5, fontweight='bold', color='#059669', zorder=3)
ax.text(1.2, bottom_y + 0.78, "Baseline (Cross-Entropy) vs. Topology-Constrained DINOv2 + clDice",
        ha='left', va='center', fontsize=12.5, fontweight='bold', color='#0F172A', zorder=3)
ax.text(1.2, bottom_y + 0.40, "Evaluated under patient-stratified validation to prevent data leakage across autopsy cases.",
        ha='left', va='center', fontsize=9.2, color='#64748B', zorder=3)

# 4 Stat Pills (Green & Blue Alternating)
metrics_cards = [
    ("+6.84 pp", "Pixel Accuracy", "57.3% -> 64.2%", "#1D4ED8", "#EFF6FF", "#BFDBFE"),
    ("+27.0%", "Mean IoU Gain", "0.300 -> 0.381", "#047857", "#ECFDF5", "#A7F3D0"),
    ("+41.8%", "Vessel Continuity", "0.514 -> 0.729 clDice", "#1D4ED8", "#EFF6FF", "#BFDBFE"),
    ("94.0%", "Continuous Ring Ratio", "vs 58.0% baseline", "#047857", "#ECFDF5", "#A7F3D0")
]

stat_w = 2.45
stat_h = 1.15
stat_x0 = 7.15
stat_gap = 0.30

for idx, (val, title, sub, col, bg_pill, border_pill) in enumerate(metrics_cards):
    sbx = stat_x0 + idx * (stat_w + stat_gap)
    
    p = FancyBboxPatch((sbx, bottom_y + 0.25), stat_w, stat_h,
                       boxstyle="round,pad=0.04,rounding_size=0.14",
                       facecolor=bg_pill, edgecolor=border_pill, linewidth=1.5, zorder=3)
    ax.add_patch(p)
    
    ax.text(sbx + stat_w / 2.0, bottom_y + 1.02, val,
            ha='center', va='center', fontsize=16.5, fontweight='bold', color=col, zorder=4)
    ax.text(sbx + stat_w / 2.0, bottom_y + 0.68, title,
            ha='center', va='center', fontsize=8.8, fontweight='bold', color='#1E293B', zorder=4)
    ax.text(sbx + stat_w / 2.0, bottom_y + 0.42, sub,
            ha='center', va='center', fontsize=8.0, color='#64748B', zorder=4)


# -----------------------------------------------------------------------------
# SAVE TO LOCATIONS
# -----------------------------------------------------------------------------
out_workspace = r"d:\Project topics\dinov3-main\LinkedIn_Thesis_Pipeline_Infographic.png"
out_downloads = r"C:\Users\Adheena Vinod\Downloads\LinkedIn_Thesis_Pipeline_Infographic.png"
out_desktop   = r"C:\Users\Adheena Vinod\OneDrive\Desktop\LinkedIn_Thesis_Pipeline_Infographic.png"

plt.tight_layout()
plt.savefig(out_workspace, dpi=200, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print(f"Generated: {out_workspace}")

for dest in [out_downloads, out_desktop]:
    try:
        shutil.copy2(out_workspace, dest)
        print(f"Copied to: {dest}")
    except Exception as e:
        print(f"Copy note for {dest}: {e}")
