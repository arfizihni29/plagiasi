import os
import time
import logging

import requests
from duckduckgo_search import DDGS  # NEW: DuckDuckGo Search client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read API key from environment variable SERPER_API_KEY
# ---------------------------------------------------------------------------
DEFAULT_SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
SERPER_ENDPOINT: str = "https://google.serper.dev/search"
REQUEST_TIMEOUT: int = 10          # seconds
DELAY_BETWEEN_QUERIES: float = 1.0  # seconds – avoids Serper rate limits


def search_google(query: str, num_results: int = 3, api_key: str = None) -> list[str]:
    """
    Send a search query to Serper.dev and extract organic result snippets.
    Fallback to DuckDuckGo if Serper fails or returns no results.

    Args:
        query:        The search query string (typically a sentence).
        num_results:  Maximum number of organic results to request (default 3).
        api_key:      Optional Serper API key to use (overrides env var).

    Returns:
        A list of snippet strings from organic search results.
        Returns an empty list if both Serper and DuckDuckGo fail or find no results.
    """
    # Determine API key to use: passed arg > env var > empty string
    current_api_key = api_key or DEFAULT_SERPER_API_KEY

    # -----------------------------------------------------------------------
    # PRIMARY STRATEGY: Serper.dev (Google Search)
    # -----------------------------------------------------------------------
    if current_api_key:
        try:
            # logger.info("Attempting Serper search for query: %.30s...", query)
            headers = {
                "X-API-KEY": current_api_key,
                "Content-Type": "application/json",
            }
            payload = {
                "q": query,
                "num": num_results,
            }

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
            organic_results = data.get("organic", [])
            
            for result in organic_results:
                snippet = result.get("snippet", "")
                if snippet:
                    snippets.append(snippet)
            
            if snippets:
                # Success via Serper!
                return snippets
            
            # If Serper returns empty list (no results found), we proceed to fallback
            logger.warning("Serper returned no organic results. Falling back to DuckDuckGo.")

        except requests.exceptions.Timeout:
            logger.warning("Serper request timed out. Falling back to DuckDuckGo.")
        except requests.exceptions.RequestException as exc:
            logger.error("Serper request failed: %s. Falling back to DuckDuckGo.", exc)
            # If 403 Forbidden (Quota limit reached/Invalid Key), definitely fallback
        finally:
            # Small delay to respect rate limits between consecutive queries
            time.sleep(DELAY_BETWEEN_QUERIES)
    
    else:
        # No API key provided at all
        logger.info("No Serper API key available. Using DuckDuckGo directly.")


    # -----------------------------------------------------------------------
    # FALLBACK STRATEGY: DuckDuckGo (No API Key Required)
    # -----------------------------------------------------------------------
    try:
        # logger.info("Attempting DuckDuckGo search for query: %.30s...", query)
        with DDGS() as ddgs:
            # DDGS().text() returns an iterator of results
            ddg_results = list(ddgs.text(query, max_results=num_results))
            
            snippets: list[str] = []
            for result in ddg_results:
                snippet = result.get("body", "")  # DDG uses 'body' for snippet
                if snippet:
                    snippets.append(snippet)
            
            if snippets:
                return snippets
            
            logger.warning("DuckDuckGo also returned no results for query: %.30s...", query)
            return []

    except Exception as exc:
        logger.error("DuckDuckGo search failed: %s", exc)
        return []
