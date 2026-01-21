"""
Main Anki card generator with PDF and JSON support.

Supports:
- AI-powered PDF processing using Gemini
- Manual card creation from JSON files
"""

import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from anki_generator import AnkiGenerator, GERMAN
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
        output_file: str = "german_learning_deck.apkg",
        registry_path: str = "deck_registry.json"
    ):
        """Initialize the card generator.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
                     Only required for PDF processing.
            model: Gemini model name. Defaults to gemini-2.0-flash.
            output_file: Path to the output .apkg file.
            registry_path: Path to the deck registry JSON file.
        """
        self.output_file = output_file
        self.model = model
        self.api_key = api_key
        self.registry = DeckRegistry(registry_path=registry_path)
        self.anki = AnkiGenerator(GERMAN)
        self._gemini: Optional[GeminiClient] = None
    
    @property
    def gemini(self) -> GeminiClient:
        """Lazy initialization of Gemini client (only when needed for PDF)."""
        if self._gemini is None:
            self._gemini = GeminiClient(api_key=self.api_key, model=self.model)
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
        
        vocab_cards = 0
        grammar_cards = 0
        categories_processed = set()
        
        # Process vocabulary cards
        if "vocabulary" in data:
            vocab_cards, categories_processed = self._process_vocabulary_from_json(
                data["vocabulary"], verbose
            )
        
        # Process grammar cards
        if "grammar" in data:
            grammar_cards = self._process_grammar_from_json(data["grammar"], verbose)
        
        # Export
        if verbose:
            print(f"💾 Exporting to {self.output_file}...")
        
        self.anki.export(self.output_file)
        
        total_cards = vocab_cards + grammar_cards
        if verbose:
            print(f"✅ Done! Generated {total_cards} cards")
        
        return {
            "vocabulary_cards": vocab_cards,
            "grammar_cards": grammar_cards,
            "categories": list(categories_processed),
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
        
        if "vocabulary" not in data and "grammar" not in data:
            raise ValueError("JSON must contain 'vocabulary' and/or 'grammar' arrays")
        
        # Validate vocabulary cards
        if "vocabulary" in data:
            if not isinstance(data["vocabulary"], list):
                raise ValueError("'vocabulary' must be an array")
            
            required_vocab_fields = ["chapter", "word", "word_translation", "sentence", "sentence_translation"]
            for i, card in enumerate(data["vocabulary"]):
                for field in required_vocab_fields:
                    if field not in card:
                        errors.append(f"Vocabulary card {i+1}: missing required field '{field}'")
                    elif not card[field] or not card[field].strip():
                        errors.append(f"Vocabulary card {i+1}: field '{field}' is empty")
        
        # Validate grammar cards
        if "grammar" in data:
            if not isinstance(data["grammar"], list):
                raise ValueError("'grammar' must be an array")
            
            required_grammar_fields = ["question", "answer"]
            for i, card in enumerate(data["grammar"]):
                for field in required_grammar_fields:
                    if field not in card:
                        errors.append(f"Grammar card {i+1}: missing required field '{field}'")
                    elif not card[field] or not card[field].strip():
                        errors.append(f"Grammar card {i+1}: field '{field}' is empty")
        
        return data, errors
    
    def _process_vocabulary_from_json(
        self,
        vocab_cards: List[Dict[str, str]],
        verbose: bool
    ) -> tuple[int, set]:
        """Process vocabulary cards from JSON data.
        
        Args:
            vocab_cards: List of vocabulary card dicts.
            verbose: Whether to print progress.
            
        Returns:
            Tuple of (number of cards added, set of categories processed).
        """
        if verbose:
            print(f"📚 Processing {len(vocab_cards)} vocabulary cards...")
        
        cards_added = 0
        categories = set()
        
        for card in vocab_cards:
            # Skip invalid cards
            if not all(card.get(f) for f in ["chapter", "word", "word_translation", "sentence", "sentence_translation"]):
                continue
            
            category = card["chapter"]
            
            # Check if category exists in registry
            existing_category = self.registry.find_matching_category(category)
            if existing_category:
                chapter_name = existing_category
            else:
                chapter_name = category
            
            # Ensure chapter exists
            if chapter_name not in categories:
                self.anki.create_vocabulary_chapter(chapter_name)
                if verbose and existing_category:
                    print(f"   → Extending existing deck: {chapter_name}")
                elif verbose:
                    print(f"   → Creating new deck: {chapter_name}")
            
            # Add the card
            self.anki.add_vocabulary_card(
                chapter=chapter_name,
                word=card["word"],
                word_translation=card["word_translation"],
                sentence=card["sentence"],
                sentence_translation=card["sentence_translation"]
            )
            
            # Register category
            self.registry.register_vocabulary_category(chapter_name)
            categories.add(chapter_name)
            cards_added += 1
        
        if verbose:
            print(f"   → Added {cards_added} vocabulary cards")
        
        return cards_added, categories
    
    def _process_grammar_from_json(
        self,
        grammar_cards: List[Dict[str, str]],
        verbose: bool
    ) -> int:
        """Process grammar cards from JSON data.
        
        Args:
            grammar_cards: List of grammar card dicts.
            verbose: Whether to print progress.
            
        Returns:
            Number of cards added.
        """
        if verbose:
            print(f"📖 Processing {len(grammar_cards)} grammar cards...")
        
        # Ensure grammar deck exists
        self.anki.create_grammar_deck()
        
        cards_added = 0
        for card in grammar_cards:
            # Skip invalid cards
            if not card.get("question") or not card.get("answer"):
                continue
            
            self.anki.add_grammar_card(
                question=card["question"],
                answer=card["answer"]
            )
            cards_added += 1
        
        if verbose:
            print(f"   → Added {cards_added} grammar cards")
        
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
            self._display_card(card, card_type, i, total)
            
            while True:
                response = input("➕ Add this card to the deck? ([yes]/no): ").strip().lower()
                if response in ("yes", "y", ""):
                    approved_cards.append(card)
                    print("   ✓ Card will be added.")
                    break
                elif response in ("no", "n"):
                    print("   ✗ Card skipped.")
                    break
                else:
                    print("   Please enter 'yes' or 'no'.")
        
        print(f"\n📊 Summary: {len(approved_cards)}/{total} cards approved for addition.")
        return approved_cards
    
    # ==================== PDF Processing ====================
    
    def generate_from_pdf(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int,
        content_type: Optional[str] = None,
        verbose: bool = True
    ) -> dict:
        """Generate Anki cards from PDF pages.
        
        Main method that orchestrates the full pipeline:
        1. Extract specified pages as PDF bytes
        2. Pass PDF to Gemini for classification (if not provided)
        3. Generate appropriate cards
        4. Extend existing deck or create new one
        5. Export updated deck
        
        Args:
            pdf_path: Path to the PDF file.
            start_page: Starting page number (1-indexed, inclusive).
            end_page: Ending page number (1-indexed, inclusive).
            content_type: Optional. "grammar" or "vocabulary". If provided,
                skips the classification API call.
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
        
        # Step 2: Classify content (skip if provided)
        if content_type:
            content_type = content_type.lower()
            if verbose:
                print(f"🔍 Using provided content type: {content_type.upper()}")
        else:
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
        
        # Ask if user wants to inspect cards before adding
        if cards and self._ask_inspect_cards():
            cards = self._inspect_cards_interactively(cards, "grammar")
        
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
        """Handle vocabulary content: detect categories and generate cards in one call.
        
        Supports PDFs with multiple vocabulary categories.
        
        Args:
            pdf_bytes: The PDF pages as bytes.
            verbose: Whether to print progress messages.
            
        Returns:
            Summary dict with content_type, categories, cards_generated, deck_actions.
        """
        if verbose:
            print("📚 Generating vocabulary cards...")
        
        # Get existing categories so Gemini can match them
        existing_categories = self.registry.get_vocabulary_categories()
        
        # Single API call to get categories and cards together
        category_data = self.gemini.generate_vocabulary_cards(pdf_bytes, existing_categories)
        
        total_cards = sum(len(cards) for _, cards in category_data)
        if verbose:
            print(f"   → Found {len(category_data)} category(ies)")
            for category, cards in category_data:
                print(f"     • {category}: {len(cards)} cards")
        
        categories_processed = []
        deck_actions = {}
        total_cards_added = 0
        
        for category, cards in category_data:
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
            
            # Ensure chapter deck exists
            self.anki.create_vocabulary_chapter(chapter_name)
            
            # Ask if user wants to inspect cards before adding (once per category)
            if cards and self._ask_inspect_cards():
                cards = self._inspect_cards_interactively(cards, "vocabulary")
            
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
            categories_processed.append(chapter_name)
            deck_actions[chapter_name] = deck_action
            total_cards_added += len(cards)
        
        return {
            "content_type": "vocabulary",
            "categories": categories_processed,
            "cards_generated": total_cards_added,
            "deck_actions": deck_actions
        }


def main():
    """CLI entry point for the card generator."""
    import argparse
    
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
        choices=["grammar", "vocabulary"],
        help="Content type for PDF (grammar or vocabulary). If provided, skips classification."
    )
    parser.add_argument(
        "-m", "--model",
        default="gemini-2.0-flash",
        help="Gemini model name (default: gemini-2.0-flash)"
    )
    
    # Common arguments
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
    
    # Validate PDF arguments
    if args.pdf:
        if args.start_page is None or args.end_page is None:
            parser.error("--start-page and --end-page are required when using --pdf")
    
    generator = CardGenerator(
        model=args.model,
        output_file=args.output,
        registry_path=args.registry
    )
    
    if args.json:
        # JSON mode
        result = generator.generate_from_json(
            json_path=args.json,
            verbose=not args.quiet
        )
        
        print(f"\nSummary:")
        print(f"  Vocabulary cards: {result['vocabulary_cards']}")
        print(f"  Grammar cards: {result['grammar_cards']}")
        if result['categories']:
            print(f"  Categories: {', '.join(result['categories'])}")
        if result['errors']:
            print(f"  Validation warnings: {len(result['errors'])}")
    else:
        # PDF mode
        result = generator.generate_from_pdf(
            pdf_path=args.pdf,
            start_page=args.start_page,
            end_page=args.end_page,
            content_type=args.type,
            verbose=not args.quiet
        )
        
        print(f"\nSummary:")
        print(f"  Content type: {result['content_type']}")
        if result.get('categories'):
            print(f"  Categories: {', '.join(result['categories'])}")
        elif result.get('category'):
            # Legacy single category support
            print(f"  Category: {result['category']}")
        print(f"  Cards generated: {result['cards_generated']}")
        if 'deck_actions' in result:
            for cat, action in result['deck_actions'].items():
                print(f"  Deck '{cat}': {action}")
        elif 'deck_action' in result:
            print(f"  Deck action: {result['deck_action']}")


if __name__ == "__main__":
    main()
