"""
Main API module for the Anki Deck Generator.

This module provides the primary interface for creating and managing Anki decks.
"""

from .config import LanguageConfig, GERMAN
from .deck_manager import DeckManager


class AnkiGenerator:
    """Main API class for generating Anki decks.
    
    This class provides a simple interface for creating vocabulary and grammar
    decks for language learning.
    
    Example usage:
        >>> from anki_generator import AnkiGenerator, GERMAN
        >>> gen = AnkiGenerator(GERMAN)
        >>> gen.create_vocabulary_chapter("ChapterA")
        >>> gen.add_vocabulary_card(
        ...     chapter="ChapterA",
        ...     word="Haus",
        ...     word_translation="house",
        ...     sentence="Das Haus ist groß.",
        ...     sentence_translation="The house is big."
        ... )
        >>> gen.export("german_deck.apkg")
    """
    
    def __init__(self, config: LanguageConfig = GERMAN):
        """Initialize the Anki generator.
        
        Args:
            config: The language configuration to use. Defaults to GERMAN.
        """
        self.config = config
        self._deck_manager = DeckManager(config)
    
    def create_qa_deck(self, deck_type: str) -> None:
        """Create a Q&A deck.
        
        Creates a deck with the structure: {Language}::{DeckType}
        For example: German::Grammar or Chinese::Radicals
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
        """
        self._deck_manager.create_qa_deck(deck_type)

    def add_qa_card(self, deck_type: str, question: str, answer: str) -> None:
        """Add a Q&A card to a specific deck type.
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
            question: The question or prompt.
            answer: The answer.
        """
        self._deck_manager.add_qa_card(deck_type, question, answer)
    
    def export(self, filename: str = "output.apkg") -> str:
        """Export all decks to an Anki package file.
        
        Args:
            filename: The output filename. Should end with .apkg.
                     Defaults to "output.apkg".
        
        Returns:
            The filename that was written to.
        """
        if not filename.endswith(".apkg"):
            filename = f"{filename}.apkg"
        
        self._deck_manager.export(filename)
        return filename
    
    @property
    def language(self) -> str:
        """Get the name of the language being learned.
        
        Returns:
            The language name (e.g., "German").
        """
        return self.config.name
    
    @property
    def translation_language(self) -> str:
        """Get the name of the translation language.
        
        Returns:
            The translation language name (e.g., "English").
        """
        return self.config.translation_language
