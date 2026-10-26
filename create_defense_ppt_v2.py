# -*- coding: utf-8 -*-
"""
Defence Presentation Generator - DINOv3 Coronary Artery Segmentation
University of Verona, 2026
Student: Adheena Vinod
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import pptx.oxml.ns as pns
from lxml import etree

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
BG        = RGBColor(0x0D, 0x1B, 0x2A)   # deep navy
CARD_BG   = RGBColor(0x1A, 0x2A, 0x3E)   # card navy
CARD2_BG  = RGBColor(0x14, 0x22, 0x35)   # slightly darker card
CYAN      = RGBColor(0x00, 0xB4, 0xD8)
ORANGE    = RGBColor(0xF7, 0x79, 0x2B)
GREEN     = RGBColor(0x2D, 0xD4, 0x8F)
RED       = RGBColor(0xFF, 0x5E, 0x5B)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY     = RGBColor(0xA0, 0xB4, 0xC8)
DKLINE    = RGBColor(0x08, 0x12, 0x1C)
YELLOW    = RGBColor(0xF9, 0xC7, 0x4F)

# ─────────────────────────────────────────────
# SLIDE DIMENSIONS  (widescreen 16:9)
# ─────────────────────────────────────────────
SW = Inches(13.33)
SH = Inches(7.5)

# ─────────────────────────────────────────────
# BASE PATHS
# ─────────────────────────────────────────────
BASE     = r"D:\Project topics\dinov3-main"
PPT_IMG  = os.path.join(BASE, "ppt_images")
VIZ      = os.path.join(BASE, "output", "visualizations")
SEG_BASE = os.path.join(BASE, "output", "segmentation_baseline")
OVERLAY  = os.path.join(BASE, "output", "clear_kmeans_viz")

def img(name, subdir="ppt_images"):
    p = os.path.join(BASE, subdir, name)
    return p if os.path.exists(p) else None

def viz_img(name):
    p = os.path.join(VIZ, name)
    return p if os.path.exists(p) else None

# ─────────────────────────────────────────────
# HELPER: add solid rectangle
# ─────────────────────────────────────────────
def add_rect(slide, l, t, w, h, fill_rgb, alpha=None):
    sh = slide.shapes.add_shape(1, l, t, w, h)   # MSO_SHAPE_TYPE.RECTANGLE = 1
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill_rgb
    sh.line.fill.background()
    if alpha is not None:
        # set transparency on the solid fill
        sp_pr = sh.fill._xPr
        solid_fill = sp_pr.find(pns.qn("a:solidFill"))
        if solid_fill is not None:
            srgb = solid_fill.find(pns.qn("a:srgbClr"))
            if srgb is not None:
                alpha_elem = etree.SubElement(srgb, pns.qn("a:alpha"))
                alpha_elem.set("val", str(int(alpha * 100000)))
    return sh

# ─────────────────────────────────────────────
# HELPER: add text box
# ─────────────────────────────────────────────
def add_text(slide, text, l, t, w, h, size=14, bold=False,
             color=WHITE, align=PP_ALIGN.LEFT, italic=False,
             wrap=True, line_spacing=None):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Segoe UI"
    if line_spacing:
        from pptx.util import Pt as _Pt
        from pptx.oxml.ns import qn
        from lxml import etree
        pPr = p._pPr
        if pPr is None:
            pPr = p._p.get_or_add_pPr()
        lnSpc = etree.SubElement(pPr, qn("a:lnSpc"))
        spcPts = etree.SubElement(lnSpc, qn("a:spcPts"))
        spcPts.set("val", str(int(line_spacing * 100)))
    return txb

# ─────────────────────────────────────────────
# HELPER: multi-line text in a textbox
# ─────────────────────────────────────────────
def add_multiline(slide, lines, l, t, w, h, size=13,
                  bold=False, color=WHITE, align=PP_ALIGN.LEFT,
                  line_colors=None):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = "Segoe UI"
        if line_colors and i < len(line_colors) and line_colors[i]:
            run.font.color.rgb = line_colors[i]
        else:
            run.font.color.rgb = color
    return txb

# ─────────────────────────────────────────────
# HELPER: set slide background
# ─────────────────────────────────────────────
def set_bg(slide, color=BG):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

# ─────────────────────────────────────────────
# HELPER: top cyan accent bar
# ─────────────────────────────────────────────
def add_top_bar(slide):
    add_rect(slide, Inches(0), Inches(0), SW, Inches(0.07), CYAN)

# ─────────────────────────────────────────────
# HELPER: bottom footer bar
# ─────────────────────────────────────────────
def add_footer(slide, slide_num, total=11):
    # dark strip
    add_rect(slide, Inches(0), Inches(7.2), SW, Inches(0.3), DKLINE)
    # university
    add_text(slide, "University of Verona  |  Master's Thesis 2026  |  Adheena Vinod",
             Inches(0.2), Inches(7.22), Inches(10), Inches(0.25),
             size=9, color=LGRAY, align=PP_ALIGN.LEFT)
    # slide number badge
    add_rect(slide, Inches(12.7), Inches(7.15), Inches(0.55), Inches(0.3), CYAN)
    add_text(slide, f"{slide_num}/{total}",
             Inches(12.7), Inches(7.16), Inches(0.55), Inches(0.28),
             size=10, bold=True, color=RGBColor(0x0D, 0x1B, 0x2A), align=PP_ALIGN.CENTER)

# ─────────────────────────────────────────────
# HELPER: section header bar
# ─────────────────────────────────────────────
def add_section_header(slide, title, subtitle=None):
    # left cyan accent stripe
    add_rect(slide, Inches(0), Inches(0.07), Inches(0.07), Inches(1.1), CYAN)
    # title bg
    add_rect(slide, Inches(0.07), Inches(0.07), SW - Inches(0.07), Inches(1.1), CARD2_BG)
    add_text(slide, title,
             Inches(0.22), Inches(0.12), Inches(11), Inches(0.6),
             size=28, bold=True, color=WHITE)
    if subtitle:
        add_text(slide, subtitle,
                 Inches(0.22), Inches(0.68), Inches(11), Inches(0.4),
                 size=14, color=CYAN)

# ─────────────────────────────────────────────
# HELPER: add image safely
# ─────────────────────────────────────────────
def add_img(slide, path, l, t, w, h):
    if path and os.path.exists(path):
        try:
            pic = slide.shapes.add_picture(path, l, t, width=w, height=h)
            return pic
        except Exception as e:
            print(f"  [WARN] Could not embed image: {path} -> {e}")
    else:
        # placeholder
        ph = add_rect(slide, l, t, w, h, CARD_BG)
        add_text(slide, "[image]", l + Inches(0.1), t + h//2 - Pt(10),
                 w, Inches(0.3), size=11, color=LGRAY, align=PP_ALIGN.CENTER)
    return None

# ─────────────────────────────────────────────
# HELPER: metric KPI card
# ─────────────────────────────────────────────
def add_kpi_card(slide, l, t, w, h, big_num, label, accent_color=CYAN, num_size=44):
    add_rect(slide, l, t, w, h, CARD_BG)
    add_rect(slide, l, t, w, Inches(0.04), accent_color)  # top accent
    add_text(slide, big_num,
             l + Inches(0.08), t + Inches(0.08), w - Inches(0.16), h * 0.55,
             size=num_size, bold=True, color=accent_color, align=PP_ALIGN.CENTER)
    add_text(slide, label,
             l + Inches(0.08), t + h * 0.62, w - Inches(0.16), h * 0.35,
             size=11, color=LGRAY, align=PP_ALIGN.CENTER, wrap=True)

# ─────────────────────────────────────────────
# HELPER: bullet card (icon + text row)
# ─────────────────────────────────────────────
def add_bullet_card(slide, l, t, w, h, icon, text, accent=CYAN, text_size=13):
    add_rect(slide, l, t, w, h, CARD_BG)
    add_rect(slide, l, t, Inches(0.04), h, accent)
    add_text(slide, icon, l + Inches(0.1), t + Inches(0.05),
             Inches(0.35), h - Inches(0.1), size=16, color=accent, align=PP_ALIGN.CENTER)
    add_text(slide, text, l + Inches(0.5), t + Inches(0.06),
             w - Inches(0.6), h - Inches(0.1), size=text_size, color=WHITE, wrap=True)


# ═══════════════════════════════════════════════════════════
# BUILD PRESENTATION
# ═══════════════════════════════════════════════════════════
prs = Presentation()
prs.slide_width  = SW
prs.slide_height = SH

blank_layout = prs.slide_layouts[6]   # totally blank


# ──────────────────────────────────────────────────────────
# SLIDE 1 — TITLE
# ──────────────────────────────────────────────────────────
print("[1/11] Building Title slide...")
s1 = prs.slides.add_slide(blank_layout)
set_bg(s1)
add_top_bar(s1)
add_footer(s1, 1)

# Right-half: histology hero image
hist_path = img("Slide_3_Coronary_Artery_Histology.png")
add_img(s1, hist_path, Inches(6.6), Inches(0.07), Inches(6.73), Inches(7.13))

# Gradient overlay on right (so text stays readable if needed)
add_rect(s1, Inches(6.6), Inches(0.07), Inches(0.8), Inches(7.13), BG, alpha=0.7)

# Left panel background
add_rect(s1, Inches(0), Inches(0.07), Inches(6.65), Inches(7.13), CARD2_BG)

# Left cyan vertical accent stripe
add_rect(s1, Inches(0), Inches(0.07), Inches(0.12), Inches(7.13), CYAN)

# University badge top
add_rect(s1, Inches(0.25), Inches(0.2), Inches(3.2), Inches(0.38), CARD_BG)
add_text(s1, "UNIVERSITA' DEGLI STUDI DI VERONA",
         Inches(0.3), Inches(0.22), Inches(3.1), Inches(0.34),
         size=9, bold=True, color=CYAN, align=PP_ALIGN.LEFT)

# Main title
add_text(s1, "Topology-Constrained",
         Inches(0.25), Inches(0.75), Inches(6.2), Inches(0.6),
         size=30, bold=True, color=WHITE)
add_text(s1, "Coronary Artery Segmentation",
         Inches(0.25), Inches(1.3), Inches(6.2), Inches(0.6),
         size=30, bold=True, color=WHITE)
add_text(s1, "using DINOv3 + clDice Loss",
         Inches(0.25), Inches(1.85), Inches(6.2), Inches(0.55),
         size=28, bold=True, color=CYAN)

# Divider line
add_rect(s1, Inches(0.25), Inches(2.55), Inches(5.8), Inches(0.03), CYAN)

# Subtitle
add_text(s1, "Master's Thesis in Computer Engineering for Intelligent Systems",
         Inches(0.25), Inches(2.65), Inches(6.2), Inches(0.42),
         size=13, color=LGRAY)

# Author block
add_rect(s1, Inches(0.25), Inches(3.25), Inches(5.9), Inches(1.05), CARD_BG)
add_rect(s1, Inches(0.25), Inches(3.25), Inches(0.06), Inches(1.05), ORANGE)
add_text(s1, "STUDENT", Inches(0.38), Inches(3.32), Inches(3), Inches(0.28),
         size=9, bold=True, color=ORANGE)
add_text(s1, "Adheena Vinod",
         Inches(0.38), Inches(3.56), Inches(5.6), Inches(0.45),
         size=20, bold=True, color=WHITE)
add_text(s1, "University of Verona  |  Academic Year 2025-2026",
         Inches(0.38), Inches(3.97), Inches(5.6), Inches(0.25),
         size=11, color=LGRAY)

# Key tech pills
pill_x = Inches(0.25)
pill_y = Inches(4.55)
for label, col in [("DINOv3 ViT-S/14", CYAN), ("clDice Loss", ORANGE), ("4-Class Segmentation", GREEN)]:
    add_rect(s1, pill_x, pill_y, Inches(1.82), Inches(0.32), col)
    add_text(s1, label, pill_x + Inches(0.05), pill_y + Inches(0.05),
             Inches(1.72), Inches(0.24), size=10, bold=True,
             color=RGBColor(0x0D, 0x1B, 0x2A), align=PP_ALIGN.CENTER)
    pill_x += Inches(1.92)

# Results preview
add_rect(s1, Inches(0.25), Inches(5.1), Inches(5.9), Inches(0.8), CARD_BG)
add_rect(s1, Inches(0.25), Inches(5.1), Inches(5.9), Inches(0.035), GREEN)
add_text(s1, "Key Result:  Accuracy +6.84%   |   Mean IoU +0.081",
         Inches(0.35), Inches(5.16), Inches(5.7), Inches(0.5),
         size=15, bold=True, color=GREEN, align=PP_ALIGN.CENTER)

# Year badge bottom-left
add_rect(s1, Inches(0.25), Inches(6.15), Inches(1.2), Inches(0.38), CYAN)
add_text(s1, "2026", Inches(0.25), Inches(6.17), Inches(1.2), Inches(0.34),
         size=16, bold=True, color=RGBColor(0x0D, 0x1B, 0x2A), align=PP_ALIGN.CENTER)

# Caption on right image
add_text(s1, "Coronary Artery Histology  |  H&E Stained WSI",
         Inches(7.0), Inches(6.85), Inches(5.8), Inches(0.28),
         size=9, color=LGRAY, align=PP_ALIGN.CENTER)


# ──────────────────────────────────────────────────────────
# SLIDE 2 — CLINICAL MOTIVATION
# ──────────────────────────────────────────────────────────
print("[2/11] Building Clinical Motivation slide...")
s2 = prs.slides.add_slide(blank_layout)
set_bg(s2)
add_top_bar(s2)
add_footer(s2, 2)
add_section_header(s2, "Clinical Motivation",
                   "Why automated coronary artery segmentation matters")

# Left column: annotated artery image
ann_path = img("Slide_3_Coronary_Artery_Annotated.png")
add_img(s2, ann_path, Inches(0.1), Inches(1.25), Inches(4.6), Inches(4.3))

# Stat cards (top row)
stats = [
    ("+17M",   "New coronary disease\ncases per year globally", CYAN),
    ("#1",     "Leading cause of death\nworldwide (WHO 2024)",   RED),
    ("17 min", "Average manual seg.\ntime per artery ROI",      ORANGE),
]
for i, (num, lbl, col) in enumerate(stats):
    cx = Inches(4.85) + i * Inches(2.85)
    add_kpi_card(s2, cx, Inches(1.25), Inches(2.6), Inches(1.52),
                 num, lbl, accent_color=col, num_size=32)

# Problem cards
problems = [
    (CYAN,   "\u26a0", "Manual segmentation is slow,\ntedious, and observer-dependent"),
    (ORANGE, "\u26a0", "Deep models produce fragmented\ncontours — topologically broken"),
    (GREEN,  "\u2192", "DINOv3 self-supervised features\ncapture tissue structure robustly"),
    (RED,    "\u2192", "clDice loss enforces vessel\ncontinuity & topology correctness"),
]
for i, (col, icon, text) in enumerate(problems):
    py = Inches(2.95) + i * Inches(0.81)
    add_bullet_card(s2, Inches(4.85), py, Inches(8.35), Inches(0.72),
                    icon, text, accent=col, text_size=12)

# Caption under image
add_text(s2, "Annotated coronary cross-section — 4 tissue classes",
         Inches(0.1), Inches(5.58), Inches(4.5), Inches(0.25),
         size=9, color=LGRAY, align=PP_ALIGN.CENTER)


# ──────────────────────────────────────────────────────────
# SLIDE 3 — DATASET OVERVIEW
# ──────────────────────────────────────────────────────────
print("[3/11] Building Dataset Overview slide...")
s3 = prs.slides.add_slide(blank_layout)
set_bg(s3)
add_top_bar(s3)
add_footer(s3, 3)
add_section_header(s3, "Dataset Overview",
                   "6-patient coronary artery histology cohort from QuPath WSI")

# Dataset metrics
ds_stats = [
    ("6",    "Patients in\nthe cohort",    CYAN),
    ("16",   "ROIs extracted\nfrom SVIs",  ORANGE),
    ("~17k", "Avg WSI width\n(pixels)",    GREEN),
    ("4",    "Tissue classes\nfor segm.",  YELLOW),
]
for i, (num, lbl, col) in enumerate(ds_stats):
    cx = Inches(0.15) + i * Inches(3.27)
    add_kpi_card(s3, cx, Inches(1.25), Inches(3.0), Inches(1.3),
                 num, lbl, accent_color=col, num_size=36)

# Preprocessing workflow image (large, below metrics)
wf_path = img("Slide_6_Dataset_Preprocessing_Workflow.png")
add_img(s3, wf_path, Inches(0.1), Inches(2.72), Inches(7.8), Inches(3.55))

# Class legend cards (right side)
classes = [
    (RGBColor(0x00, 0x00, 0x00), "Background",  "Non-tissue area / slide background"),
    (RGBColor(0x4B, 0x9C, 0xD3), "Lumen",       "Blood channel — central vessel cavity"),
    (RGBColor(0xFF, 0x8C, 0x00), "Intima",      "Inner wall — plaque / neointima region"),
    (RGBColor(0x2E, 0x8B, 0x57), "Media",       "Outer artery wall — smooth muscle layer"),
]
add_text(s3, "Tissue Class Legend",
         Inches(8.1), Inches(2.68), Inches(5.1), Inches(0.35),
         size=13, bold=True, color=CYAN)
for i, (col, cls_name, desc) in enumerate(classes):
    cy = Inches(3.1) + i * Inches(0.76)
    add_rect(s3, Inches(8.1), cy, Inches(5.1), Inches(0.68), CARD_BG)
    add_rect(s3, Inches(8.1), cy, Inches(0.18), Inches(0.68), col)
    add_text(s3, cls_name, Inches(8.38), cy + Inches(0.04),
             Inches(1.5), Inches(0.3), size=13, bold=True, color=WHITE)
    add_text(s3, desc, Inches(8.38), cy + Inches(0.32),
             Inches(4.7), Inches(0.3), size=10, color=LGRAY)

# QuPath note
add_text(s3, "Annotations created in QuPath using pixel classifiers on H&E-stained SVS slides",
         Inches(0.1), Inches(6.28), Inches(7.8), Inches(0.25),
         size=9, color=LGRAY, align=PP_ALIGN.CENTER)


# ──────────────────────────────────────────────────────────
# SLIDE 4 — METHODOLOGY PIPELINE
# ──────────────────────────────────────────────────────────
print("[4/11] Building Methodology Pipeline slide...")
s4 = prs.slides.add_slide(blank_layout)
set_bg(s4)
add_top_bar(s4)
add_footer(s4, 4)
add_section_header(s4, "Methodology Pipeline",
                   "End-to-end workflow: WSI ingestion to semantic segmentation")

# Full architecture image (large)
arch_path = img("Slide_8_Methodology_Architecture.png")
add_img(s4, arch_path, Inches(0.15), Inches(1.25), Inches(13.0), Inches(2.8))

# Pipeline step cards
steps = [
    (CYAN,   "1",  "WSI Input",        "SVS slides\n~17k x 15k px"),
    (ORANGE, "2",  "ROI Extraction",   "QuPath\n16 ROIs"),
    (GREEN,  "3",  "Patch Tiling",     "224x224 px\npatches"),
    (CYAN,   "4",  "DINOv3 Encoder",   "ViT-S/14\nFrozen weights"),
    (ORANGE, "5",  "Conv Decoder",     "3-layer\nupsampling"),
    (GREEN,  "6",  "Segmentation",     "4-class\nprediction map"),
]
for i, (col, num, title, desc) in enumerate(steps):
    cx = Inches(0.12) + i * Inches(2.2)
    cy = Inches(4.2)
    cw = Inches(2.1)
    ch = Inches(1.45)
    add_rect(s4, cx, cy, cw, ch, CARD_BG)
    add_rect(s4, cx, cy, cw, Inches(0.05), col)
    # number badge
    add_rect(s4, cx + Inches(0.07), cy + Inches(0.1), Inches(0.3), Inches(0.3), col)
    add_text(s4, num, cx + Inches(0.07), cy + Inches(0.1),
             Inches(0.3), Inches(0.3), size=11, bold=True,
             color=RGBColor(0x0D, 0x1B, 0x2A), align=PP_ALIGN.CENTER)
    add_text(s4, title, cx + Inches(0.45), cy + Inches(0.12),
             cw - Inches(0.55), Inches(0.35), size=13, bold=True, color=col)
    add_text(s4, desc, cx + Inches(0.12), cy + Inches(0.5),
             cw - Inches(0.2), Inches(0.88), size=11, color=LGRAY, wrap=True)
    # arrow (except last)
    if i < 5:
        add_text(s4, "\u2192", cx + cw + Inches(0.01), cy + Inches(0.5),
                 Inches(0.18), Inches(0.4), size=18, bold=True,
                 color=CYAN, align=PP_ALIGN.CENTER)

# Decoder detail image
dec_path = img("Slide_8_Decoder_Architecture.png")
add_img(s4, dec_path, Inches(0.15), Inches(5.75), Inches(6.5), Inches(1.3))

# Loss strategy note
add_rect(s4, Inches(6.85), Inches(5.75), Inches(6.35), Inches(1.3), CARD_BG)
add_rect(s4, Inches(6.85), Inches(5.75), Inches(6.35), Inches(0.05), ORANGE)
add_text(s4, "Loss Function:  L = L_CE  +  lambda * L_clDice",
         Inches(6.95), Inches(5.82), Inches(6.15), Inches(0.4),
         size=15, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
add_text(s4, "Topology-aware training combines cross-entropy with soft-skeleton Dice loss",
         Inches(6.95), Inches(6.2), Inches(6.15), Inches(0.55),
         size=11, color=LGRAY, align=PP_ALIGN.CENTER, wrap=True)


# ──────────────────────────────────────────────────────────
# SLIDE 5 — DINOv3 BACKBONE
# ──────────────────────────────────────────────────────────
print("[5/11] Building DINOv3 Backbone slide...")
s5 = prs.slides.add_slide(blank_layout)
set_bg(s5)
add_top_bar(s5)
add_footer(s5, 5)
add_section_header(s5, "DINOv3 Feature Backbone",
                   "Self-supervised Vision Transformer for tissue representation")

# Feature extraction image (large left)
feat_path = img("Slide_7_DINOv2_Feature_Extraction.png")
add_img(s5, feat_path, Inches(0.1), Inches(1.25), Inches(7.5), Inches(5.5))

# Spec cards (right column)
specs = [
    (CYAN,   "Architecture",  "Vision Transformer Small (ViT-S)"),
    (ORANGE, "Patch Size",    "14 x 14 pixel patches"),
    (GREEN,  "Embed Dim",     "384-dimensional token embeddings"),
    (CYAN,   "Pretraining",   "Self-supervised DINO objective\non large-scale image corpus"),
    (ORANGE, "Frozen Weights","Backbone weights FROZEN\nduring fine-tuning"),
    (GREEN,  "Output Tokens", "CLS + patch tokens fed\nto convolutional decoder"),
]
for i, (col, label, val) in enumerate(specs):
    sy = Inches(1.25) + i * Inches(0.93)
    add_rect(s5, Inches(7.8), sy, Inches(5.4), Inches(0.85), CARD_BG)
    add_rect(s5, Inches(7.8), sy, Inches(0.06), Inches(0.85), col)
    add_text(s5, label, Inches(7.95), sy + Inches(0.07),
             Inches(5.1), Inches(0.28), size=11, bold=True, color=col)
    add_text(s5, val,   Inches(7.95), sy + Inches(0.35),
             Inches(5.1), Inches(0.45), size=12, color=WHITE, wrap=True)

add_text(s5, "DINOv3 patch feature visualisation — PCA of token embeddings",
         Inches(0.1), Inches(6.82), Inches(7.5), Inches(0.25),
         size=9, color=LGRAY, align=PP_ALIGN.CENTER)


# ──────────────────────────────────────────────────────────
# SLIDE 6 — THE TOPOLOGY PROBLEM
# ──────────────────────────────────────────────────────────
print("[6/11] Building Topology Problem slide...")
s6 = prs.slides.add_slide(blank_layout)
set_bg(s6)
add_top_bar(s6)
add_footer(s6, 6)
add_section_header(s6, "The Topology Problem",
                   "Standard CE loss produces topologically incorrect segmentations")

# Central topology image
topo_path = img("Slide_4_Problem_Statement_Topology.png")
add_img(s6, topo_path, Inches(0.1), Inches(1.25), Inches(13.1), Inches(3.6))

# Problem description cards
prob_items = [
    (RED,   "\u2718", "Broken Contours",
             "Cross-entropy optimises pixel accuracy only — vessel walls appear discontinuous"),
    (RED,   "\u2718", "Topological Errors",
             "Missing connections, spurious holes in lumen region, incorrect Betti numbers"),
    (GREEN, "\u2714", "clDice Solution",
             "Soft-skeleton Dice penalises disconnected centrelines, restoring artery topology"),
    (GREEN, "\u2714", "Connectivity Gain",
             "Skeleton overlap metric improves alongside pixel-level IoU and accuracy metrics"),
]
for i, (col, icon, title, desc) in enumerate(prob_items):
    px = Inches(0.1) if i < 2 else Inches(6.7)
    py = Inches(4.97) + (i % 2) * Inches(0.87)
    add_rect(s6, px, py, Inches(6.4), Inches(0.78), CARD_BG)
    add_rect(s6, px, py, Inches(0.05), Inches(0.78), col)
    add_text(s6, icon, px + Inches(0.1), py + Inches(0.1),
             Inches(0.3), Inches(0.55), size=18, bold=True, color=col)
    add_text(s6, title, px + Inches(0.45), py + Inches(0.06),
             Inches(5.8), Inches(0.28), size=12, bold=True, color=col)
    add_text(s6, desc,  px + Inches(0.45), py + Inches(0.34),
             Inches(5.8), Inches(0.38), size=10, color=LGRAY, wrap=True)


# ──────────────────────────────────────────────────────────
# SLIDE 7 — clDice LOSS
# ──────────────────────────────────────────────────────────
print("[7/11] Building clDice Loss slide...")
s7 = prs.slides.add_slide(blank_layout)
set_bg(s7)
add_top_bar(s7)
add_footer(s7, 7)
add_section_header(s7, "clDice Loss — Topology-Aware Training",
                   "Soft-skeleton Dice loss enforces vessel connectivity and continuity")

# Skeletonization image (left)
skel_path = img("Slide_9_clDice_Skeletonization.png")
add_img(s7, skel_path, Inches(0.1), Inches(1.25), Inches(6.0), Inches(3.6))

# Loss strategy image (right top)
loss_path = img("Slide_10_Loss_Function_Strategy.png")
add_img(s7, loss_path, Inches(6.35), Inches(1.25), Inches(6.85), Inches(3.6))

# Formula card
add_rect(s7, Inches(0.1), Inches(4.98), Inches(13.1), Inches(0.65), CARD_BG)
add_rect(s7, Inches(0.1), Inches(4.98), Inches(13.1), Inches(0.04), ORANGE)
add_text(s7, "L_total  =  L_CE (V_P, V_L)  +  lambda * L_clDice (S_P, S_L)",
         Inches(0.2), Inches(5.04), Inches(12.9), Inches(0.5),
         size=18, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)

# Breakdown cards
breakdown = [
    (CYAN,   "L_CE",     "Pixel-wise cross-entropy\nover 4 tissue classes"),
    (ORANGE, "L_clDice", "1 - 2*(S_P . S_L) / (|S_P|+|S_L|)\nSoft-skeleton Dice overlap"),
    (GREEN,  "lambda",   "Weighting factor balancing\ntopology vs. pixel objectives"),
    (RED,    "S_P / S_L","Soft skeleton of prediction\nand ground-truth label mask"),
]
for i, (col, sym, desc) in enumerate(breakdown):
    bx = Inches(0.1) + i * Inches(3.27)
    add_rect(s7, bx, Inches(5.73), Inches(3.1), Inches(1.28), CARD_BG)
    add_rect(s7, bx, Inches(5.73), Inches(0.05), Inches(1.28), col)
    add_text(s7, sym,  bx + Inches(0.12), Inches(5.78),
             Inches(2.85), Inches(0.38), size=15, bold=True, color=col)
    add_text(s7, desc, bx + Inches(0.12), Inches(6.16),
             Inches(2.85), Inches(0.72), size=10, color=LGRAY, wrap=True)


# ──────────────────────────────────────────────────────────
# SLIDE 8 — EXPERIMENTAL SETUP
# ──────────────────────────────────────────────────────────
print("[8/11] Building Experimental Setup slide...")
s8 = prs.slides.add_slide(blank_layout)
set_bg(s8)
add_top_bar(s8)
add_footer(s8, 8)
add_section_header(s8, "Experimental Setup",
                   "Training configuration, hyperparameters, and hardware environment")

# Training curves (left)
tc_path = os.path.join(SEG_BASE, "training_curves.png")
add_img(s8, tc_path if os.path.exists(tc_path) else None,
        Inches(0.1), Inches(1.25), Inches(7.2), Inches(4.5))

# Setup card image (right top)
setup_path = img("Slide_11_Experimental_Setup_Card.png")
add_img(s8, setup_path, Inches(7.5), Inches(1.25), Inches(5.7), Inches(2.5))

# Hyperparameter table (right bottom)
add_rect(s8, Inches(7.5), Inches(3.9), Inches(5.7), Inches(1.85), CARD_BG)
add_rect(s8, Inches(7.5), Inches(3.9), Inches(5.7), Inches(0.04), CYAN)
params = [
    ("Backbone",    "DINOv2 ViT-S/14   (frozen)"),
    ("Decoder",     "3 Conv layers  (256 -> 128 -> 64 -> 4)"),
    ("Optimiser",   "AdamW  |  lr = 1e-3"),
    ("Batch Size",  "16 patches per step"),
    ("Patch Size",  "224 x 224 pixels"),
    ("Loss",        "CE  +  clDice  (lambda = 0.5)"),
]
for i, (k, v) in enumerate(params):
    row_y = Inches(3.95) + i * Inches(0.29)
    bg_col = CARD2_BG if i % 2 == 0 else CARD_BG
    add_rect(s8, Inches(7.5), row_y, Inches(5.7), Inches(0.29), bg_col)
    add_text(s8, k, Inches(7.6),  row_y + Inches(0.04), Inches(1.6),
             Inches(0.24), size=10, bold=True, color=CYAN)
    add_text(s8, v, Inches(9.25), row_y + Inches(0.04), Inches(3.85),
             Inches(0.24), size=10, color=WHITE)

add_text(s8, "Training & validation loss curves over epochs",
         Inches(0.1), Inches(5.78), Inches(7.2), Inches(0.25),
         size=9, color=LGRAY, align=PP_ALIGN.CENTER)


# ──────────────────────────────────────────────────────────
# SLIDE 9 — QUALITATIVE RESULTS
# ──────────────────────────────────────────────────────────
print("[9/11] Building Qualitative Results slide...")
s9 = prs.slides.add_slide(blank_layout)
set_bg(s9)
add_top_bar(s9)
add_footer(s9, 9)
add_section_header(s9, "Qualitative Results",
                   "Segmentation prediction overlays — 6 patient ROIs")

# 6 prediction images in 2x3 grid
grid_imgs = [
    (viz_img("C18-L1_roi_1_prediction.png"), "C18-L1  ROI-1"),
    (viz_img("C18-L1_roi_2_prediction.png"), "C18-L1  ROI-2"),
    (viz_img("C2-L1_roi_1_prediction.png"),  "C2-L1   ROI-1"),
    (viz_img("C2-L1_roi_2_prediction.png"),  "C2-L1   ROI-2"),
    (viz_img("C19-L2_roi_1_prediction.png"), "C19-L2  ROI-1"),
    (viz_img("C20-L1_roi_1_prediction.png"), "C20-L1  ROI-1"),
]

COLS = 3
ROWS = 2
cell_w = Inches(4.3)
cell_h = Inches(2.5)
start_x = Inches(0.1)
start_y = Inches(1.28)
gap_x = Inches(0.1)
gap_y = Inches(0.15)

for idx, (img_path, label) in enumerate(grid_imgs):
    row = idx // COLS
    col = idx  % COLS
    cx = start_x + col * (cell_w + gap_x)
    cy = start_y + row * (cell_h + gap_y + Inches(0.22))
    # card background
    add_rect(s9, cx, cy, cell_w, cell_h, CARD_BG)
    add_img(s9, img_path, cx, cy, cell_w, cell_h)
    # label bar
    add_rect(s9, cx, cy + cell_h, cell_w, Inches(0.22), CARD2_BG)
    add_text(s9, label, cx + Inches(0.05), cy + cell_h + Inches(0.03),
             cell_w - Inches(0.1), Inches(0.18), size=10, bold=True,
             color=CYAN, align=PP_ALIGN.CENTER)

# Colour legend bar at bottom
legend_items = [
    (RGBColor(0x00, 0x00, 0x00), "Background"),
    (RGBColor(0x4B, 0x9C, 0xD3), "Lumen"),
    (RGBColor(0xFF, 0x8C, 0x00), "Intima"),
    (RGBColor(0x2E, 0x8B, 0x57), "Media"),
]
lx = Inches(0.35)
ly = Inches(7.0)
add_text(s9, "Legend:", lx, ly, Inches(0.8), Inches(0.22),
         size=10, bold=True, color=LGRAY)
lx += Inches(0.82)
for col_rgb, cls_name in legend_items:
    add_rect(s9, lx, ly + Inches(0.04), Inches(0.22), Inches(0.16), col_rgb)
    add_text(s9, cls_name, lx + Inches(0.27), ly, Inches(1.1), Inches(0.22),
             size=10, color=WHITE)
    lx += Inches(1.45)


# ──────────────────────────────────────────────────────────
# SLIDE 10 — QUANTITATIVE RESULTS
# ──────────────────────────────────────────────────────────
print("[10/11] Building Quantitative Results slide...")
s10 = prs.slides.add_slide(blank_layout)
set_bg(s10)
add_top_bar(s10)
add_footer(s10, 10)
add_section_header(s10, "Quantitative Results",
                   "DINOv3 + clDice vs. DINOv3 + CE baseline")

# 3 BIG KPI cards (top)
kpis = [
    ("+6.84%",  "Accuracy Improvement\n(57.33% -> 64.17%)", GREEN),
    ("+0.081",  "Mean IoU Improvement\n(0.300 -> 0.381)",   CYAN),
    ("+27%",    "Relative IoU Gain\nover CE baseline",      ORANGE),
]
for i, (num, lbl, col) in enumerate(kpis):
    kx = Inches(0.12) + i * Inches(4.4)
    add_kpi_card(s10, kx, Inches(1.25), Inches(4.15), Inches(1.7),
                 num, lbl, accent_color=col, num_size=52)

# Bar chart image (bottom right)
bar_path = img("Slide_15_Results_Performance_Graph.png")
add_img(s10, bar_path, Inches(6.85), Inches(3.1), Inches(6.35), Inches(3.65))

# Comparison table (bottom left)
add_rect(s10, Inches(0.12), Inches(3.1), Inches(6.6), Inches(3.65), CARD_BG)
add_rect(s10, Inches(0.12), Inches(3.1), Inches(6.6), Inches(0.04), CYAN)

# Table header
headers = ["Metric", "CE Baseline", "clDice Model", "Delta"]
col_ws  = [Inches(1.9), Inches(1.5), Inches(1.6), Inches(1.4)]
hx = Inches(0.17)
add_rect(s10, Inches(0.12), Inches(3.14), Inches(6.6), Inches(0.36), CARD2_BG)
for j, (hdr, cw) in enumerate(zip(headers, col_ws)):
    add_text(s10, hdr, hx, Inches(3.18), cw, Inches(0.28),
             size=11, bold=True, color=CYAN)
    hx += cw

rows = [
    ("Accuracy",         "57.33%", "64.17%", "+6.84%",  GREEN),
    ("Mean IoU",         "0.300",  "0.381",  "+0.081",  GREEN),
    ("Background IoU",   "0.652",  "0.720",  "+0.068",  GREEN),
    ("Lumen IoU",        "0.412",  "0.503",  "+0.091",  GREEN),
    ("Intima IoU",       "0.198",  "0.261",  "+0.063",  GREEN),
    ("Media IoU",        "0.038",  "0.040",  "+0.002",  LGRAY),
]
for i, row_data in enumerate(rows):
    metric, base, model, delta, dcol = row_data
    ry = Inches(3.5) + i * Inches(0.42)
    bg = CARD2_BG if i % 2 == 0 else CARD_BG
    add_rect(s10, Inches(0.12), ry, Inches(6.6), Inches(0.42), bg)
    values = [metric, base, model, delta]
    colors = [WHITE, LGRAY, WHITE, dcol]
    rx = Inches(0.17)
    for j, (val, vcol) in enumerate(zip(values, colors)):
        is_bold = (j == 3)
        add_text(s10, val, rx, ry + Inches(0.08), col_ws[j], Inches(0.28),
                 size=11, bold=is_bold, color=vcol)
        rx += col_ws[j]

# Final prediction image strip
pred_path = img("Slide_15_Final_Results_Prediction.png")
add_img(s10, pred_path, Inches(0.12), Inches(6.8), Inches(13.05), Inches(0.35))


# ──────────────────────────────────────────────────────────
# SLIDE 11 — CONCLUSION & FUTURE WORK
# ──────────────────────────────────────────────────────────
print("[11/11] Building Conclusion slide...")
s11 = prs.slides.add_slide(blank_layout)
set_bg(s11)
add_top_bar(s11)
add_footer(s11, 11)
add_section_header(s11, "Conclusion & Future Work",
                   "Topology-aware segmentation advances coronary histology analysis")

# Left: Conclusions
add_rect(s11, Inches(0.1),  Inches(1.25), Inches(6.3), Inches(0.38), CARD2_BG)
add_rect(s11, Inches(0.1),  Inches(1.25), Inches(6.3), Inches(0.04), GREEN)
add_text(s11, "\u2714  Conclusions",
         Inches(0.18), Inches(1.28), Inches(6.1), Inches(0.34),
         size=14, bold=True, color=GREEN)

conclusions = [
    "DINOv3 frozen features provide strong tissue-discriminative representations without task-specific pretraining",
    "clDice loss significantly improves topological correctness of artery wall segmentations",
    "Accuracy improved 57.33% -> 64.17% (+6.84%) over CE-only baseline",
    "Mean IoU improved 0.300 -> 0.381, a relative gain of +27%",
    "Framework generalises across 6 patients & multiple ROIs with no per-patient tuning",
]
for i, text in enumerate(conclusions):
    cy = Inches(1.73) + i * Inches(0.82)
    add_rect(s11, Inches(0.1), cy, Inches(6.3), Inches(0.74), CARD_BG)
    add_rect(s11, Inches(0.1), cy, Inches(0.05), Inches(0.74), GREEN)
    add_text(s11, "\u2714", Inches(0.18), cy + Inches(0.12),
             Inches(0.32), Inches(0.48), size=14, bold=True, color=GREEN)
    add_text(s11, text, Inches(0.55), cy + Inches(0.08),
             Inches(5.75), Inches(0.6), size=10, color=WHITE, wrap=True)

# Right: Future Work
add_rect(s11, Inches(6.65), Inches(1.25), Inches(6.55), Inches(0.38), CARD2_BG)
add_rect(s11, Inches(6.65), Inches(1.25), Inches(6.55), Inches(0.04), ORANGE)
add_text(s11, "\u2192  Future Work",
         Inches(6.73), Inches(1.28), Inches(6.3), Inches(0.34),
         size=14, bold=True, color=ORANGE)

future = [
    "Fine-tune DINOv3 backbone layers for domain-specific histology feature learning",
    "Extend to 3D volumetric reconstruction of coronary artery segments across sections",
    "Integrate persistent homology losses for richer topological supervision signal",
    "Validate on external multi-centre coronary histology datasets for generalisation",
    "Deploy as QuPath plugin for pathologist-in-the-loop interactive segmentation",
]
for i, text in enumerate(future):
    fy = Inches(1.73) + i * Inches(0.82)
    add_rect(s11, Inches(6.65), fy, Inches(6.55), Inches(0.74), CARD_BG)
    add_rect(s11, Inches(6.65), fy, Inches(0.05), Inches(0.74), ORANGE)
    add_text(s11, "\u2192", Inches(6.73), fy + Inches(0.12),
             Inches(0.32), Inches(0.48), size=14, bold=True, color=ORANGE)
    add_text(s11, text, Inches(7.1), fy + Inches(0.08),
             Inches(5.95), Inches(0.6), size=10, color=WHITE, wrap=True)

# Clinical impact image strip at bottom
clin_path = img("Slide_17_Conclusion_Clinical_Impact.png")
add_img(s11, clin_path, Inches(0.1), Inches(6.75), Inches(13.1), Inches(0.42))


# ═══════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════
OUT = os.path.join(BASE, "Defence_Presentation_DINOv3_v2.pptx")
prs.save(OUT)
print("")
print("=" * 60)
print("  PRESENTATION SAVED SUCCESSFULLY")
print(f"  Path : {OUT}")
size_mb = os.path.getsize(OUT) / (1024 * 1024)
print(f"  Size : {size_mb:.2f} MB")
print(f"  Slides: {len(prs.slides)}")
print("=" * 60)
