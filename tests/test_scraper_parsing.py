from __future__ import annotations

from iac_matching.scraper import (
    ScraperConfig,
    extract_candidates_from_listing_html,
    extract_press_note_from_html,
)


def test_listing_parser_uses_public_iac_shape_without_network():
    html = """
    <html><body>
      <div class='card'>
        <span>Nota de prensa</span>
        <a href='/es/divulgacion/noticias/example-object'>Example object</a>
        <span>Fecha de publicación 31/07/2024</span>
      </div>
    </body></html>
    """
    rows = extract_candidates_from_listing_html(html, ScraperConfig())
    assert len(rows) == 1
    assert rows[0]["year"] == "2024"
    assert rows[0]["is_press_note_on_listing"] is True
    assert rows[0]["url"].endswith("/es/divulgacion/noticias/example-object")


def test_detail_parser_extracts_title_date_type_and_cuts_related_content():
    candidate = {
        "url": "https://www.iac.es/es/divulgacion/noticias/example-object",
        "listing_title": "Example object",
        "date": "31/07/2024",
    }
    html = """
    <html><head><title>Example object | Instituto de Astrofísica de Canarias</title></head>
    <body><main>
      <h1>Example object</h1>
      <p>Fecha de publicación 31/07/2024</p>
      <p>Scientific text. Article: Example Paper Title.</p>
      <p>Tipo de noticia Nota de prensa Astrofísica</p>
      <p>Noticias relacionadas This text must not remain.</p>
    </main></body></html>
    """
    row = extract_press_note_from_html(html, candidate)
    assert row["title"] == "Example object"
    assert row["date"] == "31/07/2024"
    assert "Nota de prensa" in row["type"]
    assert "Noticias relacionadas" not in row["body"]
