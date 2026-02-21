"""
Main PDF to Anki card generator.

Orchestrates the full pipeline from PDF to Anki deck.
"""

import sys
from pathlib import Path
from typing import Optional, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from anki_generator import AnkiGenerator, SUPPORTED_LANGUAGES

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
        model: str = "gemini-2.0-flash",
        language: str = "german",
        output_file: Optional[str] = None,
        registry_path: str = "deck_registry.json"
    ):
        """Initialize the PDF card generator.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: Gemini model name. Defaults to gemini-2.0-flash.
            language: Target language (e.g., "german", "chinese").
            output_file: Path to the output .apkg file.
            registry_path: Path to the deck registry JSON file.
        """
        self._is_default_output = output_file is None
        self.output_file = output_file or f"{language}_learning_deck.apkg"
        
        # Get language config
        lang_key = language.lower()
        self._config = SUPPORTED_LANGUAGES.get(lang_key, SUPPORTED_LANGUAGES["german"])
        
        self.gemini = GeminiClient(config=self._config, api_key=api_key, model=model)
        self.registry = DeckRegistry(registry_path=registry_path)
        self.anki = AnkiGenerator(self._config)
    
    def generate_from_pdf(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int,
        content_type: Optional[str] = None,
        verbose: bool = True,
        template: Optional[str] = None
    ) -> dict:
        """Generate cards from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            start_page: Starting page number (1-indexed, inclusive).
            end_page: Ending page number (1-indexed, inclusive).
            content_type: Optional. "grammar", "vocabulary", etc. If provided,
                skips the classification API call.
            verbose: Whether to print progress messages.
            template: Optional card formatting template (e.g., "basic", "detailed").
            
        Returns:
            A summary dict with:
                - content_type: "grammar" or "vocabulary"
                - category: Category name (for vocabulary) or None
                - cards_generated: Number of cards generated
                - deck_action: "extended" or "created"
        """
        if content_type:
            content_type = content_type.lower()
            if content_type not in self._config.deck_type_names:
                raise ValueError(
                    f"Invalid content type '{content_type}' for {self._config.name}. "
                    f"Valid types: {', '.join(self._config.deck_type_names)}"
                )
            if verbose:
                print(f"🔍 Using provided content type: {content_type.upper()}")

        if verbose:
            print(f"📄 Extracting pages {start_page}-{end_page} from PDF...")
        
        # Step 1: Extract pages as PDF bytes
        pdf_bytes = extract_pages_as_pdf(pdf_path, start_page, end_page)
        
        if verbose:
            print(f"📝 Extracted {len(pdf_bytes)} bytes ({end_page - start_page + 1} pages)")
        
        # Step 2: Classify content (skip if provided)
        if not content_type:
            if verbose:
                print("🔍 Classifying content type...")
            content_type = self.gemini.classify_content(pdf_bytes)
            if verbose:
                print(f"   → Detected: {content_type.upper()}")
        
        # Step 3 & 4: Generate cards and update decks
        deck_type = self._config.get_deck_type(content_type)
        if deck_type is None:
            deck_type = content_type.title()
        result = self._handle_qa_type(deck_type, pdf_bytes, verbose, template=template)
        
        # Step 5: Determine export path
        output_dir = Path("generated_cards") / self._config.name / deck_type.lower()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self._is_default_output:
            self.output_file = str(output_dir / f"{self._config.name}_{deck_type}.apkg")
        else:
            out_path = Path(self.output_file)
            if str(out_path.parent) == ".":
                self.output_file = str(output_dir / self.output_file)
        if verbose:
            print(f"💾 Exporting to {self.output_file}...")
        
        self.anki.export(self.output_file)
        
        if verbose:
            print(f"✅ Done! Generated {result['cards_generated']} cards")
        
        return result
    
    def _handle_qa_type(self, deck_type: str, pdf_bytes: bytes, verbose: bool, template: Optional[str] = None) -> dict:
        """Handle Q&A content: generate cards and add to the appropriate deck.
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
            pdf_bytes: The PDF pages as bytes.
            verbose: Whether to print progress messages.
            template: Optional card formatting template (e.g., "basic", "detailed").
            
        Returns:
            Summary dict with content_type and cards_generated.
        """
        if verbose:
            print(f"📚 Generating {deck_type.lower()} cards...")
        
        cards = self.gemini.generate_qa_cards(deck_type, pdf_bytes, template=template)
        
        if verbose:
            print(f"   → Generated {len(cards)} {deck_type.lower()} cards")
        
        # Ensure deck exists and add cards
        self.anki.create_qa_deck(deck_type)
        
        for card in cards:
            self.anki.add_qa_card(
                deck_type=deck_type,
                question=card["question"],
                answer=card["answer"]
            )
        
        return {
            "content_type": deck_type.lower(),
            "category": None,
            "cards_generated": len(cards),
        }
    


def main():
    """CLI entry point for the PDF card generator."""
    import argparse
    from .templates import CARD_TEMPLATES
    
    parser = argparse.ArgumentParser(
        description="Generate Anki cards from German textbook PDFs using Gemini AI"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("start_page", type=int, help="Starting page number (1-indexed)")
    parser.add_argument("end_page", type=int, help="Ending page number (1-indexed)")
    parser.add_argument(
        "-l", "--language",
        choices=list(SUPPORTED_LANGUAGES.keys()),
        default="german",
        help="Target language for cards (default: german)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output .apkg file path (default: <language>_learning_deck.apkg)"
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
    parser.add_argument(
        "-m", "--model",
        default="gemini-2.0-flash",
        help="Gemini model name (default: gemini-2.0-flash)"
    )
    parser.add_argument(
        "-t", "--type",
        help="Content type (e.g., grammar, vocabulary, radicals). If provided, skips classification."
    )
    parser.add_argument(
        "--template",
        choices=list(CARD_TEMPLATES.keys()),
        help=f"Card formatting template to use (e.g. {', '.join(CARD_TEMPLATES.keys())})"
    )
    
    args = parser.parse_args()
    
    generator = PDFCardGenerator(
        model=args.model,
        language=args.language,
        output_file=args.output,
        registry_path=args.registry
    )
    
    result = generator.generate_from_pdf(
        pdf_path=args.pdf_path,
        start_page=args.start_page,
        end_page=args.end_page,
        content_type=args.type,
        verbose=not args.quiet,
        template=args.template
    )
    
    print(f"\nSummary:")
    print(f"  Content type: {result['content_type']}")
    print(f"  Cards generated: {result['cards_generated']}")


if __name__ == "__main__":
    main()
