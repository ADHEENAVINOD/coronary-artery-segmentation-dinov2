"""
Create a visually rich 11-slide defense PPT for the DINOv3 Coronary Artery project.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
import copy
from lxml import etree
import os
from pathlib import Path

# ─── Palette ──────────────────────────────────────────────────────────────────
DARK_BG     = RGBColor(0x0D, 0x1B, 0x2A)   # deep navy
ACCENT      = RGBColor(0x00, 0xB4, 0xD8)   # vibrant cyan
ACCENT2     = RGBColor(0xF7, 0x79, 0x2B)   # warm orange
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_TEXT  = RGBColor(0xB0, 0xC4, 0xDE)
CARD_BG     = RGBColor(0x1A, 0x2A, 0x3E)
GREEN       = RGBColor(0x2D, 0xD4, 0x8F)
RED_WARN    = RGBColor(0xFF, 0x5E, 0x5B)

# ─── Slide dimensions (widescreen 16:9) ───────────────────────────────────────
W = Inches(13.33)
H = Inches(7.5)

BASE = Path(r"D:\Project topics\dinov3-main")
IMGS = BASE / "ppt_images"
VIZ  = BASE / "output" / "visualizations"
SEG  = BASE / "output" / "segmentation_baseline"


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def hex_rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def fill_slide_bg(slide, color: RGBColor):
    """Fill slide background with a solid colour."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, x, y, w, h, color: RGBColor, alpha=None):
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE
    shape.line.fill.background()
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color
    return shape

def add_text_box(slide, text, x, y, w, h,
                 font_size=18, bold=False, color=WHITE,
                 align=PP_ALIGN.LEFT, font_name="Segoe UI"):
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox

def add_img(slide, path, x, y, w, h=None):
    if not Path(path).exists():
        print(f"  [WARN] Missing: {path}")
        return None
    if h:
        return slide.shapes.add_picture(str(path), x, y, w, h)
    return slide.shapes.add_picture(str(path), x, y, w)

def title_bar(slide, title, subtitle=None):
    """Draws the top title band."""
    add_rect(slide, 0, 0, W, Inches(1.05), DARK_BG)
    add_rect(slide, 0, Inches(1.05), W, Inches(0.06), ACCENT)
    add_text_box(slide, title,
                 Inches(0.35), Inches(0.12),
                 Inches(10), Inches(0.75),
                 font_size=30, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text_box(slide, subtitle,
                     Inches(0.38), Inches(0.72),
                     Inches(10), Inches(0.35),
                     font_size=13, bold=False, color=ACCENT, align=PP_ALIGN.LEFT)

def footer(slide, text="University of Verona  •  Thesis Defence  •  2026"):
    add_rect(slide, 0, H - Inches(0.32), W, Inches(0.32), CARD_BG)
    add_text_box(slide, text,
                 Inches(0.3), H - Inches(0.31),
                 Inches(12), Inches(0.30),
                 font_size=9, color=LIGHT_TEXT, align=PP_ALIGN.LEFT)

def bullet_card(slide, x, y, w, h, icon, text, icon_color=ACCENT, text_size=15):
    add_rect(slide, x, y, w, h, CARD_BG)
    add_text_box(slide, icon,  x + Inches(0.12), y + Inches(0.08),
                 Inches(0.5), h, font_size=22, color=icon_color, bold=True)
    add_text_box(slide, text,  x + Inches(0.55), y + Inches(0.1),
                 w - Inches(0.7), h - Inches(0.15),
                 font_size=text_size, color=WHITE)

def metric_card(slide, x, y, w, h, value, label, val_color=ACCENT):
    add_rect(slide, x, y, w, h, CARD_BG)
    add_text_box(slide, value, x, y + Inches(0.08), w, Inches(0.55),
                 font_size=34, bold=True, color=val_color, align=PP_ALIGN.CENTER)
    add_text_box(slide, label, x, y + Inches(0.6), w, Inches(0.35),
                 font_size=12, color=LIGHT_TEXT, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# BUILD PPT
# ══════════════════════════════════════════════════════════════════════════════

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
blank = prs.slide_layouts[6]   # completely blank layout


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1  — TITLE
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)

# Left gradient block
add_rect(s, 0, 0, Inches(7.8), H, CARD_BG)
add_rect(s, 0, 0, Inches(0.18), H, ACCENT)         # left accent strip

# Diagonal separator (approximated with a narrow rect)
sep = s.shapes.add_shape(1, Inches(7.6), 0, Inches(0.25), H)
sep.fill.solid(); sep.fill.fore_color.rgb = DARK_BG
sep.line.fill.background()

# Title text
add_text_box(s, "Topology-Constrained",
             Inches(0.5), Inches(1.0), Inches(7.0), Inches(0.9),
             font_size=36, bold=True, color=ACCENT, align=PP_ALIGN.LEFT)
add_text_box(s, "Coronary Artery Segmentation",
             Inches(0.5), Inches(1.85), Inches(7.0), Inches(0.9),
             font_size=34, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
add_text_box(s, "Using DINOv3 + clDice Loss",
             Inches(0.5), Inches(2.7), Inches(7.0), Inches(0.7),
             font_size=26, bold=False, color=ACCENT, align=PP_ALIGN.LEFT)

add_rect(s, Inches(0.5), Inches(3.5), Inches(2.5), Inches(0.05), ACCENT2)

add_text_box(s, "Adheena Vinod",
             Inches(0.5), Inches(3.7), Inches(5), Inches(0.45),
             font_size=18, bold=True, color=WHITE)
add_text_box(s, "Master's Thesis Defence  •  University of Verona  •  2026",
             Inches(0.5), Inches(4.2), Inches(7.0), Inches(0.4),
             font_size=13, color=LIGHT_TEXT)

# Right side — image of coronary artery
img1 = IMGS / "Slide_3_Coronary_Artery_Histology.png"
add_img(s, img1, Inches(8.0), Inches(0.5), Inches(5.1), Inches(6.2))

# Slide number badge
add_rect(s, W - Inches(0.6), H - Inches(0.45), Inches(0.5), Inches(0.35), ACCENT)
add_text_box(s, "1/11", W - Inches(0.62), H - Inches(0.46), Inches(0.55), Inches(0.35),
             font_size=9, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2  — MOTIVATION & CLINICAL PROBLEM
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "Motivation", "Why automate coronary artery analysis?")
footer(s)

# Big stat cards (top row)
stats = [
    ("17.9M", "CVD deaths / year\nglobally", ACCENT2),
    ("~40%", "Sudden cardiac deaths\nlinked to stenosis", RED_WARN),
    ("Manual", "current forensic\nstaining assessment", ACCENT),
]
cx = Inches(0.4)
for val, lbl, col in stats:
    metric_card(s, cx, Inches(1.3), Inches(3.9), Inches(1.3), val, lbl, col)
    cx += Inches(4.2)

# Problem cards (lower)
cards = [
    ("🔬", "Forensic autopsies need objective stenosis % to determine cause of death"),
    ("⏱", "Manual histology assessment is slow, subjective, and expert-dependent"),
    ("🤖", "AI segmentation can automate vessel layer measurement"),
    ("📐", "Standard AI ignores topology → broken artery walls in predictions"),
]
cy = Inches(2.9)
for i, (icon, txt) in enumerate(cards):
    row = i // 2
    col = i % 2
    bullet_card(s, Inches(0.4 + col * 6.4), cy + row * Inches(1.35),
                Inches(6.1), Inches(1.2), icon, txt, text_size=14)

# Right image column
add_img(s, IMGS / "Slide_3_Coronary_Artery_Annotated.png",
        Inches(12.7) - Inches(0.05), Inches(1.25), Inches(0.5), Inches(5.8))  # placeholder space (narrow)
# Actually place image taking the far right
add_img(s, IMGS / "Slide_3_Coronary_Artery_Annotated.png",
        Inches(12.5), Inches(1.2), Inches(0.75), Inches(5.9))  # very narrow if full col not available

add_text_box(s, "2 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3  — DATASET & PROBLEM SETUP
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "Dataset & Problem Setup", "Whole-slide histology images → ROI regions of interest")
footer(s)

# Dataset stats row
dstats = [
    ("6", "Patients\n(Cases)"),
    ("16", "ROIs\nExtracted"),
    ("4", "Tissue\nClasses"),
    ("~17k×15k", "Avg. WSI\nResolution"),
]
cx = Inches(0.35)
for val, lbl in dstats:
    metric_card(s, cx, Inches(1.25), Inches(2.95), Inches(1.1), val, lbl, ACCENT)
    cx += Inches(3.2)

# Class legend cards
classes = [
    ("⬛", "Background", "Outer tissue / empty space", LIGHT_TEXT),
    ("🟣", "Media",      "Muscular outer artery wall", RGBColor(0xA0,0x60,0xB0)),
    ("🟡", "Intima",     "Plaque buildup layer",       RGBColor(0xF0,0xC0,0x30)),
    ("🔵", "Lumen",      "Blood flow channel",         RGBColor(0x30,0x90,0xF0)),
]
cy = Inches(2.6)
for i, (icon, name, desc, col) in enumerate(classes):
    add_rect(s, Inches(0.35 + i*3.2), cy, Inches(3.0), Inches(1.1), CARD_BG)
    add_text_box(s, icon + "  " + name,
                 Inches(0.5 + i*3.2), cy + Inches(0.05),
                 Inches(2.8), Inches(0.45), font_size=16, bold=True, color=col)
    add_text_box(s, desc,
                 Inches(0.5 + i*3.2), cy + Inches(0.5),
                 Inches(2.8), Inches(0.55), font_size=12, color=LIGHT_TEXT)

# Preprocessing pipeline image
add_img(s, IMGS / "Slide_6_Dataset_Preprocessing_Workflow.png",
        Inches(0.35), Inches(3.9), Inches(12.6), Inches(3.2))

add_text_box(s, "3 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4  — METHODOLOGY OVERVIEW (Architecture)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "Methodology Overview", "Frozen DINOv3 backbone + lightweight convolutional decoder")
footer(s)

# Architecture image (centre)
add_img(s, IMGS / "Slide_8_Methodology_Architecture.png",
        Inches(0.3), Inches(1.2), Inches(7.0), Inches(5.8))

# Pipeline steps on the right
steps = [
    ("①", "DINOv3 ViT-S/14 backbone\n(frozen — no fine-tuning)"),
    ("②", "Patch features → 3-layer Conv decoder"),
    ("③", "Output: 4-class semantic map"),
    ("④", "Loss: CE + clDice (topology)"),
    ("⑤", "Evaluation: Accuracy + Mean IoU"),
]
cy = Inches(1.3)
for icon, txt in steps:
    add_rect(s, Inches(7.6), cy, Inches(5.5), Inches(0.95), CARD_BG)
    add_text_box(s, icon,  Inches(7.7), cy + Inches(0.05),
                 Inches(0.55), Inches(0.85), font_size=24, bold=True, color=ACCENT)
    add_text_box(s, txt,   Inches(8.3), cy + Inches(0.08),
                 Inches(4.7), Inches(0.85), font_size=14, color=WHITE)
    cy += Inches(1.1)

add_text_box(s, "4 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5  — DINOv3 FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "DINOv3 Feature Extraction", "Self-supervised ViT encoder — LVD-1689M pretrained")
footer(s)

# Large feature viz image
add_img(s, IMGS / "Slide_7_DINOv2_Feature_Extraction.png",
        Inches(0.3), Inches(1.25), Inches(8.5), Inches(5.9))

# Key facts
facts = [
    ("🧠", "Vision Transformer (ViT-S/14)"),
    ("📦", "21M parameters — distilled"),
    ("🔒", "Backbone frozen during training"),
    ("📏", "Patch size: 14×14 pixels"),
    ("🌐", "Pretrained: 1.69B curated images"),
    ("🎯", "Output: 384-dim feature per patch"),
]
cy = Inches(1.3)
for icon, txt in facts:
    add_rect(s, Inches(9.1), cy, Inches(4.1), Inches(0.84), CARD_BG)
    add_text_box(s, icon + "  " + txt,
                 Inches(9.25), cy + Inches(0.12),
                 Inches(3.8), Inches(0.65), font_size=14, color=WHITE)
    cy += Inches(0.97)

add_text_box(s, "5 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6  — THE TOPOLOGY PROBLEM
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "The Topology Problem", "Standard cross-entropy loss breaks anatomical structure")
footer(s)

# Problem image
add_img(s, IMGS / "Slide_4_Problem_Statement_Topology.png",
        Inches(0.35), Inches(1.25), Inches(7.5), Inches(5.9))

# Problem vs Solution
add_rect(s, Inches(8.1), Inches(1.3), Inches(5.1), Inches(2.5), RGBColor(0x3A,0x10,0x10))
add_text_box(s, "❌  WITHOUT Topology Loss",
             Inches(8.2), Inches(1.4), Inches(4.9), Inches(0.5),
             font_size=16, bold=True, color=RED_WARN)
probs = ["• Fragmented artery wall contours",
         "• Broken lumen rings",
         "• Anatomically impossible holes",
         "• Unreliable stenosis calculation"]
add_text_box(s, "\n".join(probs),
             Inches(8.2), Inches(1.9), Inches(4.9), Inches(1.8),
             font_size=13, color=WHITE)

add_rect(s, Inches(8.1), Inches(4.1), Inches(5.1), Inches(2.6), RGBColor(0x0A,0x2A,0x1A))
add_text_box(s, "✅  WITH clDice Topology Loss",
             Inches(8.2), Inches(4.2), Inches(4.9), Inches(0.5),
             font_size=16, bold=True, color=GREEN)
sols = ["• Closed, connected artery walls",
        "• Complete circular lumen",
        "• Biologically plausible shapes",
        "• Accurate stenosis % measurable"]
add_text_box(s, "\n".join(sols),
             Inches(8.2), Inches(4.72), Inches(4.9), Inches(1.8),
             font_size=13, color=WHITE)

add_text_box(s, "6 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7  — clDice LOSS (visual math)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "clDice Loss Function", "Centerline Dice — enforcing connectivity via soft skeletonization")
footer(s)

# clDice diagram image
add_img(s, IMGS / "Slide_9_clDice_Skeletonization.png",
        Inches(0.3), Inches(1.25), Inches(7.5), Inches(3.8))

# Loss strategy card
add_img(s, IMGS / "Slide_10_Loss_Function_Strategy.png",
        Inches(0.3), Inches(5.15), Inches(7.5), Inches(2.0))

# Formula & steps
add_rect(s, Inches(8.1), Inches(1.3), Inches(5.1), Inches(5.8), CARD_BG)
add_text_box(s, "How clDice Works",
             Inches(8.2), Inches(1.4), Inches(4.9), Inches(0.5),
             font_size=17, bold=True, color=ACCENT)

steps2 = [
    ("①", "Soft Erosion & Dilation", "Morphological ops on probability maps"),
    ("②", "Soft Skeletonization",    "Extracts 1-px centerline of predicted walls"),
    ("③", "Skeleton Precision",      "clPrec = |Sk(P) ∩ T| / |Sk(P)|"),
    ("④", "Skeleton Sensitivity",    "clSens = |Sk(T) ∩ P| / |Sk(T)|"),
    ("⑤", "clDice Score",            "2 · (clPrec × clSens) / (clPrec + clSens)"),
    ("⑥", "Total Loss",              "L = CE + 0.5 × (1 − clDice)"),
]
cy = Inches(2.05)
for num, title_, desc in steps2:
    add_text_box(s, num,    Inches(8.2), cy, Inches(0.4), Inches(0.38),
                 font_size=14, bold=True, color=ACCENT2)
    add_text_box(s, title_, Inches(8.6), cy, Inches(4.5), Inches(0.38),
                 font_size=14, bold=True, color=WHITE)
    add_text_box(s, desc,   Inches(8.6), cy + Inches(0.35), Inches(4.5), Inches(0.4),
                 font_size=12, color=LIGHT_TEXT)
    cy += Inches(0.88)

add_text_box(s, "7 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8  — TRAINING & EXPERIMENTAL SETUP
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "Training & Experimental Setup", "Patch-based training on frozen DINOv3 features")
footer(s)

# Training curves image
add_img(s, SEG / "training_curves.png",
        Inches(0.3), Inches(1.25), Inches(7.5), Inches(5.9))

# Hyperparameter table (right)
params = [
    ("Backbone",       "DINOv3 ViT-S/14 (frozen)"),
    ("Decoder",        "3× Conv2D + BatchNorm + ReLU"),
    ("Patch size",     "512 × 512 px"),
    ("Patches/image",  "50"),
    ("Optimizer",      "Adam"),
    ("Learning rate",  "1 × 10⁻⁴"),
    ("Epochs",         "30"),
    ("Loss",           "CE + 0.5 × clDice"),
    ("Classes",        "4 (BG, Media, Intima, Lumen)"),
    ("Train/Val",      "80% / 20% per case"),
]
add_rect(s, Inches(8.1), Inches(1.3), Inches(5.1), Inches(5.9), CARD_BG)
add_text_box(s, "⚙  Hyperparameters",
             Inches(8.2), Inches(1.4), Inches(4.9), Inches(0.5),
             font_size=16, bold=True, color=ACCENT)
cy = Inches(2.0)
for k, v in params:
    add_text_box(s, k,  Inches(8.3), cy, Inches(2.1), Inches(0.38),
                 font_size=12, bold=True, color=ACCENT2)
    add_text_box(s, v,  Inches(10.4), cy, Inches(2.7), Inches(0.38),
                 font_size=12, color=WHITE)
    # thin separator
    add_rect(s, Inches(8.25), cy + Inches(0.38), Inches(4.8), Inches(0.015),
             RGBColor(0x2A,0x3A,0x55))
    cy += Inches(0.52)

add_text_box(s, "8 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9  — QUALITATIVE RESULTS (side-by-side predictions)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "Qualitative Results", "Segmentation predictions across 6 patients — 16 ROIs")
footer(s)

# 3 prediction images side by side
pred_imgs = [
    VIZ / "C18-L1_roi_1_prediction.png",
    VIZ / "C2-L1_roi_1_prediction.png",
    VIZ / "C19-L2_roi_1_prediction.png",
]
labels = ["Patient C18 – ROI 1", "Patient C2 – ROI 1", "Patient C19 – ROI 1"]
cx = Inches(0.2)
for img, lbl in zip(pred_imgs, labels):
    add_img(s, img, cx, Inches(1.25), Inches(4.2), Inches(5.5))
    add_text_box(s, lbl, cx, Inches(6.85), Inches(4.2), Inches(0.35),
                 font_size=12, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    cx += Inches(4.45)

# Colour legend bar at bottom
legend = [
    (RGBColor(0x20,0x20,0x20), "Background"),
    (RGBColor(0xA0,0x60,0xB0), "Media"),
    (RGBColor(0xF0,0xC0,0x30), "Intima"),
    (RGBColor(0x30,0x90,0xF0), "Lumen"),
]
lx = Inches(0.2)
for col, name in legend:
    add_rect(s, lx, H - Inches(0.55), Inches(0.28), Inches(0.22), col)
    add_text_box(s, name, lx + Inches(0.32), H - Inches(0.57),
                 Inches(1.2), Inches(0.25), font_size=11, color=LIGHT_TEXT)
    lx += Inches(1.65)

add_text_box(s, "9 / 11", W - Inches(0.7), H - Inches(0.32),
             Inches(0.6), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10  — QUANTITATIVE RESULTS
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
title_bar(s, "Quantitative Results", "clDice topology constraint significantly improves both metrics")
footer(s)

# Big improvement metrics top row
add_rect(s, Inches(0.3), Inches(1.3), Inches(4.0), Inches(1.8), CARD_BG)
add_text_box(s, "+6.84%", Inches(0.3), Inches(1.35), Inches(4.0), Inches(1.0),
             font_size=52, bold=True, color=GREEN, align=PP_ALIGN.CENTER)
add_text_box(s, "Accuracy improvement", Inches(0.3), Inches(2.25), Inches(4.0), Inches(0.4),
             font_size=14, color=LIGHT_TEXT, align=PP_ALIGN.CENTER)

add_rect(s, Inches(4.6), Inches(1.3), Inches(4.0), Inches(1.8), CARD_BG)
add_text_box(s, "+0.081", Inches(4.6), Inches(1.35), Inches(4.0), Inches(1.0),
             font_size=52, bold=True, color=GREEN, align=PP_ALIGN.CENTER)
add_text_box(s, "Mean IoU improvement", Inches(4.6), Inches(2.25), Inches(4.0), Inches(0.4),
             font_size=14, color=LIGHT_TEXT, align=PP_ALIGN.CENTER)

add_rect(s, Inches(8.9), Inches(1.3), Inches(4.2), Inches(1.8), CARD_BG)
add_text_box(s, "64.17%", Inches(8.9), Inches(1.35), Inches(4.2), Inches(1.0),
             font_size=52, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_text_box(s, "Final test accuracy", Inches(8.9), Inches(2.25), Inches(4.2), Inches(0.4),
             font_size=14, color=LIGHT_TEXT, align=PP_ALIGN.CENTER)

# Comparison table
add_rect(s, Inches(0.3), Inches(3.4), Inches(8.5), Inches(3.7), CARD_BG)

# Header row
add_rect(s, Inches(0.3), Inches(3.4), Inches(8.5), Inches(0.55), RGBColor(0x12,0x2A,0x4A))
cols = ["Metric", "Baseline (CE only)", "Topology (CE + clDice)", "Δ Improvement"]
widths = [2.5, 2.0, 2.5, 1.5]
cx = Inches(0.45)
for col, w in zip(cols, widths):
    add_text_box(s, col, cx, Inches(3.45), Inches(w), Inches(0.45),
                 font_size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    cx += Inches(w)

rows = [
    ["Test Accuracy",  "57.33%", "64.17%", "+6.84%"],
    ["Mean IoU",       "0.300",  "0.381",  "+0.081"],
    ["Topology valid", "❌ No",  "✅ Yes", "—"],
]
ry = Inches(3.95)
for i, row in enumerate(rows):
    bg = CARD_BG if i % 2 == 0 else RGBColor(0x14,0x2E,0x50)
    add_rect(s, Inches(0.3), ry, Inches(8.5), Inches(0.9), bg)
    cx = Inches(0.45)
    for j, (cell, w) in enumerate(zip(row, widths)):
        col = GREEN if (j == 2 and i < 2) else (RED_WARN if (j == 1 and i < 2) else WHITE)
        add_text_box(s, cell, cx, ry + Inches(0.08), Inches(w), Inches(0.75),
                     font_size=14, bold=(j == 2), color=col, align=PP_ALIGN.CENTER)
        cx += Inches(w)
    ry += Inches(0.92)

# Performance graph on the right
add_img(s, IMGS / "Slide_15_Results_Performance_Graph.png",
        Inches(9.1), Inches(3.35), Inches(4.1), Inches(3.8))

add_text_box(s, "10 / 11", W - Inches(0.75), H - Inches(0.32),
             Inches(0.65), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11  — CONCLUSION & FUTURE WORK
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(blank)
fill_slide_bg(s, DARK_BG)
add_rect(s, 0, 0, W, Inches(0.06), ACCENT)
footer(s)

# Left half — headline conclusion
add_rect(s, 0, Inches(0.06), Inches(6.8), H - Inches(0.06), CARD_BG)
add_rect(s, 0, Inches(0.06), Inches(0.12), H - Inches(0.06), ACCENT)  # left strip

add_text_box(s, "Conclusion",
             Inches(0.3), Inches(0.3), Inches(6.3), Inches(0.7),
             font_size=32, bold=True, color=ACCENT, align=PP_ALIGN.LEFT)

conclusions = [
    ("✅", "DINOv3 features transfer well to medical histology"),
    ("✅", "clDice loss enforces anatomical topology"),
    ("✅", "Accuracy: 57.33% → 64.17% (+6.84%)"),
    ("✅", "Mean IoU: 0.300 → 0.381 (+0.081)"),
    ("✅", "First DINOv3 application to coronary forensic analysis"),
]
cy = Inches(1.3)
for icon, txt in conclusions:
    add_rect(s, Inches(0.25), cy, Inches(6.35), Inches(0.85), RGBColor(0x0A,0x22,0x38))
    add_text_box(s, icon,  Inches(0.35), cy + Inches(0.08),
                 Inches(0.45), Inches(0.7), font_size=20, color=GREEN)
    add_text_box(s, txt,   Inches(0.82), cy + Inches(0.1),
                 Inches(5.7), Inches(0.7), font_size=15, color=WHITE)
    cy += Inches(1.0)

# Right half — future work
add_text_box(s, "Future Work",
             Inches(7.1), Inches(0.3), Inches(5.9), Inches(0.7),
             font_size=30, bold=True, color=ACCENT2, align=PP_ALIGN.LEFT)

future = [
    ("🔬", "Expert-annotated ground truth labels"),
    ("🔁", "End-to-end fine-tuning of DINOv3"),
    ("📐", "Automated stenosis % quantification"),
    ("🌐", "Multi-centre dataset validation"),
    ("🏥", "Clinical deployment & pathologist tool"),
]
cy = Inches(1.3)
for icon, txt in future:
    add_rect(s, Inches(7.1), cy, Inches(5.95), Inches(0.85), CARD_BG)
    add_text_box(s, icon,  Inches(7.22), cy + Inches(0.08),
                 Inches(0.45), Inches(0.7), font_size=20, color=ACCENT2)
    add_text_box(s, txt,   Inches(7.68), cy + Inches(0.1),
                 Inches(5.3), Inches(0.7), font_size=15, color=WHITE)
    cy += Inches(1.0)

# Clinical impact image
add_img(s, IMGS / "Slide_17_Conclusion_Clinical_Impact.png",
        Inches(7.1), Inches(6.5), Inches(6.0), Inches(0.65))

add_text_box(s, "11 / 11", W - Inches(0.75), H - Inches(0.32),
             Inches(0.65), Inches(0.30), font_size=9, bold=True, color=LIGHT_TEXT, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
out = BASE / "Defence_Presentation_DINOv3.pptx"
prs.save(str(out))
print(f"\nSaved OK -> {out}")
