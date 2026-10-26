# -*- coding: utf-8 -*-
"""
Generate a publication-grade, pristine Qualitative Comparison figure for GitHub README.
Clean white background, perfectly aligned 3x4 grid, zero text collisions, accurate labels (DINOv2).
"""

import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

base_dir = r"D:\Project topics\dinov3-main"
viz_dir  = os.path.join(base_dir, "output", "visualizations")
ppt_dir  = os.path.join(base_dir, "ppt_images")

c18_path = os.path.join(viz_dir, "C18-L1_roi_1_prediction.png")
c2_path  = os.path.join(viz_dir, "C2-L1_roi_1_prediction.png")
c19_path = os.path.join(viz_dir, "C19-L2_roi_1_prediction.png")

img_c18 = Image.open(c18_path)
img_c2  = Image.open(c2_path)
img_c19 = Image.open(c19_path)

def extract_cells(full_img):
    w, h = full_img.size
    cell_w = w // 3
    cell_h = h // 2
    
    # 1. Raw Histology: col 0, row 0
    orig = full_img.crop((int(cell_w * 0.02), int(cell_h * 0.08), int(cell_w * 0.98), int(cell_h * 0.98)))
    # 2. Ground Truth Mask: col 1, row 0
    gt   = full_img.crop((int(cell_w * 1.02), int(cell_h * 0.08), int(cell_w * 1.98), int(cell_h * 0.98)))
    # 3. Model Prediction: col 2, row 0
    pred = full_img.crop((int(cell_w * 2.02), int(cell_h * 0.08), int(cell_w * 2.98), int(cell_h * 0.98)))
    # 4. Prediction Overlay: col 1, row 1
    over = full_img.crop((int(cell_w * 1.02), int(cell_h * 1.08), int(cell_w * 1.98), int(cell_h * 1.98)))
    
    return orig, gt, pred, over

patients = [
    {
        "name": "Patient C18-L1",
        "tag": "Concentric Fibroatheroma",
        "acc": "Pixel Accuracy: 54.4%",
        "cells": extract_cells(img_c18)
    },
    {
        "name": "Patient C2-L1",
        "tag": "Eccentric Luminal Narrowing",
        "acc": "Pixel Accuracy: 62.1%",
        "cells": extract_cells(img_c2)
    },
    {
        "name": "Patient C19-L2",
        "tag": "Severe Obstructive Stenosis",
        "acc": "Pixel Accuracy: 66.8%",
        "cells": extract_cells(img_c19)
    }
]

# Set up matplotlib
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'

fig = plt.figure(figsize=(16, 11), dpi=220)
fig.patch.set_facecolor('#FFFFFF')

col_titles = [
    "(a) Raw Histology Image",
    "(b) Ground Truth (QuPath)",
    "(c) Predicted Mask (DINOv2 + clDice)",
    "(d) Anatomical Boundary Overlay"
]

grid_left = 0.22
grid_bottom = 0.08
grid_width = 0.75
grid_height = 0.82

row_gap = 0.03
cell_h = (grid_height - 2 * row_gap) / 3
col_gap = 0.02
cell_w = (grid_width - 3 * col_gap) / 4

for r_idx, pat in enumerate(patients):
    ry = grid_bottom + (2 - r_idx) * (cell_h + row_gap)
    
    # Left Patient Info Box
    info_ax = fig.add_axes([0.03, ry, 0.17, cell_h])
    info_ax.axis('off')
    
    # Rounded badge container
    badge = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.03,rounding_size=0.12",
                                  facecolor='#F8FAFC', edgecolor='#E2E8F0', linewidth=1.5)
    info_ax.add_patch(badge)
    
    info_ax.text(0.08, 0.78, pat["name"], fontsize=13, fontweight='bold', color='#0F172A')
    info_ax.text(0.08, 0.52, pat["tag"], fontsize=9.5, fontweight='bold', color='#2563EB')
    info_ax.text(0.08, 0.26, pat["acc"], fontsize=9.0, color='#64748B')
    
    # 4 Columns of images
    for c_idx, im in enumerate(pat["cells"]):
        cx = grid_left + c_idx * (cell_w + col_gap)
        ax = fig.add_axes([cx, ry, cell_w, cell_h])
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Border
        for spine in ax.spines.values():
            spine.set_edgecolor('#CBD5E1')
            spine.set_linewidth(1.5)
            
        # Top titles on first row
        if r_idx == 0:
            ax.set_title(col_titles[c_idx], fontsize=11, fontweight='bold', color='#1E293B', pad=10)

# Bottom Color Legend Bar
legend_ax = fig.add_axes([0.03, 0.015, 0.94, 0.045])
legend_ax.axis('off')

# Legend items
legend_items = [
    ("Lumen (Cavity)", "#DC2626"),     # Red in jet colormap
    ("Intima (Plaque)", "#F59E0B"),    # Yellow/Orange in jet
    ("Media (Wall)", "#06B6D4"),       # Cyan/Blue in jet
    ("Background", "#1E3A8A")          # Dark Blue in jet
]

leg_w = 0.20
for idx, (label, color) in enumerate(legend_items):
    lx = 0.18 + idx * 0.18
    swatch = patches.FancyBboxPatch((lx, 0.2), 0.025, 0.6, boxstyle="round,pad=0.01,rounding_size=0.05",
                                    facecolor=color, edgecolor='none')
    legend_ax.add_patch(swatch)
    legend_ax.text(lx + 0.035, 0.5, label, fontsize=10, fontweight='bold', color='#334155', va='center')

out_path = os.path.join(ppt_dir, "Slide_9_Qualitative_Clean_Composite.png")
plt.savefig(out_path, dpi=220, bbox_inches='tight', facecolor='#FFFFFF')
plt.close()
print(f"Pristine Qualitative figure generated: {out_path}")
