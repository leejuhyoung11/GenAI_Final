import fitz   # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract raw text from a PDF file (bytes).
    Requires: pip install pymupdf
    """
    text = ""
    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        for page in pdf:
            text += page.get_text()
        pdf.close()
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")
    
    return text