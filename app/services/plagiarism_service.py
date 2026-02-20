"""
Plagiarism Service — Orchestration Layer
=========================================
Coordinates the full plagiarism-checking pipeline:
  1. Split input text into sentences
  2. Filter out sentences that are too short
  3. For each sentence, query the web and compute similarity
  4. Aggregate results into a structured response
"""

import logging

from app.utils.text_processing import split_sentences, filter_short_sentences
from app.services.serper_client import search_google
from app.services.similarity import compute_similarity

logger = logging.getLogger(__name__)


def check_plagiarism(text: str) -> dict:
    """
    Run the complete plagiarism detection pipeline on the given text.

    Args:
        text: The full text to check for plagiarism.

    Returns:
        A dictionary with:
          - overall_similarity: float  (max score across all sentences)
          - sentences: list of per-sentence detail dicts
    """
    # Step 1 — Split text into individual sentences
    raw_sentences = split_sentences(text)
    logger.info("Split text into %d raw sentences.", len(raw_sentences))

    # Step 2 — Filter out sentences shorter than 5 words (too short for
    #          meaningful similarity comparison)
    sentences = filter_short_sentences(raw_sentences, min_words=5)
    logger.info("Filtered to %d sentences (>= 5 words).", len(sentences))

    if not sentences:
        return {
            "overall_similarity": 0.0,
            "sentences": [],
        }

    # Step 3 — Process each sentence: search the web → compute similarity
    results: list[dict] = []
    overall_max: float = 0.0

    for sentence in sentences:
        logger.info("Checking sentence: %.60s...", sentence)

        # Query Serper.dev for web snippets matching this sentence
        snippets = search_google(sentence, num_results=3)

        # Compute TF-IDF cosine similarity against retrieved snippets
        similarity, best_snippet = compute_similarity(sentence, snippets)

        # Track the highest similarity found across all sentences
        if similarity > overall_max:
            overall_max = similarity

        # Build a meaningful source label from the best matching snippet
        if best_snippet and similarity > 10:
            source_label = best_snippet[:120] + ("..." if len(best_snippet) > 120 else "")
        elif snippets:
            source_label = "Tidak ada sumber signifikan ditemukan"
        else:
            source_label = "Tidak ada hasil pencarian"

        results.append({
            "sentence": sentence,
            "similarity": similarity,
            "source": source_label,
        })

    # Step 4 — Return aggregated response
    return {
        "overall_similarity": overall_max,
        "sentences": results,
    }
