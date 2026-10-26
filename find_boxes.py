import easyocr

reader = easyocr.Reader(['en'], gpu=False)

targets = {
    2: ['H&E'],
    4: ['512'],
    8: ['Sampling Stride', 'stride'],
    9: ['H&E'],
    10: ['Comparative', 'DINOv3'],
    11: ['DINOv3', '+6.84%', '3D']
}

for slide_num, words in targets.items():
    img_path = f'd:/Project topics/dinov3-main/pdf_slides_extracted/slide_{slide_num}.png'
    results = reader.readtext(img_path)
    print(f'=== SLIDE {slide_num} ===')
    for bbox, text, prob in results:
        for w in words:
            if w.lower() in text.lower():
                print(f'  FOUND "{text}" at bbox: {bbox}')
