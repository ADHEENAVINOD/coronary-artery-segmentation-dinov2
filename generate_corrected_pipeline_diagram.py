# -*- coding: utf-8 -*-
"""
Generate publication-quality, corrected End-to-End Pipeline Architecture diagram.
Corrects:
  - Box 3: Spatial Reshaping & Convolutional Decoder (with Bilinear Upsampling)
  - Box 5: Automated Stenosis Quantification (% Luminal Blockage)
  - Training Supervision: Distinct Joint Loss loop (Cross-Entropy + clDice)
"""

import os
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Set up matplotlib aesthetics
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Calibri', 'Arial', 'Segoe UI']
plt.rcParams['font.family'] = 'sans-serif'

# Canvas dimensions
fig = plt.figure(figsize=(16, 7.5), dpi=300)
ax = fig.add_subplot(111)
ax.set_xlim(0, 16)
ax.set_ylim(0, 7.5)
ax.axis('off')

# Background
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Header
ax.text(8.0, 7.05, "End-to-End Proposed Pipeline Architecture", 
        ha='center', va='center', fontsize=22, fontweight='bold', color='#1E293B')
ax.text(8.0, 6.62, "Self-Supervised Vision Transformer (DINOv2) + Spatial Reshaping + Dual clDice Topology Supervision", 
        ha='center', va='center', fontsize=12, style='italic', color='#64748B')

# Box dimensions
box_w = 2.45
box_h = 3.60
box_y = 1.90
gap = 0.55
start_x = 0.80

boxes = [
    {
        "step": "INPUT DATA",
        "title": "Histology Patch\n(512 × 512)",
        "items": [
            "• H&E Coronary WSI",
            "• QuPath ROI extraction",
            "• Size: 512 × 512 × 3",
            "• Stride-14 overlap tiling",
            "• Normalized RGB values"
        ],
        "border": "#475569",
        "bg": "#F8FAFC",
        "badge_bg": "#334155",
        "title_color": "#0F172A"
    },
    {
        "step": "REPRESENTATION",
        "title": "Frozen DINOv2\nViT Encoder",
        "items": [
            "• ViT-S/14 Foundation Model",
            "• Patch tokens: 14 × 14 px",
            "• 384-d dense embeddings",
            "• Self-supervised pretraining",
            "• WEIGHTS FROZEN (no train)"
        ],
        "border": "#2563EB",
        "bg": "#EFF6FF",
        "badge_bg": "#1D4ED8",
        "title_color": "#1E3A8A"
    },
    {
        "step": "DECODER (CORRECTED)",
        "title": "Spatial Reshape &\nConv Decoder",
        "items": [
            "• 1D Tokens → 2D Grid (36×36)",
            "• 3-Layer Conv Head",
            "• 256 → 128 → 4 channels",
            "• BatchNorm + ReLU non-linear",
            "• Bilinear Upsample → 512×512"
        ],
        "border": "#16A34A",
        "bg": "#F0FDF4",
        "badge_bg": "#15803D",
        "title_color": "#14532D"
    },
    {
        "step": "MODEL OUTPUT",
        "title": "Multi-Class\nSegmentation",
        "items": [
            "• 512 × 512 × 4 Logits",
            "• Softmax probability maps",
            "• Class 0: Background",
            "• Class 1: Lumen (Center)",
            "• Class 2: Intima (Plaque)",
            "• Class 3: Media (Wall)"
        ],
        "border": "#D97706",
        "bg": "#FFFBEB",
        "badge_bg": "#B45309",
        "title_color": "#78350F"
    },
    {
        "step": "CLINICAL GOAL (CORRECTED)",
        "title": "Automated Stenosis\nQuantification",
        "items": [
            "• Area(Lumen) & Area(Media)",
            "• Stenosis % Formula:",
            "  [1 - Area(L) / Area(M)] × 100",
            "• Critical Cutoff: > 75%",
            "• Objective Forensic Cause-",
            "  of-Death Determination"
        ],
        "border": "#DC2626",
        "bg": "#FEF2F2",
        "badge_bg": "#B91C1C",
        "title_color": "#7F1D1D"
    }
]

# Draw Boxes
for i, b in enumerate(boxes):
    bx = start_x + i * (box_w + gap)
    
    # Shadow / Glow
    shadow = FancyBboxPatch((bx + 0.04, box_y - 0.04), box_w, box_h,
                            boxstyle="round,pad=0.08,rounding_size=0.15",
                            facecolor='#E2E8F0', edgecolor='none', zorder=1)
    ax.add_patch(shadow)
    
    # Main Box
    rect = FancyBboxPatch((bx, box_y), box_w, box_h,
                          boxstyle="round,pad=0.08,rounding_size=0.15",
                          facecolor=b["bg"], edgecolor=b["border"], linewidth=2.0, zorder=2)
    ax.add_patch(rect)
    
    # Step Badge
    badge_w = box_w - 0.20
    badge = FancyBboxPatch((bx + 0.10, box_y + box_h - 0.42), badge_w, 0.32,
                           boxstyle="round,pad=0.03,rounding_size=0.08",
                           facecolor=b["badge_bg"], edgecolor='none', zorder=3)
    ax.add_patch(badge)
    ax.text(bx + box_w / 2.0, box_y + box_h - 0.26, b["step"],
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#FFFFFF', zorder=4)
    
    # Title
    ax.text(bx + box_w / 2.0, box_y + box_h - 0.88, b["title"],
            ha='center', va='center', fontsize=11.5, fontweight='bold', color=b["title_color"], zorder=4, linespacing=1.15)
    
    # Divider line
    ax.plot([bx + 0.18, bx + box_w - 0.18], [box_y + box_h - 1.35, box_y + box_h - 1.35],
            color=b["border"], linewidth=0.8, alpha=0.5, zorder=4)
    
    # Items
    start_item_y = box_y + box_h - 1.62
    for j, item in enumerate(b["items"]):
        iy = start_item_y - j * 0.32
        fw = 'bold' if ("Formula" in item or "WSI" in item or "WEIGHTS" in item) else 'normal'
        ax.text(bx + 0.16, iy, item, ha='left', va='center', fontsize=9.0, color='#1E293B', fontweight=fw, zorder=4)

# Draw Inter-Box Arrows
for i in range(len(boxes) - 1):
    x1 = start_x + i * (box_w + gap) + box_w + 0.08
    x2 = start_x + (i + 1) * (box_w + gap) - 0.08
    ay = box_y + box_h / 2.0
    
    arrow = FancyArrowPatch((x1, ay), (x2, ay),
                            arrowstyle='->,head_width=5,head_length=8',
                            color='#475569', linewidth=2.4, zorder=5)
    ax.add_patch(arrow)

# -----------------------------------------------------------------------------
# Bottom Supervision Banner (Showing the Training Loss explicitly & correctly)
# -----------------------------------------------------------------------------
loss_box_x = start_x + box_w + gap + 0.20
loss_box_w = 2 * (box_w + gap) + box_w - 0.40
loss_box_y = 0.35
loss_box_h = 1.05

# Loss Container Box
l_bg = FancyBboxPatch((loss_box_x, loss_box_y), loss_box_w, loss_box_h,
                      boxstyle="round,pad=0.08,rounding_size=0.15",
                      facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.8, linestyle='--', zorder=2)
ax.add_patch(l_bg)

# Loss Title & Equation
ax.text(loss_box_x + 0.20, loss_box_y + loss_box_h - 0.28,
        "TRAINING PHASE SUPERVISION (Topology-Aware Joint Loss):",
        ha='left', va='center', fontsize=9.5, fontweight='bold', color='#92400E', zorder=4)

ax.text(loss_box_x + 0.20, loss_box_y + 0.32,
        r"$\mathcal{L}_{\mathrm{total}} = \mathcal{L}_{\mathrm{CE}}(\mathrm{Logits}, \mathrm{GT}) + 0.5 \times \mathcal{L}_{\mathrm{clDice}}(\mathrm{Skeleton}_{\mathrm{Pred}}, \mathrm{Skeleton}_{\mathrm{GT}})$",
        ha='left', va='center', fontsize=11.5, fontweight='bold', color='#B45309', zorder=4)

ax.text(loss_box_x + loss_box_w - 0.20, loss_box_y + 0.32,
        "(Enforces 100% closed vessel rings)",
        ha='right', va='center', fontsize=9.0, style='italic', color='#78350F', zorder=4)

# Dashed Supervision Arrow from Loss Box up to Decoder & Output
arr_loss1 = FancyArrowPatch((loss_box_x + 2.0, loss_box_y + loss_box_h + 0.05),
                            (loss_box_x + 2.0, box_y - 0.08),
                            arrowstyle='->,head_width=4,head_length=6',
                            color='#D97706', linewidth=1.8, linestyle='--', zorder=5)
ax.add_patch(arr_loss1)

arr_loss2 = FancyArrowPatch((loss_box_x + 5.0, box_y - 0.08),
                            (loss_box_x + 5.0, loss_box_y + loss_box_h + 0.05),
                            arrowstyle='->,head_width=4,head_length=6',
                            color='#D97706', linewidth=1.8, linestyle='--', zorder=5)
ax.add_patch(arr_loss2)

# Save to ppt_images and Desktop
base_dir = r"D:\Project topics\dinov3-main"
out_img_ppt = os.path.join(base_dir, "ppt_images", "End_to_End_Pipeline_Architecture_Corrected.png")
plt.tight_layout()
plt.savefig(out_img_ppt, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
print(f"Saved: {out_img_ppt}")

# Copy to Desktop
desktop_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop"
out_desktop = os.path.join(desktop_dir, "End_to_End_Pipeline_Architecture_Corrected.png")
shutil.copy2(out_img_ppt, out_desktop)
print(f"Copied to Desktop: {out_desktop}")
