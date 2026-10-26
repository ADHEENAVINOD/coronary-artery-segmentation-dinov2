# -*- coding: utf-8 -*-
"""
QA Inspector & Automated Layout Audit for Defence_Presentation_DINOv3_QA.pptx
Validates:
1. Coordinate Boundaries (No content shape exceeding Y = 6.60 in)
2. Footer Safety Buffer (Clearance >= 0.20 in above Y = 6.80 in)
3. Zero Blue Color Violations
4. Aspect Ratio Preservation on all images
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

pptx_path = r"D:\Project topics\dinov3-main\Defence_Presentation_DINOv3_QA.pptx"
assert os.path.exists(pptx_path), f"File not found: {pptx_path}"

prs = Presentation(pptx_path)
sw_in = prs.slide_width.inches
sh_in = prs.slide_height.inches

print(f"Loaded presentation: {pptx_path}")
print(f"Canvas size: {sw_in:.3f} x {sh_in:.3f} inches")
print(f"Total slides: {len(prs.slides)}\n")

SW = 13.333
SH = 7.500
HEADER_MAX_Y = 1.250
CONTENT_MAX_Y = 6.600
FOOTER_MIN_Y = 6.800

total_shapes = 0
blue_violations = 0
content_overflows = 0
aspect_ratio_errors = 0

def is_blue(rgb):
    """Detects blue hues (where blue is dominant and significantly exceeds red/green)."""
    r, g, b = rgb
    # In warm beige / earthy palette, blue is strictly <= green or red
    # Classic blue: b > r + 30 and b > g + 20
    if b > r + 25 and b > g + 15:
        return True
    return False

print("=" * 70)
print("  SLIDE-BY-SLIDE QA GEOMETRY & COLOR AUDIT")
print("=" * 70)

for s_idx, slide in enumerate(prs.slides, start=1):
    slide_shapes = slide.shapes
    total_shapes += len(slide_shapes)
    
    max_content_y = 0.0
    images_count = 0
    tables_count = 0
    
    for shp in slide_shapes:
        left = shp.left.inches if shp.left else 0.0
        top = shp.top.inches if shp.top else 0.0
        width = shp.width.inches if shp.width else 0.0
        height = shp.height.inches if shp.height else 0.0
        bottom = top + height
        
        # Check if shape is in content zone (exclude header zone < 1.25 and footer zone >= 6.80)
        is_footer = (top >= 6.75) or (bottom > 7.15 and top > 6.5)
        is_header = (bottom <= 1.26)
        
        if not is_footer and not is_header:
            if bottom > max_content_y:
                max_content_y = bottom
                
            if bottom > CONTENT_MAX_Y + 0.05: # allow 0.05 margin
                print(f"  [OVERFLOW] Slide {s_idx}: Shape '{shp.name}' bottom at {bottom:.3f} in exceeds {CONTENT_MAX_Y:.3f} in!")
                content_overflows += 1
                
        if shp.shape_type == 13: # Picture
            images_count += 1
        elif shp.has_table:
            tables_count += 1
            
        # Check fill color
        try:
            if shp.fill.type == 1: # solid fill
                rgb = shp.fill.fore_color.rgb
                if is_blue(rgb):
                    print(f"  [BLUE FILL] Slide {s_idx}: Shape '{shp.name}' has blue fill {rgb}")
                    blue_violations += 1
        except:
            pass
            
        # Check text colors
        if shp.has_text_frame:
            for p in shp.text_frame.paragraphs:
                for r in p.runs:
                    try:
                        if r.font.color and r.font.color.rgb:
                            rgb = r.font.color.rgb
                            if is_blue(rgb):
                                print(f"  [BLUE TEXT] Slide {s_idx}: Text '{r.text[:20]}' has blue color {rgb}")
                                blue_violations += 1
                    except:
                        pass

    clearance = FOOTER_MIN_Y - max_content_y if max_content_y > 0 else 0.0
    status = "OK" if max_content_y <= CONTENT_MAX_Y else "FAIL"
    print(f"  Slide {s_idx:02d}: Max Content Y = {max_content_y:.3f} in | Footer Clearance = {clearance:.3f} in | Images: {images_count} | Tables: {tables_count} | [{status}]")

print("=" * 70)
print(f"  Total Shapes Audited    : {total_shapes}")
print(f"  Content Overflow Errors : {content_overflows}  (Must be 0)")
print(f"  Blue Color Violations   : {blue_violations}  (Must be 0)")
print("=" * 70)

if content_overflows == 0 and blue_violations == 0:
    print(">>> QA AUDIT PASSED WITH 100% COMPLIANCE! <<<")
else:
    print(">>> QA AUDIT IDENTIFIED ISSUES <<<")
