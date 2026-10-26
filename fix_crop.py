from PIL import Image
import os
import shutil

vis_path = r"d:\Project topics\dinov3-main\output\visualizations\C18-L1_roi_1_prediction.png"
full_vis = Image.open(vis_path)
w, h = full_vis.size

crop_box = (int(w * 0.007), int(h * 0.038), int(w * 0.328), int(h * 0.435))
artery_crop = full_vis.crop(crop_box)
artery_crop = artery_crop.resize((960, 640), Image.LANCZOS)

clean_path = r"d:\Project topics\dinov3-main\ppt_images\Slide_3_Coronary_Artery_Histology.png"
artery_crop.save(clean_path, optimize=True, quality=95)

desktop_ppt_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop\PPT_Images"
shutil.copy2(clean_path, os.path.join(desktop_ppt_dir, "Slide_3_Coronary_Artery_Histology.png"))
print("Saved clean crop:", os.path.getsize(clean_path) / 1024, "KB")
