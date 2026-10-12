# 🥗 DietLab
Web application for dieticians : patient tracking, measurements, meal plans and nutritional calculations.
Personnal project to learn and practise backend development in Python. (API, relationnal database, migrations, containerization)
It tries to fill the lack of usability of existing web site and brings more tools to make dieticians life easier.

> ⚠️ **Fictional data only.** This application handles health-related concepts. It does not yet include authentication and must not be publicly exposed with real patient data.

## Why this project ? Motivation
This project was born out of a real-world need. My girlfriend, a certified dietician, often found existing tools, to be lacking in efficiency and user experience.
Faced with interface frustrations and missing features that slowed down her professional workflow. 
My goal is to provide a robust web application specifically for the daily needs of dieticians.

## Features

- **Patients**: creation, modification, deletion, detailed patient profiles
- **Measurements**: weight and height history with measurement dates
- **Comorbidities**: multiple selection from a reference list
- **Meal plans**: multiple plans per patient, numbered, with a name and objective
- **Foods**: database of over 3,400 foods (ANSES Ciqual database), real-time search
- **Nutritional calculations**: macronutrients and micronutrients per food, per time of day, and in total; daily average based on weekly frequency
- **REST API** automatically documented (Swagger)

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic |
| Database | PostgreSQL 16, SQLAlchemy 2 (ORM), Alembic (migrations) |
| Interface | Jinja2 (server-side rendering), HTMX, Bootstrap 5 |
| Containerization | Docker, Docker Compose |

## Architecture

```
DietLab-web/
├── app/
│   ├── models/          # SQLAlchemy models (tables)
│   ├── schemas/         # Pydantic schemas (inputs/outputs)
│   ├── routes/          # REST API (JSON) and HTML views
│   ├── services/        # Business logic (nutritional calculations, DER, age)
│   ├── dependencies/    # FastAPI dependencies (form data parsing)
│   ├── templates/       # Jinja2 templates and HTMX fragments
│   ├── static/          # Static files
│   ├── data/            # Ciqual food CSV
│   ├── database.py      # SQLAlchemy engine and sessions
│   ├── seed_foods.py    # Initial food data loading
│   └── main.py          # FastAPI entry point
├── alembic/             # Database migrations
├── Dockerfile
├── compose.yaml
└── requirements.txt
```

Request flow: `route → dependency/schema (validation) → service (logic) → model (database)`.
HTML views return **fragments** that HTMX inserts into the page without a full reload.

## Data Model

![Database schema](docs/schema-db.png)

Main tables: `patients`, `patient_measurement`, `comorbidities`, `patient_comorbidity`, `foods`, `recipes`, `recipe_food`, `meal_plan`, `meal_plan_food`, `appointments`.

Design decisions:
- Calculable values (BMI, calories) are **not stored**; they are calculated on demand.
- Many-to-many relationships use junction tables with uniqueness constraints.
- Measurements are stored historically to enable progress charts.
- Each plan has a number unique to its patient (unique constraint `patient + number`).

## Quick Start (Docker)

**Prerequisites**: Docker and Docker Compose.

```bash
git clone <repository-url>
cd DietLab-web
cp .env.example .env
```

Open the `.env` file and choose a password:

```env
DB_USER=dietlab_user
DB_PASSWORD=change_me
DB_NAME=dietlab
DB_PORT=5432
```

> Use an alphanumeric password: certain special characters (`@`, `:`, `/`, `#`) break the connection URL.
> If port 5432 on your machine is already in use, change `DB_PORT` (for example, `5433`). This only affects the port exposed on your machine, not the internal operation.

Start the application:

```bash
docker compose up --build
```

At startup, the application:
1. waits for PostgreSQL to be ready;
2. applies migrations (`alembic upgrade head`);
3. loads the food data if the table is empty;
4. starts the server.

| Service | Address |
|---|---|
| Application | http://localhost:8000 |
| API documentation (Swagger) | http://localhost:8000/docs |
| Database (SQL client) | `localhost:<DB_PORT>` |

### Useful Commands

```bash
docker compose up -d           # start in the background
docker compose logs -f server  # follow application logs
docker compose down            # stop (data is preserved)
docker compose down -v         # stop AND delete data ⚠️
```

## Local Development (without containerizing the application)

Run only the database with Docker, and the application in a virtual environment:

```bash
docker compose up -d db

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `app/.env`:

```env
DATABASE_URL=postgresql+psycopg2://dietlab_user:change_me@localhost:5432/dietlab
```

(adjust the username, password, and port to match your `.env` file), then:

```bash
alembic upgrade head
python -m app.seed_foods
uvicorn app.main:app --reload
```

## Migrations

The schema is managed **exclusively** by Alembic.

```bash
alembic revision --autogenerate -m "description of the change"
# review the generated file in alembic/versions/ before applying it
alembic upgrade head
alembic downgrade -1             # undo the last migration
```

For an already populated table, a required column must be added in two stages (nullable column, backfill existing rows, then add the `NOT NULL` constraint).

## Data Source

Nutritional values come from the **Ciqual** food composition database maintained by ANSES (values per 100 g), reduced to the columns used by the application: calories, protein, carbohydrates, fat, calcium, iron, and vitamin C.

## Future Improvements

- Authentication and role management (FastAPI Auth)
- Automated tests (pytest)
- Continuous integration (GitHub Actions)
- Database-managed cascading deletion (`ON DELETE CASCADE`)
- Online deployment
- Recipe and appointment management in the interface