# IAC Scientific Publication ↔ Press Note Matching Pipeline

[![CI](https://github.com/albertoreyescastro/IAC-publication-press-note-matching/actions/workflows/ci.yml/badge.svg)](https://github.com/albertoreyescastro/IAC-publication-press-note-matching/actions/workflows/ci.yml)
[![Python 3.11–3.12](https://img.shields.io/badge/python-3.11--3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![XERJ Corpus Hub contributor](https://hub.xerj.org/contributors/albertoreyescastro/badge.svg)](https://hub.xerj.org/contributors/albertoreyescastro)

A reproducible Python workflow for linking scientific publication titles with public press notes from the Instituto de Astrofísica de Canarias (IAC).

The project keeps the original matching approach deliberately interpretable: multilingual text normalisation, RapidFuzz similarity, exact-title evidence and scientific-term overlap are combined into a ranked shortlist for human review. The default path is fully offline and reproducible; live collection from the public IAC news archive is available as an explicit opt-in mode.

> **Portfolio scope:** the public repository contains a compact 29-title sample and a small regression fixture. It demonstrates the engineering and ranking workflow without publishing the larger local source list or private/internal institutional data. The heuristic score is a ranking signal, not a calibrated probability or a claim of bibliographic certainty.

## Live demo

A runnable Kaggle demonstration is available here:

**[Open the Kaggle demo](https://www.kaggle.com/code/albertoreyescastro20/iac-scientific-publication-matching-demo)**

The Kaggle notebook uses a reduced pre-collected dataset so that the matching workflow remains reproducible without relying on live web scraping. The GitHub repository is the canonical implementation.

## What this project demonstrates

- Offline-first, reproducible scientific-text matching.
- Optional defensive scraping of the public IAC news archive.
- English/Spanish text normalisation for cross-language scientific outreach data.
- RapidFuzz token-set and partial similarity signals.
- Exact-title detection when a paper title is explicitly cited in a press note.
- Scientific-term, acronym and astronomical-object overlap.
- Transparent heuristic ranking with explicit manual-review tiers.
- Compact evidence snippets for reviewer inspection.
- A reusable Python package, CLI and notebook built on the same core logic.
- Regression checks for known sample links without overstating them as generalisation metrics.
- Unit-tested deterministic behaviour and GitHub Actions CI with no network dependency.

## Pipeline

```text
Publication titles                 Public IAC press-note sample
       │                                      │
       └──────────────┬───────────────────────┘
                      ▼
          Text cleaning + normalisation
                      │
                      ▼
        Pairwise interpretable signals
      ┌───────────────┼────────────────┐
      │               │                │
 token-set        partial         exact title
 similarity      similarity        + term overlap
      └───────────────┼────────────────┘
                      ▼
             Heuristic rank score
                      │
                      ▼
            Manual-review threshold
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 Ranked candidate CSV      regression metrics
```

## Matching policy

For each publication-title / press-note pair, the workflow combines four transparent signals:

```text
score = 0.38 × token_set
      + 0.47 × partial
      + exact-title bonus
      + scientific-term overlap bonus
```

Scores are capped at `100` and used only for ranking and filtering.

| Score | Review tier |
|---:|---|
| `95–100` | `very_strong` |
| `85–94` | `strong` |
| `72–84` | `candidate` |
| `<72` | not exported by default |

The default threshold is `72`. These tiers are review aids, not calibrated confidence levels.

## Installation

Python 3.10+ is supported. CI currently tests Python 3.11 and 3.12.

### Option A — standard install

```bash
python -m venv .venv
```

Activate the environment, then install:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

### Option B — notebook support

```bash
python -m pip install -e ".[notebook]"
```

## Basic usage

Run the reproducible offline workflow:

```bash
python -m iac_matching
```

or use the installed CLI:

```bash
iac-match
```

By default, the pipeline reads the bundled sample and writes:

```text
outputs/iac_article_pressnote_matches.csv
outputs/regression_metrics.json
```

No network access is required for the default run.

## Optional live scraping

Live collection is deliberately opt-in:

```bash
python -m iac_matching --live --year 2024 --verbose
```

The collector uses bounded request timeouts, retries with exponential backoff, a descriptive User-Agent and a delay between detail-page requests.

The public IAC website can change over time, so live scraping is kept out of CI and out of the default reproducible path.

## Notebook workflow

Open:

```text
iac_publication_press_note_matching.ipynb
```

The notebook calls the same reusable package as the CLI instead of duplicating the matching implementation. Its committed path is offline and deterministic, which keeps the notebook suitable for portfolio review and hosted environments.

## Outputs

The main candidate file is:

```text
outputs/iac_article_pressnote_matches.csv
```

Each exported row includes the press-note title/date/URL, publication ID/title, component similarities, exact-title evidence, shared scientific terms, heuristic score, review tier and a compact evidence snippet.

The regression report is written to:

```text
outputs/regression_metrics.json
```

## Testing

CI intentionally avoids depending on the live IAC website. It checks deterministic behaviour such as normalisation, scoring, ranking, HTML parsing against local fixtures and preservation of known sample links.

Run locally:

```bash
ruff check src tests
pytest
python -m iac_matching \
  --output /tmp/matches.csv \
  --metrics-output /tmp/metrics.json
```

The bundled regression fixture currently contains 8 press notes and 9 known publication-note pairs. It is designed to catch software-ranking regressions, not to estimate archive-wide model quality. A larger independently labelled dataset would be required for credible precision/recall evaluation.

## Scientific outreach context

The motivating problem comes from scientific-publication and outreach material associated with the Instituto de Astrofísica de Canarias. Journal papers normally retain official English titles, while institutional outreach notes are primarily written in Spanish. Exact string matching is therefore often insufficient, especially when a note paraphrases a result or references a paper through astronomical objects, acronyms or domain-specific terminology.

- [IAC official website](https://www.iac.es/)
- [IAC news and outreach archive](https://www.iac.es/es/divulgacion/noticias)

The public sample contains 29 numbered publication titles. The earlier local workflow used a substantially larger 752-title source list, which is not included here.

This repository is also separate from the later `faster-whisper` transcription project. Earlier IAC-related transcription work and this publication-matching workflow should not be conflated with that later reusable speech pipeline.

## Limitations

- The ranking score is heuristic and not probabilistically calibrated.
- Candidate links require manual verification before being treated as confirmed matches.
- A press note can legitimately reference more than one publication.
- Translation, paraphrase and sparse scientific terminology can still produce false negatives.
- Common domain terminology can produce false positives without enough discriminative evidence.
- The live scraper may require maintenance if the public IAC website changes structure.
- The bundled regression fixture is intentionally small and is not a generalisation benchmark.
- Semantic embeddings or LLM-based retrieval could improve some indirect matches, but replacing the current method would materially change the original project rather than refine it.

## Privacy

No private institutional publication list, internal press database, private correspondence or large raw scrape dump is included in the public repository.

The sample data is intentionally compact. Evidence snippets are limited to the text needed to inspect a candidate match, and the default workflow does not require network access.

## Repository layout

```text
IAC-publication-press-note-matching/
├── src/
│   └── iac_matching/
│       ├── core.py
│       ├── scraper.py
│       ├── evaluation.py
│       ├── pipeline.py
│       └── cli.py
├── tests/
│   ├── test_core.py
│   ├── test_regression.py
│   └── test_scraper_parsing.py
├── data/
│   ├── sample_articles.txt
│   ├── sample_press_notes.csv
│   └── validation_pairs.csv
├── outputs/
│   ├── iac_article_pressnote_matches.csv
│   └── regression_metrics.json
├── docs/
│   └── METHODOLOGY.md
├── .github/workflows/
│   └── ci.yml
├── iac_publication_press_note_matching.ipynb
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── CHANGELOG.md
├── .gitignore
└── LICENSE
```

## License

MIT. See [LICENSE](LICENSE).

## Author

Alberto Reyes Castro
