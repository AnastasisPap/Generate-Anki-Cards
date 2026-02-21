"""
Deck management module.

This module handles the creation and management of Anki decks,
including the hierarchical deck structure for vocabulary chapters and Q&A decks.
"""

import genanki
from typing import Dict, List
from .config import LanguageConfig
from .models import create_qa_model


class DeckManager:
    """Manages Anki decks for a specific language configuration.
    
    This class handles:
    - Creating Q&A decks (e.g., German::Vocabulary, Chinese::Radicals)
    - Adding notes to decks
    - Exporting all decks to an .apkg file
    """
    
    def __init__(self, config: LanguageConfig):
        """Initialize the deck manager.
        
        Args:
            config: The language configuration to use.
        """
        self.config = config
        self._qa_decks: Dict[str, genanki.Deck] = {}
        
        # Create Q&A models for each deck type
        self._qa_models: Dict[str, genanki.Model] = {}
        for dt in config.deck_types:
            self._qa_models[dt] = create_qa_model(config, dt)
    
    def _generate_deck_id(self, deck_name: str) -> int:
        """Generate a consistent deck ID from the deck name.
        
        Args:
            deck_name: The full deck name.
            
        Returns:
            A unique deck ID.
        """
        return abs(hash(deck_name)) % (1 << 30) + (1 << 30)
    
    
    def create_qa_deck(self, deck_type: str) -> genanki.Deck:
        """Create a Q&A deck for the given type (e.g., Grammar, Radicals).
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
        
        Returns:
            The created or existing deck for this type.
        """
        if deck_type in self._qa_decks:
            return self._qa_decks[deck_type]
        
        deck_name = self.config.qa_deck_name(deck_type)
        deck_id = self._generate_deck_id(deck_name)
        
        self._qa_decks[deck_type] = genanki.Deck(deck_id, deck_name)
        
        return self._qa_decks[deck_type]
    
    
    def add_qa_card(self, deck_type: str, question: str, answer: str) -> None:
        """Add a Q&A card to a specific deck type.
        
        Args:
            deck_type: The deck type name (e.g., "Grammar", "Radicals").
            question: The question or prompt.
            answer: The answer.
        """
        # Ensure the deck exists
        if deck_type not in self._qa_decks:
            self.create_qa_deck(deck_type)
        
        model = self._qa_models.get(deck_type)
        if model is None:
            # Create model on the fly for dynamically added types
            model = create_qa_model(self.config, deck_type)
            self._qa_models[deck_type] = model
        
        note = genanki.Note(
            model=model,
            fields=[question, answer]
        )
        self._qa_decks[deck_type].add_note(note)
    
    def get_all_decks(self) -> List[genanki.Deck]:
        """Get all decks managed by this manager.
        
        Returns:
            A list of all decks.
        """
        return list(self._qa_decks.values())
    
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
