"""
Gemini API client for content classification and card generation.

Uses PDF bytes directly instead of extracted text for better comprehension.
"""

import json
import os
import re
from typing import Optional, List, Dict, Tuple

from google import genai
from google.genai import types

from .prompts import build_classification_prompt, get_deck_type_prompt


class GeminiClient:
    """Wrapper for Gemini API interactions.
    
    Handles content classification and card generation using Google's Gemini API.
    Accepts PDF bytes directly for better document understanding.
    """
    
    def __init__(self, config, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """Initialize the Gemini client.
        
        Args:
            config: A LanguageConfig object with name, deck_types, etc.
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
        self.config = config
        
        # Build classification prompt from config's deck types
        self._classification_prompt = build_classification_prompt(
            config.name, config.deck_types
        )
    
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
    
    def classify_content(self, pdf_bytes: bytes) -> str:
        """Classify PDF content type.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            
        Returns:
            A content type string (e.g., "grammar", "radicals", "vocabulary").
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                self._classification_prompt
            ]
        )
        result = response.text.strip().lower()
        
        # Check against all configured deck types
        for dt in self.config.deck_types:
            if dt.lower() in result:
                return dt.lower()
        # Fallback to the first available deck type
        if self.config.deck_types:
            return self.config.deck_types[0].lower()
        return "vocabulary"
    
    def generate_qa_cards(
        self,
        deck_type: str,
        pdf_bytes: bytes,
        custom_prompt: Optional[str] = None,
        template: Optional[str] = None
    ) -> List[Dict]:
        """Generate Q&A card pairs from PDF for a given deck type.
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
            pdf_bytes: The PDF pages as bytes.
            custom_prompt: Optional additional instructions to append to the prompt.
            template: Optional card formatting template (e.g., "basic", "detailed").
            
        Returns:
            List of dicts with 'question' and 'answer' keys.
        """
        prompt = get_deck_type_prompt(self.config.name, deck_type, template=template)
        if custom_prompt:
            prompt = f"{prompt}\n\nAdditional instructions: {custom_prompt}"
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
                prompt
            ]
        )
        
        data = self._extract_json(response.text)
        return data.get("cards", [])
    

