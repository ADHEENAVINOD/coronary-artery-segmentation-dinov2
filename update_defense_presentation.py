# -*- coding: utf-8 -*-
"""
Script to apply exact corrections to the defense presentation slides.
Preserves 100% of the original images, layouts, colors, and graphics.
Generates:
  1. thesis_presentation_corrected.pdf
  2. thesis_presentation_corrected.pptx
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches

def get_font(font_name, size, bold=False):
    try:
        if bold:
            return ImageFont.truetype(f"{font_name}bd.ttf", size)
        else:
            return ImageFont.truetype(f"{font_name}.ttf", size)
    except:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

extracted_dir = r"d:\Project topics\dinov3-main\pdf_slides_extracted"
corrected_dir = r"d:\Project topics\dinov3-main\pdf_slides_corrected"
os.makedirs(corrected_dir, exist_ok=True)

# Process all 12 slides
slide_images = []

for slide_idx in range(1, 13):
    img_path = os.path.join(extracted_dir, f"slide_{slide_idx}.png")
    if not os.path.exists(img_path):
        continue
    
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size
    
    # -------------------------------------------------------------
    # SLIDE 2: Fix Staining Label
    # -------------------------------------------------------------
    if slide_idx == 2:
        # Erase: "Human coronary artery cross-section · H&E staining"
        # Bounding box around bottom center text: y ~ 880 to 920, x ~ 580 to 1100
        draw.rectangle([580, 880, 1120, 920], fill=(255, 255, 255))
        font_s2 = get_font("arial", 20)
        draw.text((W // 2, 898), "Human coronary artery cross-section · Movat's pentachrome staining",
                  fill=(100, 100, 100), font=font_s2, anchor="mm")
    
    # -------------------------------------------------------------
    # SLIDE 4: Clarify 512 patch resized to 224 for ViT
    # -------------------------------------------------------------
    elif slide_idx == 4:
        # In Step 1: "Cropped into 512 x 512 patches with stride..."
        # Replace line 2 of step 1: x from 140 to 530, y from 580 to 620
        draw.rectangle([140, 582, 530, 616], fill=(255, 255, 255))
        font_s4 = get_font("arial", 18)
        draw.text((144, 586), "Cropped into 512 × 512 patches (input resized to 224 × 224)",
                  fill=(50, 50, 50), font=font_s4)

    # -------------------------------------------------------------
    # SLIDE 8: Sampling Stride -> Token Stride (ViT)
    # -------------------------------------------------------------
    elif slide_idx == 8:
        # Table row: "Sampling Stride" at x ~ 990 to 1150, y ~ 462 to 495
        # Background color in table: pure white or near-white
        draw.rectangle([988, 464, 1150, 494], fill=(255, 255, 255))
        font_s8_b = get_font("arial", 19, bold=True)
        draw.text((993, 468), "Token Stride (ViT)", fill=(30, 30, 30), font=font_s8_b)

    # -------------------------------------------------------------
    # SLIDE 9: Remove "H&E" from subtitle (since cohort has Movat too)
    # -------------------------------------------------------------
    elif slide_idx == 9:
        # Subtitle: "Model predictions overlaid on H&E histological sections demonstrating continuous ring closure"
        # x from 30 to 1300, y from 90 to 140
        draw.rectangle([30, 95, 1300, 140], fill=(255, 255, 255))
        font_s9 = get_font("arial", 26)
        draw.text((32, 100), "Model predictions overlaid on histological sections demonstrating continuous ring closure",
                  fill=(100, 100, 100), font=font_s9)

    # -------------------------------------------------------------
    # SLIDE 10: Comparative Performance Comparison -> Quantitative
    #           and DINOv3 -> DINOv2
    # -------------------------------------------------------------
    elif slide_idx == 10:
        # 1. Title: "Comparative Performance Comparison" -> "Quantitative Performance Comparison"
        draw.rectangle([30, 25, 1020, 105], fill=(255, 255, 255))
        font_s10_title = get_font("arial", 48, bold=True)
        draw.text((36, 38), "Quantitative Performance Comparison", fill=(13, 27, 42), font=font_s10_title)

        # 2. Card 1: "64.17% (DINOv3 + clDice)" -> "64.17% (DINOv2 + clDice)"
        draw.rectangle([250, 250, 510, 282], fill=(255, 255, 255))
        font_s10_card = get_font("arial", 18)
        draw.text((254, 254), "64.17% (DINOv2 + clDice)", fill=(80, 80, 80), font=font_s10_card)

        # 3. Card 2: "0.381 (DINOv3 + clDice) (+27.0%)" -> "0.381 (DINOv2 + clDice) (+27.0%)"
        draw.rectangle([775, 250, 1105, 282], fill=(255, 255, 255))
        draw.text((780, 254), "0.381 (DINOv2 + clDice) (+27.0%)", fill=(80, 80, 80), font=font_s10_card)

        # 4. Card 3: "0.729 (DINOv3 + clDice) (+41.8%)" -> "0.729 (DINOv2 + clDice) (+41.8%)"
        draw.rectangle([1320, 250, 1660, 282], fill=(255, 255, 255))
        draw.text((1326, 254), "0.729 (DINOv2 + clDice) (+41.8%)", fill=(80, 80, 80), font=font_s10_card)

        # 5. Table Header: "DINOv3 + clDice" -> "DINOv2 + clDice"
        # Bbox: x ~ 495 to 655, y ~ 380 to 410
        # Background is light gray row #F2F5F8
        draw.rectangle([495, 382, 655, 410], fill=(242, 245, 248))
        font_s10_th = get_font("arial", 20, bold=True)
        draw.text((500, 385), "DINOv2 + clDice", fill=(20, 20, 20), font=font_s10_th)

        # 6. Graph Legend: "Proposed Model (DINOv3 + cIDice Topology)"
        # Bbox: x ~ 1050 to 1430, y ~ 410 to 440
        draw.rectangle([1050, 412, 1430, 438], fill=(255, 255, 255))
        font_s10_leg = get_font("arial", 17)
        draw.text((1056, 414), "Proposed Model (DINOv2 + clDice Topology)", fill=(60, 60, 60), font=font_s10_leg)

    # -------------------------------------------------------------
    # SLIDE 11: Conclusions & Future Directions (DINOv3 -> DINOv2, +6.84 pp, 2D)
    # -------------------------------------------------------------
    elif slide_idx == 11:
        # Box 1: "DINOv3 self-supervised representations discriminate fine coronary tissue"
        draw.rectangle([170, 292, 820, 326], fill=(255, 255, 255))
        font_s11_body = get_font("arial", 18)
        draw.text((172, 296), "DINOv2 self-supervised representations discriminate fine coronary tissue",
                  fill=(60, 60, 60), font=font_s11_body)

        # Box 3: "Achieved +6.84% accuracy improvement and +27% relative gain in mean loU"
        draw.rectangle([170, 578, 830, 612], fill=(255, 255, 255))
        draw.text((172, 582), "Achieved +6.84 pp accuracy improvement and +27% relative gain in mean IoU",
                  fill=(60, 60, 60), font=font_s11_body)

        # Box 5: "Explore parameter efficient fine-tuning (LoRA) on the DINOv3 backbone"
        draw.rectangle([1000, 290, 1635, 326], fill=(255, 255, 255))
        draw.text((1002, 294), "Explore parameter efficient fine-tuning (LoRA) on the DINOv2 backbone",
                  fill=(60, 60, 60), font=font_s11_body)

        # Box 6: "Extend the 3D segmentation pipeline across serial histological slices to"
        draw.rectangle([1000, 434, 1635, 468], fill=(255, 255, 255))
        draw.text((1002, 437), "Extend the 2D segmentation pipeline across serial histological slices to",
                  fill=(60, 60, 60), font=font_s11_body)

    # Save corrected slide image
    out_img_path = os.path.join(corrected_dir, f"slide_{slide_idx}.png")
    img.save(out_img_path, quality=95)
    slide_images.append(out_img_path)
    print(f"Slide {slide_idx} processed and saved.")

# -------------------------------------------------------------
# 1. BUILD MULTI-PAGE PDF
# -------------------------------------------------------------
pdf_path_workspace = r"d:\Project topics\dinov3-main\thesis_presentation_corrected.pdf"
pdf_path_downloads = r"C:\Users\Adheena Vinod\Downloads\thesis_presentation_corrected.pdf"

pil_images = [Image.open(p).convert("RGB") for p in slide_images]
if pil_images:
    pil_images[0].save(
        pdf_path_workspace,
        save_all=True,
        append_images=pil_images[1:],
        quality=95
    )
    try:
        shutil.copy2(pdf_path_workspace, pdf_path_downloads)
        print(f"Copied PDF to Downloads: {pdf_path_downloads}")
    except Exception as e:
        print(f"Downloads copy notice: {e}")

print(f"Successfully generated PDF: {pdf_path_workspace}")

# -------------------------------------------------------------
# 2. BUILD HIGH-RESOLUTION 16:9 PPTX
# -------------------------------------------------------------
pptx_path_workspace = r"d:\Project topics\dinov3-main\thesis_presentation_corrected.pptx"
pptx_path_downloads = r"C:\Users\Adheena Vinod\Downloads\thesis_presentation_corrected.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.500)
blank_layout = prs.slide_layouts[6]  # Completely blank slide layout

for img_p in slide_images:
    slide = prs.slides.add_slide(blank_layout)
    # Add picture full bleed (covering exactly 13.333 x 7.500 in)
    slide.shapes.add_picture(img_p, Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)

prs.save(pptx_path_workspace)
try:
    shutil.copy2(pptx_path_workspace, pptx_path_downloads)
    print(f"Copied PPTX to Downloads: {pptx_path_downloads}")
except Exception as e:
    print(f"Downloads copy notice: {e}")

print(f"Successfully generated PPTX: {pptx_path_workspace}")
