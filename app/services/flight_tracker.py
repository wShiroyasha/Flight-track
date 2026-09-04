import logging
from datetime import datetime, timezone

from sqlalchemy import select

from .. import models
from ..database import SessionLocal
from .flight_provider import search_flight

logger = logging.getLogger(__name__)


def refresh_flight(db, flight: models.Flight) -> float:
    """Refresh one tracked flight and append a price-history record."""
    offer = search_flight(
        flight.origin,
        flight.destination,
        flight.outbound_departure.date(),
        flight.return_departure.date() if flight.return_departure else None,
    )
    previous_price = flight.current_price
    flight.current_price = offer["current_price"]
    flight.outbound_departure = offer["outbound_departure"]
    flight.outbound_arrival = offer["outbound_arrival"]
    flight.return_departure = offer["return_departure"]
    flight.return_arrival = offer["return_arrival"]
    db.add(
        models.PriceHistory(
            price=flight.current_price,
            checked_at=datetime.now(timezone.utc),
            flight_id=flight.id,
        )
    )
    return flight.current_price - previous_price


def refresh_all_flights() -> None:
    """Refresh every tracked flight once; one failed flight does not stop the job."""
    db = SessionLocal()
    try:
        flights = db.scalars(select(models.Flight)).all()
        for flight in flights:
            try:
                price_change = refresh_flight(db, flight)
                db.commit()
                logger.info(
                    "Flight %s refreshed; price change: %.2f",
                    flight.id,
                    price_change,
                )
            except Exception:
                db.rollback()
                logger.exception("Unable to refresh flight %s", flight.id)
    finally:
        db.close()