from __future__ import annotations

from collections import defaultdict

import pandas as pd

from .core import Article, rank_articles_for_note


def evaluate_ranking(
    press_notes_df: pd.DataFrame,
    articles: list[Article],
    validation_pairs: pd.DataFrame,
    *,
    ks: tuple[int, ...] = (1, 3, 5),
) -> dict[str, float | int]:
    """Evaluate ranking on the bundled small regression fixture.

    This is intentionally a regression/evidence check, not a statistical performance claim.
    """
    expected: dict[str, set[str]] = defaultdict(set)
    for _, row in validation_pairs.iterrows():
        expected[str(row["press_note_url"])].add(str(row["article_id"]))

    reciprocal_ranks: list[float] = []
    pair_hits = {k: 0 for k in ks}
    note_hits = {k: 0 for k in ks}
    total_pairs = 0
    evaluated_notes = 0

    for row_number, (_, note_row) in enumerate(press_notes_df.iterrows(), start=1):
        url = str(note_row["url"])
        relevant = expected.get(url, set())
        if not relevant:
            continue
        evaluated_notes += 1
        total_pairs += len(relevant)
        ranked = rank_articles_for_note(note_row, articles, note_id=str(row_number))
        ranked_ids = [str(item.article_id) for item in ranked]

        ranks = [ranked_ids.index(article_id) + 1 for article_id in relevant if article_id in ranked_ids]
        reciprocal_ranks.append(1.0 / min(ranks) if ranks else 0.0)

        for k in ks:
            top = set(ranked_ids[:k])
            recovered = relevant & top
            pair_hits[k] += len(recovered)
            note_hits[k] += int(bool(recovered))

    metrics: dict[str, float | int] = {
        "evaluated_press_notes": evaluated_notes,
        "relevant_pairs": total_pairs,
        "mrr": round(sum(reciprocal_ranks) / evaluated_notes, 4) if evaluated_notes else 0.0,
    }
    for k in ks:
        metrics[f"pair_recall_at_{k}"] = round(pair_hits[k] / total_pairs, 4) if total_pairs else 0.0
        metrics[f"note_hit_rate_at_{k}"] = round(note_hits[k] / evaluated_notes, 4) if evaluated_notes else 0.0
    return metrics
