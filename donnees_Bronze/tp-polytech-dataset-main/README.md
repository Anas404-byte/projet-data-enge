# Flight datasets — jeu de données pour TP data ingénierie

Jeu de données synthétique inspiré du dépôt
[data-engineering-practice-datasets/flightbooking](https://github.com/swapniltake1/data-engineering-practice-datasets/tree/main/flightbooking),
généré par [`_generate.py`](_generate.py) (seed fixe = reproductible).

## Arborescence

```
flight-datasets/
├── init/                          # état de départ, avant le mois simulé (jusqu'au 2025-08-31)
│   ├── airports.csv
│   ├── flights.csv
│   ├── passengers_en.csv
│   ├── passengers_fr.csv
│   └── bookings.csv
└── 2025-09/                       # 1 dossier par mois, fichiers journaliers à l'intérieur
    ├── airports_2025-09-01.csv
    ├── flights_2025-09-01.csv
    ├── passengers_en_2025-09-01.csv
    ├── passengers_fr_2025-09-01.csv
    ├── bookings_2025-09-01.csv
    └── ... (x30 jours, 2025-09-01 → 2025-09-30 — 5 fichiers/jour, 150 au total)
```

**155 fichiers CSV** au total (5 dans `init/` + 150 dans `2025-09/`).

Les fichiers `airports`, `flights`, `passengers_en` et `passengers_fr` sont des **extraits
complets** : chaque fichier journalier contient toutes les lignes existantes à la fin de la
journée, avec les changements du jour déjà appliqués. Il n'y a aucune colonne indiquant le type de
changement — c'est volontaire : dans beaucoup de systèmes sources réels, on ne reçoit qu'un export
complet quotidien. Pour détecter ce qui a changé, il faut **comparer le fichier du jour J avec celui
du jour J-1** (ou avec `init/` pour le 1er jour) : lignes apparues, lignes disparues, lignes dont le
contenu a changé (même clé, valeurs différentes).

Les fichiers `bookings_<date>.csv` contiennent uniquement les réservations effectuées ce jour-là
(pas de cumul). `init/bookings.csv` contient les 400 réservations d'août 2025.

## Contenu de `init/`

### `airports.csv` (80 lignes)
Aéroports réels (code IATA, nom, ville, pays).
`airport_id, iata_code, airport_name, city, country`

### `flights.csv` (350 lignes)
`flight_id, flight_number, airline, origin_airport_id, destination_airport_id, flight_date, departure_time, arrival_time, aircraft_type`
`origin_airport_id` / `destination_airport_id` référencent `airports.airport_id`.

### `passengers_en.csv` / `passengers_fr.csv` (900 lignes chacun)
Volontairement **deux schémas différents** pour simuler deux systèmes sources (un CRM anglophone,
un CRM francophone) à consolider :

| EN                  | FR                  | Piège                                    |
|---------------------|---------------------|-------------------------------------------|
| `passenger_id`      | `id_passager`       | nom de colonne différent                  |
| `first_name`        | `prenom`            | nom de colonne différent                  |
| `last_name`         | `nom`               | nom de colonne différent                  |
| `gender` (Male/Female) | `genre` (Homme/Femme) | valeurs catégorielles différentes    |
| `nationality`       | `nationalite`       | nom de colonne différent                  |
| `birth_date` (`YYYY-MM-DD`) | `date_naissance` (`DD/MM/YYYY`) | format de date différent |
| `signup_date` (`YYYY-MM-DD`) | `date_inscription` (`DD/MM/YYYY`) | format de date différent |

Les `passenger_id` sont uniques et non chevauchants entre les deux fichiers (une seule séquence
globale), donc la consolidation porte sur le schéma/format, pas sur la déduplication d'ID.

### `bookings.csv` (400 lignes)
`booking_id, passenger_id, flight_id, airport_id, seat_class, amount, currency, booking_date, booking_channel`

Réservations d'août 2025 (`booking_date` entre le 2025-08-01 et le 2025-08-31). Les
`passenger_id`, `flight_id` et `airport_id` référencent les fichiers d'`init/`. `airport_id` est
l'aéroport de départ du vol réservé : il est toujours égal à l'`origin_airport_id` du `flight_id`
correspondant. Les `booking_id` continuent ensuite dans les fichiers journaliers de septembre
(`B000201` et suivants).

## Contenu de `2025-09/`

### `bookings_YYYY-MM-DD.csv` (900 à 1 500 lignes/jour, ~36 000 au total sur le mois)
Mêmes colonnes que `init/bookings.csv` (`airport_id` = `origin_airport_id` du vol réservé). Chaque
réservation référence un `flight_id`, un `passenger_id` et un `airport_id` présents dans les
fichiers du même jour (cohérence vérifiée sur l'ensemble du jeu de données, 0 erreur).

### `airports_YYYY-MM-DD.csv` — très peu de changements
Sur les 30 jours : **une seule modification** (nom ou ville corrigé, `airport_id` inchangé) et
**un seul ajout** (nouvel `airport_id`), chacun un jour aléatoire du mois. Aucune suppression.

### `flights_YYYY-MM-DD.csv` — changements fréquents
Chaque jour, un nombre aléatoire d'événements (0 à 3) parmi : ajout d'un vol, modification
(horaire, avion ou date changés, même `flight_id`) et suppression (le vol disparaît simplement du
fichier à partir de ce jour). Le nombre total de vols oscille légèrement au fil du mois.

### `passengers_en_YYYY-MM-DD.csv` / `passengers_fr_YYYY-MM-DD.csv` — croissance quotidienne
0 à 16 nouveaux passagers par langue et par jour, plus occasionnellement une correction sur un
passager existant (email, nom ou nationalité — même id) et, plus rarement, une suppression (l'id
disparaît du fichier).

La fréquence des changements est volontairement différente selon le fichier (aéroports quasi
figés, vols qui changent souvent, passagers en croissance continue) pour rester réaliste.

## Pistes d'exercices

- Analyser les fichiers (clés, granularité, fréquence de changement, volumétrie) pour concevoir le
  modèle de données cible : quels fichiers représentent des événements, lesquels du contexte qui
  évolue, et comment chacun doit être chargé (ajout simple, écrasement, historisation…).
- Consolider les passagers EN + FR en un schéma unique (noms de colonnes, formats de date, valeurs
  de genre normalisés), pour un jour donné puis sur toute la période.
- Détecter les changements entre deux jours consécutifs (lignes apparues, disparues, modifiées) et
  décider comment les conserver dans le temps.
- Charger les bookings en contrôlant que chaque `passenger_id`, `flight_id` et `airport_id`
  référencé existe bien dans les fichiers du même jour.
- Agréger le montant (`amount`) par mois, par compagnie, par classe de cabine, par devise
  (attention : 3 devises différentes, pas de conversion fournie — à faire ou à assumer comme
  limite connue).

## Régénérer les données

```bash
pip install faker
python3 _generate.py
```

Seed fixe (`random.seed(42)`, `Faker.seed(42)`) : la régénération produit exactement le même jeu
de données. À la fin de la génération, le script relit tous les fichiers et vérifie la cohérence
(ids uniques, références existantes dans les fichiers du même jour, `airport_id` = départ du vol,
`booking_id` uniques) ; il s'arrête avec un code d'erreur si un problème est détecté.
