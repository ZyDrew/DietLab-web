# 🥗 DietLab
Web application for dietitians: patient tracking, measurements, meal plans and nutritional calculations.
Personal project to learn and practise backend development in Python (API, relational database, migrations, containerization).
It tries to fill the lack of usability of existing websites and brings more tools to make dietitians' lives easier.


> ⚠️ **Fictional data only.** This application handles health-related concepts. Authentication and CSRF protection are implemented, but the application is not production-ready and must remain fictional-data only until production hardening is complete.

## Why this project ? Motivation
This project was born out of a real-world need. My girlfriend, a certified dietitian, often found existing tools to be lacking in efficiency and user experience.
Faced with interface frustrations and missing features that slowed down her professional workflow.
My goal is to provide a robust web application specifically for the daily needs of dietitians.

## Features

- **Patients**: creation, modification, deletion, detailed patient profiles
- **Measurements**: weight and height history with measurement dates
- **Comorbidities**: multiple selection from a reference list
- **Meal plans**: multiple plans per patient, numbered, with a name and objective
- **Foods**: database of over 3,400 foods (ANSES Ciqual database), real-time search
- **Nutritional calculations**: macronutrients and micronutrients per food, per time of day, and in total; daily average based on weekly frequency
- **REST API** documented with Swagger (development only; must be disabled before production)
- **Authentication**: login/logout, Argon2id password hashing, PostgreSQL-backed sessions, CSRF protection and error pages

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic |
| Database | PostgreSQL 16, SQLAlchemy 2 (ORM), Alembic (migrations) |
| Security | Server-side sessions (opaque token, SHA-256 hash), Argon2id (`pwdlib[argon2]`), CSRF synchronizer token |
| Interface | Jinja2 (server-side rendering), HTMX, Bootstrap 5 |
| Containerization | Docker, Docker Compose |
| Tests | pytest, FastAPI `TestClient` |

## Architecture

```
DietLab-web/
├── app/
│   ├── models/          # SQLAlchemy models (tables)
│   ├── schemas/         # Pydantic schemas (inputs/outputs)
│   ├── routes/          # REST API (JSON), HTML views and auth/error routes
│   ├── services/        # Business logic (nutrition, DER, age), auth, sessions, helpers
│   ├── dependencies/    # FastAPI dependencies (forms, authentication, CSRF)
│   ├── templates/       # Jinja2 templates, fragments and error pages
│   ├── static/          # Static files
│   ├── data/            # Ciqual food CSV
│   ├── database.py      # SQLAlchemy engine and sessions
│   ├── cli.py           # Admin commands (users, password, session purge)
│   ├── errors.py        # App-specific errors and exception handlers
│   ├── templating.py    # Jinja2Templates instance
│   ├── seed_foods.py    # Initial food data loading
│   ├── seed_demo.py     # Fictional demo data (development only)
│   └── main.py          # FastAPI entry point
├── alembic/             # Database migrations
├── tests/               # pytest suite
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

Request flow: `route → dependency/schema (validation) → service (logic) → model (database)`.
HTML views return **fragments** that HTMX inserts into the page without a full reload.

## Data Model

![Database schema](docs/schema-db.png)

Main tables: `patients`, `patient_measurement`, `comorbidities`, `patient_comorbidity`, `foods`, `recipes`, `recipe_food`, `meal_plan`, `meal_plan_food`, `appointments`, `users`, `user_sessions`.

Design decisions:
- Calculable values (BMI, calories) are **not stored**; they are calculated on demand.
- Many-to-many relationships use junction tables with uniqueness constraints.
- Measurements are stored historically to enable progress charts.
- Each plan has a number unique to its patient (unique constraint `patient + number`).
- Only a SHA-256 hash of each session token is stored in `user_sessions`.

## Security

- **Single account, no registration and no roles.** Accounts are created and changed only through `app.cli` (`create-user`, `set-password`).
- **Passwords** are hashed with Argon2id (`pwdlib[argon2]`). Login failures return one generic message and do not reveal whether the email exists.
- **Sessions** are stored server-side in PostgreSQL as opaque tokens; only their SHA-256 hash is kept. Expiry is 8 hours idle and 7 days absolute.
- **The cookie** `dietlab_session` is `HttpOnly`, `SameSite=Lax`, `Path=/`, 7-day `Max-Age`, and `Secure` when `COOKIE_SECURE=true`.
- **Protected routes:** every route except `/login`, `/logout`, `/static` and `/error/*` requires a session. Anonymous HTML requests redirect to `/login?next=...`; HTMX requests get `401` with `HX-Redirect`; `/api` returns JSON `401`.
- **CSRF:** state-changing HTML views require a synchronizer token bound to the session, sent by HTMX in the `X-CSRF-Token` header and by the logout form in a hidden field. The JSON API is session-protected but CSRF-exempt because it is development-only.
- **Errors:** `403`, `404` and `500` return the real status and a full page. `500` responses never contain a traceback. SQL echo is off by default and SQLAlchemy hides bind parameters in exceptions, so logs do not contain emails, patient data or secrets.

These controls cover authentication; they do not make the application production-ready. Login throttling, security headers, HTTPS, disabling `/docs` and `/api`, backups and monitoring are still required (see Future Improvements).

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
4. loads the fictional demo data (`seed_demo.py` — development and demonstration only);
5. starts the server.

Create the first user account (there is no registration page):

```bash
docker compose exec server python -m app.cli create-user
```

| Service | Address |
|---|---|
| Application | http://localhost:8000 |
| API documentation (Swagger, development only) | http://localhost:8000/docs |
| Database (SQL client) | `localhost:<DB_PORT>` |

### Useful Commands

```bash
docker compose up -d           # start in the background
docker compose logs -f server  # follow application logs
docker compose down            # stop (data is preserved)
docker compose down -v         # stop AND delete data ⚠️
```

Administration commands (run inside the `server` container):

```bash
python -m app.cli create-user                 # create an account
python -m app.cli set-password <email>        # change a password and revoke all sessions
python -m app.cli purge-sessions              # delete expired sessions (no user argument)
python -m app.cli purge-sessions -d           # same, with the full traceback (local debugging)
```

`purge-sessions` is a maintenance job: it removes only rows whose absolute or idle expiry has passed. It is safe to run on a schedule and never logs out an active user.

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
COOKIE_SECURE=false
SQL_ECHO=false
```

(adjust the username, password, and port to match your `.env` file), then:

```bash
alembic upgrade head
python -m app.seed_foods
python -m app.seed_demo        # optional: fictional demo data, development only
python -m app.cli create-user  # required before the first login
uvicorn app.main:app --reload
```

For a local HTTP server, keep `COOKIE_SECURE=false`; a `Secure` cookie is only sent over HTTPS. Set it to `true` behind HTTPS.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

The suite covers authentication and session lifecycle, CSRF, authentication guards, error pages, food search and the meal plan API. It runs against the configured PostgreSQL database and rolls back every test.

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

- **Production readiness**: login throttling/lockout, security headers, HTTPS, per-environment configuration, disabling `/docs`, `/redoc`, `/openapi.json` and `/api`, removing `seed_demo` from the production startup, password-change UI and a `/health` endpoint.
- **Operations**: continuous integration (GitHub Actions), managed PostgreSQL, automated backups with a tested restore, monitoring and deployment.
- **Data**: a better food data source than Ciqual (licence, coverage, micronutrients, handling of unknown values).
- **Features**: recipes in the interface, foods/recipes pages, patient search, editing and removing foods inside a meal plan, PDF export, measurement charts, energy needs with the NAP.
- Database-managed cascading deletion (`ON DELETE CASCADE`) instead of manual child deletion.
- Better UI.