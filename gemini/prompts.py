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
Rules to generate cards:
1. For each rule you come across, create a card for it. For example:
  - Q: How are verbs ending in -eln and -ern conjugated in the present tense?
  - A: Remove the -n from the infinitive form and add the appropriate ending.
  - Q: When does eins keep the -s and when it is removed?
  - A: It keeps the -s when it is used on its own or is in the end, and it's removed if it's followed by another number.
2. If you find anything that needs to be remembered by heart, create a card for it. For example:
  - Q: Which are the modalverben?
  - A: können, dürfen, müssen, sollen, wollen, mögen, möchten
  - Q: Which propositions go with Dativ?
  - A: aus, von, zu, nach, bei, mit, seit, gegenüber, ab
3. If there are words that are used in Grammar (e.g. propositions, adverbs, etc.) create a card with its translation. For example:
  - Q: What does "aus" mean?
  - A: out of, from
  - Q: What does "was" mean?
  - A: What
  - Q: What does "wo" mean?
  - A: Where
  - Don't create cards for words that are not used in the grammar. E.g. do not create a card for what "Ankommen" means.
4. Sometimes there are tables with information that needs to be remembered. Create cards for those too. For example:
  - Q: How is the bestimmter Artikel conjugated?
  - A: Maskulin: der, den, dem, des. Feminin: die, die, der, der. Neutral: das, das, dem, des. Plural: die, die, den, der.
  - Q: Which are the reflexivpronomen?
  - A: Akkusativ: mich, dich, sich, uns, euch, sich. Dativ: mir, dir, sich, uns, euch, sich.
  - Q: How are regular verbs conjugated in Simple past?
    - Find a usual verb or use the one in the book
  - A: Fragte, Fragtest, Fragte, Fragten, Fragten, Fragten
5. If you find any exceptions, make sure to include them in the cards. Some books specifically state them by including small images (e.g. magnifying glass), or words like "Achtung!", "Wichtig!", "Beachten Sie!", etc.
6. If you find any exercises, ignore them.
7. Don't create cards for grammatic rules that you don't see in the pdf. Only include the rules you see.
8. All translations from German should be in English.
9. For each rule/exception you find, add an example in the answer to understand it better.

Generate flashcards in the following JSON format:
{
    "cards": [
        {
            "question": "Clear question about the grammar point",
            "answer": "Concise but complete answer"
        }
    ]
}

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
