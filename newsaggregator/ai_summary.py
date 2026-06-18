# Riassunto articoli tramite API Groq

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _build_prompt(keyword, articles):
    """
    Costruisce il testo da mandare a Groq.
    Concatena titoli e summary degli articoli trovati
    e aggiunge l'istruzione per il riassunto.
    """
    lines = [f"La seguente è una lista di articoli trovati cercando la keyword '{keyword}':\n"]
    for i, article in enumerate(articles, 1):
        lines.append(f"{i}. Titolo: {article['title']}")
        if article.get("summary"):
            lines.append(f"   Descrizione: {article['summary']}")
        lines.append("")
    lines.append("Scrivi un riassunto in italiano di massimo 150 parole che sintetizzi le informazioni principali trovate.")
    return "\n".join(lines)


def summarize(keyword, articles):
    """
    Genera un riassunto degli articoli trovati tramite API Groq.

    Args:
        keyword:  la keyword cercata (usata nel prompt)
        articles: lista di articoli da riassumere

    Returns:
        Stringa con il riassunto generato, oppure None se non è possibile generarlo.
    """
    if not articles:
        print("Nessun articolo trovato, riassunto non generato.")
        return None

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Errore: GROQ_API_KEY non trovata nel file .env")
        return None

    client = Groq(api_key=api_key)
    prompt = _build_prompt(keyword, articles)

    print("Generazione riassunto in corso...")
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
    )

    summary = response.choices[0].message.content.strip()
    return summary