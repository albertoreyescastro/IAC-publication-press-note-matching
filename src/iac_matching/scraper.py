from __future__ import annotations

import re
import time
from dataclasses import dataclass
from urllib.parse import unquote, urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .core import clean_spaces


@dataclass(frozen=True)
class ScraperConfig:
    year: str = "2024"
    base_url: str = "https://www.iac.es"
    list_url: str = "https://www.iac.es/es/divulgacion/noticias"
    max_pages: int = 160
    delay_seconds: float = 0.45
    timeout_seconds: float = 30.0
    user_agent: str = "iac-publication-matching-portfolio/2.0 (+educational, low-rate requests)"
    retries: int = 3
    backoff_factor: float = 0.6


def build_session(config: ScraperConfig) -> requests.Session:
    retry = Retry(
        total=config.retries,
        connect=config.retries,
        read=config.retries,
        status=config.retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    session = requests.Session()
    session.headers.update({"User-Agent": config.user_agent})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def _get_soup(session: requests.Session, url: str, timeout_seconds: float) -> BeautifulSoup:
    response = session.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_date_from_text(text: str) -> str:
    match = re.search(r"\b\d{2}/\d{2}/20\d{2}\b", text)
    return match.group(0) if match else ""


def extract_news_type(text: str) -> str:
    match = re.search(
        r"Tipo de noticia\s+(.*?)(?:\s+Ámbito|\s+Temática|\s+Líneas de investigación|"
        r"\s+Otras noticias relacionadas|\s+Noticias relacionadas|$)",
        text,
        flags=re.I | re.S,
    )
    if match:
        return clean_spaces(match.group(1))
    if "nota de prensa" in text.lower():
        return "Nota de prensa"
    return ""


def cut_related_news(text: str) -> str:
    cut_positions = []
    for pattern in (
        r"\bOtras noticias relacionadas\b",
        r"\bNoticias relacionadas\b",
        r"\bContenido relacionado\b",
        r"\bTipo de noticia\b",
    ):
        match = re.search(pattern, text, flags=re.I)
        if match:
            cut_positions.append(match.start())
    return clean_spaces(text[: min(cut_positions)] if cut_positions else text)


def slug_to_title(url: str) -> str:
    slug = unquote(url.rstrip("/").split("/")[-1])
    title = slug.replace("-", " ")
    return title[:1].upper() + title[1:] if title else ""


def clean_iac_title(title: str) -> str:
    title = clean_spaces(title)
    title = re.sub(r"\s*\|\s*Instituto de Astrofísica de Canarias.*$", "", title, flags=re.I)
    title = re.sub(r"\s*-\s*Instituto de Astrofísica de Canarias.*$", "", title, flags=re.I)
    title = re.sub(r"\s*Fecha de publicación\s+\d{2}/\d{2}/20\d{2}.*$", "", title, flags=re.I)
    title = re.sub(r"^(Nota de prensa|Reportaje|Anuncio|Comunicado)\s+", "", title, flags=re.I)
    return title.strip(" -|")


def find_best_card_text(anchor) -> str:
    current = anchor
    best = clean_spaces(anchor.get_text(" "))
    for _ in range(8):
        if current is None:
            break
        text = clean_spaces(current.get_text(" "))
        if re.search(r"\b\d{2}/\d{2}/20\d{2}\b", text) and len(text) <= 1800:
            return text
        if len(text) > len(best):
            best = text
        current = current.parent
    return best[:1800]


def extract_listing_title(card_text: str, href: str) -> str:
    match = re.search(
        r"(?:Nota de prensa|Reportaje|Anuncio|Comunicado)\s+(.*?)\s+Fecha de publicación\s+\d{2}/\d{2}/20\d{2}",
        card_text,
        flags=re.I | re.S,
    )
    if match:
        title = clean_iac_title(match.group(1))
        if len(title) >= 8:
            return title
    return slug_to_title(href)


def extract_candidates_from_listing_html(html: str, config: ScraperConfig) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    records: dict[str, dict] = {}
    canonical_list = config.list_url.rstrip("/")
    for anchor in soup.find_all("a", href=True):
        href = urljoin(config.base_url, anchor["href"]).split("?")[0].rstrip("/")
        if "/es/divulgacion/noticias/" not in href or href == canonical_list:
            continue
        card_text = find_best_card_text(anchor)
        date = extract_date_from_text(card_text)
        records[href] = {
            "url": href,
            "listing_text": card_text,
            "listing_title": extract_listing_title(card_text, href),
            "date": date,
            "year": date[-4:] if date else "",
            "is_press_note_on_listing": "nota de prensa" in card_text.lower(),
        }
    return list(records.values())


def extract_press_note_from_html(html: str, candidate: dict) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    h1 = soup.find("h1")
    if h1:
        candidates.append(h1.get_text(" "))
    for attr in ({"property": "og:title"}, {"name": "twitter:title"}):
        meta = soup.find("meta", attrs=attr)
        if meta and meta.get("content"):
            candidates.append(meta["content"])
    html_title = soup.find("title")
    if html_title:
        candidates.append(html_title.get_text(" "))
    candidates.extend([candidate.get("listing_title", ""), slug_to_title(candidate["url"])])

    title = next(
        (
            cleaned
            for raw in candidates
            if (cleaned := clean_iac_title(raw))
            and len(cleaned) >= 8
            and cleaned.lower() not in {"leer más", "leer mas"}
        ),
        slug_to_title(candidate["url"]),
    )

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body
    raw_text = clean_spaces(main.get_text(" ")) if main else ""
    date = extract_date_from_text(raw_text) or candidate.get("date", "")
    news_type = extract_news_type(raw_text)
    body = cut_related_news(raw_text)
    return {
        "title": title,
        "date": date,
        "year": date[-4:] if date else "",
        "type": news_type,
        "url": candidate["url"],
        "body": body,
    }


def scrape_iac_press_notes(config: ScraperConfig, verbose: bool = False) -> pd.DataFrame:
    """Low-rate live scraper for the public IAC news archive.

    Live scraping is deliberately opt-in in the public project. The bundled offline fixture
    is the reproducible default and CI never depends on the IAC website.
    """
    session = build_session(config)
    records: list[dict] = []
    seen_urls: set[str] = set()
    reached_target_year = False
    pages_scanned = 0
    target_year_records_seen = 0
    press_note_pages_opened = 0
    stop_reason = "maximum page limit reached"

    for page in range(config.max_pages):
        if verbose:
            print(f"Reading list page {page}...")
        list_url = f"{config.list_url}?page={page}"
        soup = _get_soup(session, list_url, config.timeout_seconds)
        candidates = extract_candidates_from_listing_html(str(soup), config)
        pages_scanned += 1
        if not candidates:
            stop_reason = "empty listing page reached"
            break

        page_years: list[int] = []
        for candidate in candidates:
            if candidate["url"] in seen_urls:
                continue
            seen_urls.add(candidate["url"])
            if candidate["year"].isdigit():
                page_years.append(int(candidate["year"]))
            if candidate["year"] != config.year:
                continue

            reached_target_year = True
            target_year_records_seen += 1
            if not candidate["is_press_note_on_listing"]:
                continue

            press_note_pages_opened += 1
            detail_soup = _get_soup(session, candidate["url"], config.timeout_seconds)
            record = extract_press_note_from_html(str(detail_soup), candidate)
            if record["year"] == config.year and "nota de prensa" in record["type"].lower():
                records.append(record)
                if verbose:
                    print(f"  saved: {record['date']} | {record['title'][:90]}")
            time.sleep(max(0.0, config.delay_seconds))

        if reached_target_year and page_years and max(page_years) < int(config.year):
            stop_reason = f"pages older than {config.year} reached"
            break

    frame = pd.DataFrame(records, columns=["title", "date", "year", "type", "url", "body"])
    frame.attrs.update(
        pages_scanned=pages_scanned,
        unique_urls_seen=len(seen_urls),
        target_year_records_seen=target_year_records_seen,
        press_note_pages_opened=press_note_pages_opened,
        press_notes_saved=len(frame),
        stop_reason=stop_reason,
    )
    return frame
