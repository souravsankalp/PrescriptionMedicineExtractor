# clean.py
from docx import Document
import re


def _read_docx_text(docx_path: str) -> str:
    """Read all non-empty paragraphs from the docx and join them with newlines."""
    doc = Document(docx_path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(lines)


def _fix_spaced_letters(line: str) -> str:
    """
    Fix patterns like: 'Cry s t a | Ey e s' -> 'Crystal Eyes'
    by joining sequences of single-letter tokens and cleaning '|'.
    """
    tokens = line.split()
    new_tokens = []
    buffer = []

    for tok in tokens:
        t = tok.replace("|", "l")  # common OCR issue: '|' instead of 'l'

        if len(t) == 1 and t.isalpha():
            # part of a spaced-out word (C r y s t a l)
            buffer.append(t)
        else:
            if buffer:
                new_tokens.append("".join(buffer))
                buffer = []
            new_tokens.append(t)

    if buffer:
        new_tokens.append("".join(buffer))

    return " ".join(new_tokens)


def clean_text(docx_path: str) -> str:
    """
    Public function:
    - Reads text from the given docx
    - Cleans spacing / junk
    - Returns a cleaned multi-line string
    """
    raw_text = _read_docx_text(docx_path)
    cleaned_lines = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # 1) Drop watermark / source lines (shutterstock etc.)
        if "shutter" in line.lower():
            continue

        # 2) Fix spaced letters and '|' issues
        line = _fix_spaced_letters(line)

        # 3) Normalize multiple spaces
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
