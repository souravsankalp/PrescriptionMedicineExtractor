# extraction.py
from pathlib import Path

import cv2
import easyocr
from docx import Document

# Folder where you want to save .docx files
TEMP_TEXT_DIR = Path(r"E:\ImageTextSqubix\temp")

# One global EasyOCR reader
reader = easyocr.Reader(['en'])   # add more langs if needed, e.g. ['en', 'hi']


def extract_text_from_image(image_path, file_id="output"):
    """
    Uses EasyOCR to extract text from the image, groups into lines
    (top-to-bottom, left-to-right), and saves:
      E:\\ImageTextSqubix\\temp\\<file_id>.docx

    Returns the docx file path as a string.
    """
    TEMP_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Read image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image from path: {image_path}")

    # 2) Run OCR with boxes + text
    # results: [ [box, text, conf], ... ]
    results = reader.readtext(img, detail=1)

    # 3) Collect boxes as (y_center, x_min, text)
    all_boxes = []
    for item in results:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue

        box = item[0]
        text = item[1]

        text = str(text).strip()
        if not text:
            continue

        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        x_min = min(xs)
        y_center = sum(ys) / len(ys)

        all_boxes.append((y_center, x_min, text))

    lines = []

    if all_boxes:
        # sort top-to-bottom, then left-to-right
        all_boxes.sort(key=lambda t: (t[0], t[1]))

        current_line = []
        current_y = None
        Y_THRESHOLD = 15  # pixels tolerance for "same line"

        for y_center, x_min, text in all_boxes:
            if current_y is None:
                current_y = y_center
                current_line.append((x_min, text))
            elif abs(y_center - current_y) <= Y_THRESHOLD:
                current_line.append((x_min, text))
            else:
                # flush previous line
                current_line.sort(key=lambda t: t[0])
                lines.append(" ".join(t for _, t in current_line))

                current_line = [(x_min, text)]
                current_y = y_center

        if current_line:
            current_line.sort(key=lambda t: t[0])
            lines.append(" ".join(t for _, t in current_line))

    # Optional: drop watermark lines like "shutterstock"
    # lines = [ln for ln in lines if "shutter" not in ln.lower()]

    # 4) Write DOCX
    docx_path = TEMP_TEXT_DIR / f"{file_id}.docx"
    doc = Document()

    if lines:
        for line in lines:
            doc.add_paragraph(line)
    else:
        doc.add_paragraph("")  # empty document if nothing recognized

    doc.save(docx_path)

    return str(docx_path)
