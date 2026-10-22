# Changelog

## 2.0.0 — portfolio hardening

- Preserved the original 2024 fuzzy/term-overlap matching approach.
- Moved reusable logic from the notebook into a small Python package.
- Made the default workflow offline and reproducible.
- Added a compact press-note fixture and regression reference mapping.
- Added ranking-regression metrics; explicitly documented that the 0–100 score is heuristic, not calibrated confidence.
- Added retries/backoff, timeout handling, a descriptive User-Agent and opt-in live scraping.
- Added unit/regression tests and GitHub Actions CI.
- Removed runtime package installation from the notebook.
- Fixed evidence-snippet indexing so normalised-string offsets are not applied to raw text.
- Added explicit limitations and project-provenance language for portfolio/recruiter review.
