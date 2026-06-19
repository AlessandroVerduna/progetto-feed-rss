# NewsAggregator

Strumento da riga di comando (CLI) scritto in Python che aggrega articoli da feed RSS configurabili, permette di cercarli per keyword, genera riassunti automatici tramite intelligenza artificiale ed esporta i risultati in formato PDF.

Progetto realizzato per il corso di **Programmazione Python** — ITS ICT Piemonte ACA  
Docente: Massimo Papa | Studente: Alessandro Verduna | A.S. 2025/2026

---

## Funzionalità

- Gestione dei feed RSS tramite un file di configurazione JSON
- Download e parsing degli articoli dai feed configurati
- Ricerca per keyword su titolo e descrizione degli articoli
- Generazione di riassunti automatici in italiano tramite API Groq (LLaMA 3)
- Esportazione dei risultati in PDF con ReportLab
- Salvataggio dello storico delle ricerche su database SQLite
- Consultazione dello storico filtrabile per keyword e per data

---

## Struttura del progetto

```
newsaggregator/
│
├── main.py                  # Punto di ingresso: avvia la CLI
├── requirements.txt         # Dipendenze Python del progetto
├── .env                     # Chiave API Groq (non versionato)
├── .gitignore
│
├── newsaggregator/          # Package principale
│   ├── __init__.py
│   ├── config.py            # Gestione feed RSS (aggiunta, lista, rimozione)
│   ├── fetcher.py           # Download e parsing degli articoli RSS
│   ├── search.py            # Ricerca per keyword sugli articoli
│   ├── database.py          # Persistenza su SQLite e query sullo storico
│   ├── ai_summary.py        # Riassunto automatico tramite API Groq
│   ├── exporter.py          # Generazione report PDF con ReportLab
│   └── cli.py               # Interfaccia a riga di comando con argparse
│
├── data/                    # Generata automaticamente, non versionata
│   ├── config.json          # Feed RSS configurati dall'utente
│   └── news.db              # Database SQLite con lo storico
│
└── output/                  # Generata automaticamente, non versionata
    └── *.pdf                # Report PDF esportati
```

---

## Requisiti

- Python 3.10 o superiore
- Una chiave API Groq (gratuita, ottenibile su [console.groq.com](https://console.groq.com))
- Le librerie elencate in `requirements.txt`

---

## Installazione

**1. Clona il repository**

```bash
git clone https://github.com/tuo-utente/newsaggregator.git
cd newsaggregator
```

**2. Installa le dipendenze**

```bash
pip install -r requirements.txt
```

**3. Configura la chiave API**

Crea un file `.env` nella cartella radice del progetto con il seguente contenuto:

```
GROQ_API_KEY=la_tua_chiave_api
```

La chiave API si ottiene gratuitamente registrandosi su [console.groq.com](https://console.groq.com). Il tier gratuito è ampiamente sufficiente per l'utilizzo normale del programma.

---

## Utilizzo

Tutti i comandi si eseguono dalla cartella radice del progetto con:

```bash
python main.py <comando>
```

### Gestione dei feed RSS

```bash
# Aggiungere un feed
python main.py config add "Repubblica" "https://www.repubblica.it/rss/homepage/rss2.0.xml"

# Visualizzare i feed configurati
python main.py config list

# Rimuovere un feed tramite il suo indice
python main.py config remove 0
```

### Ricerca articoli

```bash
# Cercare articoli per keyword (solo visualizzazione)
python main.py fetch "intelligenza artificiale"

# Cercare e salvare: genera riassunto AI, salva nel database ed esporta PDF
python main.py fetch "intelligenza artificiale" --save
```

### Storico delle ricerche

```bash
# Visualizzare tutte le ricerche effettuate
python main.py history

# Filtrare per keyword
python main.py history --keyword "clima"

# Filtrare per data
python main.py history --date 2025-06-15

# Combinare i filtri
python main.py history --keyword "clima" --date 2025-06-15
```

---

## Scelte tecnologiche e architetturali

### Architettura a moduli separati

Il progetto è suddiviso in moduli con responsabilità ben distinte: `config`, `fetcher`, `search`, `database`, `ai_summary`, `exporter` e `cli`. Questo approccio — noto come _separation of concerns_ — rende il codice più leggibile, testabile e manutenibile: ogni modulo può essere modificato senza impattare gli altri.

### feedparser per il parsing RSS

La libreria `feedparser` gestisce in modo trasparente le differenze tra i vari formati di feed esistenti (RSS 2.0, Atom, ecc.) e i feed malformati. Senza di essa, ogni feed richiederebbe un parsing XML manuale, molto più fragile.

### Groq con modello LLaMA 3

In fase di progettazione era previsto l'utilizzo delle API Google Gemini. Durante lo sviluppo si è scelto di passare a **Groq**, che offre inferenza estremamente rapida su modelli open-source come LLaMA 3. La scelta è stata guidata dalla semplicità di integrazione, dalla velocità di risposta e dalla disponibilità di un tier gratuito generoso, senza necessità di carta di credito.

### SQLite per la persistenza

Il database SQLite è integrato nella libreria standard di Python (modulo `sqlite3`) e non richiede l'installazione di un server esterno. Per un'applicazione locale monoutente come questa è la scelta ideale: semplice da configurare, portabile e più robusta di un semplice file JSON per la gestione di dati strutturati e query complesse.

### ReportLab per l'esportazione PDF

`ReportLab` è la libreria Python più consolidata per la generazione programmatica di PDF. Permette un controllo preciso sulla tipografia e sul layout senza dipendere da strumenti esterni come LibreOffice o wkhtmltopdf.

### argparse per la CLI

`argparse` è parte della libreria standard di Python e permette di costruire interfacce a riga di comando con sottocomandi (`config`, `fetch`, `history`), argomenti posizionali e flag opzionali (`--save`, `--keyword`, `--date`) in modo strutturato e con messaggi di aiuto generati automaticamente.

### python-dotenv per la gestione dei segreti

La chiave API viene caricata da un file `.env` tramite `python-dotenv`, tenendola separata dal codice sorgente. Il file `.env` è escluso dal versionamento tramite `.gitignore`, evitando di esporre credenziali nel repository.
