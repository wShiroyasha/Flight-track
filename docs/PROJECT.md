# Flight Price Tracker

## 1. Project Vision

### Purpose

Build a private flight-price tracking platform that allows users to track a specific flight and monitor how its price changes over time.

The platform should not simply notify users when a price changes. Its long-term goal is to analyze price data and help users decide whether they should buy the flight now or wait.

### Core Idea

A user provides information identifying the flight they want to monitor.

The system then:

1. Retrieves the current price from a flight-data provider.
2. Stores the price in the database.
3. Checks the price periodically.
4. Detects price changes.
5. Builds a historical price record.
6. Notifies the user about important changes.
7. Compare with original price.

### Long-Term Vision

Turn the project into a real product rather than a simple portfolio application.

The final product should provide useful price intelligence while remaining simple enough for ordinary travelers to understand.

## Database migrations

For a new database, run:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

If the database already contains the tables created by the previous application version, mark the old schema as applied, then apply the hardening migration without deleting existing data:

```powershell
.\.venv\Scripts\python.exe -m alembic stamp 0001_initial
.\.venv\Scripts\python.exe -m alembic upgrade head
```

After changing a SQLAlchemy model, generate and apply a migration:

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe the change"
.\.venv\Scripts\python.exe -m alembic upgrade head
```