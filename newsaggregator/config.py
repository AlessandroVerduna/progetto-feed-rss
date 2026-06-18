# Gestione configurazione feed RSS

import json
import os

CONFIG_PATH = os.path.join("data", "config.json")


def _load_config():
    """Carica il file di configurazione. Se non esiste, lo crea vuoto."""
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        return {"feeds": []}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _save_config(config):
    """Salva il dizionario di configurazione su file JSON."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def add_feed(name, url):
    """Aggiunge un feed RSS alla configurazione. Evita duplicati per URL."""
    config = _load_config()
    for feed in config["feeds"]:
        if feed["url"] == url:
            print(f"Il feed '{url}' è già presente.")
            return
    config["feeds"].append({"name": name, "url": url})
    _save_config(config)
    print(f"Feed '{name}' aggiunto.")


def list_feeds():
    """Stampa tutti i feed configurati con il loro indice."""
    config = _load_config()
    if not config["feeds"]:
        print("Nessun feed configurato.")
        return
    for i, feed in enumerate(config["feeds"]):
        print(f"  [{i}] {feed['name']} — {feed['url']}")


def remove_feed(index):
    """Rimuove un feed dalla configurazione tramite il suo indice."""
    config = _load_config()
    if index < 0 or index >= len(config["feeds"]):
        print(f"Indice {index} non valido.")
        return
    removed = config["feeds"].pop(index)
    _save_config(config)
    print(f"Feed '{removed['name']}' rimosso.")


def get_feeds():
    """Restituisce la lista dei feed come lista di dizionari {name, url}."""
    return _load_config()["feeds"]