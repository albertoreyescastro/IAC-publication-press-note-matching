# Methodology notes

## Scope

The project ranks scientific publication titles against IAC press-note text for human review. The original logic is deliberately retained rather than replaced with a modern embedding model, because the goal of this repository is to document and harden the original workflow faithfully.

## Why the score is not confidence

The score combines hand-selected fuzzy similarities and deterministic bonuses. It is useful for ordering candidates, but it has not been calibrated against a sufficiently large labelled corpus. Consequently, the repository avoids probability/confidence terminology.

## Public regression fixture

The bundled press-note fixture is compact evidence derived from the original exported sample. Known public pairs act as regression targets among 29 candidate publication titles. This checks that code changes do not silently damage ranking behaviour.

It does **not** estimate production precision, recall or generalisation.

## Historical IAC outcome vs public sample

The original IAC workflow was designed, implemented and run within a few hours, using a local list of 752 English-language scientific publication titles to find source-paper references for 67 Spanish-language outreach articles. A colleague carried out the same matching independently by hand over approximately two working days. The two sets of final links agreed for all 67 articles after uncertain cases were checked manually; the corresponding references were then added to each of the 67 articles on the IAC website.

The public fixture instead contains 29 candidate titles, 8 press notes and 9 known links. It is a small regression check, **not** the 67-article historical comparison. Neither the original inputs nor the independent reviewer records are distributed here; the reported time comparison and agreement therefore cannot be reproduced from these fixtures and should not be interpreted as archive-wide precision or recall.

## Scraping policy

Live collection is opt-in, uses a descriptive User-Agent, request timeouts, retry/backoff and a delay between detail-page requests. CI and the default notebook use offline fixtures instead of repeatedly hitting the public IAC website.

## Future work that would change the original project

A multilingual sentence-embedding or cross-encoder approach could better connect Spanish outreach text to English scientific titles. That would be a meaningful next experiment, but it is intentionally not mixed into this portfolio hardening pass because it would alter the project's original methodology and make before/after evidence less interpretable.
