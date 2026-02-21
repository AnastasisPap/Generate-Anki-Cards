"""
Prompt templates for Gemini API interactions.

Contains language-specific prompts used to classify content and generate cards.
These prompts are used alongside PDF content passed via Part.from_bytes().
"""


# =============================================================================
# German Prompts
# =============================================================================

CLASSIFICATION_PROMPT_DE = """You are analyzing a page from a German language learning textbook.

Analyze the PDF content and determine if it is primarily:
1. "grammar" - If it focuses on grammatical rules, verb conjugations, case endings, sentence structure, etc.
2. "vocabulary" - If it focuses on teaching new words, usually organized by topic/theme (e.g., body parts, food, clothing)

Respond with ONLY one word: either "grammar" or "vocabulary"."""


GRAMMAR_CARD_PROMPT_DE = """You are creating Anki flashcards from German grammar content.

Analyze the PDF content and create question-answer flashcard pairs.
Rules to generate cards:
1. For each rule you come across, create a card for it. For example:
  - Q: How are verbs ending in -eln and -ern conjugated in the present tense?
  - A: Remove the -n from the infinitive form and add the appropriate ending.
  - Q: When does eins keep the -s and when it is removed?
  - A: It keeps the -s when it is used on its own or is in the end, and it's removed if it's followed by another number.
2. If you find anything that needs to be remembered by heart, create a card for it. For example:
  - Q: Which are the modalverben?
  - A: können, dürfen, müssen, sollen, wollen, mögen, möchten
  - Q: Which propositions go with Dativ?
  - A: aus, von, zu, nach, bei, mit, seit, gegenüber, ab
3. If there are words that are used in Grammar (e.g. propositions, adverbs, etc.) create a card with its translation. For example:
  - Q: What does "aus" mean?
  - A: out of, from
  - Q: What does "was" mean?
  - A: What
  - Q: What does "wo" mean?
  - A: Where
  - Don't create cards for words that are not used in the grammar. E.g. do not create a card for what "Ankommen" means.
  - Only add these translations if they are introduced in that chapter.
4. Sometimes there are tables with information that needs to be remembered. Create cards for those too. For example:
  - Q: How is the bestimmter Artikel conjugated?
  - A: Maskulin: der, den, dem, des. Feminin: die, die, der, der. Neutral: das, das, dem, des. Plural: die, die, den, der.
  - Q: Which are the reflexivpronomen?
  - A: Akkusativ: mich, dich, sich, uns, euch, sich. Dativ: mir, dir, sich, uns, euch, sich.
  - Q: How are regular verbs conjugated in Simple past?
    - Find a usual verb or use the one in the book
  - A: Fragte, Fragtest, Fragte, Fragten, Fragten, Fragten
5. If you find any exceptions, make sure to include them in the cards. Some books specifically state them by including small images (e.g. magnifying glass), or words like "Achtung!", "Wichtig!", "Beachten Sie!", etc.
6. If you find any exercises, ignore them.
7. Don't create cards for grammatic rules that you don't see in the pdf. Only include the rules you see.
8. All translations from German should be in Greek.
9. For each rule/exception you find, add an example in the answer to understand it better.
10. All explanations should be in Greek.
11. Really important: the cards must be as simple to understand as possible. Don't use complex sentences or long explanations.
12. When you think a translation is important then don't make a new card, just add a parenthesis next to the German word with the translation.

Good examples, they don't include examples but you must provide an example for each rule/exception:

1. Chapter of der Artikel

- Q: πως κλίνεται το άρθρο;
- A: Maskulin: der, den, dem, des. Feminin: die, die, der, der. Neutral: das, das, dem, des. Plural: die, die, den, der.

2. Chapter of das Verb

- Q: Τι γίνεται αν το τελευταίο γράμμα του θέματος είναι d, t ή m, n και μετά υπάρχει σύμφωνο εκτός των r, l;
- A: Οι καταλήξεις γίνονται -e, -est, -et, -en, -et, -en, -en

3. Chapter of trennbare und untrennbare Verben

- Q: Πότε χωρίζεται το πρόθεμα από το κυρίως ρήμα;
- Α: Όταν το πρόθεμα τονίζεται στην προφορά τότε χωρίζεται.

4. Chapter of Wortstellung

- Q: Ποιά θέση παίρνει το ρήμα σε καταφατικές προτάσεις;
- Α: Τη δεύτερη θέση.
- Q: Ποιά θέση παίρνει το ρήμα σε ερωτηματικές προτάσεις;
- Α: Τη πρώτη θέση.

5. Chapter of konjuktionen

- Q: Ποιοι είναι οι σύνδεσμοι που δεν ανήκουν σε καμία πρόταση;
- A: Sondern (αλλά), Oder (ή), Und (και), Denn (διότι), Aber (αλλά)
- Q: Ποια είναι η διαφορά μεταξύ sondern και aber;
- A: Το sondern συνδέει αντιθετικές προτάσεις όπου η πρώτη πρέπει να είναι αρνητική."""


VOCABULARY_CARD_PROMPT_DE = """You are creating Anki flashcards from German vocabulary content.

Analyze the PDF and extract all vocabulary words with example sentences.
For each word, provide:
- The German word (as the question)
- The Greek translation, a German example sentence, and the Greek translation of the sentence (as the answer)

Extract all vocabulary words from the PDF. Create natural, useful example sentences."""


# =============================================================================
# Chinese Prompts
# =============================================================================

CLASSIFICATION_PROMPT_ZH = """You are analyzing a page from a Chinese (Mandarin) language learning textbook.

Analyze the PDF content and determine if it is primarily:
1. "radicals" - If it focuses on Chinese radicals (部首), their meanings, stroke order, or how they combine to form characters
2. "vocabulary" - If it focuses on teaching new words/characters, usually organized by topic/theme (e.g., food, family, travel)

Respond with ONLY one word: either "radicals" or "vocabulary"."""


RADICALS_CARD_PROMPT_ZH = """You are creating Anki flashcards from Chinese (Mandarin) radical (部首) content.

Analyze the PDF content and create question-answer flashcard pairs about Chinese radicals.
MOST IMPORTANT RULE: The format must follow the followed template, do not deviate from it.
Rules to generate cards:
1. For each radical you find, create a card.
2. If the radical has a variant form, create a new card for it, separate from the original radical card. For example:
  - So if a radical has a variant form, 2 cards should be created for it. One for the original radical and one for the variant form.
3. If there are tables listing radicals, create a card for each radical in the table.
4. If you find any exercises, ignore them.
5. Don't create cards for radicals that you don't see in the PDF.
6. Keep cards simple and easy to understand.
7. If the table/file contains examples use those examples in the card, find the pinyin and translation of the example. If there are no examples, create one.
8. Do not change the format of the example sentences, keep them as they are. Make sure that the pinyin and translation are correct.
 - For example if the sentence is 你很漂亮, then do not translate as you, very, beautiful. Translate it as You are very beautiful.

Bad example:
Question: What does the radical 人 mean?
Answer: rén. Human, person, people. <br> Variants: 亻<br> Examples: 今 (Jīn) - Today.

Good example:
Question: What does the radical 人 mean?
Answer: rén. Human, person, people. <br> Variants: 亻<br> Examples: 我是一个人。 (Wǒ shì yī gè rén.). I am a person.

The bad example doesn't have a full sentence which includes the radical. The good example has a full sentence which includes the radical and the appropriate translation.
"""


VOCABULARY_CARD_PROMPT_ZH = """You are creating Anki flashcards from Chinese (Mandarin) vocabulary content.

Analyze the PDF and extract all vocabulary words with example sentences.
For each word, provide:
- The Chinese word, including pinyin (as the question)
- The English translation, a Chinese example sentence, and the English translation of the sentence (as the answer)

Extract all vocabulary words from the PDF. Create natural, useful example sentences.
Always include pinyin in the question field, e.g. "苹果 (píngguǒ)".

Finally and most importantly, if the chinese word is not a radical, then identify all the radicals in the word and add them
including their translation and pinyin in the answer field."""

# =============================================================================
# Prompt Dispatch
# =============================================================================

# Maps (language_name, deck_type_lowercase) -> prompt string
DECK_TYPE_PROMPTS = {
    ("German", "grammar"): GRAMMAR_CARD_PROMPT_DE,
    ("German", "vocabulary"): VOCABULARY_CARD_PROMPT_DE,
    ("Chinese", "radicals"): RADICALS_CARD_PROMPT_ZH,
    ("Chinese", "vocabulary"): VOCABULARY_CARD_PROMPT_ZH,
}


def build_classification_prompt(language_name: str, deck_types: list) -> str:
    """Auto-generate a classification prompt from the language's deck types.
    
    Args:
        language_name: E.g., "German", "Chinese".
        deck_types: List of deck type names (e.g., ["Vocabulary", "Grammar"]).
    
    Returns:
        A classification prompt string.
    """
    type_descriptions = []
    all_types_list = []
    
    for i, dt in enumerate(deck_types, 1):
        dt_lower = dt.lower()
        if dt_lower == "vocabulary":
            desc = f'{i}. "vocabulary" - If it focuses on teaching new words, usually organized by topic/theme'
        else:
            desc = f'{i}. "{dt_lower}"'
        type_descriptions.append(desc)
        all_types_list.append(f'"{dt_lower}"')
    
    type_list = "\n".join(type_descriptions)
    
    if len(all_types_list) > 1:
        all_types = ", ".join(all_types_list[:-1]) + f', or {all_types_list[-1]}'
    else:
        all_types = all_types_list[0]
    
    return (
        f"You are analyzing a page from a {language_name} language learning textbook.\n\n"
        f"Analyze the PDF content and determine if it is primarily:\n"
        f"{type_list}\n\n"
        f"Respond with ONLY one word: {all_types}."
    )


from .templates import CARD_TEMPLATES, DEFAULT_TEMPLATES

def get_deck_type_prompt(language_name: str, deck_type: str, template: str = None) -> str:
    """Get the Q&A prompt for a specific deck type.
    
    Args:
        language_name: E.g., "German", "Chinese".
        deck_type: Deck type name (e.g., "Grammar", "Radicals").
        template: Optional template name (e.g. "basic", "detailed").
    
    Returns:
        The composed prompt string with the requested JSON template.
    
    Raises:
        ValueError: If no prompt is defined for this language/deck_type combo,
                    or if an invalid template is requested.
    """
    key = (language_name, deck_type.lower())
    base_prompt = DECK_TYPE_PROMPTS.get(key)
    if base_prompt is None:
        raise ValueError(
            f"No base prompt defined for language '{language_name}', "
            f"deck type '{deck_type}'. "
            f"Available: {list(DECK_TYPE_PROMPTS.keys())}"
        )
        
    if template is None:
        template = DEFAULT_TEMPLATES.get(deck_type.lower(), "basic")
        
    template_str = CARD_TEMPLATES.get(template.lower())
    if template_str is None:
        raise ValueError(
            f"Invalid template '{template}'. "
            f"Available templates: {list(CARD_TEMPLATES.keys())}"
        )
        
    return f"{base_prompt}\n\n{template_str}"
