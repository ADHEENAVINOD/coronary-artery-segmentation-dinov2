import os
import matplotlib.pyplot as plt
import shutil
from PIL import Image

desktop_ppt_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop\PPT_Images"
workspace_ppt_dir = r"d:\Project topics\dinov3-main\ppt_images"

vis_src = r"d:\Project topics\dinov3-main\output\visualizations\C18-L1_roi_1_prediction.png"
if os.path.exists(vis_src):
    raw_img = Image.open(vis_src)
    w, h = raw_img.size
    
    p_orig = raw_img.crop((int(w*0.01), int(h*0.04), int(w*0.328), int(h*0.48)))
    p_gt   = raw_img.crop((int(w*0.345), int(h*0.04), int(w*0.655), int(h*0.48)))
    p_pred = raw_img.crop((int(w*0.672), int(h*0.04), int(w*0.99), int(h*0.48)))
    
    p_gto  = raw_img.crop((int(w*0.01), int(h*0.54), int(w*0.328), int(h*0.98)))
    p_predo= raw_img.crop((int(w*0.345), int(h*0.54), int(w*0.655), int(h*0.98)))
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), dpi=250)
    
    # Row 1
    axes[0, 0].imshow(p_orig)
    axes[0, 0].set_title("1. Original Histology", fontsize=22, fontweight='bold', pad=12, color='#0F172A')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(p_gt)
    axes[0, 1].set_title("2. Pathologist Ground Truth", fontsize=22, fontweight='bold', pad=12, color='#0F172A')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(p_pred)
    axes[0, 2].set_title("3. Model Prediction", fontsize=22, fontweight='bold', pad=12, color='#1D4ED8')
    axes[0, 2].axis('off')
    
    # Row 2
    axes[1, 0].imshow(p_gto)
    axes[1, 0].set_title("4. Ground Truth Overlay", fontsize=22, fontweight='bold', pad=12, color='#0F172A')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(p_predo)
    axes[1, 1].set_title("5. Prediction Overlay (50%)", fontsize=22, fontweight='bold', pad=12, color='#15803D')
    axes[1, 1].axis('off')
    
    # Legend & Summary card in 1,2
    axes[1, 2].axis('off')
    legend_text = (
        "Tissue Classes:\n"
        "  • Dark Blue: Background\n"
        "  • Light Blue: Tunica Media (Wall)\n"
        "  • Green/Orange: Tunica Intima (Plaque)\n"
        "  • Dark Red: Lumen (Flow Channel)\n\n"
        "Visual Evaluation:\n"
        "  ✓ Preserves continuous annular loop\n"
        "  ✓ Substantially reduces fragmentation\n"
        "  ✓ High concordance on lumen contour"
    )
    axes[1, 2].text(0.04, 0.5, legend_text, fontsize=15, fontweight='bold', color='#0F172A',
                     family='monospace', verticalalignment='center',
                     bbox=dict(boxstyle='round,pad=1.0', facecolor='#F8FAFC', edgecolor='#94A3B8', linewidth=2.5))
    
    plt.tight_layout()
    large_vis_path = os.path.join(workspace_ppt_dir, "Slide_12_Qualitative_Enlarged_Labels.png")
    plt.savefig(large_vis_path, bbox_inches='tight')
    plt.close()
    
    # Also save as Slide_15_Final_Results_Prediction.png for convenience
    shutil.copy2(large_vis_path, os.path.join(desktop_ppt_dir, "Slide_12_Qualitative_Enlarged_Labels.png"))
    shutil.copy2(large_vis_path, os.path.join(desktop_ppt_dir, "Slide_15_Final_Results_Prediction.png"))
    print("Generated ultra-large labels image successfully!")
