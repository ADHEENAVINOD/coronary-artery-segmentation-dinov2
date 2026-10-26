# -*- coding: utf-8 -*-
"""
Generate a publication-grade, modern LinkedIn Infographic for the Thesis Pipeline.
Dimensions: 1920 x 1080 (16:9 HD, crisp for LinkedIn image posts).
"""

import os
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Matplotlib aesthetic settings
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans', 'Calibri']
plt.rcParams['font.family'] = 'sans-serif'

# Canvas setup (16:9 high-res)
fig = plt.figure(figsize=(19.2, 10.8), dpi=200)
ax = fig.add_subplot(111)
ax.set_xlim(0, 19.2)
ax.set_ylim(0, 10.8)
ax.axis('off')

# Background
BG_COLOR = '#F8FAFC'
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# -----------------------------------------------------------------------------
# 1. TOP HEADER BANNER
# -----------------------------------------------------------------------------
header_bg = FancyBboxPatch((0.8, 8.8), 17.6, 1.5,
                           boxstyle="round,pad=0.1,rounding_size=0.18",
                           facecolor='#0F172A', edgecolor='none', zorder=1)
ax.add_patch(header_bg)

# Tagline pill
pill = FancyBboxPatch((1.2, 9.85), 4.2, 0.32,
                      boxstyle="round,pad=0.04,rounding_size=0.12",
                      facecolor='#2563EB', edgecolor='none', zorder=2)
ax.add_patch(pill)
ax.text(3.3, 10.01, "MASTER'S THESIS RESEARCH · HEALTHCARE AI",
        ha='center', va='center', fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=3)

# Main Title
ax.text(1.2, 9.42, "Topology-Aware Deep Learning for Coronary Artery Segmentation",
        ha='left', va='center', fontsize=21, fontweight='bold', color='#F8FAFC', zorder=2)

# Subtitle
ax.text(1.2, 9.04, "End-to-End Pipeline: Frozen DINOv2 Foundation Backbone + Differentiable clDice Loss for Objective Stenosis Profiling",
        ha='left', va='center', fontsize=12, color='#94A3B8', zorder=2)

# Author badge on right
ax.text(18.0, 9.42, "Adheena Vinod", ha='right', va='center', fontsize=15, fontweight='bold', color='#38BDF8', zorder=2)
ax.text(18.0, 9.06, "Università di Verona", ha='right', va='center', fontsize=11, color='#CBD5E1', zorder=2)


# -----------------------------------------------------------------------------
# 2. 5 PIPELINE STAGE CARDS
# -----------------------------------------------------------------------------
card_w = 3.15
card_h = 5.20
card_y = 2.95
gap = 0.46
start_x = 0.82

stages = [
    {
        "num": "01",
        "tag": "DATA INGESTION",
        "title": "Whole-Slide\nAutopsy WSIs",
        "badge_col": "#475569",
        "card_bg": "#FFFFFF",
        "border": "#CBD5E1",
        "accent": "#0284C7",
        "points": [
            ("Clinical Source", "Univ. of Alberta Forensic Inst."),
            ("Resolution", "40× optical magnification"),
            ("Tissue Stains", "H&E + Movat's Pentachrome"),
            ("Ground Truth", "QuPath GeoJSON polygons"),
            ("Memory Cache", "Optimized RAM to <100 MB")
        ]
    },
    {
        "num": "02",
        "tag": "FOUNDATION MODEL",
        "title": "Frozen DINOv2\nViT Backbone",
        "badge_col": "#1D4ED8",
        "card_bg": "#FFFFFF",
        "border": "#93C5FD",
        "accent": "#2563EB",
        "points": [
            ("Architecture", "ViT-S/14 Foundation Model"),
            ("Weights", "FROZEN (prevents overfitting)"),
            ("Token Output", "384-dimensional dense vectors"),
            ("Self-Supervised", "Learns texture & boundaries"),
            ("Patch Grid", "16 × 16 spatial token map")
        ]
    },
    {
        "num": "03",
        "tag": "DECODER HEAD",
        "title": "3-Stage Conv\nUpsampler",
        "badge_col": "#059669",
        "card_bg": "#FFFFFF",
        "border": "#A7F3D0",
        "accent": "#10B981",
        "points": [
            ("Reshaping", "1D token sequence → 2D map"),
            ("Convolution", "Lightweight 3-layer head"),
            ("Channel Flow", "256 → 128 → 64 → 4 classes"),
            ("Activations", "Batch Normalization + ReLU"),
            ("Interpolation", "Bilinear upsampling to full-res")
        ]
    },
    {
        "num": "04",
        "tag": "TOPOLOGY LOSS",
        "title": "Differentiable\nclDice Supervision",
        "badge_col": "#D97706",
        "card_bg": "#FFFFFF",
        "border": "#FDE68A",
        "accent": "#F59E0B",
        "points": [
            ("Problem Solved", "Eliminates broken vessel rings"),
            ("Morphology", "Differentiable soft-skeleton"),
            ("Joint Loss", "L_total = L_CE + 0.5 × L_clDice"),
            ("Connectivity", "Enforces intact circular wall"),
            ("Ring Closure", "Surged from 58% to 94%")
        ]
    },
    {
        "num": "05",
        "tag": "CLINICAL TRANSLATION",
        "title": "Automated Stenosis\nQuantification",
        "badge_col": "#DC2626",
        "card_bg": "#FFFFFF",
        "border": "#FECACA",
        "accent": "#EF4444",
        "points": [
            ("Tissue Layers", "Lumen, Intima, Media"),
            ("Formula", "[1 - Area(L) / Area(M)] × 100"),
            ("Forensic Gold", "> 75% critical stenosis cutoff"),
            ("Consistency", "Eliminates manual subjectivity"),
            ("Outcome", "Automated sudden-death metric")
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
    
    # Card Body
    card = FancyBboxPatch((cx, card_y), card_w, card_h,
                          boxstyle="round,pad=0.08,rounding_size=0.18",
                          facecolor=stg["card_bg"], edgecolor=stg["border"], linewidth=2.0, zorder=2)
    ax.add_patch(card)
    
    # Step Number Circle
    num_circle = FancyBboxPatch((cx + 0.18, card_y + card_h - 0.65), 0.52, 0.52,
                                boxstyle="round,pad=0.05,rounding_size=0.25",
                                facecolor=stg["badge_col"], edgecolor='none', zorder=3)
    ax.add_patch(num_circle)
    ax.text(cx + 0.44, card_y + card_h - 0.39, stg["num"],
            ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF', zorder=4)
    
    # Stage Tag
    ax.text(cx + 0.85, card_y + card_h - 0.39, stg["tag"],
            ha='left', va='center', fontsize=8.5, fontweight='bold', color=stg["accent"], zorder=4)
    
    # Title
    ax.text(cx + 0.20, card_y + card_h - 1.25, stg["title"],
            ha='left', va='center', fontsize=14, fontweight='bold', color='#0F172A', linespacing=1.2, zorder=4)
    
    # Dividing hairline
    ax.plot([cx + 0.20, cx + card_w - 0.20], [card_y + card_h - 1.85, card_y + card_h - 1.85],
            color='#E2E8F0', linewidth=1.2, zorder=3)
    
    # Bullet specs
    point_start_y = card_y + card_h - 2.25
    for j, (k, v) in enumerate(stg["points"]):
        py = point_start_y - j * 0.55
        # bullet dot
        ax.plot(cx + 0.28, py, marker='o', markersize=4.5, color=stg["accent"], zorder=4)
        ax.text(cx + 0.48, py + 0.08, k, ha='left', va='center', fontsize=9.0, fontweight='bold', color='#334155', zorder=4)
        ax.text(cx + 0.48, py - 0.12, v, ha='left', va='center', fontsize=8.2, color='#64748B', zorder=4)

# Inter-card connective arrows
for i in range(len(stages) - 1):
    x1 = start_x + i * (card_w + gap) + card_w + 0.06
    x2 = start_x + (i + 1) * (card_w + gap) - 0.06
    ay = card_y + card_h / 2.0
    
    arrow = FancyArrowPatch((x1, ay), (x2, ay),
                            arrowstyle='->,head_width=5.5,head_length=8.5',
                            color='#94A3B8', linewidth=2.5, zorder=5)
    ax.add_patch(arrow)


# -----------------------------------------------------------------------------
# 3. BOTTOM PERFORMANCE IMPACT BAR
# -----------------------------------------------------------------------------
bottom_bar_y = 0.65
bottom_bar_h = 1.70
bottom_bar = FancyBboxPatch((0.8, bottom_bar_y), 17.6, bottom_bar_h,
                            boxstyle="round,pad=0.1,rounding_size=0.18",
                            facecolor='#FFFFFF', edgecolor='#E2E8F0', linewidth=2.0, zorder=2)
ax.add_patch(bottom_bar)

# Label
ax.text(1.2, bottom_bar_y + 1.25, "VALIDATED BENCHMARK OUTCOMES",
        ha='left', va='center', fontsize=10, fontweight='bold', color='#2563EB', zorder=3)
ax.text(1.2, bottom_bar_y + 0.80, "Cross-Entropy Baseline vs. DINOv2 + clDice Topology Model",
        ha='left', va='center', fontsize=13, fontweight='bold', color='#0F172A', zorder=3)
ax.text(1.2, bottom_bar_y + 0.40, "Evaluated on multi-patient autopsy validation set with strict patient-stratified isolation.",
        ha='left', va='center', fontsize=9.5, color='#64748B', zorder=3)

# 4 Stat Pills on the right side of the bottom bar
metrics_data = [
    ("+6.84 pp", "Pixel Accuracy", "57.3% -> 64.2%", "#0284C7", "#E0F2FE"),
    ("+27.0%", "Mean IoU Gain", "0.300 -> 0.381", "#16A34A", "#DCFCE7"),
    ("+41.8%", "Vessel Continuity", "0.514 -> 0.729 clDice", "#D97706", "#FEF3C7"),
    ("94.0%", "Closed Ring Ratio", "vs 58.0% baseline", "#9333EA", "#F3E8FF")
]

stat_box_w = 2.45
stat_box_h = 1.15
stat_start_x = 7.20
stat_gap = 0.28

for idx, (val, title, sub, text_c, bg_c) in enumerate(metrics_data):
    sbx = stat_start_x + idx * (stat_box_w + stat_gap)
    
    s_patch = FancyBboxPatch((sbx, bottom_bar_y + 0.28), stat_box_w, stat_box_h,
                             boxstyle="round,pad=0.05,rounding_size=0.14",
                             facecolor=bg_c, edgecolor='none', zorder=3)
    ax.add_patch(s_patch)
    
    ax.text(sbx + stat_box_w / 2.0, bottom_bar_y + 1.05, val,
            ha='center', va='center', fontsize=17, fontweight='bold', color=text_c, zorder=4)
    ax.text(sbx + stat_box_w / 2.0, bottom_bar_y + 0.68, title,
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E293B', zorder=4)
    ax.text(sbx + stat_box_w / 2.0, bottom_bar_y + 0.44, sub,
            ha='center', va='center', fontsize=8.0, color='#64748B', zorder=4)

# Save high-res PNG
output_workspace = r"d:\Project topics\dinov3-main\LinkedIn_Thesis_Pipeline_Infographic.png"
output_downloads = r"C:\Users\Adheena Vinod\Downloads\LinkedIn_Thesis_Pipeline_Infographic.png"
output_desktop   = r"C:\Users\Adheena Vinod\OneDrive\Desktop\LinkedIn_Thesis_Pipeline_Infographic.png"

plt.tight_layout()
plt.savefig(output_workspace, dpi=200, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print(f"Generated: {output_workspace}")

for dest in [output_downloads, output_desktop]:
    try:
        shutil.copy2(output_workspace, dest)
        print(f"Copied to: {dest}")
    except Exception as e:
        print(f"Copy note for {dest}: {e}")
