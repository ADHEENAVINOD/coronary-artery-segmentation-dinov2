import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf():
    pdf_filename = "FINAL_PROJECT_REPORT.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=54, leftMargin=54,
        topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1976d2'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#666666'),
        alignment=1, # Center
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1976d2'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#333333'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#444444'),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#444444'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#333333')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )
    
    story = []
    
    # Document Header
    story.append(Paragraph("Final Research Report: Integrating Topological Priors and Self-Supervised Learning for Coronary Artery Segmentation", title_style))
    story.append(Paragraph("A Chronological Summary of Progress and Experimental Results", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Section 1
    story.append(Paragraph("1. Clinical Context & Objective", h1_style))
    story.append(Paragraph("<b>The Clinical Need</b>: Cardiovascular disease is a leading cause of death globally. To properly diagnose, treat, and predict patient cardiac conditions, clinicians must evaluate the degree of coronary artery stenosis (arterial blockage).", body_style))
    story.append(Paragraph("<b>The Problem</b>: Pathologists traditionally estimate stenosis visually under a microscope, which introduces inter-observer subjectivity and variations.", body_style))
    story.append(Paragraph("<b>The AI Goal</b>: Build an automated deep learning pipeline that segments coronary artery tissue layers—namely the Lumen (flow channel), Intima (plaque layer), and Media (outer wall)—to calculate the stenosis percentage objectively and precisely.", body_style))
    story.append(Spacer(1, 10))
    
    # Section 2
    story.append(Paragraph("2. Chronological Project Progress", h1_style))
    story.append(Paragraph("<b>Phase 1: Data Preparation & ROI Extraction</b><br/>High-resolution Whole-Slide Images (WSIs) were cropped using annotation coordinates exported from QuPath (.geojson files). 16 high-quality Regions of Interest (ROIs) containing coronary arteries were extracted and preprocessed.", body_style))
    story.append(Paragraph("<b>Phase 2: Self-Supervised Feature Extraction</b><br/>Image patches were processed through a pre-trained Vision Transformer (DINOv2) to extract deep, robust visual feature representations of tissues.", body_style))
    story.append(Paragraph("<b>Phase 3: Unsupervised Pseudo-Labeling</b><br/>Applied K-Means Clustering and PCA to group features into 5 distinct classes (Background, Media, Intima, Lumen, Extra) to act as training ground-truth masks.", body_style))
    story.append(Paragraph("<b>Phase 4: Baseline Decoder Training</b><br/>Constructed a 3-layer Convolutional Neural Network (CNN) segmentation decoder on top of the frozen backbone and trained it using Cross-Entropy Loss.", body_style))
    story.append(Paragraph("<b>Phase 5: Integrating Topological Constraints (clDice Loss)</b><br/>Individual pixel classification led to broken artery contours and fragmented lumen regions. We integrated clDice (Centerline Dice) loss into the training loop, enforcing loop connectivity and anatomical correctness.", body_style))
    story.append(Paragraph("<b>Phase 6: Performance Engineering (Lazy Loading & Caching)</b><br/>Implemented lazy loading to load patches on-the-fly, dropping RAM usage from 16,000 MB to under 100 MB. Built an offline crop cache which reduced training speed from 6 hours to under 2 minutes.", body_style))
    story.append(Paragraph("<b>Phase 7: Final Training & Validation</b><br/>Re-trained the model on all 16 slides for 20 epochs, successfully generating smooth, continuous boundaries matching human anatomy.", body_style))
    story.append(Spacer(1, 10))
    
    # Section 3
    story.append(Paragraph("3. Quantitative Experimental Results", h1_style))
    story.append(Paragraph("Below is the comparison of the model's performance on the test set before and after implementing the topological constraint:", body_style))
    
    # Table Data
    data = [
        [
            Paragraph("Metric", table_header_style),
            Paragraph("Baseline Model", table_header_style),
            Paragraph("Topology Model (clDice)", table_header_style),
            Paragraph("Improvement", table_header_style)
        ],
        [
            Paragraph("Average Test Accuracy", table_cell_style),
            Paragraph("57.33%", table_cell_style),
            Paragraph("64.17%", table_cell_style),
            Paragraph("+6.84%", table_cell_style)
        ],
        [
            Paragraph("Average Test Mean IoU", table_cell_style),
            Paragraph("0.300", table_cell_style),
            Paragraph("0.381", table_cell_style),
            Paragraph("+0.081", table_cell_style)
        ]
    ]
    
    t = Table(data, colWidths=[180, 100, 130, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1976d2')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Section 4
    story.append(Paragraph("4. Active Code Files Summary", h1_style))
    story.append(Paragraph("&bull; <b>scripts/train_baseline.py</b>: The core training loop containing the Hugging Face model loading, the lazy-loading dataset with offline caching, and the clDice loss.", bullet_style))
    story.append(Paragraph("&bull; <b>scripts/visualize_predictions.py</b>: The evaluation script that runs inference and generates the side-by-side comparison overlays.", bullet_style))
    
    # Build Document
    doc.build(story)
    print("Successfully generated PDF: FINAL_PROJECT_REPORT.pdf")

if __name__ == "__main__":
    build_pdf()
