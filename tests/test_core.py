from __future__ import annotations

from pathlib import Path

import pandas as pd

from iac_matching.core import Article, calculate_match, extract_articles_from_txt, normalise

ROOT = Path(__file__).resolve().parents[1]


def test_normalise_handles_accents_and_punctuation():
    assert normalise("Astrofísica — CANARIAS!") == "astrofisica canarias"


def test_extract_articles_preserves_original_numbered_format():
    text = "1.- First title\n2.- Second title with\ncontinued text\n"
    rows = extract_articles_from_txt(text)
    assert [(row.article_id, row.title) for row in rows] == [
        ("1", "First title"),
        ("2", "Second title with continued text"),
    ]


def test_exact_title_match_is_ranked_as_very_strong():
    article = Article("549", "A sub-Earth-mass planet orbiting Barnard's star")
    note = pd.Series(
        {
            "title": "Barnard press note",
            "date": "01/10/2024",
            "url": "https://example.test/note",
            "body": "Article: A sub-Earth-mass planet orbiting Barnard's star.",
        }
    )
    match = calculate_match(article, "1", note)
    assert match.exact_title_match is True
    assert match.score == 100.0
    assert match.match_tier == "very_strong"


def test_bundled_article_fixture_contains_expected_size():
    rows = extract_articles_from_txt((ROOT / "data/sample_articles.txt").read_text(encoding="utf-8"))
    assert len(rows) == 29
