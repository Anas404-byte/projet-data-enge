#!/usr/bin/env python3
"""
Générateur de jeu de données 'flight-datasets' pour TP data ingénierie.
Usage: python3 _generate.py
Écrit les fichiers dans init/ et 2025-09/ relativement au script.
"""
import csv
import os
import random
from datetime import date, datetime, timedelta

from faker import Faker

random.seed(42)
fake_en = Faker("en_US")
fake_fr = Faker("fr_FR")
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INIT_DIR = os.path.join(BASE_DIR, "init")
MONTH_DIR = os.path.join(BASE_DIR, "2025-09")
os.makedirs(INIT_DIR, exist_ok=True)
os.makedirs(MONTH_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

REAL_AIRPORTS = [
    ("JFK", "John F. Kennedy International Airport", "New York", "United States"),
    ("LAX", "Los Angeles International Airport", "Los Angeles", "United States"),
    ("ORD", "O'Hare International Airport", "Chicago", "United States"),
    ("ATL", "Hartsfield-Jackson Atlanta International Airport", "Atlanta", "United States"),
    ("DFW", "Dallas/Fort Worth International Airport", "Dallas", "United States"),
    ("DEN", "Denver International Airport", "Denver", "United States"),
    ("SFO", "San Francisco International Airport", "San Francisco", "United States"),
    ("SEA", "Seattle-Tacoma International Airport", "Seattle", "United States"),
    ("LAS", "Harry Reid International Airport", "Las Vegas", "United States"),
    ("MIA", "Miami International Airport", "Miami", "United States"),
    ("IAH", "George Bush Intercontinental Airport", "Houston", "United States"),
    ("PHX", "Phoenix Sky Harbor International Airport", "Phoenix", "United States"),
    ("MSP", "Minneapolis-Saint Paul International Airport", "Minneapolis", "United States"),
    ("BOS", "Logan International Airport", "Boston", "United States"),
    ("EWR", "Newark Liberty International Airport", "Newark", "United States"),
    ("CLT", "Charlotte Douglas International Airport", "Charlotte", "United States"),
    ("YYZ", "Toronto Pearson International Airport", "Toronto", "Canada"),
    ("YVR", "Vancouver International Airport", "Vancouver", "Canada"),
    ("YUL", "Montreal-Trudeau International Airport", "Montreal", "Canada"),
    ("CDG", "Charles de Gaulle Airport", "Paris", "France"),
    ("ORY", "Paris-Orly Airport", "Paris", "France"),
    ("NCE", "Nice Cote d'Azur Airport", "Nice", "France"),
    ("LYS", "Lyon-Saint Exupery Airport", "Lyon", "France"),
    ("LHR", "Heathrow Airport", "London", "United Kingdom"),
    ("LGW", "Gatwick Airport", "London", "United Kingdom"),
    ("MAN", "Manchester Airport", "Manchester", "United Kingdom"),
    ("EDI", "Edinburgh Airport", "Edinburgh", "United Kingdom"),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
    ("MUC", "Munich Airport", "Munich", "Germany"),
    ("BER", "Berlin Brandenburg Airport", "Berlin", "Germany"),
    ("AMS", "Amsterdam Airport Schiphol", "Amsterdam", "Netherlands"),
    ("MAD", "Adolfo Suarez Madrid-Barajas Airport", "Madrid", "Spain"),
    ("BCN", "Barcelona-El Prat Airport", "Barcelona", "Spain"),
    ("FCO", "Leonardo da Vinci-Fiumicino Airport", "Rome", "Italy"),
    ("MXP", "Milan Malpensa Airport", "Milan", "Italy"),
    ("ZRH", "Zurich Airport", "Zurich", "Switzerland"),
    ("GVA", "Geneva Airport", "Geneva", "Switzerland"),
    ("VIE", "Vienna International Airport", "Vienna", "Austria"),
    ("BRU", "Brussels Airport", "Brussels", "Belgium"),
    ("CPH", "Copenhagen Airport", "Copenhagen", "Denmark"),
    ("ARN", "Stockholm Arlanda Airport", "Stockholm", "Sweden"),
    ("OSL", "Oslo Airport", "Oslo", "Norway"),
    ("HEL", "Helsinki Airport", "Helsinki", "Finland"),
    ("WAW", "Warsaw Chopin Airport", "Warsaw", "Poland"),
    ("PRG", "Vaclav Havel Airport Prague", "Prague", "Czech Republic"),
    ("BUD", "Budapest Ferenc Liszt International Airport", "Budapest", "Hungary"),
    ("ATH", "Athens International Airport", "Athens", "Greece"),
    ("LIS", "Humberto Delgado Airport", "Lisbon", "Portugal"),
    ("DUB", "Dublin Airport", "Dublin", "Ireland"),
    ("IST", "Istanbul Airport", "Istanbul", "Turkey"),
    ("DXB", "Dubai International Airport", "Dubai", "United Arab Emirates"),
    ("AUH", "Zayed International Airport", "Abu Dhabi", "United Arab Emirates"),
    ("DOH", "Hamad International Airport", "Doha", "Qatar"),
    ("JED", "King Abdulaziz International Airport", "Jeddah", "Saudi Arabia"),
    ("TLV", "Ben Gurion Airport", "Tel Aviv", "Israel"),
    ("CAI", "Cairo International Airport", "Cairo", "Egypt"),
    ("JNB", "OR Tambo International Airport", "Johannesburg", "South Africa"),
    ("NBO", "Jomo Kenyatta International Airport", "Nairobi", "Kenya"),
    ("LOS", "Murtala Muhammed International Airport", "Lagos", "Nigeria"),
    ("DEL", "Indira Gandhi International Airport", "Delhi", "India"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India"),
    ("BLR", "Kempegowda International Airport", "Bangalore", "India"),
    ("MAA", "Chennai International Airport", "Chennai", "India"),
    ("SIN", "Singapore Changi Airport", "Singapore", "Singapore"),
    ("KUL", "Kuala Lumpur International Airport", "Kuala Lumpur", "Malaysia"),
    ("BKK", "Suvarnabhumi Airport", "Bangkok", "Thailand"),
    ("CGK", "Soekarno-Hatta International Airport", "Jakarta", "Indonesia"),
    ("MNL", "Ninoy Aquino International Airport", "Manila", "Philippines"),
    ("HAN", "Noi Bai International Airport", "Hanoi", "Vietnam"),
    ("SGN", "Tan Son Nhat International Airport", "Ho Chi Minh City", "Vietnam"),
    ("HND", "Haneda Airport", "Tokyo", "Japan"),
    ("NRT", "Narita International Airport", "Tokyo", "Japan"),
    ("KIX", "Kansai International Airport", "Osaka", "Japan"),
    ("ICN", "Incheon International Airport", "Seoul", "South Korea"),
    ("PEK", "Beijing Capital International Airport", "Beijing", "China"),
    ("PVG", "Shanghai Pudong International Airport", "Shanghai", "China"),
    ("HKG", "Hong Kong International Airport", "Hong Kong", "Hong Kong"),
    ("TPE", "Taiwan Taoyuan International Airport", "Taipei", "Taiwan"),
    ("SYD", "Sydney Kingsford Smith Airport", "Sydney", "Australia"),
    ("MEL", "Melbourne Airport", "Melbourne", "Australia"),
    ("BNE", "Brisbane Airport", "Brisbane", "Australia"),
    ("AKL", "Auckland Airport", "Auckland", "New Zealand"),
    ("GRU", "Sao Paulo-Guarulhos International Airport", "Sao Paulo", "Brazil"),
    ("GIG", "Rio de Janeiro-Galeao International Airport", "Rio de Janeiro", "Brazil"),
    ("EZE", "Ministro Pistarini International Airport", "Buenos Aires", "Argentina"),
    ("BOG", "El Dorado International Airport", "Bogota", "Colombia"),
    ("MEX", "Mexico City International Airport", "Mexico City", "Mexico"),
]

AIRLINES = [
    "Air France", "Delta Air Lines", "United Airlines", "American Airlines",
    "Lufthansa", "British Airways", "Emirates", "Qatar Airways", "Singapore Airlines",
    "KLM", "Turkish Airlines", "Air Canada", "Qantas", "Cathay Pacific",
    "ANA", "Japan Airlines", "Etihad Airways", "Iberia", "Swiss International Air Lines",
    "Air China",
]
AIRLINE_CODES = {
    "Air France": "AF", "Delta Air Lines": "DL", "United Airlines": "UA",
    "American Airlines": "AA", "Lufthansa": "LH", "British Airways": "BA",
    "Emirates": "EK", "Qatar Airways": "QR", "Singapore Airlines": "SQ",
    "KLM": "KL", "Turkish Airlines": "TK", "Air Canada": "AC", "Qantas": "QF",
    "Cathay Pacific": "CX", "ANA": "NH", "Japan Airlines": "JL",
    "Etihad Airways": "EY", "Iberia": "IB", "Swiss International Air Lines": "LX",
    "Air China": "CA",
}
AIRCRAFT_TYPES = [
    "Airbus A320", "Airbus A321", "Airbus A330", "Airbus A350", "Airbus A380",
    "Boeing 737-800", "Boeing 737 MAX 8", "Boeing 777-300ER", "Boeing 787-9",
    "Embraer E190",
]
SEAT_CLASSES = ["Economy", "Premium Economy", "Business", "First"]
SEAT_CLASS_WEIGHTS = [65, 18, 13, 4]
CURRENCIES = ["EUR", "USD", "GBP"]
CURRENCY_WEIGHTS = [50, 35, 15]
BOOKING_CHANNELS = ["website", "mobile_app", "travel_agency", "call_center"]
BOOKING_CHANNEL_WEIGHTS = [45, 30, 18, 7]

NATIONALITIES = sorted({c for _, _, _, c in REAL_AIRPORTS} | {
    "Brazil", "Morocco", "Senegal", "Vietnam", "Argentina", "Ireland", "Poland",
})

N_AIRPORTS_INIT = 80
N_FLIGHTS_INIT = 350
N_PASSENGERS_EN_INIT = 900
N_PASSENGERS_FR_INIT = 900
BOOKINGS_PER_DAY_RANGE = (900, 1500)
N_BOOKINGS_INIT = 400

START_DATE = date(2025, 9, 1)
N_DAYS = 30  # September has exactly 30 days -> one folder per month

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

airports = {}          # airport_id -> dict
flights = {}           # flight_id -> dict, includes 'active' bool
passengers_en = {}      # passenger_id -> dict
passengers_fr = {}      # passenger_id -> dict

_airport_seq = 0
_flight_seq = 0
_passenger_seq = 0


def next_airport_id():
    global _airport_seq
    _airport_seq += 1
    return f"A{_airport_seq:03d}"


def next_flight_id():
    global _flight_seq
    _flight_seq += 1
    return f"F{_flight_seq:04d}"


def next_passenger_id():
    global _passenger_seq
    _passenger_seq += 1
    return f"P{_passenger_seq:05d}"


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Init: airports
# ---------------------------------------------------------------------------

airport_pool = REAL_AIRPORTS.copy()
random.shuffle(airport_pool)
for iata, name, city, country in airport_pool[:N_AIRPORTS_INIT]:
    aid = next_airport_id()
    airports[aid] = {
        "airport_id": aid,
        "iata_code": iata,
        "airport_name": name,
        "city": city,
        "country": country,
    }

write_csv(
    os.path.join(INIT_DIR, "airports.csv"),
    ["airport_id", "iata_code", "airport_name", "city", "country"],
    list(airports.values()),
)

# ---------------------------------------------------------------------------
# Init: flights
# ---------------------------------------------------------------------------


def random_time():
    h = random.randint(0, 23)
    m = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    return f"{h:02d}:{m:02d}"


def add_minutes(hhmm, minutes):
    t = datetime.strptime(hhmm, "%H:%M") + timedelta(minutes=minutes)
    return t.strftime("%H:%M")


def make_flight(flight_date):
    airport_ids = list(airports.keys())
    origin, destination = random.sample(airport_ids, 2)
    airline = random.choice(AIRLINES)
    duration_minutes = random.randint(60, 780)
    dep_time = random_time()
    arr_time = add_minutes(dep_time, duration_minutes)
    fid = next_flight_id()
    return {
        "flight_id": fid,
        "flight_number": f"{AIRLINE_CODES[airline]}{random.randint(100, 9899)}",
        "airline": airline,
        "origin_airport_id": origin,
        "destination_airport_id": destination,
        "flight_date": flight_date.isoformat(),
        "departure_time": dep_time,
        "arrival_time": arr_time,
        "aircraft_type": random.choice(AIRCRAFT_TYPES),
    }


for _ in range(N_FLIGHTS_INIT):
    fdate = START_DATE + timedelta(days=random.randint(0, N_DAYS - 1))
    f = make_flight(fdate)
    flights[f["flight_id"]] = f

FLIGHT_FIELDS = [
    "flight_id", "flight_number", "airline", "origin_airport_id",
    "destination_airport_id", "flight_date", "departure_time", "arrival_time",
    "aircraft_type",
]


def flight_row(f):
    return {k: f[k] for k in FLIGHT_FIELDS}


write_csv(
    os.path.join(INIT_DIR, "flights.csv"),
    FLIGHT_FIELDS,
    [flight_row(f) for f in flights.values()],
)

# ---------------------------------------------------------------------------
# Init: passengers (EN / FR, deliberately different schemas)
# ---------------------------------------------------------------------------

EN_FIELDS = [
    "passenger_id", "first_name", "last_name", "gender", "nationality",
    "email", "birth_date", "signup_date",
]
FR_FIELDS = [
    "id_passager", "prenom", "nom", "genre", "nationalite",
    "email", "date_naissance", "date_inscription",
]


def make_passenger_en(creation_date):
    pid = next_passenger_id()
    first = fake_en.first_name()
    last = fake_en.last_name()
    gender = random.choice(["Male", "Female"])
    birth = fake_en.date_of_birth(minimum_age=18, maximum_age=85)
    row = {
        "passenger_id": pid,
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "nationality": random.choice(NATIONALITIES),
        "email": f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{fake_en.free_email_domain()}",
        "birth_date": birth.isoformat(),
        "signup_date": creation_date.isoformat(),
    }
    passengers_en[pid] = row
    return row


def make_passenger_fr(creation_date):
    pid = next_passenger_id()
    prenom = fake_fr.first_name()
    nom = fake_fr.last_name()
    genre = random.choice(["Homme", "Femme"])
    naissance = fake_fr.date_of_birth(minimum_age=18, maximum_age=85)
    row = {
        "id_passager": pid,
        "prenom": prenom,
        "nom": nom,
        "genre": genre,
        "nationalite": random.choice(NATIONALITIES),
        "email": f"{prenom.lower()}.{nom.lower()}{random.randint(1,999)}@{fake_fr.free_email_domain()}",
        "date_naissance": naissance.strftime("%d/%m/%Y"),
        "date_inscription": creation_date.strftime("%d/%m/%Y"),
    }
    passengers_fr[pid] = row
    return row


for _ in range(N_PASSENGERS_EN_INIT):
    make_passenger_en(START_DATE - timedelta(days=random.randint(1, 400)))

for _ in range(N_PASSENGERS_FR_INIT):
    make_passenger_fr(START_DATE - timedelta(days=random.randint(1, 400)))

write_csv(os.path.join(INIT_DIR, "passengers_en.csv"), EN_FIELDS, list(passengers_en.values()))
write_csv(os.path.join(INIT_DIR, "passengers_fr.csv"), FR_FIELDS, list(passengers_fr.values()))

print(f"Init: {len(airports)} airports, {len(flights)} flights, "
      f"{len(passengers_en)} EN passengers, {len(passengers_fr)} FR passengers")

# ---------------------------------------------------------------------------
# Daily simulation: mutate reference data in place, dump a FULL snapshot of each
# file every day (<name>_<date>.csv, same naming pattern as bookings_<date>.csv).
# Change frequency is tuned per file so it stays realistic:
#   - airports barely ever change (a rename/fix or a new airport once in a while)
#   - flights (schedules/routes) churn moderately, several times a week
#   - passengers grow every day, with occasional corrections or closures
# ---------------------------------------------------------------------------

_booking_seq = 0


def next_booking_id():
    global _booking_seq
    _booking_seq += 1
    return f"B{_booking_seq:06d}"


BOOKING_FIELDS = [
    "booking_id", "passenger_id", "flight_id", "airport_id", "seat_class",
    "amount", "currency", "booking_date", "booking_channel",
]


def make_booking(booking_date, flight_ids, passenger_ids):
    flight_id = random.choice(flight_ids)
    seat_class = weighted_choice(SEAT_CLASSES, SEAT_CLASS_WEIGHTS)
    base_amount = {"Economy": 90, "Premium Economy": 220, "Business": 650, "First": 1400}[seat_class]
    return {
        "booking_id": next_booking_id(),
        "passenger_id": random.choice(passenger_ids),
        "flight_id": flight_id,
        "airport_id": flights[flight_id]["origin_airport_id"],
        "seat_class": seat_class,
        "amount": round(base_amount * random.uniform(0.8, 2.2), 2),
        "currency": weighted_choice(CURRENCIES, CURRENCY_WEIGHTS),
        "booking_date": booking_date,
        "booking_channel": weighted_choice(BOOKING_CHANNELS, BOOKING_CHANNEL_WEIGHTS),
    }


# Initial bookings: made in August, before the simulated month, against the initial reference files
init_booking_dates = sorted(
    (START_DATE - timedelta(days=random.randint(1, 31))).isoformat() for _ in range(N_BOOKINGS_INIT)
)
init_booking_rows = [
    make_booking(
        booking_date,
        list(flights.keys()),
        list(passengers_en.keys()) + list(passengers_fr.keys()),
    )
    for booking_date in init_booking_dates
]
write_csv(os.path.join(INIT_DIR, "bookings.csv"), BOOKING_FIELDS, init_booking_rows)
print(f"Init: {len(init_booking_rows)} bookings")


RENAME_SUFFIXES = ["International Airport", "Airport", "Int'l Airport"]

# Airports: very sparse changes -> exactly ~1 update and ~1 addition somewhere
# in the month (random day, but guaranteed to happen so the scenario is visible)
AIRPORT_UPDATE_DAY = random.randrange(N_DAYS)
AIRPORT_ADD_DAY = random.randrange(N_DAYS)

# Flights: a live schedule churns often (several events most weeks)
N_FLIGHT_EVENTS_OPTIONS = [0, 1, 2, 3]
N_FLIGHT_EVENTS_WEIGHTS = [25, 35, 28, 12]
FLIGHT_EVENT_TYPES = ["DELETE", "ADD", "UPDATE"]
FLIGHT_EVENT_WEIGHTS = [32, 40, 28]

# Passengers: frequent signups, rare deletions/corrections
N_NEW_PASSENGER_OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7, 8]
N_NEW_PASSENGER_WEIGHTS = [10, 12, 14, 14, 12, 12, 10, 8, 8]
P_PASSENGER_REMOVE = 0.08   # per language, per day
P_PASSENGER_UPDATE = 0.12   # per language, per day
MIN_PASSENGERS_PER_LANG = 50  # never shrink a language pool below this


def update_random_airport(day_str):
    aid = random.choice(list(airports.keys()))
    a = airports[aid]
    field_changed = weighted_choice(["airport_name", "city"], [70, 30])
    if field_changed == "airport_name":
        base = a["airport_name"].split(" International Airport")[0].split(" Airport")[0]
        a["airport_name"] = f"{base} {random.choice(RENAME_SUFFIXES)}"
    else:
        # simulate a data-quality fix: hyphenation / spacing correction
        if "-" in a["city"]:
            a["city"] = a["city"].replace("-", " ")
        elif " " in a["city"]:
            a["city"] = a["city"].replace(" ", "-", 1)
        else:
            a["city"] = a["city"] + " City"


def add_random_airport():
    unused = [t for t in REAL_AIRPORTS if t[0] not in {v["iata_code"] for v in airports.values()}]
    if not unused:
        return
    iata, name, city, country = random.choice(unused)
    aid = next_airport_id()
    airports[aid] = {"airport_id": aid, "iata_code": iata, "airport_name": name, "city": city, "country": country}


def update_random_flight(current_date):
    fid = random.choice(list(flights.keys()))
    f = flights[fid]
    change = random.choice(["time", "aircraft", "date"])
    if change == "time":
        f["departure_time"] = random_time()
        f["arrival_time"] = add_minutes(f["departure_time"], random.randint(60, 780))
    elif change == "aircraft":
        f["aircraft_type"] = random.choice(AIRCRAFT_TYPES)
    else:
        f["flight_date"] = (current_date + timedelta(days=random.randint(1, 10))).isoformat()


def update_random_passenger_en():
    pid = random.choice(list(passengers_en.keys()))
    p = passengers_en[pid]
    field = random.choice(["email", "nationality", "last_name"])
    if field == "email":
        p["email"] = f"{p['first_name'].lower()}.{p['last_name'].lower()}{random.randint(1,999)}@{fake_en.free_email_domain()}"
    elif field == "nationality":
        p["nationality"] = random.choice(NATIONALITIES)
    else:
        p["last_name"] = fake_en.last_name()


def update_random_passenger_fr():
    pid = random.choice(list(passengers_fr.keys()))
    p = passengers_fr[pid]
    field = random.choice(["email", "nationalite", "nom"])
    if field == "email":
        p["email"] = f"{p['prenom'].lower()}.{p['nom'].lower()}{random.randint(1,999)}@{fake_fr.free_email_domain()}"
    elif field == "nationalite":
        p["nationalite"] = random.choice(NATIONALITIES)
    else:
        p["nom"] = fake_fr.last_name()


log_lines = []

for day_idx in range(N_DAYS):
    current_date = START_DATE + timedelta(days=day_idx)
    day_str = current_date.isoformat()

    # --- Airports: rare update / rare addition --------------------------
    n_airport_updates = n_airport_adds = 0
    if day_idx == AIRPORT_UPDATE_DAY and airports:
        update_random_airport(day_str)
        n_airport_updates = 1
    if day_idx == AIRPORT_ADD_DAY:
        before = len(airports)
        add_random_airport()
        n_airport_adds = len(airports) - before

    # --- Flights: moderate churn (add / update / delete) -----------------
    n_flight_add = n_flight_update = n_flight_delete = 0
    n_flight_events = weighted_choice(N_FLIGHT_EVENTS_OPTIONS, N_FLIGHT_EVENTS_WEIGHTS)
    for _ in range(n_flight_events):
        etype = weighted_choice(FLIGHT_EVENT_TYPES, FLIGHT_EVENT_WEIGHTS)
        if etype == "DELETE" and flights:
            fid = random.choice(list(flights.keys()))
            del flights[fid]
            n_flight_delete += 1
        elif etype == "ADD":
            f = make_flight(current_date + timedelta(days=random.randint(0, 5)))
            flights[f["flight_id"]] = f
            n_flight_add += 1
        elif etype == "UPDATE" and flights:
            update_random_flight(current_date)
            n_flight_update += 1

    # --- Passengers: daily signups + rare removal/correction -------------
    n_new_en = sum(weighted_choice(N_NEW_PASSENGER_OPTIONS, N_NEW_PASSENGER_WEIGHTS) for _ in range(2))
    n_new_fr = sum(weighted_choice(N_NEW_PASSENGER_OPTIONS, N_NEW_PASSENGER_WEIGHTS) for _ in range(2))
    for _ in range(n_new_en):
        make_passenger_en(current_date)
    for _ in range(n_new_fr):
        make_passenger_fr(current_date)

    n_removed_en = n_removed_fr = 0
    if random.random() < P_PASSENGER_REMOVE and len(passengers_en) > MIN_PASSENGERS_PER_LANG:
        del passengers_en[random.choice(list(passengers_en.keys()))]
        n_removed_en = 1
    if random.random() < P_PASSENGER_REMOVE and len(passengers_fr) > MIN_PASSENGERS_PER_LANG:
        del passengers_fr[random.choice(list(passengers_fr.keys()))]
        n_removed_fr = 1

    n_updated_en = n_updated_fr = 0
    if random.random() < P_PASSENGER_UPDATE and passengers_en:
        update_random_passenger_en()
        n_updated_en = 1
    if random.random() < P_PASSENGER_UPDATE and passengers_fr:
        update_random_passenger_fr()
        n_updated_fr = 1

    # --- Bookings, drawn from today's post-change state -------------------
    all_flight_ids = list(flights.keys())
    all_passenger_ids = list(passengers_en.keys()) + list(passengers_fr.keys())

    n_bookings = random.randint(*BOOKINGS_PER_DAY_RANGE)
    booking_rows = [
        make_booking(day_str, all_flight_ids, all_passenger_ids)
        for _ in range(n_bookings)
    ]

    # --- Write the full snapshots + the day's bookings --------------------
    write_csv(os.path.join(MONTH_DIR, f"airports_{day_str}.csv"),
              ["airport_id", "iata_code", "airport_name", "city", "country"], list(airports.values()))
    write_csv(os.path.join(MONTH_DIR, f"flights_{day_str}.csv"),
              FLIGHT_FIELDS, [flight_row(f) for f in flights.values()])
    write_csv(os.path.join(MONTH_DIR, f"passengers_en_{day_str}.csv"), EN_FIELDS, list(passengers_en.values()))
    write_csv(os.path.join(MONTH_DIR, f"passengers_fr_{day_str}.csv"), FR_FIELDS, list(passengers_fr.values()))
    write_csv(os.path.join(MONTH_DIR, f"bookings_{day_str}.csv"), BOOKING_FIELDS, booking_rows)

    log_lines.append(
        f"{day_str}: bookings={len(booking_rows)} "
        f"airports(total={len(airports)},upd={n_airport_updates},add={n_airport_adds}) "
        f"flights(total={len(flights)},add={n_flight_add},upd={n_flight_update},del={n_flight_delete}) "
        f"passengers_en(total={len(passengers_en)},new={n_new_en},rm={n_removed_en},upd={n_updated_en}) "
        f"passengers_fr(total={len(passengers_fr)},new={n_new_fr},rm={n_removed_fr},upd={n_updated_fr})"
    )

print("\n".join(log_lines))

# ---------------------------------------------------------------------------
# Consistency check: re-read every generated file and verify references
# ---------------------------------------------------------------------------


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_consistency():
    errors = []
    seen_booking_ids = set()
    n_bookings = 0

    def check_day(label, airports_rows, flights_rows, en_rows, fr_rows, booking_rows):
        nonlocal n_bookings
        airport_ids = [r["airport_id"] for r in airports_rows]
        flight_ids = [r["flight_id"] for r in flights_rows]
        passenger_ids = [r["passenger_id"] for r in en_rows] + [r["id_passager"] for r in fr_rows]
        for name, ids in (("airports", airport_ids), ("flights", flight_ids), ("passengers", passenger_ids)):
            if len(ids) != len(set(ids)):
                errors.append(f"{label}: duplicate ids in {name}")
        airport_set, passenger_set = set(airport_ids), set(passenger_ids)
        origin = {r["flight_id"]: r["origin_airport_id"] for r in flights_rows}
        for r in flights_rows:
            if r["origin_airport_id"] not in airport_set or r["destination_airport_id"] not in airport_set:
                errors.append(f"{label}: flight {r['flight_id']} references an unknown airport")
            if r["origin_airport_id"] == r["destination_airport_id"]:
                errors.append(f"{label}: flight {r['flight_id']} has identical origin and destination")
        for r in booking_rows:
            n_bookings += 1
            if r["booking_id"] in seen_booking_ids:
                errors.append(f"{label}: duplicate booking_id {r['booking_id']}")
            seen_booking_ids.add(r["booking_id"])
            if r["flight_id"] not in origin:
                errors.append(f"{label}: booking {r['booking_id']} references unknown flight {r['flight_id']}")
            elif origin[r["flight_id"]] != r["airport_id"]:
                errors.append(f"{label}: booking {r['booking_id']} airport_id differs from flight origin")
            if r["passenger_id"] not in passenger_set:
                errors.append(f"{label}: booking {r['booking_id']} references unknown passenger {r['passenger_id']}")

    check_day(
        "init",
        read_csv(os.path.join(INIT_DIR, "airports.csv")),
        read_csv(os.path.join(INIT_DIR, "flights.csv")),
        read_csv(os.path.join(INIT_DIR, "passengers_en.csv")),
        read_csv(os.path.join(INIT_DIR, "passengers_fr.csv")),
        read_csv(os.path.join(INIT_DIR, "bookings.csv")),
    )
    for day_idx in range(N_DAYS):
        d = (START_DATE + timedelta(days=day_idx)).isoformat()
        check_day(
            d,
            read_csv(os.path.join(MONTH_DIR, f"airports_{d}.csv")),
            read_csv(os.path.join(MONTH_DIR, f"flights_{d}.csv")),
            read_csv(os.path.join(MONTH_DIR, f"passengers_en_{d}.csv")),
            read_csv(os.path.join(MONTH_DIR, f"passengers_fr_{d}.csv")),
            read_csv(os.path.join(MONTH_DIR, f"bookings_{d}.csv")),
        )

    print(f"\nConsistency check: {n_bookings} bookings, {len(errors)} error(s)")
    for e in errors[:20]:
        print(" -", e)
    if errors:
        raise SystemExit(1)


check_consistency()
print("\nDone.")
