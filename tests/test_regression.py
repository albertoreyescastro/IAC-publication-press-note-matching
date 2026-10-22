from __future__ import annotations

from pathlib import Path

import pandas as pd

from iac_matching.core import extract_articles_from_txt, match_articles_to_press_notes
from iac_matching.evaluation import evaluate_ranking


ROOT = Path(__file__).resolve().parents[1]


def load_inputs():
    articles = extract_articles_from_txt((ROOT / "data/sample_articles.txt").read_text(encoding="utf-8"))
    notes = pd.read_csv(ROOT / "data/sample_press_notes.csv", dtype={"press_note_id": str})
    validation = pd.read_csv(ROOT / "data/validation_pairs.csv", dtype={"article_id": str})
    return articles, notes, validation


def test_public_fixture_recovers_all_reference_pairs_within_top_three():
    articles, notes, validation = load_inputs()
    metrics = evaluate_ranking(notes, articles, validation)
    assert metrics["pair_recall_at_3"] == 1.0
    assert metrics["note_hit_rate_at_1"] == 1.0


def test_default_export_contains_expected_reference_pairs():
    articles, notes, validation = load_inputs()
    matches = match_articles_to_press_notes(notes, articles)
    actual = set(zip(matches["press_note_url"].astype(str), matches["article_id"].astype(str), strict=True))
    expected = set(zip(validation["press_note_url"].astype(str), validation["article_id"].astype(str), strict=True))
    assert expected <= actual
    assert set(matches["match_tier"]) <= {"very_strong", "strong", "candidate"}
