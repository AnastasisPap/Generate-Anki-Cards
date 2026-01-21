"""
Main PDF to Anki card generator.

Orchestrates the full pipeline from PDF to Anki deck.
"""

import sys
from pathlib import Path
from typing import Optional, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from anki_generator import AnkiGenerator, GERMAN

from .pdf_processor import extract_pages_as_pdf
from .gemini_client import GeminiClient
from .deck_registry import DeckRegistry


class PDFCardGenerator:
    """Main orchestration class for generating Anki cards from PDFs.
    
    This class:
    1. Extracts specified pages from PDF
    2. Uses Gemini to classify content (grammar vs vocabulary)
    3. Generates appropriate cards
    4. Extends existing decks or creates new ones
    5. Exports the updated deck
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        output_file: str = "german_learning_deck.apkg",
        registry_path: str = "deck_registry.json"
    ):
        """Initialize the PDF card generator.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            output_file: Path to the output .apkg file.
            registry_path: Path to the deck registry JSON file.
        """
        self.output_file = output_file
        self.gemini = GeminiClient(api_key=api_key)
        self.registry = DeckRegistry(registry_path=registry_path)
        self.anki = AnkiGenerator(GERMAN)
    
    def generate_from_pdf(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int,
        verbose: bool = True
    ) -> dict:
        """Generate Anki cards from PDF pages.
        
        Main method that orchestrates the full pipeline:
        1. Extract specified pages as PDF bytes
        2. Pass PDF to Gemini for classification
        3. Generate appropriate cards
        4. Extend existing deck or create new one
        5. Export updated deck
        
        Args:
            pdf_path: Path to the PDF file.
            start_page: Starting page number (1-indexed, inclusive).
            end_page: Ending page number (1-indexed, inclusive).
            verbose: Whether to print progress messages.
            
        Returns:
            A summary dict with:
                - content_type: "grammar" or "vocabulary"
                - category: Category name (for vocabulary) or None
                - cards_generated: Number of cards generated
                - deck_action: "extended" or "created"
        """
        if verbose:
            print(f"📄 Extracting pages {start_page}-{end_page} from PDF...")
        
        # Step 1: Extract pages as PDF bytes
        pdf_bytes = extract_pages_as_pdf(pdf_path, start_page, end_page)
        
        if verbose:
            print(f"📝 Extracted {len(pdf_bytes)} bytes ({end_page - start_page + 1} pages)")
        
        # Step 2: Classify content
        if verbose:
            print("🔍 Classifying content type...")
        
        content_type = self.gemini.classify_content(pdf_bytes)
        
        if verbose:
            print(f"   → Detected: {content_type.upper()}")
        
        # Step 3 & 4: Generate cards and update decks
        if content_type == "grammar":
            result = self._handle_grammar(pdf_bytes, verbose)
        else:
            result = self._handle_vocabulary(pdf_bytes, verbose)
        
        # Step 5: Export
        if verbose:
            print(f"💾 Exporting to {self.output_file}...")
        
        self.anki.export(self.output_file)
        
        if verbose:
            print(f"✅ Done! Generated {result['cards_generated']} cards")
        
        return result
    
    def _handle_grammar(self, pdf_bytes: bytes, verbose: bool) -> dict:
        """Handle grammar content: generate cards and add to grammar deck.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            verbose: Whether to print progress messages.
            
        Returns:
            Summary dict with content_type and cards_generated.
        """
        if verbose:
            print("📚 Generating grammar cards...")
        
        cards = self.gemini.generate_grammar_cards(pdf_bytes)
        
        if verbose:
            print(f"   → Generated {len(cards)} grammar cards")
        
        # Ensure grammar deck exists and add cards
        self.anki.create_grammar_deck()
        
        for card in cards:
            self.anki.add_grammar_card(
                question=card["question"],
                answer=card["answer"]
            )
        
        return {
            "content_type": "grammar",
            "category": None,
            "cards_generated": len(cards),
        }
    
    def _handle_vocabulary(self, pdf_bytes: bytes, verbose: bool) -> dict:
        """Handle vocabulary content: detect category, generate cards, manage deck.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            verbose: Whether to print progress messages.
            
        Returns:
            Summary dict with content_type, category, cards_generated, deck_action.
        """
        if verbose:
            print("🏷️  Detecting vocabulary category...")
        
        # Get existing categories so Gemini can match them
        existing_categories = self.registry.get_vocabulary_categories()
        category = self.gemini.extract_vocabulary_category(pdf_bytes, existing_categories)
        
        if verbose:
            print(f"   → Category: {category}")
        
        # Check if category exists (Gemini should match, but do case-insensitive check)
        existing_category = self.registry.find_matching_category(category)
        
        if existing_category:
            deck_action = "extended"
            chapter_name = existing_category
            if verbose:
                print(f"   → Extending existing deck: {existing_category}")
        else:
            deck_action = "created"
            chapter_name = category
            if verbose:
                print(f"   → Creating new deck: {category}")
        
        # Generate vocabulary cards
        if verbose:
            print("📚 Generating vocabulary cards...")
        
        cards = self.gemini.generate_vocabulary_cards(pdf_bytes)
        
        if verbose:
            print(f"   → Generated {len(cards)} vocabulary cards")
        
        # Ensure chapter deck exists
        self.anki.create_vocabulary_chapter(chapter_name)
        
        # Add cards
        for card in cards:
            self.anki.add_vocabulary_card(
                chapter=chapter_name,
                word=card["word"],
                word_translation=card["word_translation"],
                sentence=card["sentence"],
                sentence_translation=card["sentence_translation"]
            )
        
        # Register the category
        self.registry.register_vocabulary_category(chapter_name)
        
        return {
            "content_type": "vocabulary",
            "category": chapter_name,
            "cards_generated": len(cards),
            "deck_action": deck_action
        }


def main():
    """CLI entry point for the PDF card generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Anki cards from German textbook PDFs using Gemini AI"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("start_page", type=int, help="Starting page number (1-indexed)")
    parser.add_argument("end_page", type=int, help="Ending page number (1-indexed)")
    parser.add_argument(
        "-o", "--output",
        default="german_learning_deck.apkg",
        help="Output .apkg file path (default: german_learning_deck.apkg)"
    )
    parser.add_argument(
        "-r", "--registry",
        default="deck_registry.json",
        help="Deck registry file path (default: deck_registry.json)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    generator = PDFCardGenerator(
        output_file=args.output,
        registry_path=args.registry
    )
    
    result = generator.generate_from_pdf(
        pdf_path=args.pdf_path,
        start_page=args.start_page,
        end_page=args.end_page,
        verbose=not args.quiet
    )
    
    print(f"\nSummary:")
    print(f"  Content type: {result['content_type']}")
    if result['category']:
        print(f"  Category: {result['category']}")
    print(f"  Cards generated: {result['cards_generated']}")
    if 'deck_action' in result:
        print(f"  Deck action: {result['deck_action']}")


if __name__ == "__main__":
    main()
