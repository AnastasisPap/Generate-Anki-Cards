"""
Card formatting templates for Gemini generated flashcards.
Defines how the Q&A JSON is structured for different types of cards.
"""

CARD_TEMPLATES = {
    "basic": """Generate flashcards in the following JSON format:
{
    "cards": [
        {
            "question": "The main word, character or question",
            "answer": "The direct translation or concise answer"
        }
    ]
}

Respond with ONLY the JSON object, no additional text.""",

    "detailed": """Generate flashcards in the following JSON format:
{
    "cards": [
        {
            "question": "The main word, character or question",
            "answer": "The direct translation or concise answer\\n\\n Example sentence or usage notes\\n Translation of the example"
        }
    ]
}

Format the answer nicely, for example with the word translation first, followed by the example sentence on a new line.
Respond with ONLY the JSON object, no additional text.""",

    "chinese_characters": """Generate flashcards in the following JSON format:
{
    "cards": [
        {
            "question": "The main word, character or question",
            "answer": "The direct translation or concise answer\\n\\n Radicals \\n Translation of the radicals \\n Example sentence or usage notes\\n Translation of the example"
        }
    ]
}

Respond with ONLY the JSON object, no additional text.""",

    "radicals": """The response must follow this format exactly: Generate flashcards in the following JSON format:
{
    "cards": [
        {
            "question": "word or character",
            "answer": "Pinyin. direct translation<br> Variants/original <br> Example sentence (Pinyin). translation"
        }
    ]
}

Example:
{
    "cards": [
        {
            "question": "What does 人 mean?",
            "answer": "rén. Person. <br> Variants: 亻<br> 我是一个人。 (Wǒ shì yī gè rén.). I am a person."
        },
        {
            "question": "What does 亻mean?",
            "answer": "rén. Person. <br> Original: 人<br> 今仁休位他 (Jīn rén xiū wèi tā). Jin Renxiu took his place."
        }
    ]
}
Respond with ONLY the JSON object, no additional text.""",
}

DEFAULT_TEMPLATES = {
    "vocabulary": "detailed",
    "grammar": "detailed",
    "radicals": "radicals",
    "chinese_characters": "chinese_characters"
}
