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


def create_native_to_translation_model(config: LanguageConfig) -> genanki.Model:
    """Create a model for native language → translation language cards.
    
    For German→English:
    - Front: German word + German sentence (with TTS for sentence)
    - Back: English word + English sentence translation
    
    Args:
        config: The language configuration to use.
        
    Returns:
        A genanki Model configured for native→translation cards.
    """
    # Generate a unique model ID based on language name
    # Using a hash to ensure consistency across runs
    # Added _v3 suffix to force Anki to update the styling
    model_id = abs(hash(f"{config.name}_to_{config.translation_language}_vocab_v3")) % (1 << 30) + (1 << 30)
    
    return genanki.Model(
        model_id,
        f'{config.name} → {config.translation_language} Vocabulary',
        fields=[
            {'name': 'NativeWord'},      # e.g., German word
            {'name': 'NativeSentence'},  # e.g., German sentence
            {'name': 'TranslatedWord'},  # e.g., English word
            {'name': 'TranslatedSentence'},  # e.g., English sentence
        ],
        templates=[
            {
                'name': f'{config.name} → {config.translation_language}',
                'qfmt': f'''
                    <div class="word">{{{{NativeWord}}}}</div>
                    <div class="sentence">{{{{tts {config.native_code}:NativeSentence}}}}</div>
                    <div class="sentence">{{{{NativeSentence}}}}</div>
                ''',
                'afmt': '''
                    {{FrontSide}}
                    <hr id="answer">
                    <div class="translation">{{TranslatedWord}}</div>
                    <div class="sentence-translation">{{TranslatedSentence}}</div>
                ''',
            },
        ],
        css=CARD_CSS
    )


def create_translation_to_native_model(config: LanguageConfig) -> genanki.Model:
    """Create a model for translation language → native language cards.
    
    For English→German:
    - Front: English word
    - Back: German word
    
    Args:
        config: The language configuration to use.
        
    Returns:
        A genanki Model configured for translation→native cards.
    """
    # Generate a unique model ID based on language name
    # Added _v3 suffix to force Anki to update the styling
    model_id = abs(hash(f"{config.translation_language}_to_{config.name}_vocab_v3")) % (1 << 30) + (1 << 30)
    
    return genanki.Model(
        model_id,
        f'{config.translation_language} → {config.name} Vocabulary',
        fields=[
            {'name': 'TranslatedWord'},  # e.g., English word
            {'name': 'NativeWord'},      # e.g., German word
        ],
        templates=[
            {
                'name': f'{config.translation_language} → {config.name}',
                'qfmt': '''
                    <div class="word">{{TranslatedWord}}</div>
                ''',
                'afmt': '''
                    {{FrontSide}}
                    <hr id="answer">
                    <div class="translation">{{NativeWord}}</div>
                ''',
            },
        ],
        css=CARD_CSS
    )


def create_grammar_model(config: LanguageConfig) -> genanki.Model:
    """Create a model for grammar cards.
    
    - Front: Question
    - Back: Answer
    
    Args:
        config: The language configuration to use.
        
    Returns:
        A genanki Model configured for grammar cards.
    """
    # Generate a unique model ID based on language name
    # Added _v3 suffix to force Anki to update the styling
    model_id = abs(hash(f"{config.name}_grammar_v3")) % (1 << 30) + (1 << 30)
    
    return genanki.Model(
        model_id,
        f'{config.name} Grammar',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Grammar Card',
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
