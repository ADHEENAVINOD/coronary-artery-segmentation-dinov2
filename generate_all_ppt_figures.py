import os
import matplotlib.pyplot as plt
import numpy as np
import shutil
from PIL import Image, ImageDraw, ImageFont

desktop_ppt_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop\PPT_Images"
workspace_ppt_dir = r"d:\Project topics\dinov3-main\ppt_images"
os.makedirs(desktop_ppt_dir, exist_ok=True)
os.makedirs(workspace_ppt_dir, exist_ok=True)

# Set global matplotlib style
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# ==============================================================================
# 1. GRAPH FOR SLIDE 15: Baseline vs. Proposed Topology-Constrained Model
# ==============================================================================
fig, ax = plt.subplots(figsize=(7, 4.8), dpi=200)

metrics = ['Accuracy (%)', 'Mean IoU (x100)', 'Vessel Continuity (clDice %)']
baseline_vals = [57.33, 30.00, 81.20]
proposed_vals = [64.17, 38.10, 94.10]
improvements = ['+6.84%', '+27.0%', '+15.9%']

x = np.arange(len(metrics))
width = 0.35

rects1 = ax.bar(x - width/2, baseline_vals, width, label='Baseline Model (Cross-Entropy)', color='#8E9AAF', edgecolor='#4A5568')
rects2 = ax.bar(x + width/2, proposed_vals, width, label='Proposed Model (+ clDice Topology)', color='#1D3557', edgecolor='#0D1B2A')

ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold', color='#1D3557')
ax.set_title('Quantitative Performance Comparison', fontsize=14, fontweight='bold', pad=15, color='#1D3557')
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=10.5, fontweight='bold')
ax.legend(frameon=True, facecolor='#F8F9FA', edgecolor='#CED4DA', fontsize=10, loc='upper left')
ax.set_ylim(0, 110)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

# Add values above bars
for i in range(len(metrics)):
    b_val = baseline_vals[i]
    p_val = proposed_vals[i]
    ax.annotate(f"{b_val:.1f}%", (x[i] - width/2, b_val + 2), ha='center', va='bottom', fontsize=9.5, color='#4A5568')
    ax.annotate(f"{p_val:.1f}%\n({improvements[i]})", (x[i] + width/2, p_val + 2), ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1D3557')

plt.tight_layout()
graph_path = os.path.join(workspace_ppt_dir, "Slide_15_Results_Performance_Graph.png")
plt.savefig(graph_path, bbox_inches='tight')
plt.close()
shutil.copy2(graph_path, os.path.join(desktop_ppt_dir, "Slide_15_Results_Performance_Graph.png"))
print("Generated Slide 15 graph:", graph_path)

# ==============================================================================
# 2. IMAGE FOR SLIDE 4: Problem Statement (The Broken Ring / Topology Failure)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.8), dpi=200)

# Simulate circular ground truth
theta = np.linspace(0, 2*np.pi, 200)
r_inner, r_outer = 0.5, 0.85

# Left: Standard Loss Failure (Broken ring, disconnected fragments)
ax1.set_xlim(-1.2, 1.2)
ax1.set_ylim(-1.2, 1.2)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('Standard Pixel Loss (Cross-Entropy)\nTopology Violation', fontsize=11, fontweight='bold', color='#E63946', pad=10)

# Draw broken fragments
theta1 = np.linspace(0.2, 1.8, 60)
theta2 = np.linspace(2.4, 4.0, 60)
theta3 = np.linspace(4.6, 5.8, 50)
for th in [theta1, theta2, theta3]:
    x_in, y_in = r_inner * np.cos(th), r_inner * np.sin(th)
    x_out, y_out = r_outer * np.cos(th), r_outer * np.sin(th)
    ax1.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]), color='#457B9D', alpha=0.85)

# Add random noise/speckle
np.random.seed(42)
noise_x = np.random.uniform(-0.3, 0.3, 12)
noise_y = np.random.uniform(-0.3, 0.3, 12)
ax1.scatter(noise_x, noise_y, color='#E63946', s=30, alpha=0.8, marker='s')
ax1.text(0, -1.1, 'Gaps in Arterial Ring & False Lumen Islands\n(Invalid for Clinical Caliber Measurement)', 
         ha='center', fontsize=8.5, color='#E63946', fontweight='bold')

# Right: Required Anatomy (Continuous Closed Loop)
ax2.set_xlim(-1.2, 1.2)
ax2.set_ylim(-1.2, 1.2)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('Required Vascular Anatomy\nTopology Preserved (clDice)', fontsize=11, fontweight='bold', color='#2A9D8F', pad=10)

x_in, y_in = r_inner * np.cos(theta), r_inner * np.sin(theta)
x_out, y_out = r_outer * np.cos(theta), r_outer * np.sin(theta)
ax2.fill(np.append(x_in, x_out[::-1]), np.append(y_in, y_out[::-1]), color='#2A9D8F', alpha=0.85)
# Lumen center
ax2.text(0, 0, 'Lumen\n(Intact)', ha='center', va='center', fontsize=9, fontweight='bold', color='#1D3557')
ax2.text(0, -1.1, 'Continuous Annular Artery Wall\n(Enforces Homotopy Equivalence)', 
         ha='center', fontsize=8.5, color='#2A9D8F', fontweight='bold')

plt.tight_layout()
prob_path = os.path.join(workspace_ppt_dir, "Slide_4_Problem_Statement_Topology.png")
plt.savefig(prob_path, bbox_inches='tight')
plt.close()
shutil.copy2(prob_path, os.path.join(desktop_ppt_dir, "Slide_4_Problem_Statement_Topology.png"))
print("Generated Slide 4 problem graphic:", prob_path)

# ==============================================================================
# 3. IMAGE FOR SLIDE 8 / 10: Proposed Architecture Flowchart
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.5)

boxes = [
    (0.4, 1.0, 1.6, 1.6, 'Histology Patch\n(512x512)', '#E2E8F0', '#475569'),
    (2.4, 0.8, 1.9, 2.0, 'Frozen DINOv2\nViT Encoder\n(384-d Tokens)', '#DBEAFE', '#1D4ED8'),
    (4.7, 0.9, 1.7, 1.8, 'Convolutional\nDecoder Head\n(3 Conv Layers)', '#DCFCE7', '#15803D'),
    (6.8, 0.9, 1.5, 1.8, 'Multi-Class\nSegmentation\nLogits', '#FEF3C7', '#B45309'),
    (8.7, 0.7, 1.1, 2.2, 'clDice Loss\n&\nStenosis %', '#FEE2E2', '#B91C1C')
]

for bx, by, bw, bh, text, facecolor, edgecolor in boxes:
    rect = plt.Rectangle((bx, by), bw, bh, facecolor=facecolor, edgecolor=edgecolor, linewidth=2, transform=ax.transData, zorder=2)
    ax.add_patch(rect)
    ax.text(bx + bw/2, by + bh/2, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color=edgecolor, zorder=3)

# Arrows between boxes
arrows = [(2.0, 1.8, 2.4, 1.8), (4.3, 1.8, 4.7, 1.8), (6.4, 1.8, 6.8, 1.8), (8.3, 1.8, 8.7, 1.8)]
for x1, y1, x2, y2 in arrows:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(facecolor='#475569', edgecolor='#475569', width=1.8, headwidth=6), zorder=4)

ax.set_title('End-to-End Proposed Pipeline Architecture', fontsize=12, fontweight='bold', color='#1E293B', pad=10)
plt.tight_layout()
arch_path = os.path.join(workspace_ppt_dir, "Slide_8_Methodology_Architecture.png")
plt.savefig(arch_path, bbox_inches='tight')
plt.close()
shutil.copy2(arch_path, os.path.join(desktop_ppt_dir, "Slide_8_Methodology_Architecture.png"))
print("Generated Slide 8 architecture graphic:", arch_path)

# ==============================================================================
# 4. IMAGE FOR SLIDE 17: Conclusion (Clinical Translation & Impact)
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=200)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)

# Create 3 summary cards
cards = [
    (0.4, 0.5, 2.7, 3.0, '1. Foundation Model\nEfficiency\n\n• Frozen DINOv2\n• <100 MB RAM\n• 5.8h -> <2 min training\n• No GPU memory crashes', '#EFF6FF', '#1E40AF'),
    (3.5, 0.5, 2.9, 3.0, '2. Topological\nIntegrity\n\n• Differentiable clDice\n• Annular loop continuity\n• +6.8% accuracy gain\n• Anatomically correct', '#F0FDF4', '#166534'),
    (6.8, 0.5, 2.8, 3.0, '3. Automated Clinical\nGrading\n\n• Quantitative Stenosis %\n• AHA severity grading\n• 92.1% pathologist concordance\n• Objective & reproducible', '#FFFBEB', '#92400E')
]

for cx, cy, cw, ch, text, bg, border in cards:
    rect = plt.Rectangle((cx, cy), cw, ch, facecolor=bg, edgecolor=border, linewidth=2, transform=ax.transData)
    ax.add_patch(rect)
    ax.text(cx + cw/2, cy + ch/2, text, ha='center', va='center', fontsize=9, fontweight='bold', color=border)

ax.set_title('Key Thesis Contributions & Clinical Impact', fontsize=13, fontweight='bold', color='#1E293B', pad=12)
plt.tight_layout()
concl_path = os.path.join(workspace_ppt_dir, "Slide_17_Conclusion_Clinical_Impact.png")
plt.savefig(concl_path, bbox_inches='tight')
plt.close()
shutil.copy2(concl_path, os.path.join(desktop_ppt_dir, "Slide_17_Conclusion_Clinical_Impact.png"))
print("Generated Slide 17 conclusion graphic:", concl_path)

print("All PPT graphics generated and copied to Desktop!")
