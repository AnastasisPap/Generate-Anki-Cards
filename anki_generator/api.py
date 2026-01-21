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
    
    def create_vocabulary_chapter(self, chapter_name: str) -> None:
        """Create a vocabulary chapter deck.
        
        Creates a deck with the structure: {Language}::Vocabulary::{chapter_name}
        For example: German::Vocabulary::ChapterA
        
        Args:
            chapter_name: The name of the chapter (e.g., "ChapterA", "ChapterB").
        """
        self._deck_manager.create_vocabulary_chapter(chapter_name)
    
    def create_grammar_deck(self) -> None:
        """Create the grammar deck.
        
        Creates a deck with the structure: {Language}::Grammar
        For example: German::Grammar
        """
        self._deck_manager.create_grammar_deck()
    
    def add_vocabulary_card(
        self,
        chapter: str,
        word: str,
        word_translation: str,
        sentence: str,
        sentence_translation: str
    ) -> None:
        """Add a vocabulary card to a chapter.
        
        This creates two cards automatically:
        1. Native → Translation: Shows the native word and sentence on front,
           translations on back. TTS is enabled for the native sentence.
        2. Translation → Native: Shows the translated word on front,
           native word on back.
        
        Args:
            chapter: The chapter name to add the card to.
            word: The word in the native language (e.g., German word).
            word_translation: The translation of the word (e.g., English translation).
            sentence: A sentence using the word in the native language.
            sentence_translation: The translation of the sentence.
        """
        self._deck_manager.add_vocabulary_card(
            chapter_name=chapter,
            native_word=word,
            translated_word=word_translation,
            native_sentence=sentence,
            translated_sentence=sentence_translation
        )
    
    def add_grammar_card(self, question: str, answer: str) -> None:
        """Add a grammar card to the grammar deck.
        
        Args:
            question: The grammar question or prompt.
            answer: The answer to the question.
        """
        self._deck_manager.add_grammar_card(question, answer)
    
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
