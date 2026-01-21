"""
PDF processing module.

Handles extracting specific pages from PDF files for Gemini processing.
"""

import fitz  # PyMuPDF


def extract_pages_as_pdf(pdf_path: str, start_page: int, end_page: int) -> bytes:
    """Extract specified pages from a PDF and return as PDF bytes.
    
    This creates a new PDF containing only the specified pages,
    which can be passed directly to Gemini's API.
    
    Args:
        pdf_path: Path to the PDF file.
        start_page: Starting page number (1-indexed, inclusive).
        end_page: Ending page number (1-indexed, inclusive).
    
    Returns:
        The extracted pages as PDF bytes.
    
    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        ValueError: If page numbers are invalid.
    """
    doc = fitz.open(pdf_path)
    
    # Validate page numbers
    if start_page < 1:
        raise ValueError("start_page must be at least 1")
    if end_page > len(doc):
        raise ValueError(f"end_page ({end_page}) exceeds document pages ({len(doc)})")
    if start_page > end_page:
        raise ValueError("start_page must be less than or equal to end_page")
    
    # Create new PDF with only the specified pages
    new_doc = fitz.open()  # Empty PDF
    
    # PyMuPDF uses 0-indexed pages
    for page_num in range(start_page - 1, end_page):
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
    # Get as bytes
    pdf_bytes = new_doc.tobytes()
    
    new_doc.close()
    doc.close()
    
    return pdf_bytes


def get_pdf_page_count(pdf_path: str) -> int:
    """Get the total number of pages in a PDF file.
    
    Args:
        pdf_path: Path to the PDF file.
    
    Returns:
        The number of pages in the PDF.
    """
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count
