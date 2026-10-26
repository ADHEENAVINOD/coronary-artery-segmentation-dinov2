import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf():
    pdf_filename = "machine_learning_summary.pdf"
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
        fontSize=22,
        leading=26,
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
        fontSize=15,
        leading=19,
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
        leading=13,
        textColor=colors.HexColor('#444444'),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#444444'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # Document Header
    story.append(Paragraph("Technical Summary: Machine Learning Methodologies", title_style))
    story.append(Paragraph("Project: Coronary Artery Segmentation & Stenosis Detection", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Section 1
    story.append(Paragraph("1. Self-Supervised Representation Learning (Backbone)", h1_style))
    story.append(Paragraph("<b>Model</b>: facebook/dinov2-small (Hugging Face transformers)", h2_style))
    story.append(Paragraph("&bull; Extracts high-quality semantic visual features from artery tissue patch inputs.", bullet_style))
    story.append(Paragraph("&bull; Utilizes self-supervised pre-trained weights to capture visual contours, textures, and structures without requiring human-annotated labels.", bullet_style))
    story.append(Paragraph("&bull; Operates with frozen parameters during training to prevent overfitting on the custom dataset.", bullet_style))
    story.append(Spacer(1, 8))
    
    # Section 2
    story.append(Paragraph("2. Supervised Segmentation Head (Decoder)", h1_style))
    story.append(Paragraph("<b>Architecture</b>: 3-layer Convolutional Segmentation Head", h2_style))
    story.append(Paragraph("&bull; Consists of consecutive 2D convolutions, Batch Normalization, and ReLU activations.", bullet_style))
    story.append(Paragraph("&bull; Decodes the extracted 384-dimensional DINOv2 features into the spatial segmentation maps.", bullet_style))
    story.append(Paragraph("&bull; Outputs pixel-level predictions across the 5 target classes representing vessel anatomy.", bullet_style))
    story.append(Spacer(1, 8))
    
    # Section 3
    story.append(Paragraph("3. Anatomy-Aware Loss Functions", h1_style))
    story.append(Paragraph("<b>Cross-Entropy Loss (CE)</b>", h2_style))
    story.append(Paragraph("Evaluates pixel-by-pixel classification errors compared to the pseudo-ground truth masks.", body_style))
    story.append(Paragraph("<b>clDice (Centerline Dice) Loss</b>", h2_style))
    story.append(Paragraph("&bull; Applies soft morphological erosion and dilation (soft skeletonization) during backpropagation.", bullet_style))
    story.append(Paragraph("&bull; Enforces connectivity on the Media (outer wall) and Lumen (blood channel) to guarantee biologically plausible loop shapes rather than fragmented boundaries.", bullet_style))
    story.append(Spacer(1, 8))
    
    # Section 4
    story.append(Paragraph("4. Unsupervised Data Processing", h1_style))
    story.append(Paragraph("<b>K-Means Clustering</b>", h2_style))
    story.append(Paragraph("Groups deep visual feature patches into 5 structural clusters (Background, Media, Intima, Lumen, Extra) to automatically construct ground-truth annotations.", body_style))
    story.append(Paragraph("<b>Principal Component Analysis (PCA)</b>", h2_style))
    story.append(Paragraph("Reduces the 384-dimensional features to 3 principal components mapped as RGB channels to visually confirm feature grouping quality.", body_style))
    
    # Build Document
    doc.build(story)
    print("Successfully generated PDF: machine_learning_summary.pdf")

if __name__ == "__main__":
    build_pdf()
