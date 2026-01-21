"""
Deck management module.

This module handles the creation and management of Anki decks,
including the hierarchical deck structure for vocabulary chapters and grammar.
"""

import genanki
from typing import Dict, List
from .config import LanguageConfig
from .models import (
    create_native_to_translation_model,
    create_translation_to_native_model,
    create_grammar_model
)


class DeckManager:
    """Manages Anki decks for a specific language configuration.
    
    This class handles:
    - Creating vocabulary chapter decks (e.g., German::Vocabulary::ChapterA)
    - Creating grammar decks (e.g., German::Grammar)
    - Adding notes to decks
    - Exporting all decks to an .apkg file
    """
    
    def __init__(self, config: LanguageConfig):
        """Initialize the deck manager.
        
        Args:
            config: The language configuration to use.
        """
        self.config = config
        self._vocabulary_decks: Dict[str, genanki.Deck] = {}
        self._grammar_deck: genanki.Deck | None = None
        
        # Create models
        self._native_to_translation_model = create_native_to_translation_model(config)
        self._translation_to_native_model = create_translation_to_native_model(config)
        self._grammar_model = create_grammar_model(config)
    
    def _generate_deck_id(self, deck_name: str) -> int:
        """Generate a consistent deck ID from the deck name.
        
        Args:
            deck_name: The full deck name.
            
        Returns:
            A unique deck ID.
        """
        return abs(hash(deck_name)) % (1 << 30) + (1 << 30)
    
    def create_vocabulary_chapter(self, chapter_name: str) -> genanki.Deck:
        """Create a vocabulary chapter deck.
        
        Args:
            chapter_name: The name of the chapter (e.g., "ChapterA").
            
        Returns:
            The created or existing deck for this chapter.
        """
        if chapter_name in self._vocabulary_decks:
            return self._vocabulary_decks[chapter_name]
        
        deck_name = f"{self.config.vocabulary_deck_name}::{chapter_name}"
        deck_id = self._generate_deck_id(deck_name)
        
        deck = genanki.Deck(deck_id, deck_name)
        self._vocabulary_decks[chapter_name] = deck
        
        return deck
    
    def create_grammar_deck(self) -> genanki.Deck:
        """Create the grammar deck.
        
        Returns:
            The created or existing grammar deck.
        """
        if self._grammar_deck is not None:
            return self._grammar_deck
        
        deck_name = self.config.grammar_deck_name
        deck_id = self._generate_deck_id(deck_name)
        
        self._grammar_deck = genanki.Deck(deck_id, deck_name)
        
        return self._grammar_deck
    
    def add_vocabulary_card(
        self,
        chapter_name: str,
        native_word: str,
        translated_word: str,
        native_sentence: str,
        translated_sentence: str
    ) -> None:
        """Add vocabulary cards to a chapter deck.
        
        This creates two cards:
        1. Native → Translation (e.g., German → English)
        2. Translation → Native (e.g., English → German)
        
        Args:
            chapter_name: The chapter to add the card to.
            native_word: The word in the native language (e.g., German).
            translated_word: The translation of the word (e.g., English).
            native_sentence: A sentence using the word in the native language.
            translated_sentence: The translation of the sentence.
        """
        # Ensure the chapter deck exists
        if chapter_name not in self._vocabulary_decks:
            self.create_vocabulary_chapter(chapter_name)
        
        deck = self._vocabulary_decks[chapter_name]
        
        # Create Native → Translation note
        native_to_translation_note = genanki.Note(
            model=self._native_to_translation_model,
            fields=[native_word, native_sentence, translated_word, translated_sentence]
        )
        deck.add_note(native_to_translation_note)
        
        # Create Translation → Native note
        translation_to_native_note = genanki.Note(
            model=self._translation_to_native_model,
            fields=[translated_word, native_word]
        )
        deck.add_note(translation_to_native_note)
    
    def add_grammar_card(self, question: str, answer: str) -> None:
        """Add a grammar card to the grammar deck.
        
        Args:
            question: The grammar question.
            answer: The answer to the question.
        """
        # Ensure the grammar deck exists
        if self._grammar_deck is None:
            self.create_grammar_deck()
        
        note = genanki.Note(
            model=self._grammar_model,
            fields=[question, answer]
        )
        self._grammar_deck.add_note(note)
    
    def get_all_decks(self) -> List[genanki.Deck]:
        """Get all decks managed by this manager.
        
        Returns:
            A list of all decks.
        """
        decks = list(self._vocabulary_decks.values())
        if self._grammar_deck is not None:
            decks.append(self._grammar_deck)
        return decks
    
    def export(self, filename: str) -> None:
        """Export all decks to an .apkg file.
        
        Args:
            filename: The output filename (should end with .apkg).
        """
        decks = self.get_all_decks()
        if not decks:
            raise ValueError("No decks to export. Create at least one deck first.")
        
        package = genanki.Package(decks)
        package.write_to_file(filename)
