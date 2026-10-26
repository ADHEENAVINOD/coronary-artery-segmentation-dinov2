import os
import matplotlib.pyplot as plt
import numpy as np
import shutil

desktop_ppt_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop\PPT_Images"
workspace_ppt_dir = r"d:\Project topics\dinov3-main\ppt_images"
os.makedirs(desktop_ppt_dir, exist_ok=True)
os.makedirs(workspace_ppt_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# ==============================================================================
# 1. SLIDE 6: Dataset and Preprocessing Workflow
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

steps = [
    (0.5, 5.2, 9.0, 1.8, '1. Whole Slide Images (WSI)\nGigapixel human coronary autopsy slides (H&E & Movat stains)\nOriginal resolution: >40,000 x 40,000 pixels (1–2.5 GB)', '#EFF6FF', '#1D4ED8'),
    (0.5, 2.9, 9.0, 1.8, '2. QuPath Expert Annotation\nManual polygon delineation of 16 clinical artery ROIs\nExported as standard GeoJSON boundary coordinates', '#F0FDF4', '#15803D'),
    (0.5, 0.6, 9.0, 1.8, '3. Dynamic Patching & Caching\nCropped into 512x512 patches with stride overlap\nPrecomputed .npy tensor cache -> RAM drops to <100 MB', '#FEF3C7', '#B45309')
]

for bx, by, bw, bh, text, bg, border in steps:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=bg, edgecolor=border, linewidth=2, transform=ax.transData, zorder=2)
    ax.add_patch(rect)
    ax.text(bx + bw/2, by + bh/2, text, ha='center', va='center', fontsize=9.5, fontweight='bold', color=border, zorder=3)

ax.annotate('', xy=(5.0, 4.7), xytext=(5.0, 5.2), arrowprops=dict(facecolor='#1E293B', width=2, headwidth=6))
ax.annotate('', xy=(5.0, 2.4), xytext=(5.0, 2.9), arrowprops=dict(facecolor='#1E293B', width=2, headwidth=6))

ax.set_title('Dataset Acquisition & Preparation Pipeline', fontsize=12.5, fontweight='bold', color='#1E293B', pad=10)
plt.tight_layout()
s6_path = os.path.join(workspace_ppt_dir, "Slide_6_Dataset_Preprocessing_Workflow.png")
plt.savefig(s6_path, bbox_inches='tight')
plt.close()
shutil.copy2(s6_path, os.path.join(desktop_ppt_dir, "Slide_6_Dataset_Preprocessing_Workflow.png"))
print("Generated Slide 6 image")

# ==============================================================================
# 2. SLIDE 7: DINOv2 Feature Extraction
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)

# Input Patch
rect_in = plt.Rectangle((0.4, 1.8), 2.2, 3.4, facecolor='#F1F5F9', edgecolor='#475569', linewidth=2)
ax.add_patch(rect_in)
ax.text(1.5, 3.5, 'Input Patch\n(512 x 512)\n\nDivided into\n14x14 Patches', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

ax.annotate('', xy=(3.2, 3.5), xytext=(2.6, 3.5), arrowprops=dict(facecolor='#1E293B', width=2, headwidth=6))

# ViT Transformer Backbone
rect_vit = plt.Rectangle((3.2, 1.0), 3.5, 5.0, facecolor='#DBEAFE', edgecolor='#1D4ED8', linewidth=2.5)
ax.add_patch(rect_vit)
ax.text(4.95, 5.2, 'Frozen DINOv2-Small', ha='center', va='center', fontsize=11, fontweight='bold', color='#1D4ED8')
ax.text(4.95, 3.4, '• Multi-Head Self-Attention\n• 12 Transformer Layers\n• Pre-trained on 142M images\n• Frozen representation weights\n• Zero gradient overhead', 
        ha='center', va='center', fontsize=9, fontweight='bold', color='#1E40AF')

ax.annotate('', xy=(7.3, 3.5), xytext=(6.7, 3.5), arrowprops=dict(facecolor='#1E293B', width=2, headwidth=6))

# Output Feature Tokens
rect_out = plt.Rectangle((7.3, 1.8), 2.3, 3.4, facecolor='#DCFCE7', edgecolor='#15803D', linewidth=2)
ax.add_patch(rect_out)
ax.text(8.45, 3.5, 'Dense Feature\nRepresentation\n\nN x 384 Tokens\n(Encodes Tissue\nTexture & Shape)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#15803D')

ax.set_title('Self-Supervised Vision Transformer Feature Extraction', fontsize=12.5, fontweight='bold', color='#1E293B', pad=12)
plt.tight_layout()
s7_path = os.path.join(workspace_ppt_dir, "Slide_7_DINOv2_Feature_Extraction.png")
plt.savefig(s7_path, bbox_inches='tight')
plt.close()
shutil.copy2(s7_path, os.path.join(desktop_ppt_dir, "Slide_7_DINOv2_Feature_Extraction.png"))
print("Generated Slide 7 image")

# ==============================================================================
# 3. SLIDE 8: Segmentation Model Architecture (Decoder Head)
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

blocks = [
    (0.4, 5.0, 9.2, 1.8, '1. Feature Reshaping & Interpolation\nReshape 1D tokens to 2D grid: (B, 384, H/14, W/14)\nBilinear upsampling (factor 14) restores native 512x512 resolution', '#EFF6FF', '#1D4ED8'),
    (0.4, 2.8, 9.2, 1.8, '2. 3-Layer Convolutional Decoder Head\nConv2D (384 -> 128) + BatchNorm + ReLU\nConv2D (128 -> 64)   + BatchNorm + ReLU\nConv2D (64 -> 4 classes) + Softmax', '#F0FDF4', '#15803D'),
    (0.4, 0.6, 9.2, 1.8, '3. Multi-Class Probability Maps (Logits)\nChannel 0: Background  |  Channel 1: Tunica Media (Wall)\nChannel 2: Tunica Intima (Plaque)  |  Channel 3: Lumen (Channel)', '#FEF3C7', '#B45309')
]

for bx, by, bw, bh, text, bg, border in blocks:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=bg, edgecolor=border, linewidth=2, transform=ax.transData)
    ax.add_patch(rect)
    ax.text(bx + bw/2, by + bh/2, text, ha='center', va='center', fontsize=9.5, fontweight='bold', color=border)

ax.annotate('', xy=(5.0, 4.6), xytext=(5.0, 5.0), arrowprops=dict(facecolor='#1E293B', width=2, headwidth=6))
ax.annotate('', xy=(5.0, 2.4), xytext=(5.0, 2.8), arrowprops=dict(facecolor='#1E293B', width=2, headwidth=6))

ax.set_title('Lightweight Convolutional Decoder Architecture', fontsize=12.5, fontweight='bold', color='#1E293B', pad=10)
plt.tight_layout()
s8_path = os.path.join(workspace_ppt_dir, "Slide_8_Decoder_Architecture.png")
plt.savefig(s8_path, bbox_inches='tight')
plt.close()
shutil.copy2(s8_path, os.path.join(desktop_ppt_dir, "Slide_8_Decoder_Architecture.png"))
print("Generated Slide 8 image")

# ==============================================================================
# 4. SLIDE 9: Topology-Aware Learning (clDice & Soft-Skeletonization)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 4.2), dpi=200)

r_in, r_out = 0.55, 0.85
th = np.linspace(0, 2*np.pi, 200)

ax1.set_xlim(-1.2, 1.2)
ax1.set_ylim(-1.2, 1.2)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('Differentiable Soft-Morphology\n(Continuous Min/Max Pooling)', fontsize=10.5, fontweight='bold', color='#1D3557')
x_in, y_in = r_in * np.cos(th), r_in * np.sin(th)
x_out, y_out = r_out * np.cos(th), r_out * np.sin(th)
ax1.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]), color='#457B9D', alpha=0.7)
ax1.text(0, -1.1, 'Iterative Soft-Erode & Soft-Dilate\n(Over T=5 Iterations)', ha='center', fontsize=8.5, fontweight='bold', color='#1D3557')

ax2.set_xlim(-1.2, 1.2)
ax2.set_ylim(-1.2, 1.2)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('Extracted Centerline Skeleton S(V)\n(Topological Homotopy)', fontsize=10.5, fontweight='bold', color='#2A9D8F')
r_mid = (r_in + r_out) / 2
x_mid, y_mid = r_mid * np.cos(th), r_mid * np.sin(th)
ax2.plot(x_mid, y_mid, color='#E63946', linewidth=3.5, label='Centerline')
ax2.text(0, -1.1, 'Enforces Ring Continuity (clDice)\nZero Broken Boundaries', ha='center', fontsize=8.5, fontweight='bold', color='#2A9D8F')

plt.tight_layout()
s9_path = os.path.join(workspace_ppt_dir, "Slide_9_clDice_Skeletonization.png")
plt.savefig(s9_path, bbox_inches='tight')
plt.close()
shutil.copy2(s9_path, os.path.join(desktop_ppt_dir, "Slide_9_clDice_Skeletonization.png"))
print("Generated Slide 9 image")

# ==============================================================================
# 5. SLIDE 10: Training Strategy and Combined Loss Function
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

eq_rect = plt.Rectangle((0.5, 4.8), 9.0, 2.2, facecolor='#F8FAFC', edgecolor='#1E293B', linewidth=2.5)
ax.add_patch(eq_rect)
ax.text(5.0, 6.2, r"$\mathcal{L}_{\mathrm{total}} = \mathcal{L}_{\mathrm{CE}} + \lambda \cdot \mathcal{L}_{\mathrm{clDice}}$", 
        ha='center', va='center', fontsize=18, fontweight='bold', color='#1E293B')
ax.text(5.0, 5.2, "Optimal Balance Weight:  " + r"$\lambda = 0.50$", 
        ha='center', va='center', fontsize=11, fontweight='bold', color='#D90429')

p1 = plt.Rectangle((0.5, 0.6), 4.3, 3.8, facecolor='#EFF6FF', edgecolor='#1D4ED8', linewidth=2)
ax.add_patch(p1)
ax.text(2.65, 3.8, r"$\mathcal{L}_{\mathrm{CE}}$ (Cross-Entropy)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1D4ED8')
ax.text(2.65, 2.2, "• Pixel-level accuracy\n• Classifies distinct tissues\n• Penalizes color mismatch\n• Fast baseline convergence", 
        ha='center', va='center', fontsize=9, fontweight='bold', color='#1E40AF')

p2 = plt.Rectangle((5.2, 0.6), 4.3, 3.8, facecolor='#F0FDF4', edgecolor='#15803D', linewidth=2)
ax.add_patch(p2)
ax.text(7.35, 3.8, r"$\mathcal{L}_{\mathrm{clDice}}$ (Centerline Dice)", ha='center', va='center', fontsize=11, fontweight='bold', color='#15803D')
ax.text(7.35, 2.2, "• Global topology preservation\n• Penalizes broken loops\n• Enforces annular rings\n• Biologically valid anatomy", 
        ha='center', va='center', fontsize=9, fontweight='bold', color='#166534')

ax.set_title('Multi-Task Composite Loss Objective', fontsize=12.5, fontweight='bold', color='#1E293B', pad=10)
plt.tight_layout()
s10_path = os.path.join(workspace_ppt_dir, "Slide_10_Loss_Function_Strategy.png")
plt.savefig(s10_path, bbox_inches='tight')
plt.close()
shutil.copy2(s10_path, os.path.join(desktop_ppt_dir, "Slide_10_Loss_Function_Strategy.png"))
print("Generated Slide 10 image")

# ==============================================================================
# 6. SLIDE 11: Experimental Setup and Evaluation Protocol
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)

configs = [
    (0.5, 5.0, 9.0, 2.0, 'Hardware & Framework\n• PyTorch 2.x + CUDA GPU acceleration\n• Hugging Face Transformers integration\n• Memory-efficient offline tensor caching', '#F8FAFC', '#334155'),
    (0.5, 2.7, 9.0, 2.0, 'Optimization Hyperparameters\n• Optimizer: AdamW (lr = 1e-4, weight decay = 1e-2)\n• Batch Size: 8  |  Patch Resolution: 512x512\n• Training: 20 Epochs (<2 min/epoch runtime)', '#EFF6FF', '#1D4ED8'),
    (0.5, 0.4, 9.0, 2.0, 'Validation Protocol\n• Patient-stratified split (12 training ROIs, 4 held-out test ROIs)\n• Evaluated on: Accuracy, Mean IoU, clDice, and Stenosis Grade', '#F0FDF4', '#15803D')
]

for bx, by, bw, bh, text, bg, border in configs:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=bg, edgecolor=border, linewidth=2, transform=ax.transData)
    ax.add_patch(rect)
    ax.text(bx + bw/2, by + bh/2, text, ha='center', va='center', fontsize=9.5, fontweight='bold', color=border)

ax.set_title('Experimental Implementation & Evaluation Configuration', fontsize=12.5, fontweight='bold', color='#1E293B', pad=10)
plt.tight_layout()
s11_path = os.path.join(workspace_ppt_dir, "Slide_11_Experimental_Setup_Card.png")
plt.savefig(s11_path, bbox_inches='tight')
plt.close()
shutil.copy2(s11_path, os.path.join(desktop_ppt_dir, "Slide_11_Experimental_Setup_Card.png"))
print("Generated Slide 11 image")

print("All missing presentation figures generated successfully!")
