"""Reusable components for the IAC publication-to-press-note matching demo."""

from .core import (
    MATCH_COLUMNS,
    Article,
    Match,
    calculate_match,
    extract_articles_from_txt,
    match_articles_to_press_notes,
    meaningful_tokens,
    normalise,
)
from .evaluation import evaluate_ranking
from .scraper import ScraperConfig, scrape_iac_press_notes

__all__ = [
    "Article",
    "Match",
    "MATCH_COLUMNS",
    "ScraperConfig",
    "calculate_match",
    "evaluate_ranking",
    "extract_articles_from_txt",
    "match_articles_to_press_notes",
    "meaningful_tokens",
    "normalise",
    "scrape_iac_press_notes",
]
