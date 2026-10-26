"""
À compléter : ingestion de l'entité `bookings`, découpée en 3 fonctions bronze/silver/gold
(même structure que `ingest_airports.py`, à utiliser comme modèle).
"""
from datetime import date

from common import fetch_csv, get_connection


def _snapshot_file(day: date = None, init: bool = False):
    if init:
        return "init", "bookings.csv"
    assert day is not None
    return "2025-09", f"bookings_{day.isoformat()}.csv"


def ingest_bronze(day: date = None, init: bool = False):
    """Télécharge le snapshot bronze de réservations pour un jour donné ou l'init."""
    subdir, filename = _snapshot_file(day, init)
    fetch_csv(subdir, filename)


def create_silver_table(con):
    # Pas de is_active / deleted_date : une réservation est un évènement immuable, elle ne
    # disparaît ni ne change jamais. amount en DECIMAL (montant monétaire, 2 décimales max
    # dans la source) plutôt qu'en DOUBLE pour éviter les erreurs d'arrondi dans les sommes.
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_bookings (
            booking_id VARCHAR PRIMARY KEY,
            passenger_id VARCHAR,
            flight_id VARCHAR,
            airport_id VARCHAR,
            seat_class VARCHAR,
            amount DECIMAL(10, 2),
            currency VARCHAR,
            booking_date DATE,
            booking_channel VARCHAR,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)


def ingest_silver(day: date = None, init: bool = False):
    """Relit le fichier du jour depuis bronze/ et insère ses réservations dans silver_bookings."""
    subdir, filename = _snapshot_file(day, init)
    df = fetch_csv(subdir, filename)  # déjà en cache local : pas de nouveau téléchargement

    con = get_connection()
    create_silver_table(con)
    con.register("daily", df)

    # Insert simple : le fichier ne contient que les réservations du jour (pas de cumul) et
    # une réservation ne change jamais. ON CONFLICT DO NOTHING rend le chargement idempotent :
    # rejouer un jour déjà chargé n'insère aucun doublon et ne retouche aucune ligne.
    con.execute("""
        INSERT INTO silver_bookings
        SELECT
            booking_id, passenger_id, flight_id, airport_id, seat_class,
            CAST(amount AS DECIMAL(10, 2)), currency, CAST(booking_date AS DATE),
            booking_channel, now(), now()
        FROM daily
        ON CONFLICT (booking_id) DO NOTHING
    """)

    # Contrôle d'intégrité référentielle (silver flights/passengers du même jour déjà chargés,
    # cf. run_month.py) : on ne rejette rien, on signale. airport_id doit aussi valoir
    # l'aéroport de départ du vol réservé.
    orphans = con.execute("""
        SELECT
            count(*) FILTER (WHERE f.flight_id IS NULL),
            count(*) FILTER (WHERE p.passenger_id IS NULL),
            count(*) FILTER (WHERE f.flight_id IS NOT NULL AND d.airport_id <> f.origin_airport_id)
        FROM daily d
        LEFT JOIN silver_flights f ON d.flight_id = f.flight_id
        LEFT JOIN silver_passengers p ON d.passenger_id = p.passenger_id
    """).fetchone()
    if any(orphans):
        print(f"[bookings {filename}] vol inconnu: {orphans[0]}, passager inconnu: {orphans[1]}, "
              f"aéroport != départ du vol: {orphans[2]}")

    con.unregister("daily")
    con.close()


def ingest_gold():
    """Reconstruit fact_booking (avec amount_eur) puis l'agrégat de CA journalier par compagnie."""
    con = get_connection()

    # Table de fait : grain = une réservation. INNER JOIN sur dim_currency : les 3 devises
    # de la source y sont toutes, une devise inconnue ferait disparaître la ligne, d'où le
    # contrôle juste après.
    con.execute("""
        CREATE OR REPLACE TABLE fact_booking AS
        SELECT
            b.* EXCLUDE (insert_timestamp, update_timestamp),
            CAST(round(b.amount * c.rate_to_eur, 2) AS DECIMAL(12, 2)) AS amount_eur,
            b.insert_timestamp,
            b.update_timestamp
        FROM silver_bookings b
        JOIN dim_currency c ON b.currency = c.currency
    """)
    missing = con.execute("""
        SELECT (SELECT count(*) FROM silver_bookings) - (SELECT count(*) FROM fact_booking)
    """).fetchone()[0]
    if missing:
        print(f"[fact_booking] {missing} réservation(s) avec une devise absente de dim_currency")

    # Agrégat gold : CA (en EUR) par jour de réservation et par compagnie. Il vit ici parce
    # qu'il ne dépend que de fact_booking (juste reconstruite) et de dim_flight (reconstruite
    # avant dans la boucle gold, cf. ordre de run_month.py). Reconstruit entièrement à chaque
    # passage, comme le reste du gold. Les timestamps techniques sont ceux des réservations
    # agrégées : première et dernière fois qu'une réservation du groupe a été chargée.
    con.execute("""
        CREATE OR REPLACE TABLE agg_revenue_daily_airline AS
        SELECT
            fb.booking_date,
            f.airline,
            count(*) AS nb_bookings,
            sum(fb.amount_eur) AS revenue_eur,
            CAST(round(avg(fb.amount_eur), 2) AS DECIMAL(12, 2)) AS avg_basket_eur,
            min(fb.insert_timestamp) AS insert_timestamp,
            max(fb.update_timestamp) AS update_timestamp
        FROM fact_booking fb
        JOIN dim_flight f ON fb.flight_id = f.flight_id
        GROUP BY fb.booking_date, f.airline
    """)
    con.close()


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Réservations (init) ingérés.")


if __name__ == "__main__":
    init()
