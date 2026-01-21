"""
Prompt templates for Gemini API interactions.

Contains all prompts used to classify content and generate cards.
These prompts are used alongside PDF content passed via Part.from_bytes().
"""

CLASSIFICATION_PROMPT = """You are analyzing a page from a German language learning textbook.

Analyze the PDF content and determine if it is primarily:
1. "grammar" - If it focuses on grammatical rules, verb conjugations, case endings, sentence structure, etc.
2. "vocabulary" - If it focuses on teaching new words, usually organized by topic/theme (e.g., body parts, food, clothing)

Respond with ONLY one word: either "grammar" or "vocabulary"."""


GRAMMAR_CARD_PROMPT = """You are creating Anki flashcards from German grammar content.

Analyze the PDF content and create question-answer flashcard pairs.
Focus on:
- Key grammatical rules
- Verb conjugations
- Case usage (nominative, accusative, dative, genitive)
- Word order rules
- Common exceptions or patterns

Generate flashcards in the following JSON format:
{
    "cards": [
        {
            "question": "Clear question about the grammar point",
            "answer": "Concise but complete answer"
        }
    ]
}

Create between 5-15 cards depending on the content density. Make questions specific and testable.
Respond with ONLY the JSON object, no additional text."""


VOCABULARY_CARDS_PROMPT_TEMPLATE = """You are creating Anki flashcards from German vocabulary content.

Analyze the PDF and identify all vocabulary categories/topics being taught.
Some PDFs may contain vocabulary from multiple different categories (e.g., both "Body Parts" and "Clothing" on the same pages).
{existing_categories_section}

For each category found, extract all vocabulary words with example sentences.
For each word, provide:
- The German word
- The English translation
- A German example sentence using the word
- The English translation of the sentence

Generate your response in the following JSON format:
{{
    "categories": [
        {{
            "category": "The vocabulary category (2-4 words, Title Case)",
            "cards": [
                {{
                    "word": "German word",
                    "word_translation": "English translation",
                    "sentence": "German sentence using the word",
                    "sentence_translation": "English translation of the sentence"
                }}
            ]
        }}
    ]
}}

Group words by their appropriate category. If all words belong to one category, return a single category object.
Extract all vocabulary words from the PDF. Create natural, useful example sentences.
Respond with ONLY the JSON object, no additional text."""


def get_vocabulary_cards_prompt(existing_categories: list) -> str:
    """Generate the vocabulary cards prompt with existing categories.
    
    Args:
        existing_categories: List of existing category names.
        
    Returns:
        The formatted prompt string.
    """
    if existing_categories:
        categories_list = ", ".join(f'"{cat}"' for cat in existing_categories)
        section = f"""Existing categories: {categories_list}

If the content matches one of these existing categories, use that exact category name.
Otherwise, create a new appropriate category name."""
    else:
        section = """Examples of categories: "Body Parts", "Food and Drinks", "Clothing", "Family Members", "Colors", "Animals", "Transportation", "Weather", "Professions", etc."""
    
    return VOCABULARY_CARDS_PROMPT_TEMPLATE.format(existing_categories_section=section)
