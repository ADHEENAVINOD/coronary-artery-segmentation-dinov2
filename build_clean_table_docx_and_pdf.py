import os
import shutil
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

def set_cell_borders(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        r'<w:tcBorders %s>'
        r'  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        r'  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        r'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        r'  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        r'</w:tcBorders>' % nsdecls('w')
    )
    tcPr.append(tcBorders)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(r'<w:shd %s w:fill="%s"/>' % (nsdecls('w'), hex_color))
    tcPr.append(shd)

def create_word_table_doc(filename="Foglio_Presenze_Stage_Adheena_Vinod_Table.docx"):
    doc = Document()
    
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.45)
        section.right_margin = Inches(0.45)

    # 1. Header
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    
    cell_left = header_table.cell(0, 0)
    cell_left.width = Inches(5.2)
    p_logo = cell_left.paragraphs[0]
    p_logo.paragraph_format.space_after = Pt(0)
    if os.path.exists("univr_logo_clean.png"):
        p_logo.add_run().add_picture("univr_logo_clean.png", width=Inches(3.3))
    else:
        run = p_logo.add_run("UNIVERSITÀ di VERONA")
        run.bold = True
        run.font.size = Pt(12)

    cell_right = header_table.cell(0, 1)
    cell_right.width = Inches(2.1)
    p_right = cell_right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_right.paragraph_format.space_after = Pt(0)
    run_right = p_right.add_run("Stage e Tirocini")
    run_right.font.size = Pt(9)
    run_right.font.name = "Arial"

    # 2. Main Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("FOGLIO PRESENZE STAGE")
    run_title.bold = True
    run_title.font.size = Pt(13)
    run_title.font.name = "Arial"

    # 3. Red Notice
    p_notice = doc.add_paragraph()
    p_notice.paragraph_format.space_before = Pt(0)
    p_notice.paragraph_format.space_after = Pt(6)
    p_notice.paragraph_format.line_spacing = Pt(9.5)
    r_not1 = p_notice.add_run(
        "Il file deve essere compilato in ogni sezione e completo dell’ultima pagina comprensiva di firma dello "
        "studente, firma del tutor aziendale e totale delle ore di stage effettivamente svolte, nel rispetto del periodo "
        "e degli orari dichiarati nel progetto formativo, al netto delle variazioni regolarmente comunicate durante lo stage. "
    )
    r_not1.font.size = Pt(7.5)
    r_not1.font.name = "Arial"
    r_not1.font.color.rgb = RGBColor(217, 0, 0)

    r_not2 = p_notice.add_run("IL FILE VA ALLEGATO IN ESSE3 IN UN UNICO FILE IN FORMATO PDF.")
    r_not2.bold = True
    r_not2.font.size = Pt(7.5)
    r_not2.font.name = "Arial"
    r_not2.font.color.rgb = RGBColor(217, 0, 0)

    # 4. Student & Stage Info
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False

    rows_info = [
        [("Cognome ", "VINOD"), ("Nome ", "ADHEENA")],
        [("Corso di studio ", "Laurea Magistrale in Data Science"), ("Matricola ", "VR503834")],
        [("Azienda ospitante ", "Università degli Studi di Verona"), ("Tutor aziendale ", "Prof. FRANCESCO SETTI")],
        [("Periodo di svolgimento dello stage ", "dal 16/09/2026 al 09/10/2026"), ("", "")]
    ]

    for r_idx, row_content in enumerate(rows_info):
        for c_idx, (label, val) in enumerate(row_content):
            cell = info_table.cell(r_idx, c_idx)
            cell.width = Inches(4.3 if c_idx == 0 else 3.0)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(1)
            if label:
                r_lbl = p.add_run(label)
                r_lbl.bold = True
                r_lbl.font.size = Pt(8.5)
                r_lbl.font.name = "Arial"
            if val:
                r_val = p.add_run(val)
                r_val.font.size = Pt(8.5)
                r_val.font.name = "Arial"

    # 5. Note
    p_nb = doc.add_paragraph()
    p_nb.paragraph_format.space_before = Pt(6)
    p_nb.paragraph_format.space_after = Pt(4)
    r_nb = p_nb.add_run("N.B. è possibile aggiungere righe, se non sufficienti rispetto alle giornate di presenza, proseguendo nella numerazione progressiva")
    r_nb.bold = True
    r_nb.font.size = Pt(7)
    r_nb.font.name = "Arial"

    # 6. Main Presence Table (Header + 18 rows + blank rows up to 25)
    table = doc.add_table(rows=1, cols=7)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    col_widths = [Inches(0.28), Inches(0.72), Inches(0.62), Inches(0.62), Inches(0.85), Inches(3.25), Inches(1.05)]

    headers = [
        "",
        "DATA",
        "ORA\nINGRESSO",
        "ORA\nUSCITA",
        "ORE DI\nPRESENZA\n(non superiore a\nquelle dichiarate\nnel progetto)",
        "ATTIVITÀ SVOLTE\n(necessarie al tutor accademico per la valutazione)",
        "FIRMA TUTOR\nAZIENDALE\n(firma autografa o\nsigla)"
    ]

    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(6.5)
        run.font.name = "Arial"
        set_cell_borders(hdr_cells[i])
        set_cell_background(hdr_cells[i], "F0F0F0")

    # Add 18 active rows (10:00 - 18:00, 8 hours, clean empty signature cell)
    for idx in range(18):
        row_cells = table.add_row().cells
        data_row = [
            str(idx + 1),
            DATES[idx],
            "10:00",
            "18:00",
            "8",
            ACTIVITIES[idx],
            ""
        ]
        for col_idx, text in enumerate(data_row):
            row_cells[col_idx].width = col_widths[col_idx]
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = Pt(9.5)
            if col_idx < 5:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            run.font.size = Pt(7.2)
            run.font.name = "Arial"
            set_cell_borders(row_cells[col_idx])

    # Add blank rows (rows 19-25)
    for idx in range(18, 25):
        row_cells = table.add_row().cells
        for col_idx in range(7):
            row_cells[col_idx].width = col_widths[col_idx]
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.space_before = Pt(2.5)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(str(idx + 1))
                run.font.size = Pt(7)
                run.font.name = "Arial"
            set_cell_borders(row_cells[col_idx])

    # 7. Bottom Signatures & Total Hours: 150
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(14)
    p_space.paragraph_format.space_after = Pt(4)

    footer_table = doc.add_table(rows=3, cols=2)
    footer_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    footer_table.autofit = False

    foot_data = [
        ("TOTALE ORE EFFETTUATE NEL PERIODO COMPLESSIVO DI STAGE", "150"),
        ("FIRMA AUTOGRAFA DELLO STAGISTA", "................................................................................"),
        ("TIMBRO E FIRMA AUTOGRAFA DEL TUTOR AZIENDALE", "................................................................................")
    ]

    for r_idx, (lbl, val) in enumerate(foot_data):
        cell_lbl = footer_table.cell(r_idx, 0)
        cell_lbl.width = Inches(4.5)
        p_l = cell_lbl.paragraphs[0]
        p_l.paragraph_format.space_before = Pt(6)
        p_l.paragraph_format.space_after = Pt(4)
        r_l = p_l.add_run(lbl)
        r_l.bold = True
        r_l.font.size = Pt(8.5)
        r_l.font.name = "Arial"

        cell_val = footer_table.cell(r_idx, 1)
        cell_val.width = Inches(2.8)
        p_v = cell_val.paragraphs[0]
        p_v.paragraph_format.space_before = Pt(6)
        p_v.paragraph_format.space_after = Pt(4)
        r_v = p_v.add_run(val)
        if r_idx == 0:
            r_v.bold = True
        r_v.font.size = Pt(8.5)
        r_v.font.name = "Arial"

    doc.save(filename)
    print(f"Successfully generated clean Word DOCX: {filename}")


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
            Paragraph("", style_td_center)
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
            Paragraph("", style_td_center)
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
    docx_file = "Foglio_Presenze_Stage_Adheena_Vinod_Table.docx"
    pdf_file = "Foglio_Presenze_Stage_Adheena_Vinod_Table.pdf"
    
    create_word_table_doc(docx_file)
    build_clean_pdf(pdf_file)

    # Render PDF pages to images for inspection
    pdf_doc = pdfium.PdfDocument(pdf_file)
    print(f"Total pages in clean PDF: {len(pdf_doc)}")
    for i, page in enumerate(pdf_doc):
        image = page.render(scale=2.0).to_pil()
        image.save(f"clean_table_page_{i+1}.png")
        print(f"Saved clean_table_page_{i+1}.png")

    desktop_dir = r"C:\Users\Adheena Vinod\OneDrive\Desktop"
    if os.path.exists(desktop_dir):
        shutil.copy2(docx_file, os.path.join(desktop_dir, docx_file))
        shutil.copy2(pdf_file, os.path.join(desktop_dir, pdf_file))
        print(f"Copied {docx_file} and {pdf_file} to Desktop!")
