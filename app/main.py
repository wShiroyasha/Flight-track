from contextlib import asynccontextmanager
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app import models
from app.config import settings
from app.routers import flights, users, auth
from app.services.flight_tracker import refresh_all_flights


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        refresh_all_flights,
        "interval",
        minutes=settings.price_check_interval_minutes,
        id="refresh-flight-prices",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(flights.router)

@app.get("/")
def root():
    return {"message": "Flight Tracker app is running!"}

