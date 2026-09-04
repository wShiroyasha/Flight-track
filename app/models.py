from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    flights: Mapped[list["Flight"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(primary_key=True)

    origin: Mapped[str] = mapped_column(String, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)

    outbound_departure: Mapped[datetime] = mapped_column(nullable=False)
    outbound_arrival: Mapped[datetime] = mapped_column(nullable=False)

    return_departure: Mapped[datetime | None] = mapped_column(nullable=True)
    return_arrival: Mapped[datetime | None] = mapped_column(nullable=True)

    original_price: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False
    )
    current_price: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="flights"
    )
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="flight",
        cascade="all, delete-orphan",
    )

class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    price: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False
    )
    checked_at: Mapped[datetime] = mapped_column(nullable=False, index=True)

    flight_id: Mapped[int] = mapped_column(
        ForeignKey("flights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flight: Mapped["Flight"] = relationship(
    back_populates="price_history"
    )