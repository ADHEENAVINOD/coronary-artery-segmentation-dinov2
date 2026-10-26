import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as PlatypusImage,
    Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas
import pypdfium2 as pdfium
import shutil

# --- 18 WORKING DAYS: September 16, 2026 to October 09, 2026 (10:00 - 18:00, 8 hours, Total: 150h) ---
DATES = [
    "16/09/2026", "17/09/2026", "18/09/2026", "21/09/2026", "22/09/2026",
    "23/09/2026", "24/09/2026", "25/09/2026", "28/09/2026", "29/09/2026",
    "30/09/2026", "01/10/2026", "02/10/2026", "05/10/2026", "06/10/2026",
    "07/10/2026", "08/10/2026", "09/10/2026"
]

ACTIVITIES = [
    "Stage kickoff and briefing with academic supervisor Prof. Francesco Setti; defined research scope on topological priors for coronary histopathology segmentation.",
    "Comprehensive literature review on coronary artery disease, histological cross-section analysis, and clinical luminal stenosis grading criteria.",
    "Investigated theoretical limitations of pixel-wise loss functions (Cross-Entropy, soft-Dice) regarding vascular loop and boundary continuity.",
    "Studied persistent homology and graph-based topological segmentation approaches (Clough et al., Hu et al., Topograph).",
    "Dataset exploration and inspection: evaluated 16 coronary autopsy whole-slide images (H&E and Movat stains) and QuPath polygon annotations.",
    "Analysis of gigapixel image I/O and RAM bottlenecks; designed the offline patch extraction and dynamic caching pipeline architecture.",
    "Implemented and benchmarked the PyTorch patch caching pipeline, reducing RAM usage to <100 MB and training time from 5.8 hours to under 2 minutes per epoch.",
    "Exploration of self-supervised Vision Transformers; extracted and evaluated frozen DINOv2-Small patch token features on histological textures.",
    "Designed the hybrid segmentation model: paired the frozen DINOv2 backbone with a lightweight 3-layer convolutional decoder head.",
    "Implemented token reshaping and spatial upsampling with bilinear interpolation (factor 14) and symmetric center-cropping to 512x512 resolution.",
    "Formulated differentiable soft morphological operations (continuous min/max pooling for erosion and dilation).",
    "Developed the iterative soft-skeletonization module (T=5 iterations) to extract continuous centerlines of annular vessel wall structures.",
    "Formulated the continuous Centerline Dice (clDice) loss function to enforce topological boundary continuity in the Tunica Media and Lumen.",
    "Integrated the multi-task composite loss balancing categorical cross-entropy with the clDice topological regularizer (lambda=0.50).",
    "Implemented automated morphometric post-processing algorithms for lumen area, vessel caliber integration, and percentage stenosis calculation.",
    "Benchmarked the proposed architecture against standard U-Net, DeepLabv3+, and SegFormer on the held-out clinical test cohort.",
    "Validated diagnostic concordance against pathologist ground truth, constructing the four-tier confusion matrix (achieving 92.1% agreement).",
    "Analyzed failure mode mitigations for histological artifacts (calcification, tissue folds) and finalized thesis and internship documentation."
]

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.black)
        self.drawRightString(A4[0] - 32, 20, f"{self._pageNumber}")
        self.restoreState()

def build_clean_pdf(filename="Foglio_Presenze_Stage_Adheena_Vinod_Table.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=32,
        rightMargin=32,
        topMargin=26,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    style_header_right = ParagraphStyle(
        'HeaderRight', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11, alignment=2, textColor=colors.HexColor('#222222')
    )
    style_main_title = ParagraphStyle(
        'MainTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12.5, leading=15, alignment=1, spaceBefore=2, spaceAfter=7
    )
    style_red_notice = ParagraphStyle(
        'RedNotice', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.2, leading=9.5, textColor=colors.HexColor('#D90000'), spaceAfter=7
    )
    style_student_info = ParagraphStyle(
        'StudentInfo', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=13.5, textColor=colors.black
    )
    style_student_bold = ParagraphStyle(
        'StudentBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=13.5, textColor=colors.black
    )
    style_nb = ParagraphStyle(
        'NBStyle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7, leading=9.5, textColor=colors.black, spaceBefore=4, spaceAfter=4
    )
    style_th = ParagraphStyle(
        'THStyle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=6.8, leading=8.2, alignment=1, textColor=colors.black
    )
    style_td_center = ParagraphStyle(
        'TDCenter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.4, leading=9.5, alignment=1, textColor=colors.black
    )
    style_td_desc = ParagraphStyle(
        'TDDesc', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.2, leading=9.2, textColor=colors.black
    )
    style_footer_bold = ParagraphStyle(
        'FooterBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.black
    )

    story = []

    # --- PAGE 1 ---
    logo_path = 'univr_logo_clean.png'
    logo_img = PlatypusImage(logo_path, width=240, height=44)
    right_text = Paragraph("Stage e Tirocini", style_header_right)

    header_table = Table([[logo_img, right_text]], colWidths=[380, 150])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("FOGLIO PRESENZE STAGE", style_main_title))

    notice_text = (
        "Il file deve essere compilato in ogni sezione e completo dell’ultima pagina comprensiva di firma dello "
        "studente, firma del tutor aziendale e totale delle ore di stage effettivamente svolte, nel rispetto del periodo "
        "e degli orari dichiarati nel progetto formativo, al netto delle variazioni regolarmente comunicate durante lo "
        "stage. <b>IL FILE VA ALLEGATO IN ESSE3 IN UN UNICO FILE IN FORMATO PDF.</b>"
    )
    story.append(Paragraph(notice_text, style_red_notice))
    story.append(Spacer(1, 3))

    info_data = [
        [
            Paragraph("<b>Cognome</b> VINOD", style_student_info),
            Paragraph("<b>Nome</b> ADHEENA", style_student_info)
        ],
        [
            Paragraph("<b>Corso di studio</b> Laurea Magistrale in Data Science", style_student_info),
            Paragraph("<b>Matricola</b> VR503834", style_student_info)
        ],
        [
            Paragraph("<b>Azienda ospitante</b> Università degli Studi di Verona", style_student_info),
            Paragraph("<b>Tutor aziendale</b> Prof. FRANCESCO SETTI", style_student_info)
        ],
        [
            Paragraph("<b>Periodo di svolgimento dello stage</b>  dal 16/09/2026 al 09/10/2026", style_student_info),
            Paragraph("", style_student_info)
        ]
    ]
    info_table = Table(info_data, colWidths=[310, 220])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "N.B. è possibile aggiungere righe, se non sufficienti rispetto alle giornate di presenza, proseguendo nella numerazione progressiva",
        style_nb
    ))
    story.append(Spacer(1, 2))

    th_row = [
        Paragraph("<b></b>", style_th),
        Paragraph("<b>DATA</b>", style_th),
        Paragraph("<b>ORA<br/>INGRESSO</b>", style_th),
        Paragraph("<b>ORA<br/>USCITA</b>", style_th),
        Paragraph("<b>ORE DI<br/>PRESENZA</b><br/>(non superiore a quelle dichiarate nel progetto)", style_th),
        Paragraph("<b>ATTIVITÀ SVOLTE</b><br/>(necessarie al tutor accademico per la valutazione)", style_th),
        Paragraph("<b>FIRMA TUTOR<br/>AZIENDALE</b><br/>(firma autografa o sigla)", style_th)
    ]
    col_widths = [18, 52, 45, 45, 58, 238, 74]

    # Rows 1 to 10 on Page 1 (No signature images - clean empty cell for signature)
    table_p1_data = [th_row]
    for i in range(10):
        table_p1_data.append([
            Paragraph(f"{i+1}", style_td_center),
            Paragraph(DATES[i], style_td_center),
            Paragraph("10:00", style_td_center),
            Paragraph("18:00", style_td_center),
            Paragraph("8", style_td_center),
            Paragraph(ACTIVITIES[i], style_td_desc),
            Paragraph("", style_td_center) # Clean empty cell
        ])

    table_p1 = Table(table_p1_data, colWidths=col_widths)
    table_p1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (4,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8F8F8')),
    ]))
    story.append(table_p1)

    # --- PAGE 2 ---
    story.append(PageBreak())

    story.append(Paragraph("<b>FOGLIO PRESENZE STAGE (seguito)</b> — Studente: <b>ADHEENA VINOD</b> (Matr. <b>VR503834</b>)", ParagraphStyle(
        'P2Title', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#444444'), spaceAfter=5
    )))

    # Rows 11 to 18 on Page 2 (Finishes on 09/10/2026!)
    table_p2_data = [th_row]
    for i in range(10, 18):
        table_p2_data.append([
            Paragraph(f"{i+1}", style_td_center),
            Paragraph(DATES[i], style_td_center),
            Paragraph("10:00", style_td_center),
            Paragraph("18:00", style_td_center),
            Paragraph("8", style_td_center),
            Paragraph(ACTIVITIES[i], style_td_desc),
            Paragraph("", style_td_center) # Clean empty cell
        ])

    # Blank rows 19 to 25
    for i in range(18, 25):
        table_p2_data.append([
            Paragraph(f"{i+1}", style_td_center),
            Paragraph("", style_td_center),
            Paragraph("", style_td_center),
            Paragraph("", style_td_center),
            Paragraph("", style_td_center),
            Paragraph("", style_td_desc),
            Paragraph("", style_td_center)
        ])

    table_p2 = Table(table_p2_data, colWidths=col_widths)
    table_p2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (4,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8F8F8')),
    ]))
    story.append(table_p2)
    story.append(Spacer(1, 20))

    # Clean dotted signature lines at the bottom (ready for manual signing)
    footer_data = [
        [
            Paragraph("<b>TOTALE ORE EFFETTUATE NEL PERIODO COMPLESSIVO DI STAGE</b>", style_footer_bold),
            Paragraph("<b>150</b>", style_student_bold)
        ],
        [
            Paragraph("<br/><b>FIRMA AUTOGRAFA DELLO STAGISTA</b>", style_footer_bold),
            Paragraph("<br/>....................................................................................", style_student_info)
        ],
        [
            Paragraph("<br/><b>TIMBRO E FIRMA AUTOGRAFA DEL TUTOR AZIENDALE</b>", style_footer_bold),
            Paragraph("<br/>....................................................................................", style_student_info)
        ]
    ]
    footer_table = Table(footer_data, colWidths=[330, 200])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(footer_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated clean unsigned PDF: {filename}")

if __name__ == '__main__':
    build_clean_pdf()
