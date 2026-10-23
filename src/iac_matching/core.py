from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass

import pandas as pd
from rapidfuzz import fuzz

EN_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
    "has", "have", "how", "in", "into", "is", "it", "its", "new", "of", "on",
    "or", "that", "the", "their", "this", "through", "to", "under", "was",
    "were", "which", "with", "will", "where", "who", "why", "research",
    "researchers", "scientists", "astronomers", "study", "studies", "team",
    "group", "find", "finds", "found", "discover", "discovers", "discovered",
    "detect", "detects", "detected", "show", "shows", "reveals", "reveal",
    "observe", "observes", "observed", "using", "use", "used", "results",
    "analysis", "data",
}

ES_STOPWORDS = {
    "a", "al", "ante", "bajo", "con", "contra", "como", "de", "del", "desde",
    "durante", "e", "el", "ella", "ellas", "ellos", "en", "entre", "era",
    "es", "esa", "ese", "eso", "esta", "este", "esto", "estos", "ha", "han",
    "hasta", "la", "las", "lo", "los", "mas", "más", "para", "pero", "por",
    "que", "se", "sin", "sobre", "su", "sus", "tras", "un", "una", "unas",
    "unos", "y", "o", "nueva", "nuevo", "estudio", "investigadores",
    "investigadoras", "equipo", "cientificos", "científicos", "cientificas",
    "científicas", "resultados", "datos", "analisis", "análisis",
}

LOW_SIGNAL_TERMS = {
    "iac", "instituto", "astrofisica", "astrofísica", "canarias", "canary",
    "islands", "tenerife", "lapalma", "palma", "observatorio", "observatory",
    "teide", "fundacion", "fundación", "canaria", "astronomy", "astrophysics",
    "star", "stars", "earth", "sun", "solar", "galaxy", "galaxies", "planet",
    "planets", "space", "universe", "black", "hole", "holes", "mass",
    "stellar", "formation", "telescope", "observations",
}

STOPWORDS = EN_STOPWORDS | ES_STOPWORDS | LOW_SIGNAL_TERMS


@dataclass(frozen=True)
class Article:
    article_id: str
    title: str


@dataclass(frozen=True)
class Match:
    press_note_id: str
    press_note_title: str
    press_note_date: str
    press_note_url: str
    article_id: str
    article_title: str
    score: float
    match_tier: str
    token_set_score: float
    partial_score: float
    exact_title_match: bool
    shared_term_count: int
    shared_terms: str
    context_snippet: str


MATCH_COLUMNS = [
    "press_note_id",
    "press_note_title",
    "press_note_date",
    "press_note_url",
    "article_id",
    "article_title",
    "score",
    "match_tier",
    "token_set_score",
    "partial_score",
    "exact_title_match",
    "shared_term_count",
    "shared_terms",
    "context_snippet",
]


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(text))
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def normalise(text: str) -> str:
    """Return a conservative ASCII-like form used for fuzzy comparison."""
    text = strip_accents(str(text).lower())
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return clean_spaces(text)


def meaningful_tokens(text: str, min_len: int = 4) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", normalise(text))
    return [token for token in tokens if len(token) >= min_len and token not in STOPWORDS]


def extract_articles_from_txt(text: str) -> list[Article]:
    """Parse records in the original ``<id>.- <title>`` format."""
    pattern = re.compile(r"(?m)^\s*(\d+)\.\-\s*(.+?)(?=^\s*\d+\.\-|\Z)", re.S)
    articles: list[Article] = []
    for match in pattern.finditer(text):
        article_id = match.group(1).strip()
        title = clean_spaces(match.group(2).strip())
        if title:
            articles.append(Article(article_id=article_id, title=title))
    return articles


def token_set_ratio(a: str, b: str) -> float:
    return float(fuzz.token_set_ratio(a, b))


def partial_ratio(a: str, b: str) -> float:
    return float(fuzz.partial_ratio(a, b))


def _find_raw_term(text: str, term: str) -> int:
    """Best-effort location of a normalised token in raw text."""
    match = re.search(re.escape(term), text, flags=re.I)
    if match:
        return match.start()
    return -1


def make_snippet(text: str, terms: list[str], max_len: int = 320) -> str:
    """Return compact evidence without using incompatible normalised-string offsets."""
    text = clean_spaces(text)
    if not text:
        return ""
    for term in terms:
        idx = _find_raw_term(text, term)
        if idx >= 0:
            start = max(0, idx - 120)
            if start > 0:
                next_space = text.find(" ", start)
                if next_space != -1 and next_space < idx:
                    start = next_space + 1
            end = min(len(text), start + max_len)
            if end < len(text):
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space
            return clean_spaces(text[start:end])
    return text[:max_len].rstrip()


def score_to_tier(score: float) -> str:
    if score >= 95:
        return "very_strong"
    if score >= 85:
        return "strong"
    if score >= 72:
        return "candidate"
    return "below_threshold"


def calculate_match(article: Article, note_id: str, note_row: pd.Series) -> Match:
    """Calculate the original heuristic ranking score.

    The 0-100 score is a ranking heuristic, *not* a calibrated probability or confidence.
    We intentionally retain the original weighting so the public reconstruction remains
    faithful to the project, while making that limitation explicit in the API/docs.
    """
    note_title = str(note_row.get("title", ""))
    note_text = f"{note_title}\n\n{note_row.get('body', '')}"

    article_norm = normalise(article.title)
    note_norm = normalise(note_text)

    article_tokens = set(meaningful_tokens(article.title))
    note_tokens = set(meaningful_tokens(note_text))
    shared = sorted(article_tokens & note_tokens)

    exact = bool(article_norm and article_norm in note_norm)
    ts_score = token_set_ratio(article_norm, note_norm)
    pr_score = partial_ratio(article_norm, note_norm)

    score = (0.38 * ts_score) + (0.47 * pr_score) + (15.0 if exact else 0.0)
    if len(shared) >= 5:
        score += 8.0
    elif len(shared) == 4:
        score += 6.0
    elif len(shared) == 3:
        score += 4.0
    elif len(shared) == 2:
        score += 2.0
    score = min(score, 100.0)

    rounded = round(score, 2)
    return Match(
        press_note_id=str(note_id),
        press_note_title=note_title,
        press_note_date=str(note_row.get("date", "")),
        press_note_url=str(note_row.get("url", "")),
        article_id=article.article_id,
        article_title=article.title,
        score=rounded,
        match_tier=score_to_tier(rounded),
        token_set_score=round(ts_score, 2),
        partial_score=round(pr_score, 2),
        exact_title_match=exact,
        shared_term_count=len(shared),
        shared_terms=", ".join(shared),
        context_snippet=make_snippet(note_text, shared),
    )


def rank_articles_for_note(note_row: pd.Series, articles: list[Article], note_id: str = "") -> list[Match]:
    ranked = [calculate_match(article, note_id, note_row) for article in articles]
    return sorted(
        ranked,
        key=lambda item: (
            -item.score,
            int(item.article_id) if str(item.article_id).isdigit() else item.article_id,
        ),
    )


def match_articles_to_press_notes(
    press_notes_df: pd.DataFrame,
    articles: list[Article],
    *,
    threshold: float = 72.0,
    top_k: int = 8,
    min_shared_terms: int = 1,
) -> pd.DataFrame:
    """Rank article candidates for each press note and return review candidates."""
    matches: list[Match] = []
    for row_number, (_, note_row) in enumerate(press_notes_df.iterrows(), start=1):
        note_id = str(note_row.get("press_note_id", row_number))
        ranked = rank_articles_for_note(note_row, articles, note_id=note_id)
        filtered = [
            item
            for item in ranked
            if item.score >= threshold and item.shared_term_count >= min_shared_terms
        ]
        matches.extend(filtered[:top_k])

    return pd.DataFrame([asdict(match) for match in matches], columns=MATCH_COLUMNS)
