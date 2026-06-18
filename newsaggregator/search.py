# Ricerca per keyword sugli articoli fetchati


def search_articles(articles, keyword):
    """
    Filtra gli articoli che contengono la keyword nel titolo o nel summary.
    La ricerca non è case-sensitive.

    Args:
        articles: lista di dizionari articolo come restituita da fetcher.fetch_articles()
        keyword:  stringa da cercare

    Returns:
        Lista di articoli filtrati che contengono la keyword.
    """
    keyword_lower = keyword.lower()
    results = []

    for article in articles:
        if (keyword_lower in article["title"].lower() or
                keyword_lower in article["summary"].lower()):
            results.append(article)

    return results