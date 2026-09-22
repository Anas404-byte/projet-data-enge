"""
À compléter : ingestion de l'entité `passengers`, découpée en 3 fonctions bronze/silver/gold
(même structure que `ingest_airports.py`, à utiliser comme modèle).
"""
from datetime import date


def ingest_bronze(day: date = None, init: bool = False):
    # TODO : télécharger les deux snapshots (EN et FR) du jour (ou de init/) vers bronze/.
    raise NotImplementedError


def create_silver_table(con):
    # TODO : créer silver_passengers avec un schéma de table UNIQUE
    # + is_active + deleted_date + insert_timestamp/update_timestamp (cf. ingest_airports.py).
    raise NotImplementedError


def ingest_silver(day: date = None, init: bool = False):
    # TODO : chargement de la données dans dans silver_passengers par passenger_id
    raise NotImplementedError


def ingest_gold():
    # TODO : reconstruire la/les table(s) de gold avec les données passengers à partir de silver_passengers
    raise NotImplementedError


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Passagers (init) ingérés.")


if __name__ == "__main__":
    init()
