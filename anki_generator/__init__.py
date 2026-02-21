"""
Anki Deck Generator API

A Python API to programmatically create and update Anki decks for language learning.
"""

from .api import AnkiGenerator
from .config import LanguageConfig, GERMAN, CHINESE, SUPPORTED_LANGUAGES

__version__ = "1.0.0"
__all__ = ["AnkiGenerator", "LanguageConfig", "GERMAN", "CHINESE", "SUPPORTED_LANGUAGES"]
