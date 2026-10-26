import os
from PIL import Image, ImageDraw, ImageFont
import shutil

# 1. Create a dedicated folder on Desktop for PPT Images
desktop_ppt_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop\PPT_Images"
os.makedirs(desktop_ppt_dir, exist_ok=True)
workspace_ppt_dir = r"d:\Project topics\dinov3-main\ppt_images"
os.makedirs(workspace_ppt_dir, exist_ok=True)

# 2. Extract and optimize the single coronary artery image for Slide 3
vis_path = r"d:\Project topics\dinov3-main\output\visualizations\C18-L1_roi_1_prediction.png"
if os.path.exists(vis_path):
    full_vis = Image.open(vis_path)
    w, h = full_vis.size
    
    # Top-left cell contains the "Original Image" (w/3 wide, h/2 tall)
    # The image is roughly x: [0, w//3], y: [h*0.04, h//2]
    crop_x1 = int(w * 0.005)
    crop_y1 = int(h * 0.04)
    crop_x2 = int(w * 0.325)
    crop_y2 = int(h * 0.495)
    
    artery_crop = full_vis.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    
    # Resize to standard crisp PPT dimensions (e.g. 1000 x 750, ~400 KB)
    artery_crop = artery_crop.resize((1000, 750), Image.LANCZOS)
    
    # Save Clean Version
    clean_slide3_path = os.path.join(workspace_ppt_dir, "Slide_3_Coronary_Artery_Histology.png")
    artery_crop.save(clean_slide3_path, optimize=True, quality=95)
    shutil.copy2(clean_slide3_path, os.path.join(desktop_ppt_dir, "Slide_3_Coronary_Artery_Histology.png"))
    print(f"Created Slide 3 clean histology image: {clean_slide3_path}")
    
    # Create Annotated Version with anatomical labels for Lumen, Intima, Media
    annotated_img = artery_crop.copy()
    draw = ImageDraw.Draw(annotated_img)
    
    # Draw nice anatomical pointer tags
    # Lumen is center (approx 500, 375)
    # Media is muscular ring (approx 350, 480)
    # Intima is inner layer (approx 420, 420)
    # Plaque / adventitia
    try:
        font = ImageFont.truetype("arial.ttf", 26)
        font_sm = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        font_sm = font

    # Draw label boxes
    labels = [
        ("1. Lumen (Blood flow channel)", (20, 25), "#D90429"),
        ("2. Tunica Intima (Plaque accumulation)", (20, 70), "#2B9348"),
        ("3. Tunica Media (Muscular vessel wall)", (20, 115), "#0077B6")
    ]
    for text, (lx, ly), color in labels:
        # Background pill
        draw.rectangle([lx, ly, lx + 440, ly + 36], fill="white", outline=color, width=2)
        draw.text((lx + 10, ly + 4), text, fill=color, font=font_sm)
        
    annotated_slide3_path = os.path.join(workspace_ppt_dir, "Slide_3_Coronary_Artery_Annotated.png")
    annotated_img.save(annotated_slide3_path, optimize=True, quality=95)
    shutil.copy2(annotated_slide3_path, os.path.join(desktop_ppt_dir, "Slide_3_Coronary_Artery_Annotated.png"))
    print(f"Created Slide 3 annotated histology image: {annotated_slide3_path}")

# 3. Optimize and copy Slide 15 Final Results Image
slide15_dest = os.path.join(desktop_ppt_dir, "Slide_15_Final_Results_Prediction.png")
shutil.copy2(vis_path, slide15_dest)
shutil.copy2(vis_path, os.path.join(workspace_ppt_dir, "Slide_15_Final_Results_Prediction.png"))
print(f"Created Slide 15 results image: {slide15_dest}")

# 4. Check file sizes
for fname in os.listdir(desktop_ppt_dir):
    fpath = os.path.join(desktop_ppt_dir, fname)
    fsize_kb = os.path.getsize(fpath) / 1024
    print(f"Desktop PPT Image: {fname} -> {fsize_kb:.1f} KB")
