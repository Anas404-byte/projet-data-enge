"""
Utilitaires partagés par les scripts d'ingestion. `get_connection` est fourni tel quel ;
`fetch_csv` est à vous d'implémenter (cf. TODO)
"""
import os

import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE_DIR = os.path.join(BASE_DIR, "bronze")
DB_PATH = os.path.join(BASE_DIR, "warehouse.duckdb")
RAW_BASE = "https://raw.githubusercontent.com/kevinl75/tp-polytech-dataset/main"


def fetch_csv(subdir: str, filename: str) -> pd.DataFrame:
    """Doit renvoyer le contenu de <subdir>/<filename> sous forme de DataFrame pandas."""
    # TODO : le fichier CSV source est disponible à l'URL f"{RAW_BASE}/{subdir}/{filename}".
    # - S'il n'existe pas déjà en local dans BRONZE_DIR/<subdir>/<filename>, téléchargez-le et
    #   écrivez-le tel quel sur disque à cet emplacement (créez les dossiers nécessaires).
    # - Eviter si possible de le retéléchargez s'il est déjà présent.
    raise NotImplementedError


def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH)
