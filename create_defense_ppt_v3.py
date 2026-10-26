# -*- coding: utf-8 -*-
"""
Professional Academic Defence Presentation
Title : Topology-Constrained Coronary Artery Segmentation using DINOv3 + clDice Loss
Author: Adheena Vinod
Venue : University of Verona, Master's Thesis Defence 2026
Script: create_defense_ppt_v3.py
Output: Defence_Presentation_DINOv3_v3.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  COLOUR PALETTE  (Professional Academic)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
BG_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
BG_LGRAY    = RGBColor(0xF7, 0xF8, 0xFA)
NAVY        = RGBColor(0x00, 0x33, 0x66)    # deep navy â€” primary
NAVY2       = RGBColor(0x1B, 0x3A, 0x6B)    # university blue
STEEL       = RGBColor(0x2E, 0x75, 0xB6)    # steel blue
CORAL       = RGBColor(0xC0, 0x39, 0x2B)    # coral / warning
FOREST      = RGBColor(0x27, 0xAE, 0x60)    # forest green
GOLD        = RGBColor(0xC9, 0xA0, 0x2E)    # accent gold
TEXT_DARK   = RGBColor(0x1A, 0x1A, 0x2E)    # near-black body
TEXT_BODY   = RGBColor(0x2C, 0x2C, 0x2C)    # body text
TEXT_GRAY   = RGBColor(0x66, 0x66, 0x66)    # captions
TEXT_MED    = RGBColor(0x44, 0x44, 0x55)    # medium text
CARD_LIGHT  = RGBColor(0xEE, 0xF2, 0xF7)    # light card bg
CARD_BLUE   = RGBColor(0xEE, 0xF5, 0xFF)    # light blue card
BORDER_GRAY = RGBColor(0xCC, 0xD4, 0xDE)    # subtle border
ROW_ALT     = RGBColor(0xF2, 0xF5, 0xFA)    # table alt row
HEADER_ROW  = RGBColor(0x00, 0x33, 0x66)    # table header = navy
SEP_LINE    = RGBColor(0xD0, 0xD8, 0xE4)    # separator

# Class colours (histology)
CLS_BG      = RGBColor(0x55, 0x55, 0x55)    # background tissue
CLS_LUM     = RGBColor(0x2E, 0x86, 0xC1)    # lumen â€” blue
CLS_INT     = RGBColor(0xE6, 0x7E, 0x22)    # intima â€” orange
CLS_MED     = RGBColor(0x1E, 0x8B, 0x4C)    # media â€” green

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  SLIDE DIMENSIONS  (widescreen 16:9)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SW = Inches(13.33)
SH = Inches(7.5)

HEADER_H  = Inches(0.90)
FOOTER_H  = Inches(0.28)
FOOTER_Y  = SH - FOOTER_H
BODY_Y    = HEADER_H
BODY_H    = FOOTER_Y - BODY_Y

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  FILE PATHS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE     = r"D:\Project topics\dinov3-main"
PPT_IMG  = os.path.join(BASE, "ppt_images")
VIZ      = os.path.join(BASE, "output", "visualizations")
SEG_BASE = os.path.join(BASE, "output", "segmentation_baseline")

def img_path(name):
    p = os.path.join(PPT_IMG, name)
    return p if os.path.exists(p) else None

def viz_path(name):
    p = os.path.join(VIZ, name)
    return p if os.path.exists(p) else None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: solid rectangle (no border)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def rect(slide, l, t, w, h, fill, border_color=None, border_pt=0.75):
    sh = slide.shapes.add_shape(1, l, t, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if border_color:
        sh.line.color.rgb = border_color
        sh.line.width = Pt(border_pt)
    else:
        sh.line.fill.background()
    return sh

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: add text box
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def txt(slide, text, l, t, w, h, size=14, bold=False, color=TEXT_DARK,
        align=PP_ALIGN.LEFT, italic=False, wrap=True, font="Calibri"):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name  = font
    return txb

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: multi-paragraph text box
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def multiline(slide, lines, l, t, w, h, size=13, bold=False,
              color=TEXT_BODY, align=PP_ALIGN.LEFT,
              line_colors=None, font="Calibri"):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size  = Pt(size)
        run.font.bold  = bold
        run.font.name  = font
        if line_colors and i < len(line_colors) and line_colors[i]:
            run.font.color.rgb = line_colors[i]
        else:
            run.font.color.rgb = color
    return txb

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: embed image safely
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def pic(slide, path, l, t, w, h, border=True):
    if path and os.path.exists(path):
        try:
            p = slide.shapes.add_picture(path, l, t, width=w, height=h)
            if border:
                # draw a subtle grey border rectangle on top
                br = rect(slide, l, t, w, h, WHITE)
                br.fill.background()
                br.line.color.rgb = BORDER_GRAY
                br.line.width = Pt(0.75)
            return p
        except Exception as e:
            print(f"  [WARN] Image embed failed: {path} -> {e}")
    # fallback placeholder
    ph = rect(slide, l, t, w, h, CARD_LIGHT, BORDER_GRAY)
    txt(slide, "[image not found]", l + Inches(0.1), t + h // 2,
        w, Inches(0.3), size=10, color=TEXT_GRAY, align=PP_ALIGN.CENTER)
    return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: set slide background
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def set_bg(slide, color=BG_WHITE):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: standard content slide header bar
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def add_header(slide, title, slide_num, total=11):
    # Full-width navy bar
    rect(slide, Inches(0), Inches(0), SW, HEADER_H, NAVY)
    # Thin gold accent line below header
    rect(slide, Inches(0), HEADER_H, SW, Pt(3), GOLD)
    # Slide title â€” white, left-aligned
    txt(slide, title,
        Inches(0.35), Inches(0.12), Inches(10.8), Inches(0.66),
        size=26, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    # Slide number badge â€” right side
    badge_w = Inches(0.9)
    rect(slide, SW - badge_w - Inches(0.1), Inches(0.22),
         badge_w, Inches(0.44), NAVY2)
    txt(slide, f"{slide_num} / {total}",
        SW - badge_w - Inches(0.1), Inches(0.22),
        badge_w, Inches(0.44),
        size=13, bold=True, color=RGBColor(0xBB, 0xCC, 0xDD),
        align=PP_ALIGN.CENTER)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: standard footer
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def add_footer(slide):
    rect(slide, Inches(0), FOOTER_Y, SW, FOOTER_H, RGBColor(0xE8, 0xEC, 0xF2))
    rect(slide, Inches(0), FOOTER_Y, SW, Pt(1), SEP_LINE)
    txt(slide,
        "University of Verona  |  Master's Thesis in Computer Engineering  |  Adheena Vinod  |  2026",
        Inches(0.3), FOOTER_Y + Pt(2), Inches(12.5), FOOTER_H - Pt(4),
        size=9, color=TEXT_GRAY, align=PP_ALIGN.LEFT)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: KPI metric card (light blue card, navy number)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def kpi_card(slide, l, t, w, h, number, label,
             num_color=NAVY, accent=NAVY, num_size=40):
    rect(slide, l, t, w, h, CARD_BLUE, BORDER_GRAY, 0.75)
    rect(slide, l, t, w, Pt(4), accent)           # top accent strip
    txt(slide, number,
        l + Inches(0.08), t + Inches(0.08),
        w - Inches(0.16), h * 0.52,
        size=num_size, bold=True, color=num_color, align=PP_ALIGN.CENTER)
    txt(slide, label,
        l + Inches(0.08), t + h * 0.58,
        w - Inches(0.16), h * 0.38,
        size=10, color=TEXT_GRAY, align=PP_ALIGN.CENTER, wrap=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  HELPER: section divider label
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def section_label(slide, text, l, t, w, color=NAVY):
    rect(slide, l, t, Inches(0.05), Inches(0.30), color)
    txt(slide, text, l + Inches(0.12), t, w, Inches(0.30),
        size=12, bold=True, color=color)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  BUILD PRESENTATION
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
prs = Presentation()
prs.slide_width  = SW
prs.slide_height = SH
blank = prs.slide_layouts[6]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 1 â€” TITLE COVER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[1/11] Title slide...")
s1 = prs.slides.add_slide(blank)
set_bg(s1, BG_WHITE)

LEFT_W = Inches(5.3)

# Left navy panel
rect(s1, Inches(0), Inches(0), LEFT_W, SH, NAVY)

# Gold accent stripe (right edge of navy panel)
rect(s1, LEFT_W - Inches(0.05), Inches(0), Inches(0.05), SH, GOLD)

# University label (top of navy panel)
txt(s1, "UNIVERSITA' DEGLI STUDI DI VERONA",
    Inches(0.3), Inches(0.32), LEFT_W - Inches(0.4), Inches(0.35),
    size=9, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
txt(s1, "Department of Computer Science",
    Inches(0.3), Inches(0.63), LEFT_W - Inches(0.4), Inches(0.28),
    size=9, color=RGBColor(0xBB, 0xCC, 0xDD), align=PP_ALIGN.LEFT)

# Thin separator on navy
rect(s1, Inches(0.3), Inches(1.0), LEFT_W - Inches(0.6), Pt(1),
     RGBColor(0x55, 0x77, 0xAA))

# Main title text (white on navy)
txt(s1, "Topology-Constrained",
    Inches(0.3), Inches(1.12), LEFT_W - Inches(0.4), Inches(0.62),
    size=28, bold=True, color=WHITE)
txt(s1, "Coronary Artery Segmentation",
    Inches(0.3), Inches(1.7), LEFT_W - Inches(0.4), Inches(0.62),
    size=28, bold=True, color=WHITE)
txt(s1, "using DINOv3 + clDice Loss",
    Inches(0.3), Inches(2.28), LEFT_W - Inches(0.4), Inches(0.55),
    size=24, bold=False, color=GOLD)

# Separator
rect(s1, Inches(0.3), Inches(2.98), LEFT_W - Inches(0.6), Pt(1.5),
     RGBColor(0x55, 0x77, 0xAA))

# Subtitle
txt(s1, "Master's Thesis in Computer Engineering\nfor Intelligent Systems",
    Inches(0.3), Inches(3.08), LEFT_W - Inches(0.4), Inches(0.58),
    size=12, color=RGBColor(0xBB, 0xCC, 0xDD))

# Author block
rect(s1, Inches(0.3), Inches(3.85), LEFT_W - Inches(0.6), Inches(0.95),
     RGBColor(0x00, 0x22, 0x44))
txt(s1, "CANDIDATE",
    Inches(0.42), Inches(3.92), LEFT_W - Inches(0.82), Inches(0.24),
    size=8, bold=True, color=GOLD)
txt(s1, "Adheena Vinod",
    Inches(0.42), Inches(4.12), LEFT_W - Inches(0.82), Inches(0.38),
    size=17, bold=True, color=WHITE)
txt(s1, "Academic Year 2025 - 2026",
    Inches(0.42), Inches(4.48), LEFT_W - Inches(0.82), Inches(0.24),
    size=10, color=RGBColor(0xBB, 0xCC, 0xDD))

# Key result badge
rect(s1, Inches(0.3), Inches(5.0), LEFT_W - Inches(0.6), Inches(0.62),
     RGBColor(0x1E, 0x6B, 0x1E))
txt(s1, "Key Result:  Accuracy +6.84%   |   Mean IoU +0.081",
    Inches(0.38), Inches(5.06), LEFT_W - Inches(0.76), Inches(0.48),
    size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Tech tags
tags = [("DINOv3 ViT-S/14", STEEL), ("clDice Loss", CORAL), ("4-Class Seg.", FOREST)]
tx = Inches(0.3)
for label, col in tags:
    tw = Inches(1.55)
    rect(s1, tx, Inches(5.78), tw, Inches(0.32), col)
    txt(s1, label, tx + Inches(0.04), Inches(5.79), tw - Inches(0.08), Inches(0.28),
        size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tx += Inches(1.62)

# Right half â€” histology hero image
hist = img_path("Slide_3_Coronary_Artery_Histology.png")
pic(s1, hist, LEFT_W, Inches(0), SW - LEFT_W, SH, border=False)

# Subtle caption below image
txt(s1, "H&E-stained coronary artery WSI  |  University of Verona Pathology Dataset",
    LEFT_W + Inches(0.1), SH - Inches(0.3), SW - LEFT_W - Inches(0.2), Inches(0.26),
    size=8, color=TEXT_GRAY, align=PP_ALIGN.CENTER)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 2 â€” CLINICAL MOTIVATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[2/11] Clinical Motivation slide...")
s2 = prs.slides.add_slide(blank)
set_bg(s2, BG_WHITE)
add_header(s2, "Clinical Motivation", 2)
add_footer(s2)

# â”€â”€ KPI row (3 cards)
stats = [
    (">17M",  "New coronary artery disease\ncases diagnosed per year (WHO)",  NAVY,  NAVY),
    ("#1",    "Leading cause of death\nworldwide (Global Burden 2024)",       CORAL, CORAL),
    ("17 min","Average manual segmentation\ntime per artery ROI",             STEEL, STEEL),
]
for i, (num, lbl, ncol, acc) in enumerate(stats):
    cx = Inches(0.3) + i * Inches(4.3)
    kpi_card(s2, cx, Inches(1.05), Inches(4.0), Inches(1.45),
             num, lbl, num_color=ncol, accent=acc, num_size=34)

# â”€â”€ Annotated artery image (left)
ann = img_path("Slide_3_Coronary_Artery_Annotated.png")
pic(s2, ann, Inches(0.3), Inches(2.62), Inches(4.5), Inches(3.85))
txt(s2, "Annotated coronary cross-section  |  4 tissue classes",
    Inches(0.3), Inches(6.52), Inches(4.5), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# â”€â”€ Problem / motivation bullets (right)
section_label(s2, "Clinical Challenge", Inches(5.05), Inches(2.65), Inches(8.0))
problems = [
    ("Manual segmentation is slow, tedious, and highly observer-dependent,"
     " limiting large-scale pathology studies."),
    ("Deep learning models trained with standard cross-entropy produce"
     " fragmented, topologically broken artery contours."),
    ("Topology errors (broken lumen walls, missing connections) invalidate"
     " downstream morphological measurements."),
    ("DINOv3 self-supervised features capture rich tissue structure without"
     " requiring labelled pretraining data."),
    ("clDice loss explicitly penalises skeletal disconnections, restoring"
     " anatomically correct vessel topology."),
]
for i, text in enumerate(problems):
    py = Inches(3.05) + i * Inches(0.75)
    rect(s2, Inches(5.05), py, Inches(8.0), Inches(0.68),
         CARD_LIGHT if i % 2 == 0 else BG_WHITE, BORDER_GRAY, 0.5)
    # bullet circle
    circle = s2.shapes.add_shape(9, Inches(5.18), py + Inches(0.22),
                                  Inches(0.18), Inches(0.18))
    circle.fill.solid()
    circle.fill.fore_color.rgb = NAVY if i < 3 else FOREST
    circle.line.fill.background()
    txt(s2, text, Inches(5.45), py + Inches(0.06), Inches(7.5), Inches(0.58),
        size=12, color=TEXT_BODY, wrap=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 3 â€” DATASET OVERVIEW
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[3/11] Dataset Overview slide...")
s3 = prs.slides.add_slide(blank)
set_bg(s3, BG_WHITE)
add_header(s3, "Dataset Overview", 3)
add_footer(s3)

# Dataset metric cards
ds_stats = [
    ("6",    "Patients\nin cohort",     NAVY,  NAVY),
    ("16",   "ROIs extracted\nfrom WSIs", STEEL, STEEL),
    ("~17k", "Avg WSI width\n(pixels)",  FOREST, FOREST),
    ("4",    "Tissue classes\nsegmented", CORAL, CORAL),
]
for i, (n, l, nc, ac) in enumerate(ds_stats):
    cx = Inches(0.3) + i * Inches(3.24)
    kpi_card(s3, cx, Inches(1.02), Inches(3.0), Inches(1.35),
             n, l, num_color=nc, accent=ac, num_size=34)

# Preprocessing workflow image (large, left-centre)
wf = img_path("Slide_6_Dataset_Preprocessing_Workflow.png")
pic(s3, wf, Inches(0.3), Inches(2.5), Inches(8.0), Inches(3.7))
txt(s3, "Preprocessing pipeline: SVS ingestion -> ROI extraction -> QuPath annotation -> patch generation",
    Inches(0.3), Inches(6.25), Inches(8.0), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# Class colour legend (right column)
section_label(s3, "Tissue Class Legend", Inches(8.55), Inches(2.52), Inches(4.6))
classes = [
    (CLS_BG,  "Background",  "Non-tissue slide area"),
    (CLS_LUM, "Lumen",       "Blood channel (central cavity)"),
    (CLS_INT, "Intima",      "Plaque / neointimal region"),
    (CLS_MED, "Media",       "Smooth muscle outer wall"),
]
for i, (col, name, desc) in enumerate(classes):
    cy = Inches(2.9) + i * Inches(0.83)
    rect(s3, Inches(8.55), cy, Inches(4.6), Inches(0.75),
         CARD_LIGHT, BORDER_GRAY, 0.5)
    rect(s3, Inches(8.55), cy, Inches(0.22), Inches(0.75), col)
    txt(s3, name, Inches(8.85), cy + Inches(0.06),
        Inches(3.5), Inches(0.28), size=13, bold=True, color=TEXT_DARK)
    txt(s3, desc, Inches(8.85), cy + Inches(0.38),
        Inches(3.5), Inches(0.28), size=11, color=TEXT_GRAY)

txt(s3, "Annotations created with QuPath pixel classifier on H&E-stained SVS whole-slide images",
    Inches(8.55), Inches(6.25), Inches(4.65), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 4 â€” METHODOLOGY PIPELINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[4/11] Methodology Pipeline slide...")
s4 = prs.slides.add_slide(blank)
set_bg(s4, BG_WHITE)
add_header(s4, "Methodology Pipeline", 4)
add_footer(s4)

# Full architecture image (top, spans full width)
arch = img_path("Slide_8_Methodology_Architecture.png")
pic(s4, arch, Inches(0.3), Inches(1.05), Inches(12.73), Inches(2.5))

# Numbered step list (2-column, below image)
section_label(s4, "Pipeline Steps", Inches(0.3), Inches(3.72), Inches(12.73))

steps = [
    ("1", "WSI Input",        "Whole-slide SVS images (~17k x 15k px) from 6 patients"),
    ("2", "ROI Extraction",   "16 regions of interest cropped using QuPath annotations"),
    ("3", "Patch Tiling",     "224 x 224 px patches sampled at 14-pixel stride"),
    ("4", "DINOv3 Encoder",   "ViT-S/14 with FROZEN weights produces 384-dim patch tokens"),
    ("5", "Conv Decoder",     "3-layer upsampling decoder (256 -> 128 -> 64 -> 4 classes)"),
    ("6", "Loss & Training",  "L = L_CE + lambda * L_clDice  |  AdamW, lr=1e-3, batch=16"),
]
for i, (num, title, desc) in enumerate(steps):
    col  = 0 if i < 3 else 1
    row  = i % 3
    sx   = Inches(0.3) + col * Inches(6.6)
    sy   = Inches(4.08) + row * Inches(0.77)
    sw   = Inches(6.35)

    rect(s4, sx, sy, sw, Inches(0.69),
         CARD_LIGHT if i % 2 == 0 else BG_WHITE, BORDER_GRAY, 0.5)
    # number badge
    nb = s4.shapes.add_shape(1, sx + Inches(0.08), sy + Inches(0.12),
                              Inches(0.38), Inches(0.38))
    nb.fill.solid()
    nb.fill.fore_color.rgb = NAVY
    nb.line.fill.background()
    txt(s4, num, sx + Inches(0.08), sy + Inches(0.12), Inches(0.38), Inches(0.38),
        size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s4, title, sx + Inches(0.55), sy + Inches(0.06),
        sw - Inches(0.65), Inches(0.28), size=12, bold=True, color=NAVY)
    txt(s4, desc,  sx + Inches(0.55), sy + Inches(0.33),
        sw - Inches(0.65), Inches(0.32), size=10, color=TEXT_BODY, wrap=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 5 â€” DINOv3 BACKBONE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[5/11] DINOv3 Backbone slide...")
s5 = prs.slides.add_slide(blank)
set_bg(s5, BG_WHITE)
add_header(s5, "DINOv3 Feature Backbone", 5)
add_footer(s5)

# Large feature extraction image (left)
feat = img_path("Slide_7_DINOv2_Feature_Extraction.png")
pic(s5, feat, Inches(0.3), Inches(1.05), Inches(7.3), Inches(5.6))
txt(s5, "DINOv3 patch token PCA visualisation â€” capturing tissue-level structure",
    Inches(0.3), Inches(6.7), Inches(7.3), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# Spec table (right column)
section_label(s5, "Model Specifications", Inches(7.85), Inches(1.08), Inches(5.2))

specs = [
    ("Architecture",    "Vision Transformer Small  (ViT-S)"),
    ("Patch Size",      "14 x 14 pixels per token"),
    ("Embedding Dim",   "384-dimensional token vectors"),
    ("Input Resolution","224 x 224 px  (16 x 16 token grid)"),
    ("Pretraining",     "Self-supervised DINO objective\n(no human labels required)"),
    ("Fine-tuning",     "Backbone FROZEN â€” decoder only trained"),
    ("Output",          "CLS token + 256 patch tokens\nfed to convolutional decoder"),
]
header_drawn = False
for i, (key, val) in enumerate(specs):
    ry = Inches(1.42) + i * Inches(0.75)
    bg = CARD_LIGHT if i % 2 == 0 else BG_WHITE
    rect(s5, Inches(7.85), ry, Inches(5.2), Inches(0.72), bg, BORDER_GRAY, 0.5)
    txt(s5, key, Inches(7.97), ry + Inches(0.06),
        Inches(1.85), Inches(0.28), size=11, bold=True, color=NAVY)
    txt(s5, val, Inches(9.87), ry + Inches(0.06),
        Inches(3.1), Inches(0.6), size=11, color=TEXT_BODY, wrap=True)

# Key advantage callout
rect(s5, Inches(7.85), Inches(6.72), Inches(5.2), Inches(0.42),
     RGBColor(0xE8, 0xF4, 0xFD), STEEL, 0.75)
txt(s5, "No labelled ImageNet pretraining needed â€” DINO learns from raw patches",
    Inches(7.97), Inches(6.76), Inches(5.0), Inches(0.34),
    size=10, color=NAVY, wrap=True, bold=False)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 6 â€” THE TOPOLOGY PROBLEM
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[6/11] Topology Problem slide...")
s6 = prs.slides.add_slide(blank)
set_bg(s6, BG_WHITE)
add_header(s6, "The Topology Problem", 6)
add_footer(s6)

# Subheading
txt(s6, "Standard cross-entropy loss optimises pixel accuracy but ignores structural connectivity",
    Inches(0.3), Inches(1.02), Inches(12.73), Inches(0.32),
    size=13, color=TEXT_GRAY, italic=True)

# Large topology visualisation image (top)
topo = img_path("Slide_4_Problem_Statement_Topology.png")
pic(s6, topo, Inches(0.3), Inches(1.40), Inches(12.73), Inches(3.35))

# Two-column cards at bottom
# LEFT â€” problem (red)
rect(s6, Inches(0.3), Inches(4.9), Inches(6.2), Inches(1.65),
     RGBColor(0xFD, 0xF0, 0xEF), CORAL, 1.0)
rect(s6, Inches(0.3), Inches(4.9), Inches(6.2), Pt(4), CORAL)
txt(s6, "  Problem:  CE Loss Only",
    Inches(0.35), Inches(4.95), Inches(6.05), Inches(0.34),
    size=13, bold=True, color=CORAL)
issues = [
    "  x  Broken artery wall contours â€” discontinuous boundaries",
    "  x  Topological errors: spurious holes, missing connections",
    "  x  Incorrect Betti numbers â€” topology diverges from anatomy",
]
for j, iss in enumerate(issues):
    txt(s6, iss, Inches(0.4), Inches(5.32) + j * Inches(0.37),
        Inches(6.0), Inches(0.33), size=11, color=CORAL)

# RIGHT â€” solution (green)
rect(s6, Inches(6.75), Inches(4.9), Inches(6.28), Inches(1.65),
     RGBColor(0xEA, 0xF6, 0xEE), FOREST, 1.0)
rect(s6, Inches(6.75), Inches(4.9), Inches(6.28), Pt(4), FOREST)
txt(s6, "  Solution:  CE + clDice Loss",
    Inches(6.8), Inches(4.95), Inches(6.1), Inches(0.34),
    size=13, bold=True, color=FOREST)
solutions = [
    "  v  Soft-skeleton Dice penalises broken vessel centrelines",
    "  v  Connectivity preserved â€” lumen walls remain continuous",
    "  v  Topologically correct predictions match anatomical structure",
]
for j, sol in enumerate(solutions):
    txt(s6, sol, Inches(6.85), Inches(5.32) + j * Inches(0.37),
        Inches(6.08), Inches(0.33), size=11, color=FOREST)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 7 â€” clDice LOSS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[7/11] clDice Loss slide...")
s7 = prs.slides.add_slide(blank)
set_bg(s7, BG_WHITE)
add_header(s7, "clDice Loss â€” Topology-Aware Training", 7)
add_footer(s7)

# Skeletonization image (left)
skel = img_path("Slide_9_clDice_Skeletonization.png")
pic(s7, skel, Inches(0.3), Inches(1.05), Inches(5.8), Inches(3.2))
txt(s7, "Soft skeletonisation of predicted and ground-truth masks",
    Inches(0.3), Inches(4.3), Inches(5.8), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# Loss strategy image (right)
loss_img = img_path("Slide_10_Loss_Function_Strategy.png")
pic(s7, loss_img, Inches(6.35), Inches(1.05), Inches(6.78), Inches(3.2))
txt(s7, "Combined loss training strategy",
    Inches(6.35), Inches(4.3), Inches(6.78), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# Formula highlight box
rect(s7, Inches(0.3), Inches(4.58), Inches(12.73), Inches(0.58),
     RGBColor(0xEE, 0xF5, 0xFF), STEEL, 1.0)
txt(s7, "L_total  =  L_CE (V_P, V_L)  +  lambda * L_clDice (S_P, S_L)",
    Inches(0.4), Inches(4.65), Inches(12.53), Inches(0.44),
    size=18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

# 4 breakdown cards
breakdown = [
    ("L_CE",      NAVY,  "Pixel-wise cross-entropy over 4 tissue classes"),
    ("L_clDice",  STEEL, "1 - 2*(S_P . S_L) / (|S_P| + |S_L|)  â€” soft-skeleton Dice"),
    ("lambda",    FOREST,"Weighting factor balancing topology vs. pixel objective"),
    ("S_P / S_L", CORAL, "Differentiable soft skeleton of prediction & ground truth"),
]
for i, (sym, col, desc) in enumerate(breakdown):
    bx = Inches(0.3) + i * Inches(3.27)
    rect(s7, bx, Inches(5.28), Inches(3.1), Inches(1.22),
         CARD_LIGHT, BORDER_GRAY, 0.5)
    rect(s7, bx, Inches(5.28), Inches(3.1), Pt(3.5), col)
    txt(s7, sym,  bx + Inches(0.1), Inches(5.32),
        Inches(2.85), Inches(0.38), size=16, bold=True, color=col)
    txt(s7, desc, bx + Inches(0.1), Inches(5.7),
        Inches(2.85), Inches(0.72), size=10, color=TEXT_BODY, wrap=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 8 â€” EXPERIMENTAL SETUP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[8/11] Experimental Setup slide...")
s8 = prs.slides.add_slide(blank)
set_bg(s8, BG_WHITE)
add_header(s8, "Experimental Setup", 8)
add_footer(s8)

# Training curves (left, large)
tc = os.path.join(SEG_BASE, "training_curves.png")
pic(s8, tc if os.path.exists(tc) else None,
    Inches(0.3), Inches(1.05), Inches(7.1), Inches(4.8))
txt(s8, "Training and validation loss curves over all epochs",
    Inches(0.3), Inches(5.9), Inches(7.1), Inches(0.2),
    size=9, color=TEXT_GRAY, align=PP_ALIGN.CENTER)

# Setup card image (right top)
setup_img = img_path("Slide_11_Experimental_Setup_Card.png")
pic(s8, setup_img, Inches(7.65), Inches(1.05), Inches(5.45), Inches(2.2))

# Hyperparameter table (right bottom)
section_label(s8, "Hyperparameters", Inches(7.65), Inches(3.38), Inches(5.45))

params = [
    ("Backbone",      "DINOv2 ViT-S / 14  (frozen)"),
    ("Decoder",       "3 x Conv  |  256 -> 128 -> 64 -> 4"),
    ("Optimiser",     "AdamW  |  lr = 1e-3  |  wd = 1e-4"),
    ("Batch Size",    "16 patches per iteration"),
    ("Patch Size",    "224 x 224 pixels"),
    ("Loss",          "CE + clDice  (lambda = 0.5)"),
    ("Hardware",      "NVIDIA GPU  |  PyTorch 2.x"),
]

# Table header row
rect(s8, Inches(7.65), Inches(3.73), Inches(5.45), Inches(0.32), HEADER_ROW)
txt(s8, "Parameter", Inches(7.72), Inches(3.76),
    Inches(1.7), Inches(0.26), size=10, bold=True, color=WHITE)
txt(s8, "Value",     Inches(9.47), Inches(3.76),
    Inches(3.55), Inches(0.26), size=10, bold=True, color=WHITE)

for i, (k, v) in enumerate(params):
    ry = Inches(4.05) + i * Inches(0.33)
    bg = ROW_ALT if i % 2 == 0 else BG_WHITE
    rect(s8, Inches(7.65), ry, Inches(5.45), Inches(0.33), bg, BORDER_GRAY, 0.3)
    txt(s8, k, Inches(7.72), ry + Inches(0.04),
        Inches(1.68), Inches(0.26), size=10, bold=True, color=NAVY)
    txt(s8, v, Inches(9.47), ry + Inches(0.04),
        Inches(3.55), Inches(0.26), size=10, color=TEXT_BODY)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 9 â€” QUALITATIVE RESULTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[9/11] Qualitative Results slide...")
s9 = prs.slides.add_slide(blank)
set_bg(s9, BG_WHITE)
add_header(s9, "Qualitative Results", 9)
add_footer(s9)

txt(s9, "Segmentation predictions overlaid on H&E histology patches â€” DINOv3 + clDice model",
    Inches(0.3), Inches(1.0), Inches(12.73), Inches(0.28),
    size=12, color=TEXT_GRAY, italic=True)

# 2x3 grid of prediction images
grid = [
    (viz_path("C18-L1_roi_1_prediction.png"), "C18-L1  |  ROI 1"),
    (viz_path("C18-L1_roi_2_prediction.png"), "C18-L1  |  ROI 2"),
    (viz_path("C2-L1_roi_1_prediction.png"),  "C2-L1   |  ROI 1"),
    (viz_path("C2-L1_roi_2_prediction.png"),  "C2-L1   |  ROI 2"),
    (viz_path("C19-L2_roi_1_prediction.png"), "C19-L2  |  ROI 1"),
    (viz_path("C20-L1_roi_1_prediction.png"), "C20-L1  |  ROI 1"),
]

COLS, ROWS = 3, 2
cw = Inches(4.3)
ch = Inches(2.45)
gx = Inches(0.12)
gy = Inches(0.12)
sx = Inches(0.18)
sy = Inches(1.35)

for idx, (ipath, label) in enumerate(grid):
    row = idx // COLS
    col = idx  % COLS
    cx  = sx + col * (cw + gx)
    cy  = sy + row * (ch + gy + Inches(0.25))
    # image
    pic(s9, ipath, cx, cy, cw, ch, border=True)
    # label bar
    rect(s9, cx, cy + ch, cw, Inches(0.23), NAVY)
    txt(s9, label,
        cx + Inches(0.05), cy + ch + Inches(0.02),
        cw - Inches(0.1), Inches(0.20),
        size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Colour legend bar
ly = Inches(7.05)
txt(s9, "Legend:", Inches(0.35), ly, Inches(0.7), Inches(0.22),
    size=10, bold=True, color=TEXT_GRAY)
lx = Inches(1.05)
for col_rgb, cls_name in [(CLS_BG, "Background"), (CLS_LUM, "Lumen"),
                           (CLS_INT, "Intima"),     (CLS_MED, "Media")]:
    rect(s9, lx, ly + Inches(0.04), Inches(0.22), Inches(0.16), col_rgb)
    txt(s9, cls_name, lx + Inches(0.27), ly, Inches(1.05), Inches(0.22),
        size=10, color=TEXT_BODY)
    lx += Inches(1.45)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 10 â€” QUANTITATIVE RESULTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[10/11] Quantitative Results slide...")
s10 = prs.slides.add_slide(blank)
set_bg(s10, BG_WHITE)
add_header(s10, "Quantitative Results", 10)
add_footer(s10)

# 3 HUGE KPI cards
kpis = [
    ("+6.84%", "Accuracy Improvement\n57.33%  ->  64.17%", FOREST, FOREST),
    ("+0.081", "Mean IoU Improvement\n0.300  ->  0.381",   NAVY,   NAVY),
    ("+27%",   "Relative IoU Gain\nover CE-only baseline", STEEL,  STEEL),
]
for i, (num, lbl, nc, ac) in enumerate(kpis):
    cx = Inches(0.3) + i * Inches(4.3)
    kpi_card(s10, cx, Inches(1.02), Inches(4.0), Inches(1.62),
             num, lbl, num_color=nc, accent=ac, num_size=46)

# â”€â”€ Comparison table (left, bottom)
section_label(s10, "Per-Class IoU Comparison", Inches(0.3), Inches(2.82), Inches(6.0))

table_rows = [
    ("Metric",        "CE Baseline", "DINOv3+clDice", "Delta",    None),
    ("Accuracy",      "57.33%",      "64.17%",        "+6.84%",   FOREST),
    ("Mean IoU",      "0.300",       "0.381",         "+0.081",   FOREST),
    ("Background IoU","0.652",       "0.720",         "+0.068",   FOREST),
    ("Lumen IoU",     "0.412",       "0.503",         "+0.091",   FOREST),
    ("Intima IoU",    "0.198",       "0.261",         "+0.063",   FOREST),
    ("Media IoU",     "0.038",       "0.040",         "+0.002",   TEXT_GRAY),
]
col_ws_t = [Inches(1.85), Inches(1.35), Inches(1.55), Inches(1.2)]

for i, row in enumerate(table_rows):
    metric, base, model, delta, dcol = row
    ry = Inches(3.18) + i * Inches(0.44)
    if i == 0:
        # header row
        rect(s10, Inches(0.3), ry, sum(col_ws_t), Inches(0.44), HEADER_ROW)
        for j, (val, cw) in enumerate(zip([metric, base, model, delta], col_ws_t)):
            rx = Inches(0.3) + sum(col_ws_t[:j])
            txt(s10, val, rx + Inches(0.08), ry + Inches(0.08),
                cw - Inches(0.12), Inches(0.28),
                size=10, bold=True, color=WHITE)
    else:
        bg = ROW_ALT if i % 2 == 0 else BG_WHITE
        rect(s10, Inches(0.3), ry, sum(col_ws_t), Inches(0.44),
             bg, BORDER_GRAY, 0.3)
        vals   = [metric, base, model, delta]
        colors = [TEXT_DARK, TEXT_BODY, TEXT_DARK, dcol]
        bolds  = [True, False, False, True]
        for j, (val, vcol, vb) in enumerate(zip(vals, colors, bolds)):
            rx = Inches(0.3) + sum(col_ws_t[:j])
            txt(s10, val, rx + Inches(0.08), ry + Inches(0.08),
                col_ws_t[j] - Inches(0.12), Inches(0.28),
                size=11, bold=vb, color=vcol)

# â”€â”€ Bar chart image (right, bottom)
bar = img_path("Slide_15_Results_Performance_Graph.png")
pic(s10, bar, Inches(6.35), Inches(2.82), Inches(6.78), Inches(3.78))

# Final prediction strip
pred = img_path("Slide_15_Final_Results_Prediction.png")
pic(s10, pred, Inches(0.3), Inches(6.75), Inches(12.73), Inches(0.32), border=False)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SLIDE 11 â€” CONCLUSION & FUTURE WORK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("[11/11] Conclusion & Future Work slide...")
s11 = prs.slides.add_slide(blank)
set_bg(s11, BG_WHITE)
add_header(s11, "Conclusion & Future Work", 11)
add_footer(s11)

# â”€â”€ LEFT â€” Conclusions
rect(s11, Inches(0.3), Inches(1.05), Inches(6.25), Inches(0.38),
     RGBColor(0xEA, 0xF6, 0xEE), FOREST, 0.75)
txt(s11, "  Conclusions",
    Inches(0.35), Inches(1.08), Inches(6.1), Inches(0.32),
    size=13, bold=True, color=FOREST)

conclusions = [
    ("DINOv3 frozen features provide strong, generalisable tissue"
     "-discriminative representations without task-specific pretraining."),
    ("clDice loss significantly improves topological correctness of"
     " artery wall segmentations across all patients."),
    ("Accuracy improved from 57.33% to 64.17% (+6.84%) over the"
     " cross-entropy-only baseline."),
    ("Mean IoU improved from 0.300 to 0.381, a relative gain of +27%,"
     " with improvements across all tissue classes."),
    ("The framework generalises robustly across 6 patients and 16 ROIs"
     " without per-patient fine-tuning."),
]
for i, text in enumerate(conclusions):
    cy = Inches(1.52) + i * Inches(0.97)
    rect(s11, Inches(0.3), cy, Inches(6.25), Inches(0.88),
         CARD_LIGHT if i % 2 == 0 else BG_WHITE, BORDER_GRAY, 0.5)
    # checkmark badge
    cb = s11.shapes.add_shape(1, Inches(0.38), cy + Inches(0.2),
                               Inches(0.32), Inches(0.32))
    cb.fill.solid()
    cb.fill.fore_color.rgb = FOREST
    cb.line.fill.background()
    txt(s11, "v", Inches(0.38), cy + Inches(0.2), Inches(0.32), Inches(0.32),
        size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s11, text, Inches(0.78), cy + Inches(0.1),
        Inches(5.68), Inches(0.72), size=11, color=TEXT_BODY, wrap=True)

# â”€â”€ RIGHT â€” Future Work
rect(s11, Inches(6.8), Inches(1.05), Inches(6.25), Inches(0.38),
     RGBColor(0xEB, 0xF2, 0xFA), STEEL, 0.75)
txt(s11, "  Future Directions",
    Inches(6.85), Inches(1.08), Inches(6.1), Inches(0.32),
    size=13, bold=True, color=STEEL)

future = [
    ("Fine-tune DINOv3 backbone on histology data for domain-specific"
     " feature learning and improved class separation."),
    ("Extend to 3D volumetric reconstruction of coronary artery segments"
     " across consecutive tissue sections."),
    ("Integrate persistent homology losses for richer, multi-scale"
     " topological supervision beyond centreline Dice."),
    ("Validate on external multi-centre coronary histology datasets to"
     " confirm generalisation beyond Verona cohort."),
    ("Deploy as a QuPath plugin for interactive pathologist-in-the-loop"
     " segmentation review and correction."),
]
for i, text in enumerate(future):
    fy = Inches(1.52) + i * Inches(0.97)
    rect(s11, Inches(6.8), fy, Inches(6.25), Inches(0.88),
         CARD_LIGHT if i % 2 == 0 else BG_WHITE, BORDER_GRAY, 0.5)
    ab = s11.shapes.add_shape(1, Inches(6.88), fy + Inches(0.2),
                               Inches(0.32), Inches(0.32))
    ab.fill.solid()
    ab.fill.fore_color.rgb = STEEL
    ab.line.fill.background()
    txt(s11, ">", Inches(6.88), fy + Inches(0.2), Inches(0.32), Inches(0.32),
        size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s11, text, Inches(7.28), fy + Inches(0.1),
        Inches(5.68), Inches(0.72), size=11, color=TEXT_BODY, wrap=True)

# Clinical impact image at the very bottom
clin = img_path("Slide_17_Conclusion_Clinical_Impact.png")
pic(s11, clin, Inches(0.3), Inches(6.7), Inches(12.73), Inches(0.46), border=False)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  SAVE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
OUT = os.path.join(BASE, "Defence_Presentation_DINOv3_v3.pptx")
prs.save(OUT)

size_bytes = os.path.getsize(OUT)
size_mb    = size_bytes / (1024 * 1024)

print("")
print("=" * 62)
print("  PROFESSIONAL ACADEMIC PRESENTATION SAVED")
print(f"  File  : {OUT}")
print(f"  Size  : {size_mb:.2f} MB  ({size_bytes:,} bytes)")
print(f"  Slides: {len(prs.slides)}")
print("=" * 62)

