from datetime import date, datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

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

    @model_validator(mode="after")
    def validate_dates(self):
        if self.departure_date < date.today():
            raise ValueError("departure_date cannot be in the past")
        if self.return_date is not None and self.return_date < self.departure_date:
            raise ValueError("return_date cannot be before departure_date")
        return self

class FlightInfos(Flight):
    flight_name: str
    original_price: float
    current_price: float
    outbound_departure: datetime
    outbound_arrival: datetime
    return_departure: Optional[datetime] = None
    return_arrival: Optional[datetime] = None
    flight_id: int

class PriceHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    price: float
    checked_at: datetime

class FlightDetails(FlightInfos):
    price_history: list[PriceHistoryOut] = Field(default_factory=list)
