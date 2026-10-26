# -*- coding: utf-8 -*-
"""
Generate Warm Editorial presentation diagrams and graphs.
Strictly NO BLUE. Warm Linen / Cream, Terracotta, Olive Sage, Warm Ochre, Deep Espresso.
Fonts: Georgia & Segoe UI.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

output_dir = r"d:\Project topics\dinov3-main\ppt_images_editorial"
os.makedirs(output_dir, exist_ok=True)

# Colors
BG_WARM = '#FAF7F2'      # Warm Linen / Cream
CARD_BG = '#EDE8DF'      # Warm Alabaster / Light Sand
TEXT_DARK = '#1C1A17'    # Deep Espresso / Warm Charcoal
TEXT_MUTED = '#6B655F'   # Slate Umber / Warm Taupe
TERRACOTTA = '#9E4733'   # Primary Accent: Terracotta
OLIVE = '#4A5A48'        # Accent 2: Deep Olive Sage
OCHRE = '#B08A56'        # Accent 3: Warm Ochre
BORDER = '#D8D1C5'       # Delicate taupe hairline
BAR_BASE = '#B8AFA6'     # Muted sandstone taupe for baseline

# Set global matplotlib defaults
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
plt.rcParams['font.serif'] = ['Georgia', 'Palatino Linotype', 'DejaVu Serif']
plt.rcParams['font.family'] = 'sans-serif'


# ==============================================================================
# 1. Slide 10: Quantitative Performance Graph (Baseline vs Proposed + clDice)
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.4, 4.8), dpi=220, facecolor=BG_WARM)
ax.set_facecolor(BG_WARM)

metrics = ['Accuracy (%)', 'Mean IoU (x100)', 'Vessel Continuity (clDice)']
baseline_vals = [57.33, 30.00, 51.40]
proposed_vals = [64.17, 38.10, 72.90]
improvements = ['+6.84%', '+27.0%', '+41.8%']

x = np.arange(len(metrics))
width = 0.32

rects1 = ax.bar(x - width/2, baseline_vals, width, label='Baseline (Cross-Entropy)',
                color=BAR_BASE, edgecolor='#7A7167', linewidth=1.2)
rects2 = ax.bar(x + width/2, proposed_vals, width, label='Proposed (+ clDice Topology)',
                color=TERRACOTTA, edgecolor='#6D2B1E', linewidth=1.2)

ax.set_ylabel('Metric Value / Score', fontsize=11, fontweight='bold', color=TEXT_DARK, labelpad=8)
ax.set_title('Quantitative Performance Comparison', fontname='Georgia', fontsize=14, fontweight='bold', pad=16, color=TEXT_DARK)
ax.set_xticks(x)
ax.set_xticklabels(['Overall Accuracy\n(%)', 'Mean IoU\n(x100)', 'Vessel Continuity\n(clDice Score)'],
                   fontsize=10.5, fontweight='bold', color=TEXT_DARK)

ax.legend(frameon=True, facecolor=CARD_BG, edgecolor=BORDER, fontsize=10, loc='upper left', labelcolor=TEXT_DARK)
ax.set_ylim(0, 88)
ax.grid(axis='y', linestyle=':', color=BORDER, alpha=0.8)
ax.set_axisbelow(True)

# Clean spines: remove top and right, subtle bottom/left
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(BORDER)
ax.spines['bottom'].set_color(BORDER)
ax.tick_params(colors=TEXT_DARK)

# Annotate values
for i in range(len(metrics)):
    b_val = baseline_vals[i]
    p_val = proposed_vals[i]
    if i == 2:
        ax.annotate(f"0.514", (x[i] - width/2, b_val + 2.0), ha='center', va='bottom',
                    fontsize=9.5, color=TEXT_MUTED, fontweight='bold')
        ax.annotate(f"0.729\n({improvements[i]})", (x[i] + width/2, p_val + 2.0), ha='center', va='bottom',
                    fontsize=9.5, fontweight='bold', color=TERRACOTTA)
    else:
        ax.annotate(f"{b_val:.1f}%", (x[i] - width/2, b_val + 2.0), ha='center', va='bottom',
                    fontsize=9.5, color=TEXT_MUTED, fontweight='bold')
        ax.annotate(f"{p_val:.1f}%\n({improvements[i]})", (x[i] + width/2, p_val + 2.0), ha='center', va='bottom',
                    fontsize=9.5, fontweight='bold', color=TERRACOTTA)

plt.tight_layout()
p1 = os.path.join(output_dir, "Slide_15_Results_Performance_Graph.png")
plt.savefig(p1, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm bar chart:", p1)


# ==============================================================================
# 2. Slide 6: The Topology Problem (Broken Ring vs Continuous Ring)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 4.0), dpi=220, facecolor=BG_WARM)
theta = np.linspace(0, 2*np.pi, 250)
r_inner, r_outer = 0.52, 0.88

# Left: Standard CE Loss (Broken ring, disconnected fragments)
ax1.set_facecolor(BG_WARM)
ax1.set_xlim(-1.25, 1.25)
ax1.set_ylim(-1.25, 1.25)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('Standard Pixel Loss (Cross-Entropy)\nTopological Fragmentation',
              fontname='Georgia', fontsize=12, fontweight='bold', color=TERRACOTTA, pad=12)

theta1 = np.linspace(0.2, 1.8, 60)
theta2 = np.linspace(2.35, 3.95, 60)
theta3 = np.linspace(4.55, 5.75, 50)
for th in [theta1, theta2, theta3]:
    x_in, y_in = r_inner * np.cos(th), r_inner * np.sin(th)
    x_out, y_out = r_outer * np.cos(th), r_outer * np.sin(th)
    ax1.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]),
             color=TERRACOTTA, alpha=0.75, edgecolor='#7A2C1C', linewidth=1.5)

np.random.seed(42)
noise_x = np.random.uniform(-0.35, 0.35, 14)
noise_y = np.random.uniform(-0.35, 0.35, 14)
ax1.scatter(noise_x, noise_y, color=TERRACOTTA, s=35, alpha=0.85, marker='s', edgecolors='#7A2C1C')
ax1.text(0, -1.18, 'Gaps in Arterial Ring & False Lumen Islands\n(Invalid for clinical caliber measurement)',
         ha='center', fontsize=9.0, color=TERRACOTTA, fontweight='bold')

# Right: Proposed clDice (Continuous Annular Loop)
ax2.set_facecolor(BG_WARM)
ax2.set_xlim(-1.25, 1.25)
ax2.set_ylim(-1.25, 1.25)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('Topology-Preserving Learning (clDice)\nContinuous Annular Geometry',
              fontname='Georgia', fontsize=12, fontweight='bold', color=OLIVE, pad=12)

x_in, y_in = r_inner * np.cos(theta), r_inner * np.sin(theta)
x_out, y_out = r_outer * np.cos(theta), r_outer * np.sin(theta)
ax2.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]),
         color=OLIVE, alpha=0.8, edgecolor='#2E382D', linewidth=1.5)

# Center intact lumen
ax2.text(0, 0, 'Intact\nLumen', ha='center', va='center', fontsize=10, fontweight='bold', color=TEXT_DARK)
ax2.text(0, -1.18, 'Continuous Annular Artery Wall\n(Enforces Homotopy Equivalence, Betti = 1)',
         ha='center', fontsize=9.0, color=OLIVE, fontweight='bold')

plt.tight_layout()
p2 = os.path.join(output_dir, "Slide_4_Problem_Statement_Topology.png")
plt.savefig(p2, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm topology diagram:", p2)


# ==============================================================================
# 3. Slide 7: clDice Skeletonization (Soft morphology & Centerline skeleton)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 4.2), dpi=220, facecolor=BG_WARM)
r_in, r_out = 0.55, 0.85
th = np.linspace(0, 2*np.pi, 250)

# Left: Differentiable Soft Morphology
ax1.set_facecolor(BG_WARM)
ax1.set_xlim(-1.25, 1.25)
ax1.set_ylim(-1.25, 1.25)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('Differentiable Soft-Morphology\n(Iterative Continuous Min/Max Pooling)',
              fontname='Georgia', fontsize=11.5, fontweight='bold', color=TEXT_DARK, pad=12)

x_in, y_in = r_in * np.cos(th), r_in * np.sin(th)
x_out, y_out = r_out * np.cos(th), r_out * np.sin(th)
ax1.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]),
         color=OCHRE, alpha=0.65, edgecolor='#7D5F38', linewidth=1.5)
ax1.text(0, -1.18, 'Iterative Soft-Erode & Soft-Dilate\n(Over T = 5 iterations, preserves gradient flow)',
         ha='center', fontsize=9.0, fontweight='bold', color=TEXT_DARK)

# Right: Extracted Centerline Skeleton S(V)
ax2.set_facecolor(BG_WARM)
ax2.set_xlim(-1.25, 1.25)
ax2.set_ylim(-1.25, 1.25)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('Extracted Centerline Skeleton S(V)\n(Topological Homotopy Preservation)',
              fontname='Georgia', fontsize=11.5, fontweight='bold', color=OLIVE, pad=12)

ax2.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]),
         color=CARD_BG, alpha=0.9, edgecolor=BORDER, linewidth=1.2)
r_mid = (r_in + r_out) / 2
x_mid, y_mid = r_mid * np.cos(th), r_mid * np.sin(th)
ax2.plot(x_mid, y_mid, color=TERRACOTTA, linewidth=3.5, label='Centerline Skeleton')
ax2.text(0, 0, 'S(V)', ha='center', va='center', fontsize=11, fontweight='bold', color=TERRACOTTA)
ax2.text(0, -1.18, 'Enforces Annular Continuity (clDice)\nZero Broken Boundaries across Vessels',
         ha='center', fontsize=9.0, fontweight='bold', color=OLIVE)

plt.tight_layout()
p3 = os.path.join(output_dir, "Slide_9_clDice_Skeletonization.png")
plt.savefig(p3, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm skeletonization diagram:", p3)


# ==============================================================================
# 4. Slide 3: Dataset Acquisition & Preprocessing Workflow
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=220, facecolor=BG_WARM)
ax.set_facecolor(BG_WARM)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

steps = [
    (0.5, 5.1, 9.0, 1.9,
     '1. Whole Slide Image (WSI) Ingestion\n'
     'Gigapixel human coronary autopsy slides (H&E & Movat pentachrome)\n'
     'Original resolution: >40,000 x 40,000 pixels (1.0 – 2.5 GB per slide)',
     CARD_BG, TERRACOTTA),
    (0.5, 2.8, 9.0, 1.9,
     '2. QuPath Expert Pathologist Annotation\n'
     'Manual polygon delineation of 16 clinical coronary artery ROIs\n'
     '4 tissue classes: Background, Media, Intima, and Lumen geometry',
     CARD_BG, OLIVE),
    (0.5, 0.5, 9.0, 1.9,
     '3. Dynamic Patching & Tensor Caching\n'
     'Cropped into 512x512 patches with stride overlap\n'
     'Precomputed .npy tensor cache reducing active RAM to <100 MB',
     CARD_BG, OCHRE)
]

for bx, by, bw, bh, text, bg, accent in steps:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=bg, edgecolor=BORDER, linewidth=1.2, zorder=2)
    ax.add_patch(rect)
    # Left accent bar
    abar = plt.Rectangle((bx, by), 0.22, bh, facecolor=accent, edgecolor='none', zorder=3)
    ax.add_patch(abar)
    ax.text(bx + 0.5, by + bh/2, text, ha='left', va='center', fontsize=9.5,
            fontweight='bold', color=TEXT_DARK, zorder=4)

ax.annotate('', xy=(5.0, 4.7), xytext=(5.0, 5.1),
            arrowprops=dict(facecolor=TEXT_MUTED, edgecolor='none', width=1.5, headwidth=5))
ax.annotate('', xy=(5.0, 2.4), xytext=(5.0, 2.8),
            arrowprops=dict(facecolor=TEXT_MUTED, edgecolor='none', width=1.5, headwidth=5))

ax.set_title('Dataset Acquisition & Preparation Pipeline', fontname='Georgia',
             fontsize=13, fontweight='bold', color=TEXT_DARK, pad=12)
plt.tight_layout()
p4 = os.path.join(output_dir, "Slide_6_Dataset_Preprocessing_Workflow.png")
plt.savefig(p4, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm workflow diagram:", p4)


# ==============================================================================
# 5. Slide 5: DINOv3 Feature Extraction Backbone
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=220, facecolor=BG_WARM)
ax.set_facecolor(BG_WARM)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.0)

# 1. Input Patch
r1 = plt.Rectangle((0.4, 1.8), 2.2, 3.5, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.2)
ax.add_patch(r1)
ax.add_patch(plt.Rectangle((0.4, 5.0), 2.2, 0.3, facecolor=OCHRE, edgecolor='none'))
ax.text(1.5, 3.4, 'Input Patch\n(512 x 512)\n\nDivided into\n14 x 14 Patches',
        ha='center', va='center', fontsize=9.5, fontweight='bold', color=TEXT_DARK)

ax.annotate('', xy=(3.2, 3.5), xytext=(2.6, 3.5),
            arrowprops=dict(facecolor=TEXT_MUTED, edgecolor='none', width=1.5, headwidth=5))

# 2. Transformer
r2 = plt.Rectangle((3.2, 1.0), 3.6, 5.1, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.2)
ax.add_patch(r2)
ax.add_patch(plt.Rectangle((3.2, 5.8), 3.6, 0.3, facecolor=TERRACOTTA, edgecolor='none'))
ax.text(5.0, 5.4, 'Frozen DINOv3 (ViT-S/14)', fontname='Georgia', ha='center', va='center',
        fontsize=11.5, fontweight='bold', color=TERRACOTTA)
ax.text(5.0, 3.4, '• Multi-Head Self-Attention\n• 12 Transformer Layers\n• Pretrained on 142M images\n• Frozen representation weights\n• Zero gradient memory overhead',
        ha='center', va='center', fontsize=9.0, fontweight='bold', color=TEXT_DARK)

ax.annotate('', xy=(7.4, 3.5), xytext=(6.8, 3.5),
            arrowprops=dict(facecolor=TEXT_MUTED, edgecolor='none', width=1.5, headwidth=5))

# 3. Output tokens
r3 = plt.Rectangle((7.4, 1.8), 2.2, 3.5, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.2)
ax.add_patch(r3)
ax.add_patch(plt.Rectangle((7.4, 5.0), 2.2, 0.3, facecolor=OLIVE, edgecolor='none'))
ax.text(8.5, 3.4, 'Dense Feature\nRepresentation\n\nN x 384 Tokens\n(Encodes Tissue\nTexture & Shape)',
        ha='center', va='center', fontsize=9.5, fontweight='bold', color=TEXT_DARK)

ax.set_title('Self-Supervised Vision Transformer Feature Extraction', fontname='Georgia',
             fontsize=13, fontweight='bold', color=TEXT_DARK, pad=12)
plt.tight_layout()
p5 = os.path.join(output_dir, "Slide_7_DINOv2_Feature_Extraction.png")
plt.savefig(p5, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm feature extraction diagram:", p5)


# ==============================================================================
# 6. Slide 4: Decoder Architecture
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=220, facecolor=BG_WARM)
ax.set_facecolor(BG_WARM)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

d_blocks = [
    (0.4, 5.0, 9.2, 1.9,
     '1. Spatial Feature Reshaping & Interpolation\n'
     'Reshape 1D patch tokens to 2D spatial grid: (Batch, 384, H/14, W/14)\n'
     'Bilinear upsampling restores continuous 512 x 512 spatial coordinates',
     CARD_BG, OCHRE),
    (0.4, 2.7, 9.2, 1.9,
     '2. 3-Layer Lightweight Convolutional Decoder\n'
     'Conv2D (384 -> 128) + BatchNorm + ReLU\n'
     'Conv2D (128 -> 64)   + BatchNorm + ReLU  ->  Conv2D (64 -> 4) + Softmax',
     CARD_BG, TERRACOTTA),
    (0.4, 0.4, 9.2, 1.9,
     '3. Multi-Class Probability Distribution (Logits)\n'
     'Channel 0: Background  |  Channel 1: Tunica Media (Outer Wall)\n'
     'Channel 2: Tunica Intima (Plaque)  |  Channel 3: Lumen (Cavity)',
     CARD_BG, OLIVE)
]

for bx, by, bw, bh, text, bg, accent in d_blocks:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=bg, edgecolor=BORDER, linewidth=1.2, zorder=2)
    ax.add_patch(rect)
    ax.add_patch(plt.Rectangle((bx, by), 0.22, bh, facecolor=accent, edgecolor='none', zorder=3))
    ax.text(bx + 0.5, by + bh/2, text, ha='left', va='center', fontsize=9.5,
            fontweight='bold', color=TEXT_DARK, zorder=4)

ax.annotate('', xy=(5.0, 4.6), xytext=(5.0, 5.0),
            arrowprops=dict(facecolor=TEXT_MUTED, edgecolor='none', width=1.5, headwidth=5))
ax.annotate('', xy=(5.0, 2.3), xytext=(5.0, 2.7),
            arrowprops=dict(facecolor=TEXT_MUTED, edgecolor='none', width=1.5, headwidth=5))

ax.set_title('Lightweight Convolutional Decoder Head', fontname='Georgia',
             fontsize=13, fontweight='bold', color=TEXT_DARK, pad=12)
plt.tight_layout()
p6 = os.path.join(output_dir, "Slide_8_Decoder_Architecture.png")
plt.savefig(p6, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm decoder diagram:", p6)


# ==============================================================================
# 7. Slide 7: Combined Loss Function Strategy
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=220, facecolor=BG_WARM)
ax.set_facecolor(BG_WARM)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

# Formula header card
eq_rect = plt.Rectangle((0.5, 4.9), 9.0, 2.1, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.2)
ax.add_patch(eq_rect)
ax.add_patch(plt.Rectangle((0.5, 4.9), 9.0, 0.08, facecolor=TERRACOTTA, edgecolor='none'))
ax.text(5.0, 6.2, r"$\mathcal{L}_{\mathrm{total}} = \mathcal{L}_{\mathrm{CE}} + \lambda \cdot \mathcal{L}_{\mathrm{clDice}}$",
        ha='center', va='center', fontsize=18, fontweight='bold', color=TEXT_DARK)
ax.text(5.0, 5.3, "Optimal Balance Weight:  " + r"$\lambda = 0.50$",
        ha='center', va='center', fontsize=11, fontweight='bold', color=TERRACOTTA)

# CE Card
p1 = plt.Rectangle((0.5, 0.6), 4.3, 3.9, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.2)
ax.add_patch(p1)
ax.add_patch(plt.Rectangle((0.5, 4.2), 4.3, 0.3, facecolor=OCHRE, edgecolor='none'))
ax.text(2.65, 3.8, r"$\mathcal{L}_{\mathrm{CE}}$ (Cross-Entropy)", fontname='Georgia',
        ha='center', va='center', fontsize=11.5, fontweight='bold', color=TEXT_DARK)
ax.text(2.65, 2.2, "• Pixel-level accuracy\n• Classifies distinct tissues\n• Penalizes color mismatch\n• Fast baseline convergence",
        ha='center', va='center', fontsize=9.0, fontweight='bold', color=TEXT_MUTED)

# clDice Card
p2 = plt.Rectangle((5.2, 0.6), 4.3, 3.9, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.2)
ax.add_patch(p2)
ax.add_patch(plt.Rectangle((5.2, 4.2), 4.3, 0.3, facecolor=OLIVE, edgecolor='none'))
ax.text(7.35, 3.8, r"$\mathcal{L}_{\mathrm{clDice}}$ (Centerline Dice)", fontname='Georgia',
        ha='center', va='center', fontsize=11.5, fontweight='bold', color=TEXT_DARK)
ax.text(7.35, 2.2, "• Global topology preservation\n• Penalizes broken loops\n• Enforces annular rings\n• Biologically valid anatomy",
        ha='center', va='center', fontsize=9.0, fontweight='bold', color=TEXT_MUTED)

ax.set_title('Composite Multi-Task Loss Objective', fontname='Georgia',
             fontsize=13, fontweight='bold', color=TEXT_DARK, pad=12)
plt.tight_layout()
p7 = os.path.join(output_dir, "Slide_10_Loss_Function_Strategy.png")
plt.savefig(p7, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm loss strategy diagram:", p7)


# ==============================================================================
# 8. Slide 8: Experimental Setup Card
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=220, facecolor=BG_WARM)
ax.set_facecolor(BG_WARM)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

configs = [
    (0.5, 5.0, 9.0, 2.0,
     'Hardware & Framework\n• PyTorch 2.x + CUDA GPU acceleration\n• Hugging Face Transformers integration\n• Memory-efficient offline tensor caching',
     CARD_BG, OCHRE),
    (0.5, 2.7, 9.0, 2.0,
     'Optimization Hyperparameters\n• Optimizer: AdamW (lr = 1e-4, weight decay = 1e-2)\n• Batch Size: 8  |  Patch Resolution: 512x512\n• Training: 20 Epochs (<2 min/epoch runtime)',
     CARD_BG, TERRACOTTA),
    (0.5, 0.4, 9.0, 2.0,
     'Validation Protocol\n• Patient-stratified split (12 training ROIs, 4 held-out test ROIs)\n• Evaluated on: Accuracy, Mean IoU, clDice, and Stenosis Grade',
     CARD_BG, OLIVE)
]

for bx, by, bw, bh, text, bg, accent in configs:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=bg, edgecolor=BORDER, linewidth=1.2)
    ax.add_patch(rect)
    ax.add_patch(plt.Rectangle((bx, by), 0.22, bh, facecolor=accent, edgecolor='none'))
    ax.text(bx + 0.5, by + bh/2, text, ha='left', va='center', fontsize=9.5,
            fontweight='bold', color=TEXT_DARK)

ax.set_title('Experimental Implementation & Evaluation Configuration', fontname='Georgia',
             fontsize=13, fontweight='bold', color=TEXT_DARK, pad=12)
plt.tight_layout()
p8 = os.path.join(output_dir, "Slide_11_Experimental_Setup_Card.png")
plt.savefig(p8, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print("Saved warm experimental setup card:", p8)

print("\n--- ALL EDITORIAL DIAGRAMS SUCCESSFULLY GENERATED ---")
