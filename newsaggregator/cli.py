# Interfaccia a riga di comando (argparse)

import argparse
from datetime import datetime

from newsaggregator import config, fetcher, search, database, ai_summary, exporter


def _ask_selection(results):
    raw = input("Seleziona gli articoli da salvare (es: 1 3 5), 'tutti', o invio per annullare: ").strip()

    if raw == "":
        return None

    if raw.lower() == "tutti":
        return results

    try:
        indices = [int(x) for x in raw.split()]
    except ValueError:
        print("Input non valido.")
        return None

    if not all(1 <= i <= len(results) for i in indices):
        print("Input non valido.")
        return None

    return [results[i - 1] for i in indices]


def handle_config(args):
    """Gestisce i sottocomandi di 'config'."""
    if args.config_command == "add":
        config.add_feed(args.name, args.url)
    elif args.config_command == "list":
        config.list_feeds()
    elif args.config_command == "remove":
        config.remove_feed(args.index)
    else:
        print("Comando config non riconosciuto. Usa: add, list, remove")

def handle_commands(args):
    """Stampa la lista di tutti i comandi disponibili con una breve descrizione."""
    print("""
Comandi disponibili — NewsAggregator
=====================================

  python main.py commands
      Mostra questa lista di comandi.

  python main.py config add <nome> <url>
      Aggiunge un feed RSS con il nome e l'URL specificati.

  python main.py config list
      Mostra tutti i feed RSS configurati.

  python main.py config remove <indice>
      Rimuove il feed RSS all'indice specificato (vedi 'config list').

  python main.py fetch <keyword>
      Scarica gli articoli dai feed configurati e filtra per keyword.

  python main.py fetch <keyword> --save
      Come sopra, ma salva i risultati nel database,
      genera un riassunto AI e produce un PDF nella cartella output/.

  python main.py history
      Mostra lo storico di tutte le ricerche effettuate.

  python main.py history --keyword <keyword>
      Filtra lo storico per keyword.

  python main.py history --date <YYYY-MM-DD>
      Filtra lo storico per data.

  python main.py history --keyword <keyword> --date <YYYY-MM-DD>
      Combina i due filtri.
""")

def handle_fetch(args):
    feeds = config.get_feeds()
    if not feeds:
        print("Nessun feed configurato. Aggiungine uno con: python main.py config add <nome> <url>")
        return

    articles = fetcher.fetch_articles(feeds)
    if not articles:
        print("Nessun articolo recuperato.")
        return

    results = search.search_articles(articles, args.keyword)

    if not results:
        print(f"\nNessun articolo trovato per la keyword '{args.keyword}'.")
        return

    print(f"\nTrovati {len(results)} articoli per '{args.keyword}':\n")
    for i, article in enumerate(results, 1):
        print(f"  [{i}] {article['title']}")
        print(f"       {article['feed_name']} | {article['published']}")
        print(f"       {article['url']}")
        print()

    if args.save:
        selected = _ask_selection(results)
        if selected is None:
            print("Selezione annullata.")
            return

        summary = ai_summary.summarize(args.keyword, selected)
        if summary:
            print(f"\nRiassunto AI:\n{summary}\n")

        today = datetime.now().strftime("%Y-%m-%d")
        search_id = database.save_search(args.keyword, selected)
        print(f"Ricerca salvata nel database (id={search_id}).")

        exporter.export_pdf(args.keyword, today, summary, selected)


def handle_history(args):
    searches = database.get_searches(keyword=args.keyword, date=args.date)

    if not searches:
        print("Nessuna ricerca trovata.")
        return

    print(f"\nStorico ricerche ({len(searches)} trovate):\n")
    for s in searches:
        print(f"  [id={s['id']}] '{s['keyword']}' — {s['timestamp']}")

    if args.keyword or args.date:
        print()
        for s in searches:
            results = database.get_results_by_search_id(s["id"])
            print(f"  Ricerca '{s['keyword']}' del {s['date']} — {len(results)} articoli:")
            for article in results:
                print(f"    - {article['title']} ({article['feed_name']})")
            print()


def main():
    database.init_db()

    parser = argparse.ArgumentParser(
        prog="newsaggregator",
        description="Aggregatore di feed RSS con ricerca e riassunto AI"
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- config ---
    config_parser = subparsers.add_parser("config", help="Gestisci i feed RSS")
    config_sub = config_parser.add_subparsers(dest="config_command")

    add_parser = config_sub.add_parser("add", help="Aggiungi un feed")
    add_parser.add_argument("name", help="Nome del feed")
    add_parser.add_argument("url", help="URL del feed RSS")

    config_sub.add_parser("list", help="Lista i feed configurati")

    remove_parser = config_sub.add_parser("remove", help="Rimuovi un feed")
    remove_parser.add_argument("index", type=int, help="Indice del feed da rimuovere")

    # --- fetch ---
    fetch_parser = subparsers.add_parser("fetch", help="Scarica articoli e cerca per keyword")
    fetch_parser.add_argument("keyword", help="Keyword da cercare negli articoli")
    fetch_parser.add_argument("--save", action="store_true", help="Salva risultati nel db e genera PDF")

    # --- history ---
    history_parser = subparsers.add_parser("history", help="Consulta lo storico delle ricerche")
    history_parser.add_argument("--keyword", help="Filtra per keyword")
    history_parser.add_argument("--date", help="Filtra per data (YYYY-MM-DD)")

    # --- commands ---
    subparsers.add_parser("commands", help="Mostra la lista di tutti i comandi disponibili")

    args = parser.parse_args()

    if args.command == "config":
        handle_config(args)
    elif args.command == "fetch":
        handle_fetch(args)
    elif args.command == "history":
        handle_history(args)
    elif args.command == "commands":
        handle_commands(args)
    else:
        parser.print_help()