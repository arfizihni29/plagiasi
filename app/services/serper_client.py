"""
Serper.dev Google Search Client
================================
Queries the Serper.dev API to retrieve Google search result snippets
for a given query string. Used to find web sources that may match
user-submitted text.
"""

import os
import time
import logging

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read API key from environment variable SERPER_API_KEY
# ---------------------------------------------------------------------------
SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
SERPER_ENDPOINT: str = "https://google.serper.dev/search"
REQUEST_TIMEOUT: int = 10          # seconds
DELAY_BETWEEN_QUERIES: float = 1.0  # seconds – avoids Serper rate limits


def search_google(query: str, num_results: int = 3) -> list[str]:
    """
    Send a search query to Serper.dev and extract organic result snippets.

    Args:
        query:        The search query string (typically a sentence).
        num_results:  Maximum number of organic results to request (default 3).

    Returns:
        A list of snippet strings from organic search results.
        Returns an empty list if the request fails or no results are found.
    """
    # Guard: API key must be configured
    if not SERPER_API_KEY:
        logger.error("SERPER_API_KEY environment variable is not set.")
        return []

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "q": query,
        "num": num_results,
    }

    try:
        response = requests.post(
            SERPER_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()

        # Extract snippet text from each organic result
        snippets: list[str] = []
        for result in data.get("organic", []):
            snippet = result.get("snippet", "")
            if snippet:
                snippets.append(snippet)

        return snippets

    except requests.exceptions.Timeout:
        logger.warning("Serper request timed out for query: %s", query)
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("Serper request failed: %s", exc)
        return []
    finally:
        # Small delay to respect rate limits between consecutive queries
        time.sleep(DELAY_BETWEEN_QUERIES)
