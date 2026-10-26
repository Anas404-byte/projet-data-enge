"""
À compléter : ingestion de l'entité `flights`, découpée en 3 fonctions bronze/silver/gold
(même structure que `ingest_airports.py`, à utiliser comme modèle).
"""
from datetime import date

from common import fetch_csv, get_connection

FLIGHT_COLS = [
    "flight_number", "airline", "origin_airport_id", "destination_airport_id",
    "flight_date", "departure_time", "arrival_time", "aircraft_type",
]


def _snapshot_file(day: date = None, init: bool = False):
    if init:
        return "init", "flights.csv"
    assert day is not None
    return "2025-09", f"flights_{day.isoformat()}.csv"


def ingest_bronze(day: date = None, init: bool = False):
    """Télécharge le snapshot bronze des vols pour un jour donné ou l'init."""
    subdir, filename = _snapshot_file(day, init)
    fetch_csv(subdir, filename)


def create_silver_table(con):
    # Même colonnes techniques que silver_airports. Contrairement au bronze (tout en texte),
    # on type ici les dates/heures : c'est ce qui permettra de calculer la durée en gold.
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_flights (
            flight_id VARCHAR PRIMARY KEY,
            flight_number VARCHAR,
            airline VARCHAR,
            origin_airport_id VARCHAR,
            destination_airport_id VARCHAR,
            flight_date DATE,
            departure_time TIME,
            arrival_time TIME,
            aircraft_type VARCHAR,
            is_active BOOLEAN,
            deleted_date DATE,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)


def ingest_silver(day: date = None, init: bool = False):
    """Relit le snapshot depuis bronze/ et l'upsert dans silver_flights."""
    subdir, filename = _snapshot_file(day, init)
    df = fetch_csv(subdir, filename)  # déjà en cache local : pas de nouveau téléchargement
    snapshot_date = date(2025, 8, 31) if init else day

    con = get_connection()
    create_silver_table(con)
    con.register("snapshot", df)

    # Upsert sur flight_id, comme pour airports. Différence : les vols changent vraiment
    # (horaire, avion, date), donc on ne retouche la ligne que si une valeur a changé ou si
    # elle était désactivée — sinon update_timestamp bougerait chaque jour pour rien et ne
    # dirait plus quand le vol a réellement été modifié.
    set_clause = ", ".join(f"{c} = excluded.{c}" for c in FLIGHT_COLS)
    set_clause += ", is_active = true, deleted_date = NULL, update_timestamp = now()"
    changed = " OR ".join(f"silver_flights.{c} IS DISTINCT FROM excluded.{c}" for c in FLIGHT_COLS)

    con.execute(f"""
        INSERT INTO silver_flights (
            flight_id, {", ".join(FLIGHT_COLS)}, is_active, deleted_date,
            insert_timestamp, update_timestamp
        )
        SELECT
            flight_id, flight_number, airline, origin_airport_id, destination_airport_id,
            CAST(flight_date AS DATE), CAST(departure_time AS TIME), CAST(arrival_time AS TIME),
            aircraft_type, true, NULL, now(), now()
        FROM snapshot
        ON CONFLICT (flight_id) DO UPDATE SET {set_clause}
        WHERE {changed} OR NOT silver_flights.is_active
    """)

    # Vol absent du snapshot du jour = annulé côté source : désactivation, jamais de DELETE
    # (des réservations déjà faites le référencent).
    con.execute(
        """
        UPDATE silver_flights SET is_active = false, deleted_date = ?, update_timestamp = now()
        WHERE is_active = true AND flight_id NOT IN (SELECT flight_id FROM snapshot)
        """,
        [snapshot_date],
    )

    con.unregister("snapshot")
    con.close()


def ingest_gold():
    """Reconstruit dim_flight à partir de l'état courant de silver_flights, avec la durée de vol."""
    con = get_connection()
    # Durée = arrivée - départ, en minutes. Si l'arrivée est avant le départ, le vol atterrit
    # le lendemain (vol de nuit, ~1/4 des vols) : on ajoute 24h. Les heures étant des heures
    # locales sans fuseau horaire, c'est une durée "affichée" (cf. limites, DOCUMENTATION.md).
    con.execute("""
        CREATE OR REPLACE TABLE dim_flight AS
        SELECT
            * EXCLUDE (insert_timestamp, update_timestamp),
            CASE
                WHEN arrival_time < departure_time
                    THEN date_diff('minute', departure_time, arrival_time) + 24 * 60
                ELSE date_diff('minute', departure_time, arrival_time)
            END AS duration_minutes,
            arrival_time < departure_time AS arrives_next_day,
            insert_timestamp,
            update_timestamp
        FROM silver_flights
    """)
    con.close()


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Vols (init) ingérés.")


if __name__ == "__main__":
    init()
