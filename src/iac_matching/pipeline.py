from __future__ import annotations

from pathlib import Path

import pandas as pd

from .core import extract_articles_from_txt, match_articles_to_press_notes
from .evaluation import evaluate_ranking


def run_offline_pipeline(
    *,
    articles_path: str | Path,
    press_notes_path: str | Path,
    output_path: str | Path,
    validation_path: str | Path | None = None,
    threshold: float = 72.0,
    top_k: int = 8,
    min_shared_terms: int = 1,
) -> tuple[pd.DataFrame, dict | None]:
    article_text = Path(articles_path).read_text(encoding="utf-8", errors="ignore")
    articles = extract_articles_from_txt(article_text)
    notes = pd.read_csv(press_notes_path, dtype={"press_note_id": str})
    matches = match_articles_to_press_notes(
        notes,
        articles,
        threshold=threshold,
        top_k=top_k,
        min_shared_terms=min_shared_terms,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    matches.to_csv(output, index=False, encoding="utf-8")

    metrics = None
    if validation_path is not None:
        validation = pd.read_csv(validation_path, dtype={"article_id": str})
        metrics = evaluate_ranking(notes, articles, validation)
    return matches, metrics
