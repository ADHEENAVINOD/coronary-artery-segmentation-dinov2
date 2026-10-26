# -*- coding: utf-8 -*-
"""
Generate a clean, high-resolution qualitative presentation image for Slide 9
and update Slide 9 in the presentation to have a clean, readable layout.
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. Base Paths
base_dir = r"D:\Project topics\dinov3-main"
viz_dir  = os.path.join(base_dir, "output", "visualizations")
ppt_dir  = os.path.join(base_dir, "ppt_images")
desktop_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop"

# 2. Extract crops from C18-L1 and C2-L1 predictions to create a crystal-clear side-by-side
c18_path = os.path.join(viz_dir, "C18-L1_roi_1_prediction.png")
c2_path  = os.path.join(viz_dir, "C2-L1_roi_1_prediction.png")
c19_path = os.path.join(viz_dir, "C19-L2_roi_1_prediction.png")

# Let's create an elegant, high-res presentation composite graphic for Slide 9
fig = plt.figure(figsize=(16, 8.5), dpi=300)
fig.patch.set_facecolor('#F7F4EE')

# Subplots grid: 
# Row 1: Patient C18-L1 (ROI 1) - Concentric Plaque (Original, Ground Truth, Prediction Overlay)
# Row 2: Patient C2-L1 (ROI 1)  - Eccentric Plaque  (Original, Ground Truth, Prediction Overlay)
# Row 3: Patient C19-L2 (ROI 1) - Severe Stenosis   (Original, Ground Truth, Prediction Overlay)

# Load full visualization images
img_c18 = Image.open(c18_path)
img_c2  = Image.open(c2_path)
img_c19 = Image.open(c19_path)

def extract_cells(full_img):
    """Extracts: (1) Original Image, (2) Ground Truth, (3) Prediction Overlay from 2x3 grid"""
    w, h = full_img.size
    cell_w = w // 3
    cell_h = h // 2
    
    # Original: top-left (col 0, row 0)
    orig = full_img.crop((int(cell_w * 0.02), int(cell_h * 0.08), int(cell_w * 0.98), int(cell_h * 0.98)))
    # Ground Truth: top-center (col 1, row 0)
    gt   = full_img.crop((int(cell_w * 1.02), int(cell_h * 0.08), int(cell_w * 1.98), int(cell_h * 0.98)))
    # Pred Overlay: bottom-center (col 1, row 1)
    over = full_img.crop((int(cell_w * 1.02), int(cell_h * 1.08), int(cell_w * 1.98), int(cell_h * 1.98)))
    
    return orig, gt, over

patients = [
    ("Patient C18-L1 (Concentric Plaque | 54.4% Acc)", extract_cells(img_c18)),
    ("Patient C2-L1 (Eccentric Narrowing | 62.1% Acc)", extract_cells(img_c2)),
    ("Patient C19-L2 (Severe Luminal Stenosis | 66.8% Acc)", extract_cells(img_c19)),
]

cols_titles = ["(a) Raw H&E Histology", "(b) Ground Truth (QuPath)", "(c) Proposed DINOv3 + clDice Overlay"]

# Create 3x3 layout
for r_idx, (p_name, (orig, gt, over)) in enumerate(patients):
    # Patient Row Header
    y_pos = 0.92 - r_idx * 0.31
    fig.text(0.04, y_pos, p_name, fontsize=12, fontweight='bold', color='#1C1A17', va='top')
    
    for c_idx, cell_img in enumerate([orig, gt, over]):
        ax = fig.add_axes([0.30 + c_idx * 0.23, 0.69 - r_idx * 0.31, 0.21, 0.26])
        ax.imshow(cell_img)
        ax.axis('off')
        
        # Border
        for spine in ax.spines.values():
            spine.set_edgecolor('#DDD6CA')
            spine.set_linewidth(1.0)
            
        if r_idx == 0:
            ax.set_title(cols_titles[c_idx], fontsize=11, fontweight='bold', color='#9E4733', pad=8)

# Left Side Summary Card Text
summary_ax = fig.add_axes([0.04, 0.08, 0.23, 0.58])
summary_ax.axis('off')

card = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.04,rounding_size=0.08",
                              facecolor='#FFFFFF', edgecolor='#DDD6CA', linewidth=1.2)
summary_ax.add_patch(card)

summary_ax.text(0.08, 0.92, "QUALITATIVE FINDINGS", fontsize=11, fontweight='bold', color='#B08A56')
summary_ax.plot([0.08, 0.92], [0.87, 0.87], color='#DDD6CA', linewidth=0.8)

points = [
    ("1. Continuous Ring Closure", "Muscular Media wall is segmented as an unbroken, continuous circle without fragmentation."),
    ("2. Sharp Plaque Isolation", "Accurately separates central open Lumen from diseased Intima plaque layer across all cases."),
    ("3. Multi-Patient Robustness", "Maintains strong boundary fidelity across concentric (C18), eccentric (C2), and severe (C19) stenosis."),
    ("4. Clinically Aligned Overlays", "50% opacity overlays (c) demonstrate tight spatial concordance with pathologist ground truth (b).")
]

y_pt = 0.80
for title, desc in points:
    summary_ax.text(0.08, y_pt, title, fontsize=9.5, fontweight='bold', color='#1C1A17')
    summary_ax.text(0.08, y_pt - 0.06, desc, fontsize=8.0, color='#736B63', wrap=True)
    y_pt -= 0.18

# Save Clean Qualitative Image
out_img_ppt = os.path.join(ppt_dir, "Slide_9_Qualitative_Clean_Composite.png")
plt.savefig(out_img_ppt, dpi=300, bbox_inches='tight', facecolor='#F7F4EE')
print(f"Saved: {out_img_ppt}")

# Copy to Desktop
out_desktop = os.path.join(desktop_dir, "Slide_9_Qualitative_Clean_Composite.png")
shutil.copy2(out_img_ppt, out_desktop)
print(f"Copied to Desktop: {out_desktop}")
