"""
Deck registry for tracking existing vocabulary categories.

Maintains a JSON file to track which vocabulary categories have been created,
enabling the system to extend existing decks rather than creating duplicates.
"""

import json
from pathlib import Path
from typing import Optional, List


class DeckRegistry:
    """Tracks vocabulary categories to determine extend vs create behavior.
    
    Maintains a JSON registry file that stores vocabulary categories
    that have been created.
    """
    
    def __init__(self, registry_path: str = "deck_registry.json"):
        """Initialize the deck registry.
        
        Args:
            registry_path: Path to the registry JSON file.
        """
        self.registry_path = Path(registry_path)
        self._data = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Load the registry from disk, or create a new one."""
        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                return json.load(f)
        return {"vocabulary_categories": []}
    
    def _save_registry(self) -> None:
        """Save the registry to disk."""
        with open(self.registry_path, "w") as f:
            json.dump(self._data, f, indent=2)
    
    def vocabulary_category_exists(self, category: str) -> bool:
        """Check if a vocabulary category deck exists.
        
        Args:
            category: The category name to check (case-insensitive).
            
        Returns:
            True if the category exists, False otherwise.
        """
        normalized = category.lower().strip()
        existing = [c.lower() for c in self._data["vocabulary_categories"]]
        return normalized in existing
    
    def register_vocabulary_category(self, category: str) -> None:
        """Register a new vocabulary category.
        
        Args:
            category: The category name to register.
        """
        if not self.vocabulary_category_exists(category):
            self._data["vocabulary_categories"].append(category)
            self._save_registry()
    
    def get_vocabulary_categories(self) -> List[str]:
        """Get all registered vocabulary categories.
        
        Returns:
            List of all vocabulary category names.
        """
        return self._data["vocabulary_categories"].copy()
    
    def find_matching_category(self, category: str) -> Optional[str]:
        """Find an existing category that matches the given one.
        
        Args:
            category: The category name to match (case-insensitive).
            
        Returns:
            The matching category name with original casing, or None if not found.
        """
        normalized = category.lower().strip()
        for existing in self._data["vocabulary_categories"]:
            if existing.lower() == normalized:
                return existing
        return None
