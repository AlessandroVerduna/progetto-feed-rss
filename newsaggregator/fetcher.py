# Scarica e parsa gli articoli dai feed RSS

import re
import feedparser
from datetime import datetime


def _clean_html(text):
    """Rimuove tutti i tag HTML da una stringa e restituisce testo pulito."""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


def _parse_date(entry):
    """
    Normalizza la data di pubblicazione a stringa YYYY-MM-DD.
    Se la data non è presente o non è leggibile, restituisce 'data sconosciuta'.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
        except Exception:
            pass
    return "data sconosciuta"


def fetch_articles(feeds):
    """
    Scarica gli articoli da una lista di feed RSS.

    Args:
        feeds: lista di dizionari con chiavi 'name' e 'url',
               come restituita da config.get_feeds()

    Returns:
        Lista di dizionari, uno per articolo, con campi:
        title, url, published, summary, feed_name
    """
    all_articles = []

    for feed in feeds:
        print(f"Fetching: {feed['name']}...")
        parsed = feedparser.parse(feed["url"])

        # bozo=True significa che feedparser ha trovato errori nel feed.
        # Se ci sono anche entries le mostriamo comunque; se non ce ne sono
        # il feed è inutilizzabile e lo saltiamo.
        if parsed.bozo and not parsed.entries:
            print(f"  Attenzione: impossibile leggere il feed '{feed['name']}'.")
            continue

        for entry in parsed.entries:
            article = {
                "title":     entry.get("title", "Senza titolo").strip(),
                "url":       entry.get("link", ""),
                "published": _parse_date(entry),
                "summary":   _clean_html(entry.get("summary", "")),
                "feed_name": feed["name"],
            }
            all_articles.append(article)

        print(f"  Trovati {len(parsed.entries)} articoli.")

    return all_articles