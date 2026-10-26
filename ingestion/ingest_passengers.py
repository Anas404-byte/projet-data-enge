"""
À compléter : ingestion de l'entité `passengers`, découpée en 3 fonctions bronze/silver/gold
(même structure que `ingest_airports.py`, à utiliser comme modèle).
"""
from datetime import date

from common import fetch_csv, get_connection

LANGS = ["en", "fr"]

PASSENGER_COLS = [
    "first_name", "last_name", "gender", "nationality", "email",
    "birth_date", "signup_date", "source_system",
]

# Date à laquelle on calcule l'âge des passagers en gold : dernier jour de données disponible.
AGE_REFERENCE_DATE = date(2025, 9, 30)


def _snapshot_file(lang: str, day: date = None, init: bool = False):
    if init:
        return "init", f"passengers_{lang}.csv"
    assert day is not None
    return "2025-09", f"passengers_{lang}_{day.isoformat()}.csv"


def ingest_bronze(day: date = None, init: bool = False):
    """Télécharge les deux snapshots bronze (EN et FR) des passagers pour un jour donné ou l'init."""
    for lang in LANGS:
        subdir, filename = _snapshot_file(lang, day, init)
        fetch_csv(subdir, filename)


def create_silver_table(con):
    # Schéma unique pour les deux CRM : noms de colonnes EN, genre normalisé en Male/Female,
    # dates typées. source_system garde la trace du CRM d'origine de chaque passager.
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_passengers (
            passenger_id VARCHAR PRIMARY KEY,
            first_name VARCHAR,
            last_name VARCHAR,
            gender VARCHAR,
            nationality VARCHAR,
            email VARCHAR,
            birth_date DATE,
            signup_date DATE,
            source_system VARCHAR,
            is_active BOOLEAN,
            deleted_date DATE,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)


def ingest_silver(day: date = None, init: bool = False):
    """Relit les snapshots EN et FR depuis bronze/, les consolide et les upsert dans silver_passengers."""
    df_en = fetch_csv(*_snapshot_file("en", day, init))
    df_fr = fetch_csv(*_snapshot_file("fr", day, init))
    snapshot_date = date(2025, 8, 31) if init else day

    con = get_connection()
    create_silver_table(con)
    con.register("snapshot_en", df_en)
    con.register("snapshot_fr", df_fr)

    # Consolidation des deux CRM vers le schéma silver : le FR est renommé, son genre traduit
    # et ses dates (DD/MM/YYYY) parsées. Les id ne se chevauchent pas entre les deux sources
    # (séquence globale), un UNION ALL suffit, sans déduplication.
    con.execute("""
        CREATE OR REPLACE TEMP TABLE snapshot AS
        SELECT
            passenger_id, first_name, last_name, gender, nationality, email,
            CAST(birth_date AS DATE) AS birth_date,
            CAST(signup_date AS DATE) AS signup_date,
            'en' AS source_system
        FROM snapshot_en
        UNION ALL
        SELECT
            id_passager, prenom, nom,
            CASE genre WHEN 'Homme' THEN 'Male' WHEN 'Femme' THEN 'Female' END,
            nationalite, email,
            CAST(strptime(date_naissance, '%d/%m/%Y') AS DATE),
            CAST(strptime(date_inscription, '%d/%m/%Y') AS DATE),
            'fr'
        FROM snapshot_fr
    """)

    # Upsert sur passenger_id, avec la même logique que silver_flights : on ne retouche la
    # ligne que si une valeur a changé (corrections d'email, nom, nationalité) ou si elle
    # était désactivée.
    set_clause = ", ".join(f"{c} = excluded.{c}" for c in PASSENGER_COLS)
    set_clause += ", is_active = true, deleted_date = NULL, update_timestamp = now()"
    changed = " OR ".join(f"silver_passengers.{c} IS DISTINCT FROM excluded.{c}" for c in PASSENGER_COLS)

    con.execute(f"""
        INSERT INTO silver_passengers (
            passenger_id, {", ".join(PASSENGER_COLS)}, is_active, deleted_date,
            insert_timestamp, update_timestamp
        )
        SELECT passenger_id, {", ".join(PASSENGER_COLS)}, true, NULL, now(), now()
        FROM snapshot
        ON CONFLICT (passenger_id) DO UPDATE SET {set_clause}
        WHERE {changed} OR NOT silver_passengers.is_active
    """)

    # Passager absent des deux snapshots du jour : supprimé côté CRM, on le désactive
    # (ses réservations passées doivent toujours pointer vers lui).
    con.execute(
        """
        UPDATE silver_passengers SET is_active = false, deleted_date = ?, update_timestamp = now()
        WHERE is_active = true AND passenger_id NOT IN (SELECT passenger_id FROM snapshot)
        """,
        [snapshot_date],
    )

    con.execute("DROP TABLE snapshot")
    con.unregister("snapshot_en")
    con.unregister("snapshot_fr")
    con.close()


def ingest_gold():
    """Reconstruit dim_passenger à partir de l'état courant de silver_passengers, avec l'âge et sa tranche."""
    con = get_connection()
    # L'âge est calculé à une date de référence fixe (fin de la période simulée) et non à
    # current_date : sinon le gold changerait d'un jour à l'autre sans que la donnée change,
    # et rejouer le pipeline plus tard ne redonnerait pas le même résultat.
    con.execute(
        """
        CREATE OR REPLACE TABLE dim_passenger AS
        WITH p AS (
            SELECT *, CAST(date_part('year', age(CAST(? AS DATE), birth_date)) AS INTEGER) AS age
            FROM silver_passengers
        )
        SELECT
            * EXCLUDE (insert_timestamp, update_timestamp),
            CASE
                WHEN age < 18 THEN '0-17'
                WHEN age < 25 THEN '18-24'
                WHEN age < 35 THEN '25-34'
                WHEN age < 50 THEN '35-49'
                WHEN age < 65 THEN '50-64'
                ELSE '65+'
            END AS age_range,
            insert_timestamp,
            update_timestamp
        FROM p
        """,
        [AGE_REFERENCE_DATE],
    )
    con.close()


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Passagers (init) ingérés.")


if __name__ == "__main__":
    init()
