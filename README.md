# IAC Scientific Publication ↔ Press Note Matching Pipeline

A compact Python/Colab pipeline for linking scientific publication titles with public press notes from the Instituto de Astrofísica de Canarias (IAC).

The project combines live web scraping, text cleaning, fuzzy matching and evidence-based ranking. It is designed as a GitHub-friendly demo of a larger local workflow that used a full publication-title list.

## Demo

A Kaggle-friendly demo version is available here:

[Open the Kaggle demo](https://www.kaggle.com/code/albertoreyescastro20/iac-scientific-publication-matching-demo)

The Kaggle version uses a reduced pre-collected dataset uploaded through Kaggle, so the matching workflow can be reproduced without relying on live scraping during execution.

## Source website

The press notes are collected from the public website of the Instituto de Astrofísica de Canarias:

[IAC official website](https://www.iac.es/)

The live scraping workflow targets the public IAC news archive:

[IAC news archive](https://www.iac.es/es/divulgacion/noticias)

## What it does

- Scrapes public IAC news pages for a target year.
- Filters records by year and press-note type.
- Loads a compact sample of scientific publication titles.
- Cleans and normalizes Spanish and English scientific text.
- Matches publication titles with press-note text using fuzzy similarity, exact title detection and shared scientific terms.
- Exports ranked candidate matches with scores, shared terms and evidence snippets.

## Repository structure

```text
iac-publication-press-note-matching/
│
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── iac_publication_press_note_matching.ipynb
│
├── data/
│   └── sample_articles.txt
│
└── outputs/
    └── iac_article_pressnote_matches.csv
```

## Demo data

The notebook includes an embedded GitHub sample and can also read a local text file from:

```text
data/sample_articles.txt
```

The sample contains 29 numbered publication titles. It mixes likely matches with distractor articles so the matching pipeline can be demonstrated without uploading the full publication list.

## Outputs

The main exported file is:

```text
outputs/iac_article_pressnote_matches.csv
```

It contains:

- press-note title, date and URL;
- matched article ID and title;
- final score;
- fuzzy matching components;
- exact-title detection;
- shared scientific terms;
- an evidence snippet from the press-note text.

## Matching strategy

Publication titles are mostly in English, while the IAC press notes are written in Spanish. This reflects the real structure of the data: journal articles use their official English titles, and institutional press notes are published for a Spanish-speaking audience.

The matching strategy is conservative. It looks for strong evidence such as original paper-title mentions, astronomical object names, acronyms, references, DOI sections and shared scientific terms.

The final table should be read as a ranked list of candidate links for manual review, not as a fully automatic bibliographic authority.

## Score interpretation

Each candidate match receives a score from `0` to `100`.

| Score range | Interpretation |
|---:|---|
| `95–100` | Very strong candidate. Usually supported by an exact title mention or highly specific shared evidence. |
| `85–94` | Strong candidate. Likely match, but still worth checking manually. |
| `72–84` | Possible candidate. It passes the default threshold, but the evidence may be weaker or more indirect. |
| `<72` | Not exported by default. These candidates are treated as too weak for the GitHub demo. |

## Installation

Install the required packages with:

```bash
pip install -r requirements.txt
```

## Requirements

```text
pandas
requests
beautifulsoup4
rapidfuzz
ipython
```

## Usage

Open the notebook in Colab or Jupyter:

```text
iac_publication_press_note_matching.ipynb
```

Then run the cells in order.

By default, the notebook uses the embedded sample. To use an external article-title list, place it at:

```text
data/sample_articles.txt
```

with records in this format:

```text
77.- Publication title
```

## Notes

The public GitHub version uses a compact sample for reproducibility and readability. The full local workflow can be adapted to larger publication lists.

The Kaggle demo is intended as a lightweight, reproducible version of the matching workflow. The GitHub notebook keeps the live scraping workflow visible as part of the full pipeline.

Large raw scrape outputs, full-text dumps and private/local publication files should not be committed to the repository.

## Author

Alberto Reyes Castro

