# Anki Deck Generator

A Python tool to create Anki flashcard decks for German language learning. Supports both manual card creation and **AI-powered generation from PDF textbooks** using Google's Gemini API.

## Features

- 📚 **Vocabulary Cards**: German→English and English→German with TTS support
- 📖 **Grammar Cards**: Question/answer format for grammar rules
- 🤖 **AI-Powered PDF Processing**: Automatically extract cards from textbook PDFs
- 🗂️ **Smart Deck Management**: Extends existing decks instead of creating duplicates
- 🏷️ **Category Detection**: AI detects vocabulary topics (Body Parts, Food, etc.)

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

### Option 1: AI-Powered PDF Generation (Recommended)

Generate Anki cards automatically from your German textbook PDF.

**Setup:**

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"
```

**Command Line:**

```bash
# Generate cards from pages 10-15 of your textbook
python -m gemini.generator german_textbook.pdf 10 15

# Skip classification if you know the content type (saves 1 API call)
python -m gemini.generator german_textbook.pdf 10 15 -t vocabulary
python -m gemini.generator german_textbook.pdf 10 15 -t grammar

# Specify a different Gemini model
python -m gemini.generator german_textbook.pdf 10 15 -m gemini-1.5-pro

# Specify custom output file
python -m gemini.generator german_textbook.pdf 10 15 -o my_deck.apkg
```

**Python API:**

```python
from gemini import PDFCardGenerator

generator = PDFCardGenerator()
result = generator.generate_from_pdf(
    pdf_path="german_textbook.pdf",
    start_page=10,
    end_page=15
)

print(f"Generated {result['cards_generated']} cards")
print(f"Content type: {result['content_type']}")  # "grammar" or "vocabulary"
```

### Option 2: Manual Card Creation

Create cards programmatically with full control.

```python
from anki_generator import AnkiGenerator, GERMAN

gen = AnkiGenerator(GERMAN)

# Create vocabulary chapter
gen.create_vocabulary_chapter("Body Parts")

# Add vocabulary cards (creates German→English and English→German pairs)
gen.add_vocabulary_card(
    chapter="Body Parts",
    word="der Kopf",
    word_translation="head",
    sentence="Mein Kopf tut weh.",
    sentence_translation="My head hurts."
)

# Create grammar cards
gen.create_grammar_deck()
gen.add_grammar_card(
    question="What is the accusative form of 'der'?",
    answer="den"
)

# Export to Anki package
gen.export("german_learning_deck.apkg")
```

## Deck Structure

```
German
├── Vocabulary
│   ├── Body Parts
│   ├── Food and Drinks
│   └── [other categories...]
└── Grammar
```

## How the AI Works

1. **PDF Processing**: Extracts specified pages from your PDF
2. **Content Classification**: Gemini determines if it's grammar or vocabulary content
3. **Category Detection**: For vocabulary, detects the topic (e.g., "Body Parts")
4. **Card Generation**: Creates appropriate flashcards with translations and example sentences
5. **Deck Management**:
   - Grammar → Extends the single Grammar deck
   - Vocabulary → Extends existing category or creates new one

## Files

```
GenerateAnki/
├── anki_generator/          # Core Anki deck creation
│   ├── api.py              # Main AnkiGenerator class
│   ├── config.py           # Language configurations
│   ├── deck_manager.py     # Deck creation and management
│   └── models.py           # Card templates and styling
│
├── gemini/                  # AI-powered PDF processing
│   ├── generator.py        # Main PDFCardGenerator class
│   ├── gemini_client.py    # Gemini API wrapper
│   ├── pdf_processor.py    # PDF page extraction
│   ├── prompts.py          # AI prompts
│   └── deck_registry.py    # Tracks existing categories
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

### Deck Registry

The file `deck_registry.json` tracks created vocabulary categories. This ensures:

- New cards for "Body Parts" extend the existing deck
- Case-insensitive matching ("body parts" → "Body Parts")

## Adding New Languages

```python
from anki_generator import AnkiGenerator
from anki_generator.config import LanguageConfig

SPANISH = LanguageConfig(
    name="Spanish",
    native_code="es_ES",
    translation_language="English",
    translation_code="en_US"
)

gen = AnkiGenerator(SPANISH)
```

## Importing to Anki

1. Open Anki
2. Go to **File → Import**
3. Select the generated `.apkg` file
4. Cards will appear under `German::Vocabulary::` or `German::Grammar`

## Code

Claude was used to generate most of this code.

## License

MIT
