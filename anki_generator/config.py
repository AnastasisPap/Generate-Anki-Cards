"""
Language configuration module.

This module defines language configurations that can be used with the Anki Generator.
To add a new language, simply create a new LanguageConfig instance.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LanguageConfig:
    """Configuration for a language learning setup.
    
    Attributes:
        name: The name of the language being learned (e.g., "German")
        native_code: The TTS language code for the native language (e.g., "de_DE")
        translation_language: The name of the translation language (e.g., "English")
        translation_code: The TTS language code for the translation language (e.g., "en_US")
        deck_types: List of Q&A deck type names (e.g., ["Grammar"], ["Radicals"])
    """
    name: str
    native_code: str
    translation_language: str
    translation_code: str
    deck_types: List[str] = field(default_factory=lambda: ["Vocabulary", "Grammar"])
    
    @property
    def deck_prefix(self) -> str:
        """Returns the deck name prefix (e.g., 'German')."""
        return self.name
    
    def qa_deck_name(self, deck_type: str) -> str:
        """Returns the Q&A deck name for a given type (e.g., 'German::Grammar')."""
        return f"{self.name}::{deck_type}"
    
    @property
    def deck_type_names(self) -> List[str]:
        """Returns lowercase list of Q&A deck type names (e.g., ['grammar', 'vocabulary'])."""
        return [dt.lower() for dt in self.deck_types]
    
    def get_deck_type(self, name: str) -> Optional[str]:
        """Look up a deck type by lowercase name, returning the original-case name."""
        for dt in self.deck_types:
            if dt.lower() == name.lower():
                return dt
        return None


# Pre-defined language configurations
GERMAN = LanguageConfig(
    name="German",
    native_code="de_DE",
    translation_language="Greek",
    translation_code="el_GR",
    deck_types=["Vocabulary", "Grammar"]
)

CHINESE = LanguageConfig(
    name="Chinese",
    native_code="zh_CN",
    translation_language="English",
    translation_code="en_US",
    deck_types=["Vocabulary", "Radicals"]
)

SUPPORTED_LANGUAGES = {
    "german": GERMAN,
    "chinese": CHINESE,
}
