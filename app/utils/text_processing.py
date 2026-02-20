"""
Text Processing Utilities
=========================
Handles text splitting and filtering using NLTK sentence tokenizer.
"""

import nltk

# ---------------------------------------------------------------------------
# Ensure the NLTK tokenizer model is downloaded on first use.
# 'punkt_tab' is the updated tokenizer resource for sent_tokenize.
# ---------------------------------------------------------------------------
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def split_sentences(text: str) -> list[str]:
    """
    Split a block of text into individual sentences using NLTK.

    Args:
        text: The raw input text.

    Returns:
        A list of sentence strings.
    """
    return nltk.sent_tokenize(text)


def filter_short_sentences(sentences: list[str], min_words: int = 5) -> list[str]:
    """
    Remove sentences that are too short to produce meaningful similarity scores.

    Args:
        sentences:  List of sentence strings.
        min_words:  Minimum number of words required (default 5).

    Returns:
        Filtered list containing only sentences with >= min_words words.
    """
    return [s for s in sentences if len(s.split()) >= min_words]
