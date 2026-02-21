"""
Main Anki card generator with PDF and JSON support.

Supports:
- AI-powered PDF processing using Gemini
- Manual card creation from JSON files
"""

import warnings
warnings.filterwarnings("ignore")

import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from anki_generator import AnkiGenerator, SUPPORTED_LANGUAGES
from gemini.pdf_processor import extract_pages_as_pdf
from gemini.gemini_client import GeminiClient
from gemini.deck_registry import DeckRegistry


class CardGenerator:
    """Main orchestration class for generating Anki cards.
    
    Supports both:
    - AI-powered PDF processing using Gemini
    - Manual card creation from JSON files
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
        language: str = "german",
        output_file: Optional[str] = None,
        registry_path: str = "deck_registry.json",
        custom_prompt: Optional[str] = None
    ):
        """Initialize the card generator.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
                     Only required for PDF processing.
            model: Gemini model name. Defaults to gemini-2.0-flash.
            language: Target language (e.g., "german", "chinese").
            output_file: Path to the output .apkg file.
            registry_path: Path to the deck registry JSON file.
            custom_prompt: Optional additional instructions to pass to Gemini.
        """
        self._is_default_output = output_file is None
        self.output_file = output_file or f"{language}_learning_deck.apkg"
        self.model = model
        self.api_key = api_key
        self.custom_prompt = custom_prompt
        self.registry = DeckRegistry(registry_path=registry_path)
        
        # Get language config
        lang_key = language.lower()
        self._config = SUPPORTED_LANGUAGES.get(lang_key, SUPPORTED_LANGUAGES["german"])
        
        self.anki = AnkiGenerator(self._config)
        self._gemini: Optional[GeminiClient] = None
    
    @property
    def gemini(self) -> GeminiClient:
        """Lazy initialization of Gemini client (only when needed for PDF)."""
        if self._gemini is None:
            self._gemini = GeminiClient(config=self._config, api_key=self.api_key, model=self.model)
        return self._gemini
    
    # ==================== JSON Import ====================
    
    def generate_from_json(
        self,
        json_path: str,
        verbose: bool = True
    ) -> dict:
        """Generate Anki cards from a JSON file.
        
        JSON format:
        {
            "vocabulary": [
                {
                    "chapter": "Body Parts",
                    "word": "der Kopf",
                    "word_translation": "head",
                    "sentence": "Mein Kopf tut weh.",
                    "sentence_translation": "My head hurts."
                }
            ],
            "grammar": [
                {
                    "question": "What is the accusative form of 'der'?",
                    "answer": "den"
                }
            ]
        }
        
        Args:
            json_path: Path to the JSON file.
            verbose: Whether to print progress messages.
            
        Returns:
            A summary dict with:
                - vocabulary_cards: Number of vocabulary cards generated
                - grammar_cards: Number of grammar cards generated
                - categories: List of vocabulary categories processed
                - errors: List of validation errors (if any)
        """
        if verbose:
            print(f"📄 Loading cards from {json_path}...")
        
        # Load and validate JSON
        data, errors = self._load_and_validate_json(json_path)
        
        if errors:
            if verbose:
                print(f"⚠️  Found {len(errors)} validation warnings:")
                for error in errors:
                    print(f"   - {error}")
        
        deck_counts = {}
        
        # Process all cards in JSON
        for key, cards_list in data.items():
            key_lower = key.lower()
            if key_lower in self._config.deck_type_names:
                deck_type = self._config.get_deck_type(key_lower) or key.title()
                cards_processed = self._process_qa_from_json(deck_type, cards_list, verbose)
                deck_counts[deck_type] = cards_processed
        
        # Determine export path if not manually specified
        if self._is_default_output:
            if len(deck_counts) == 1:
                deck_type_for_path = list(deck_counts.keys())[0]
                output_dir = Path(self._config.name) / deck_type_for_path.lower()
                output_dir.mkdir(parents=True, exist_ok=True)
                self.output_file = str(output_dir / f"{self._config.name}_{deck_type_for_path}.apkg")
            elif len(deck_counts) > 1:
                output_dir = Path(self._config.name)
                output_dir.mkdir(parents=True, exist_ok=True)
                self.output_file = str(output_dir / f"{self._config.name}_learning_deck.apkg")

        # Export
        if verbose:
            print(f"💾 Exporting to {self.output_file}...")
        
        self.anki.export(self.output_file)
        
        total_cards = sum(deck_counts.values())
        if verbose:
            print(f"✅ Done! Generated {total_cards} cards")
        
        return {
            "total_cards": total_cards,
            "deck_counts": deck_counts,
            "errors": errors
        }
    
    def _load_and_validate_json(self, json_path: str) -> tuple[dict, List[str]]:
        """Load and validate the JSON file.
        
        Args:
            json_path: Path to the JSON file.
            
        Returns:
            Tuple of (data dict, list of validation errors).
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist.
            json.JSONDecodeError: If the JSON is invalid.
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        errors = []
        
        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        
        valid_keys = [k for k in data.keys() if k.lower() in self._config.deck_type_names]
        if not valid_keys:
            raise ValueError(f"JSON must contain at least one valid array: {self._config.deck_type_names}")
        
        for key in list(data.keys()):
            key_lower = key.lower()
            if key_lower not in self._config.deck_type_names:
                errors.append(f"Unknown content type in JSON: {key}")
                continue
                
            if not isinstance(data[key], list):
                raise ValueError(f"'{key}' must be an array")
                
            required_qa_fields = ["question", "answer"]
            for i, card in enumerate(data[key]):
                for field in required_qa_fields:
                    if field not in card:
                        errors.append(f"{key.title()} card {i+1}: missing required field '{field}'")
                    elif not card[field] or not card[field].strip():
                        errors.append(f"{key.title()} card {i+1}: field '{field}' is empty")
        
        return data, errors
    
    def _process_qa_from_json(
        self,
        deck_type: str,
        cards_data: List[Dict[str, str]],
        verbose: bool
    ) -> int:
        """Process Q&A cards from JSON data.
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
            cards_data: List of card dicts with question/answer.
            verbose: Whether to print progress.
            
        Returns:
            Number of cards added.
        """
        if verbose:
            print(f"📖 Processing {len(cards_data)} {deck_type.lower()} cards...")
        
        # Ensure deck exists
        self.anki.create_qa_deck(deck_type)
        
        cards_added = 0
        for card in cards_data:
            # Skip invalid cards
            if not card.get("question") or not card.get("answer"):
                continue
            
            self.anki.add_qa_card(
                deck_type=deck_type,
                question=card["question"],
                answer=card["answer"]
            )
            cards_added += 1
        
        if verbose:
            print(f"   → Added {cards_added} cards")
        
        return cards_added
    
    # ==================== Card Inspection ====================
    
    def _ask_inspect_cards(self) -> bool:
        """Ask the user if they want to inspect cards before adding them.
        
        Returns:
            True if user wants to inspect, False otherwise.
        """
        while True:
            response = input("\n🔍 Do you want to inspect cards before adding them to the deck? (yes/no): ").strip().lower()
            if response in ("yes", "y"):
                return True
            elif response in ("no", "n"):
                return False
            else:
                print("   Please enter 'yes' or 'no'.")
    
    def _display_card(self, card: Dict[str, Any], card_type: str, index: int, total: int) -> None:
        """Display a single card in the terminal.
        
        Args:
            card: The card data dict.
            card_type: Either "vocabulary" or "grammar".
            index: Current card index (0-based).
            total: Total number of cards.
        """
        print(f"\n{'='*50}")
        print(f"📇 Card {index + 1} of {total} ({card_type})")
        print(f"{'='*50}")
        
        if card_type == "vocabulary":
            print(f"📝 Word: {card.get('word', 'N/A')}")
            print(f"🔤 Translation: {card.get('word_translation', 'N/A')}")
            print(f"💬 Sentence: {card.get('sentence', 'N/A')}")
            print(f"🔤 Sentence Translation: {card.get('sentence_translation', 'N/A')}")
        else:  # grammar
            print(f"❓ Question: {card.get('question', 'N/A')}")
            print(f"✅ Answer: {card.get('answer', 'N/A')}")
        
        print(f"{'='*50}")
    
    def _edit_card(self, card: Dict[str, Any], card_type: str) -> Dict[str, Any]:
        """Let the user edit individual fields of a card.
        
        Args:
            card: The card data dict to edit.
            card_type: Either "vocabulary" or "grammar".
            
        Returns:
            The edited card dict.
        """
        edited_card = card.copy()
        
        print("\n✏️  Edit mode - press Enter to keep the current value")
        print("-" * 40)
        
        if card_type == "vocabulary":
            fields = [
                ("word", "📝 Word"),
                ("word_translation", "🔤 Translation"),
                ("sentence", "💬 Sentence"),
                ("sentence_translation", "🔤 Sentence Translation")
            ]
        else:  # grammar
            fields = [
                ("question", "❓ Question"),
                ("answer", "✅ Answer")
            ]
        
        for field_key, field_label in fields:
            current_value = edited_card.get(field_key, "")
            new_value = input(f"{field_label} [{current_value}]: ").strip()
            if new_value:
                edited_card[field_key] = new_value
        
        print("-" * 40)
        print("✓ Card updated!")
        
        return edited_card

    def _inspect_cards_interactively(
        self,
        cards: List[Dict[str, Any]],
        card_type: str
    ) -> List[Dict[str, Any]]:
        """Let the user inspect cards one by one and choose which to add.
        
        Args:
            cards: List of card dicts.
            card_type: Either "vocabulary" or "grammar".
            
        Returns:
            List of approved cards.
        """
        approved_cards = []
        total = len(cards)
        
        for i, card in enumerate(cards):
            current_card = card.copy()
            
            while True:
                self._display_card(current_card, card_type, i, total)
                
                response = input("➕ Add this card to the deck? ([yes]/no/edit): ").strip().lower()
                if response in ("yes", "y", ""):
                    approved_cards.append(current_card)
                    print("   ✓ Card will be added.")
                    break
                elif response in ("no", "n"):
                    print("   ✗ Card skipped.")
                    break
                elif response in ("edit", "e"):
                    current_card = self._edit_card(current_card, card_type)
                    # Loop continues to re-display the edited card
                else:
                    print("   Please enter 'yes', 'no', or 'edit'.")
        
        print(f"\n📊 Summary: {len(approved_cards)}/{total} cards approved for addition.")
        return approved_cards
    
    # ==================== PDF Processing ====================
    
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
        
        # Step 5: Determine export path if default, and Export
        if self._is_default_output:
            output_dir = Path(self._config.name) / deck_type.lower()
            output_dir.mkdir(parents=True, exist_ok=True)
            self.output_file = str(output_dir / f"{self._config.name}_{deck_type}.apkg")
            
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
        
        cards = self.gemini.generate_qa_cards(
            deck_type, 
            pdf_bytes, 
            custom_prompt=self.custom_prompt,
            template=template
        )
        
        if verbose:
            print(f"   → Generated {len(cards)} {deck_type.lower()} cards")
        
        # Ask if user wants to inspect cards before adding
        if cards and self._ask_inspect_cards():
            cards = self._inspect_cards_interactively(cards, deck_type.lower())
        
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
    """CLI entry point for the card generator."""
    import argparse
    from gemini.templates import CARD_TEMPLATES
    
    parser = argparse.ArgumentParser(
        description="Generate Anki cards from German textbook PDFs or JSON files"
    )
    
    # Source options (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--json", "-j",
        metavar="JSON_FILE",
        help="Path to JSON file containing cards"
    )
    source_group.add_argument(
        "--pdf", "-p",
        metavar="PDF_FILE",
        help="Path to PDF file"
    )
    
    # PDF-specific arguments
    parser.add_argument(
        "--start-page", "-s",
        type=int,
        help="Starting page number for PDF (1-indexed, required with --pdf)"
    )
    parser.add_argument(
        "--end-page", "-e",
        type=int,
        help="Ending page number for PDF (1-indexed, required with --pdf)"
    )
    parser.add_argument(
        "-t", "--type",
        help="Content type for PDF (e.g., grammar, vocabulary, radicals). If provided, skips classification."
    )
    parser.add_argument(
        "-m", "--model",
        default="gemini-2.0-flash",
        help="Gemini model name (default: gemini-2.0-flash)"
    )
    
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
        "--prompt",
        type=str,
        help="Additional instructions to pass to Gemini (e.g., 'Focus on verbs only')"
    )
    parser.add_argument(
        "--template",
        choices=list(CARD_TEMPLATES.keys()),
        help=f"Card formatting template to use (e.g. {', '.join(CARD_TEMPLATES.keys())})"
    )
    
    args = parser.parse_args()
    
    # Validate PDF arguments
    if args.pdf:
        if args.start_page is None or args.end_page is None:
            parser.error("--start-page and --end-page are required when using --pdf")
    
    generator = CardGenerator(
        model=args.model,
        language=args.language,
        output_file=args.output,
        registry_path=args.registry,
        custom_prompt=args.prompt
    )
    
    if args.json:
        # JSON mode
        result = generator.generate_from_json(
            json_path=args.json,
            verbose=not args.quiet
        )
        
        print(f"\nSummary:")
        print(f"  Total cards: {result['total_cards']}")
        for deck, count in result['deck_counts'].items():
            print(f"  {deck} cards: {count}")
        if result['errors']:
            print(f"  Validation warnings: {len(result['errors'])}")
    else:
        # PDF mode
        result = generator.generate_from_pdf(
            pdf_path=args.pdf,
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
