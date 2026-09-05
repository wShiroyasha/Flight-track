from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2
from ..database import get_db
from ..services.flight_provider import search_flight

router = APIRouter()


@router.post(
    "/flights/track",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.FlightInfos,
)
def track_flight(
    flight: schemas.FlightTrack,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    try:
        offer = search_flight(
            flight.origin,
            flight.destination,
            flight.departure_date,
            flight.return_date,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except LookupError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    new_flight = models.Flight(
        origin=flight.origin,
        destination=flight.destination,
        outbound_departure=offer["outbound_departure"],
        outbound_arrival=offer["outbound_arrival"],
        return_departure=offer["return_departure"],
        return_arrival=offer["return_arrival"],
        original_price=offer["original_price"],
        current_price=offer["current_price"],
        user_id=current_user.id,
    )
    db.add(new_flight)
    db.flush()
    db.add(
        models.PriceHistory(
            price=new_flight.current_price,
            checked_at=datetime.now(timezone.utc),
            flight_id=new_flight.id,
        )
    )
    db.commit()
    db.refresh(new_flight)

    return {
        **offer,
        "origin": new_flight.origin,
        "destination": new_flight.destination,
        "flight_name": f"{new_flight.origin} - {new_flight.destination}",
        "return_departure": new_flight.return_departure,
        "return_arrival": new_flight.return_arrival,
        "flight_id": new_flight.id,
    }


@router.delete(
    "/flights/{flight_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    flight = db.scalar(
        select(models.Flight).where(
            models.Flight.id == flight_id,
            models.Flight.user_id == current_user.id,
        )
    )
    if flight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )

    db.delete(flight)
    db.commit()