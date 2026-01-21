"""
Gemini API client for content classification and card generation.

Uses PDF bytes directly instead of extracted text for better comprehension.
"""

import json
import os
import re
from typing import Literal, Optional, List, Dict, Tuple

from google import genai
from google.genai import types

from .prompts import (
    CLASSIFICATION_PROMPT,
    GRAMMAR_CARD_PROMPT,
    get_vocabulary_cards_prompt,
)


class GeminiClient:
    """Wrapper for Gemini API interactions.
    
    Handles content classification and card generation using Google's Gemini API.
    Accepts PDF bytes directly for better document understanding.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """Initialize the Gemini client.
        
        Args:
            api_key: The Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: The Gemini model to use. Defaults to gemini-2.0-flash.
        
        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Provide via api_key parameter or "
                "set GEMINI_API_KEY environment variable."
            )
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from model response, handling markdown code blocks.
        
        Args:
            text: The raw model response text.
            
        Returns:
            Parsed JSON dictionary.
        
        Raises:
            ValueError: If text is None or empty.
        """
        if not text:
            raise ValueError("Gemini returned empty response. The model may have failed to process the PDF.")
        
        # Try to find JSON in code blocks first
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = text
        
        return json.loads(json_str)
    
    def classify_content(self, pdf_bytes: bytes) -> Literal["grammar", "vocabulary"]:
        """Classify if PDF content is grammar or vocabulary.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            
        Returns:
            Either "grammar" or "vocabulary".
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                CLASSIFICATION_PROMPT
            ]
        )
        result = response.text.strip().lower()
        
        if "grammar" in result:
            return "grammar"
        return "vocabulary"
    
    def generate_grammar_cards(self, pdf_bytes: bytes) -> List[Dict]:
        """Generate grammar card Q&A pairs from PDF.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            
        Returns:
            List of dicts with 'question' and 'answer' keys.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                GRAMMAR_CARD_PROMPT
            ]
        )
        
        data = self._extract_json(response.text)
        return data.get("cards", [])
    
    def generate_vocabulary_cards(
        self, 
        pdf_bytes: bytes, 
        existing_categories: List[str] = None
    ) -> List[Tuple[str, List[Dict]]]:
        """Generate vocabulary cards from PDF, including category detection.
        
        This combines category detection and card generation into a single API call.
        Supports PDFs with multiple vocabulary categories.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            existing_categories: List of existing category names. If provided,
                Gemini will prefer matching one of these.
            
        Returns:
            A list of tuples, each containing (category_name, cards) where:
            - category_name: The detected/matched category (e.g., "Body Parts")
            - cards: List of dicts with 'word', 'word_translation', 
                     'sentence', and 'sentence_translation' keys.
        """
        prompt = get_vocabulary_cards_prompt(existing_categories or [])
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                prompt
            ]
        )
        
        data = self._extract_json(response.text)
        
        # Handle new multi-category format
        if "categories" in data:
            result = []
            for cat_data in data["categories"]:
                category = cat_data.get("category", "Vocabulary")
                cards = cat_data.get("cards", [])
                result.append((category, cards))
            return result
        
        # Fallback for legacy single-category format
        category = data.get("category", "Vocabulary")
        cards = data.get("cards", [])
        return [(category, cards)]

