import os
import matplotlib.pyplot as plt
import numpy as np
import shutil
from PIL import Image

desktop_ppt_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop\PPT_Images"
workspace_ppt_dir = r"d:\Project topics\dinov3-main\ppt_images"
os.makedirs(desktop_ppt_dir, exist_ok=True)
os.makedirs(workspace_ppt_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# ==============================================================================
# 1. REGENERATE GRAPH FOR SLIDE 13: With Verified Thesis clDice (0.514 vs 0.729)
# ==============================================================================
fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=200)

metrics = ['Accuracy (%)', 'Mean IoU (x100)', 'Vessel Continuity (clDice)']
baseline_vals = [57.33, 30.00, 51.40]
proposed_vals = [64.17, 38.10, 72.90]
improvements = ['+6.84%', '+27.0%', '+41.8%']

x = np.arange(len(metrics))
width = 0.35

rects1 = ax.bar(x - width/2, baseline_vals, width, label='Baseline Model (Cross-Entropy)', color='#8E9AAF', edgecolor='#4A5568')
rects2 = ax.bar(x + width/2, proposed_vals, width, label='Proposed Model (+ clDice Topology)', color='#1D3557', edgecolor='#0D1B2A')

ax.set_ylabel('Score / Metric Value', fontsize=12, fontweight='bold', color='#1D3557')
ax.set_title('Quantitative Performance Comparison', fontsize=14, fontweight='bold', pad=15, color='#1D3557')
ax.set_xticks(x)
ax.set_xticklabels(['Accuracy\n(%)', 'Mean IoU\n(x100)', 'Vessel Continuity\n(clDice: 0.514 -> 0.729)'], fontsize=10.5, fontweight='bold')
ax.legend(frameon=True, facecolor='#F8F9FA', edgecolor='#CED4DA', fontsize=10, loc='upper left')
ax.set_ylim(0, 88)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

for i in range(len(metrics)):
    b_val = baseline_vals[i]
    p_val = proposed_vals[i]
    if i == 2:
        # Display as decimal for clDice
        ax.annotate(f"0.514", (x[i] - width/2, b_val + 2), ha='center', va='bottom', fontsize=9.5, color='#4A5568')
        ax.annotate(f"0.729\n(+41.8%)", (x[i] + width/2, p_val + 2), ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1D3557')
    else:
        ax.annotate(f"{b_val:.1f}%", (x[i] - width/2, b_val + 2), ha='center', va='bottom', fontsize=9.5, color='#4A5568')
        ax.annotate(f"{p_val:.1f}%\n({improvements[i]})", (x[i] + width/2, p_val + 2), ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1D3557')

plt.tight_layout()
graph_path = os.path.join(workspace_ppt_dir, "Slide_15_Results_Performance_Graph.png")
plt.savefig(graph_path, bbox_inches='tight')
plt.close()
shutil.copy2(graph_path, os.path.join(desktop_ppt_dir, "Slide_15_Results_Performance_Graph.png"))
print("Regenerated Slide 13/15 graph with verified clDice values: 0.514 vs 0.729")

# ==============================================================================
# 2. ENLARGE LABELS ON 6-PANEL PREDICTION IMAGE FOR SLIDE 12
# ==============================================================================
# Let's rebuild the figure with large, clear font titles for each panel
vis_src = r"d:\Project topics\dinov3-main\output\visualizations\C18-L1_roi_1_prediction.png"
if os.path.exists(vis_src):
    raw_img = Image.open(vis_src)
    w, h = raw_img.size
    
    # Subplots approximate coordinates in the original 18x12 grid:
    # 0,0: Original Image
    # 0,1: Ground Truth
    # 0,2: Prediction
    # 1,0: GT Overlay
    # 1,1: Prediction Overlay
    # 1,2: Metrics
    
    # Let's crop the 5 visual panels and assemble with extra-large, prominent titles!
    cell_w = int(w / 3)
    cell_h = int(h / 2)
    
    # Crop each panel without its old small title
    # Header area is roughly 0.05 * cell_h
    p_orig = raw_img.crop((int(w*0.01), int(h*0.04), int(w*0.328), int(h*0.48)))
    p_gt   = raw_img.crop((int(w*0.345), int(h*0.04), int(w*0.655), int(h*0.48)))
    p_pred = raw_img.crop((int(w*0.672), int(h*0.04), int(w*0.99), int(h*0.48)))
    
    p_gto  = raw_img.crop((int(w*0.01), int(h*0.54), int(w*0.328), int(h*0.98)))
    p_predo= raw_img.crop((int(w*0.345), int(h*0.54), int(w*0.655), int(h*0.98)))
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 11), dpi=200)
    
    axes[0, 0].imshow(p_orig)
    axes[0, 0].set_title("1. Original Histology (WSI)", fontsize=16, fontweight='bold', pad=8, color='#1E293B')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(p_gt)
    axes[0, 1].set_title("2. Pathologist Ground Truth", fontsize=16, fontweight='bold', pad=8, color='#1E293B')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(p_pred)
    axes[0, 2].set_title("3. Model Prediction", fontsize=16, fontweight='bold', pad=8, color='#1D4ED8')
    axes[0, 2].axis('off')
    
    axes[1, 0].imshow(p_gto)
    axes[1, 0].set_title("4. Ground Truth Overlay", fontsize=16, fontweight='bold', pad=8, color='#1E293B')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(p_predo)
    axes[1, 1].set_title("5. Prediction Overlay (50%)", fontsize=16, fontweight='bold', pad=8, color='#15803D')
    axes[1, 1].axis('off')
    
    # Legend & Summary card in 1,2
    axes[1, 2].axis('off')
    legend_text = (
        "Tissue Classes:\n"
        "  • Dark Blue: Background\n"
        "  • Light Blue: Tunica Media (Muscular Wall)\n"
        "  • Green/Orange: Tunica Intima (Plaque)\n"
        "  • Dark Red: Lumen (Blood Channel)\n\n"
        "Visual Evaluation:\n"
        "  ✓ Preserves continuous annular loop\n"
        "  ✓ Substantially reduces wall fragmentation\n"
        "  ✓ High concordance on lumen contour"
    )
    axes[1, 2].text(0.05, 0.5, legend_text, fontsize=13, fontweight='bold', color='#1E293B',
                     family='monospace', verticalalignment='center',
                     bbox=dict(boxstyle='round,pad=0.8', facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=2))
    
    plt.tight_layout()
    large_vis_path = os.path.join(workspace_ppt_dir, "Slide_15_Final_Results_Prediction.png")
    plt.savefig(large_vis_path, bbox_inches='tight')
    plt.close()
    shutil.copy2(large_vis_path, os.path.join(desktop_ppt_dir, "Slide_15_Final_Results_Prediction.png"))
    print("Regenerated 6-panel prediction image with extra-large labels")
