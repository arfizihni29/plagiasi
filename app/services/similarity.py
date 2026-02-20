"""
Similarity Computation Module
==============================
Uses TF-IDF vectorization and cosine similarity to compare a sentence
against a list of web snippets. Returns the highest similarity score
found across all snippets.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(sentence: str, snippets: list[str]) -> tuple[float, str]:
    """
    Compute the TF-IDF cosine similarity between a sentence and each snippet.

    Args:
        sentence:  The original user sentence.
        snippets:  List of web search result snippets to compare against.

    Returns:
        A tuple of (highest_similarity_percentage, best_matching_snippet).
        Returns (0.0, "") if no snippets are provided or computation fails.
    """
    if not snippets:
        return 0.0, ""

    try:
        # Build a corpus: the user sentence + all retrieved snippets
        corpus = [sentence] + snippets

        # Vectorize using TF-IDF — converts text to numerical feature vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Compute cosine similarity between the sentence (index 0) and every snippet
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

        # Find the highest similarity score and its corresponding snippet
        max_index = similarities[0].argmax()
        max_score = float(similarities[0][max_index])

        # Convert to percentage (0–100) and round to 1 decimal place
        return round(max_score * 100, 1), snippets[max_index]

    except ValueError:
        # Can occur if all texts are empty or contain only stop-words
        return 0.0, ""
