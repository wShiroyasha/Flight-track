# Flight Tracker

A FastAPI service for tracking flight prices over time. Users can save a flight, record its current price, and let the application refresh tracked prices on a schedule.

## What it includes

- User registration and password hashing
- OAuth2 password login with bearer tokens
- Flight searches through SerpApi Google Flights
- PostgreSQL storage with SQLAlchemy
- Alembic database migrations
- Automatic price refresh with a background scheduler
- Price history for tracked flights

## Requirements

- Python 3.11 or newer
- PostgreSQL
- A SerpApi account and API key for flight searches

## Setup on Windows

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root with the database and authentication settings:

```env
DATABASE_HOSTNAME=your-database-host
DATABASE_PORT=5432
DATABASE_USERNAME=your-database-username
DATABASE_PASSWORD=your-database-password
DATABASE_NAME=flight_tracker

SECRET_KEY=replace-with-a-long-random-value
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

SERPAPI_KEY=your-serpapi-key
PRICE_CHECK_INTERVAL_MINUTES=60
```

For a PostgreSQL server running on your own computer, use `localhost` as the database host.

The database must exist before running the migrations. For example, in `psql`:

```sql
CREATE DATABASE flight_tracker;
```

Apply the schema:

```powershell
python -m alembic upgrade head
```

Start the development server:

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Existing database

If the database was created by the previous application version, preserve its data and apply the hardening migration:

```powershell
python -m alembic stamp 0001_initial
python -m alembic upgrade head
```

## API endpoints

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/` | No | Health check |
| `POST` | `/users` | No | Create a user |
| `POST` | `/login` | No | Obtain a bearer access token |
| `POST` | `/flights/track` | Bearer token | Search for and save a flight |
| `DELETE` | `/flights/{flight_id}` | Bearer token | Delete one of the current user's flights |

For `/login`, send form fields named `username` and `password`. The username is the registered email address.

## Project layout

```text
app/
  main.py                 FastAPI application and scheduled refresh job
  config.py               Environment-backed settings
  database.py             PostgreSQL engine and session setup
  models.py               SQLAlchemy models
  schemas.py              Pydantic request and response schemas
  routers/                Authentication, user, and flight endpoints
  services/               Flight provider and price refresh logic
migrations/               Alembic migrations
docs/                     Project notes
```

## Database changes

After changing a SQLAlchemy model, create and apply a migration:

```powershell
python -m alembic revision --autogenerate -m "describe the change"
python -m alembic upgrade head
```

The scheduler starts with the application and runs a price refresh immediately, then repeats according to `PRICE_CHECK_INTERVAL_MINUTES`.
