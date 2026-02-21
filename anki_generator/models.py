"""
Card model definitions for Anki.

This module defines the card templates for vocabulary and grammar cards,
including TTS support for the native language.
"""

import genanki
from .config import LanguageConfig


# CSS styling for cards
CARD_CSS = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: #1a1a1a;
    background-color: #ffffff;
    padding: 20px;
}

.word {
    font-size: 32px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 20px;
}

.sentence {
    font-size: 22px;
    color: #e0e0e0;
    font-style: italic;
    margin: 15px 0;
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.translation {
    font-size: 28px;
    font-weight: bold;
    color: #66bb6a;
    margin-top: 15px;
}

.sentence-translation {
    font-size: 20px;
    color: #81c784;
    margin-top: 10px;
}

hr#answer {
    border: none;
    border-top: 2px solid rgba(255, 255, 255, 0.3);
    margin: 20px 0;
}
"""


def create_qa_model(config: LanguageConfig, deck_type_name: str) -> genanki.Model:
    """Create a model for Q&A cards (Grammar, Radicals, etc.).
    
    - Front: Question
    - Back: Answer
    
    Args:
        config: The language configuration to use.
        deck_type_name: The deck type name (e.g., "Grammar", "Radicals").
        
    Returns:
        A genanki Model configured for Q&A cards.
    """
    model_id = abs(hash(f"{config.name}_{deck_type_name.lower()}_v3")) % (1 << 30) + (1 << 30)
    
    return genanki.Model(
        model_id,
        f'{config.name} {deck_type_name}',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': f'{deck_type_name} Card',
                'qfmt': '''
                    <div class="word">{{Question}}</div>
                ''',
                'afmt': '''
                    {{FrontSide}}
                    <hr id="answer">
                    <div class="translation">{{Answer}}</div>
                ''',
            },
        ],
        css=CARD_CSS
    )
