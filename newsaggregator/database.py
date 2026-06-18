# Persistenza su SQLite e query storico ricerche

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "news.db")


def _get_connection():
    """
    Apre e restituisce una connessione al database.
    row_factory = sqlite3.Row permette di accedere alle colonne per nome
    invece che per indice, rendendo il codice più leggibile.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Crea le tabelle se non esistono ancora.
    Va chiamata una volta all'avvio del programma.

    Tabelle:
    - searches:       una riga per ogni ricerca effettuata
    - search_results: gli articoli trovati, collegati alla ricerca tramite search_id
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS searches (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword   TEXT NOT NULL,
            date      TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS search_results (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            search_id INTEGER NOT NULL,
            title     TEXT,
            url       TEXT,
            published TEXT,
            summary   TEXT,
            feed_name TEXT,
            FOREIGN KEY (search_id) REFERENCES searches(id)
        );
    """)
    conn.commit()
    conn.close()


def save_search(keyword, articles):
    """
    Salva una ricerca e i suoi risultati nel database.

    Args:
        keyword:  la keyword cercata
        articles: lista di articoli trovati da search.search_articles()

    Returns:
        L'id della ricerca appena salvata.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO searches (keyword, date, timestamp) VALUES (?, ?, ?)",
        (keyword, date_str, timestamp_str)
    )
    search_id = cursor.lastrowid

    for article in articles:
        cursor.execute("""
            INSERT INTO search_results (search_id, title, url, published, summary, feed_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            search_id,
            article.get("title", ""),
            article.get("url", ""),
            article.get("published", ""),
            article.get("summary", ""),
            article.get("feed_name", ""),
        ))

    conn.commit()
    conn.close()
    return search_id


def get_searches(keyword=None, date=None):
    """
    Restituisce lo storico delle ricerche, con filtri opzionali.

    Args:
        keyword: se fornita, filtra le ricerche che contengono questa parola
        date:    se fornita, filtra per data esatta nel formato YYYY-MM-DD

    Returns:
        Lista di dizionari con i campi di 'searches'.
    """
    conn = _get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM searches WHERE 1=1"
    params = []

    if keyword:
        query += " AND keyword LIKE ?"
        params.append(f"%{keyword}%")
    if date:
        query += " AND date = ?"
        params.append(date)

    query += " ORDER BY timestamp DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_results_by_search_id(search_id):
    """
    Restituisce gli articoli salvati per una ricerca specifica.

    Args:
        search_id: l'id della ricerca (da get_searches)

    Returns:
        Lista di dizionari con i campi di 'search_results'.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM search_results WHERE search_id = ?",
        (search_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]