from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .core import extract_articles_from_txt, match_articles_to_press_notes
from .evaluation import evaluate_ranking
from .scraper import ScraperConfig, scrape_iac_press_notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank IAC scientific publication titles against IAC press-note text."
    )
    parser.add_argument("--articles", default="data/sample_articles.txt")
    parser.add_argument("--press-notes", default="data/sample_press_notes.csv")
    parser.add_argument("--validation", default="data/validation_pairs.csv")
    parser.add_argument("--output", default="outputs/iac_article_pressnote_matches.csv")
    parser.add_argument("--metrics-output", default="outputs/regression_metrics.json")
    parser.add_argument("--threshold", type=float, default=72.0)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--min-shared-terms", type=int, default=1)
    parser.add_argument("--live", action="store_true", help="Opt in to live scraping instead of the bundled fixture.")
    parser.add_argument("--year", default="2024")
    parser.add_argument("--max-pages", type=int, default=160)
    parser.add_argument("--delay-seconds", type=float, default=0.45)
    parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    article_text = Path(args.articles).read_text(encoding="utf-8", errors="ignore")
    articles = extract_articles_from_txt(article_text)

    if args.live:
        config = ScraperConfig(year=args.year, max_pages=args.max_pages, delay_seconds=args.delay_seconds)
        press_notes = scrape_iac_press_notes(config, verbose=args.verbose)
        live_path = Path(f"outputs/iac_press_notes_{args.year}_live.csv")
        live_path.parent.mkdir(parents=True, exist_ok=True)
        press_notes.to_csv(live_path, index=False, encoding="utf-8")
        print(f"Live scrape saved: {live_path} ({len(press_notes)} press notes)")
    else:
        press_notes = pd.read_csv(args.press_notes, dtype={"press_note_id": str})

    matches = match_articles_to_press_notes(
        press_notes,
        articles,
        threshold=args.threshold,
        top_k=args.top_k,
        min_shared_terms=args.min_shared_terms,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    matches.to_csv(output, index=False, encoding="utf-8")
    print(f"Matches saved: {output} ({len(matches)} rows)")

    if not args.live and args.validation and Path(args.validation).exists():
        validation = pd.read_csv(args.validation, dtype={"article_id": str})
        metrics = evaluate_ranking(press_notes, articles, validation)
        metrics_path = Path(args.metrics_output)
        metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        print("Regression fixture metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        print(f"Metrics saved: {metrics_path}")


if __name__ == "__main__":
    main()
