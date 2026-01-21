"""
Gemini-powered PDF to Anki card generator.

This module provides functionality to:
- Extract specific pages from PDF files
- Pass PDF directly to Gemini for better visual understanding
- Classify content as grammar or vocabulary
- Generate Anki cards using Google's Gemini API
- Integrate with the anki_generator module
"""

from .generator import PDFCardGenerator
from .gemini_client import GeminiClient
from .deck_registry import DeckRegistry
from .pdf_processor import extract_pages_as_pdf, get_pdf_page_count

__all__ = [
    "PDFCardGenerator",
    "GeminiClient", 
    "DeckRegistry",
    "extract_pages_as_pdf",
    "get_pdf_page_count",
]
