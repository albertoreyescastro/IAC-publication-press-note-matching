# Methodology notes

## Scope

The project ranks scientific publication titles against IAC press-note text for human review. The original logic is deliberately retained rather than replaced with a modern embedding model, because the goal of this repository is to document and harden the original workflow faithfully.

## Why the score is not confidence

The score combines hand-selected fuzzy similarities and deterministic bonuses. It is useful for ordering candidates, but it has not been calibrated against a sufficiently large labelled corpus. Consequently, the repository avoids probability/confidence terminology.

## Public regression fixture

The bundled press-note fixture is compact evidence derived from the original exported sample. Known public pairs act as regression targets among 29 candidate publication titles. This checks that code changes do not silently damage ranking behaviour.

It does **not** estimate production precision, recall or generalisation.

## Scraping policy

Live collection is opt-in, uses a descriptive User-Agent, request timeouts, retry/backoff and a delay between detail-page requests. CI and the default notebook use offline fixtures instead of repeatedly hitting the public IAC website.

## Future work that would change the original project

A multilingual sentence-embedding or cross-encoder approach could better connect Spanish outreach text to English scientific titles. That would be a meaningful next experiment, but it is intentionally not mixed into this portfolio hardening pass because it would alter the project's original methodology and make before/after evidence less interpretable.
