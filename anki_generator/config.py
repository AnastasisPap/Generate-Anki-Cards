"""
Language configuration module.

This module defines language configurations that can be used with the Anki Generator.
To add a new language, simply create a new LanguageConfig instance.
"""

from dataclasses import dataclass


@dataclass
class LanguageConfig:
    """Configuration for a language learning setup.
    
    Attributes:
        name: The name of the language being learned (e.g., "German")
        native_code: The TTS language code for the native language (e.g., "de_DE")
        translation_language: The name of the translation language (e.g., "English")
        translation_code: The TTS language code for the translation language (e.g., "en_US")
    """
    name: str
    native_code: str
    translation_language: str
    translation_code: str
    
    @property
    def deck_prefix(self) -> str:
        """Returns the deck name prefix (e.g., 'German')."""
        return self.name
    
    @property
    def vocabulary_deck_name(self) -> str:
        """Returns the vocabulary parent deck name (e.g., 'German::Vocabulary')."""
        return f"{self.name}::Vocabulary"
    
    @property
    def grammar_deck_name(self) -> str:
        """Returns the grammar deck name (e.g., 'German::Grammar')."""
        return f"{self.name}::Grammar"


# Pre-defined language configurations
GERMAN = LanguageConfig(
    name="German",
    native_code="de_DE",
    translation_language="English",
    translation_code="en_US"
)

# Example: To add Spanish, you would create:
# SPANISH = LanguageConfig(
#     name="Spanish",
#     native_code="es_ES",
#     translation_language="English",
#     translation_code="en_US"
# )

# Example: To add French, you would create:
# FRENCH = LanguageConfig(
#     name="French",
#     native_code="fr_FR",
#     translation_language="English",
#     translation_code="en_US"
# )
