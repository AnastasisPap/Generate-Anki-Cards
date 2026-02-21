# Anki Deck Generator

A Python tool to create Anki flashcard decks for German language learning. Supports both manual card creation and **AI-powered generation from PDF textbooks** using Google's Gemini API.

## Features

- 📚 **Dynamic Deck Types**: Define any number of custom deck types per language (e.g., Vocabulary, Grammar, Radicals).
- 🤖 **AI-Powered Flashcards**: Automatically extract Q&A pairs from textbook PDFs using Google's Gemini API.
- 🎯 **Smart Content Routing**: AI analyzes PDF pages and routes generated cards into the correct sub-deck.
- 💬 **Custom Instructions**: Pass additional prompts to guide AI card generation styling perfectly.

## Installation

```bash
# Clone the repository
cd /Users/anastasispap/Desktop/Programming/GenerateAnki

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.9+
- Dependencies: `genanki`, `google-genai`, `pymupdf`

## Usage

### Option 1: AI-Powered PDF Generation

Generate Anki cards automatically from your German textbook PDF using Gemini AI.

**Setup:**

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"
```

**Command Line:**

```bash
# Generate cards from pages 10-15 of your textbook
python generator.py --pdf german_textbook.pdf -s 10 -e 15

# Skip classification if you know the content type (saves 1 API call)
python generator.py --pdf german_textbook.pdf -s 10 -e 15 -t vocabulary
python generator.py --pdf chinese_textbook.pdf -s 10 -e 15 --language chinese -t radicals

# Specify a different Gemini model
python generator.py --pdf german_textbook.pdf -s 10 -e 15 -m gemini-1.5-pro

# Specify custom output file (by default saves to Language/deck_type/Language_DeckType.apkg)
python generator.py --pdf german_textbook.pdf -s 10 -e 15 -o my_deck.apkg

# Use a specific card formatting template (e.g. 'basic', 'detailed', 'radicals', 'chinese_characters')
python generator.py --pdf german_textbook.pdf -s 10 -e 15 -t vocabulary --template basic

# Add custom instructions to Gemini
python generator.py --pdf german_textbook.pdf -s 10 -e 15 --prompt "Make the example sentences shorter"
```

**Python API:**

```python
from generator import CardGenerator

# Will automatically use GERMAN config by default
generator = CardGenerator()
result = generator.generate_from_pdf(
    pdf_path="german_textbook.pdf",
    start_page=10,
    end_page=15
)

# With custom instructions and a specific formatting template
generator = CardGenerator(custom_prompt="Focus on verbs and include conjugations")
result = generator.generate_from_pdf(
    pdf_path="german_textbook.pdf",
    start_page=10,
    end_page=15,
    content_type="grammar",
    template="detailed"
)

print(f"Generated {result['cards_generated']} cards")
print(f"Deck route: {result['content_type']}")  # e.g. "grammar"
```

### Option 2: JSON File Import (Recommended for Manual Cards)

Add cards manually using a JSON file. This is ideal for adding custom cards or importing from other sources.

**Command Line:**

```bash
# Import cards from JSON file
python generator.py --json cards.json

# Specify custom output file (by default saves to Language/Language_learning_deck.apkg for multiple decks)
python generator.py --json cards.json -o my_deck.apkg
```

**JSON Format:**

```json
{
  "vocabulary": [
    {
      "question": "der Kopf",
      "answer": "head\n\nMein Kopf tut weh.\nMy head hurts."
    }
  ],
  "grammar": [
    {
      "question": "What is the accusative form of 'der'?",
      "answer": "den"
    }
  ],
  "radicals": [
    {
      "question": "What does the radical 氵 mean?",
      "answer": "Water (水 shuǐ). Common characters: 海, 洗."
    }
  ]
}
```

See `example_cards.json` for a complete example.

**Python API:**

```python
from generator import CardGenerator

generator = CardGenerator(language="german")
result = generator.generate_from_json("cards.json")

print(f"Total cards: {result['total_cards']}")
for deck, count in result['deck_counts'].items():
    print(f"{deck}: {count} cards")
```

### Option 3: Programmatic Card Creation

Create cards programmatically with full control.

```python
from anki_generator import AnkiGenerator, GERMAN

gen = AnkiGenerator(GERMAN)

# Standard generic Q&A card creation for any type
gen.create_qa_deck("Vocabulary")
gen.add_qa_card(
    deck_type="Vocabulary",
    question="der Kopf",
    answer="head\n\nMein Kopf tut weh.\nMy head hurts."
)

gen.create_qa_deck("Grammar")
gen.add_qa_card(
    deck_type="Grammar",
    question="What is the accusative form of 'der'?",
    answer="den"
)

# Export to Anki package
gen.export("german_learning_deck.apkg")
```

## Deck Structure (in Anki)

```text
German
├── Vocabulary
└── Grammar
```

## Default Output Directory Structure (on Disk)

If no `--output` path is specified, the pipeline will automatically organize generated `.apkg` files into an intuitive directory tree:

```text
Language/
└── deck_type/
    └── Language_DeckType.apkg
```

Example: `Chinese/radicals/Chinese_Radicals.apkg`

If importing a JSON file with multiple mapped deck types at once, it saves to the language root:

```text
German/
└── German_learning_deck.apkg
```

## How the AI Works

1. **PDF Processing**: Extracts specified pages from your PDF
2. **Content Classification**: Gemini dynamically determines the content type based on the active language's configured `deck_types` lists (e.g. is this "vocabulary" or "radicals"?).
3. **Card Generation**: Evaluates the PDF against a highly targeted formatting prompt to pull Q&A flashcards.
4. **Deck Routing**: Dynamically ensures the sub-deck for that type exists (`Language::Type`) and loads the cards into it.

## Files

```text
GenerateAnki/
├── generator.py             # Main CLI (PDF + JSON import)
├── example_cards.json       # Example JSON file for manual import
│
├── anki_generator/          # Core Anki deck creation
│   ├── api.py              # AnkiGenerator class
│   ├── config.py           # Language configurations
│   ├── deck_manager.py     # Deck creation and management
│   └── models.py           # Card templates and styling
│
├── gemini/                  # AI-powered PDF processing
│   ├── gemini_client.py    # Gemini API wrapper
│   ├── prompts.py          # AI prompts
│   ├── templates.py        # Card formatting JSON templates
│   └── pdf_processor.py    # PDF page extraction
│
├── requirements.txt
└── README.md
```

## Configuration

### Gemini API Key

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
# Set for current session
export GEMINI_API_KEY="your-api-key"

# Or add to ~/.zshrc for persistence
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.zshrc
source ~/.zshrc
```

## Adding New Languages & Deck Types

Adding a new language or type is driven completely by the `config.py` and `prompts.py` files.

```python
from anki_generator import AnkiGenerator
from anki_generator.config import LanguageConfig

SPANISH = LanguageConfig(
    name="Spanish",
    native_code="es_ES",
    translation_language="English",
    translation_code="en_US",
    deck_types=["Vocabulary", "Grammar", "Conjugations"] # Define any N types
)

gen = AnkiGenerator(SPANISH)
```

## Importing to Anki

1. Open Anki
2. Go to **File → Import**
3. Select the generated `.apkg` file
4. Cards will appear under `Language::Type` (e.g. `German::Vocabulary` or `Chinese::Radicals`)

## Code

Claude was used to generate most of this code.

## License

MIT
