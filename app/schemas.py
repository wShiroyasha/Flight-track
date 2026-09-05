from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str

class Token_data_Model(BaseModel):
    id: Optional[int] = None

class Flight(BaseModel):
    origin: str = Field(
        min_length=2,
        description="Departure city name, for example Paris",
    )
    destination: str = Field(
        min_length=2,
        description="Arrival city name, for example New York",
    )

    @field_validator("origin", "destination")
    @classmethod
    def normalize_city_name(cls, value: str) -> str:
        return value.strip()

class FlightTrack(Flight):
    departure_date: date
    return_date: Optional[date] = None

class FlightInfos(Flight):
    flight_name: str
    original_price: float
    current_price: float
    outbound_departure: datetime
    outbound_arrival: datetime
    return_departure: Optional[datetime] = None
    return_arrival: Optional[datetime] = None
    flight_id: int
