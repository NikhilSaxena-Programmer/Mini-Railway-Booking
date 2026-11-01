from datetime import datetime, date

from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# 1. USER MODEL
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="customer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# 2. TRAIN MODEL
class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_number: Mapped[str] = mapped_column(String(10), unique=True)
    train_name: Mapped[str] = mapped_column(String(120))
    source: Mapped[str] = mapped_column(String(100), index=True)
    destination: Mapped[str] = mapped_column(String(100), index=True)
    departure_time: Mapped[str] = mapped_column(String(5))
    arrival_time: Mapped[str] = mapped_column(String(5))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


# 3. INVENTORY MODEL
class Inventory(Base):
    __tablename__ = "inventories"

    __table_args__ = (
        UniqueConstraint("train_id", "journey_date", "travel_class"),
        CheckConstraint("capacity >= 0 AND available >= 0 AND available <= capacity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"), index=True)
    journey_date: Mapped[date] = mapped_column(Date, index=True)
    travel_class: Mapped[str] = mapped_column(String(10))
    capacity: Mapped[int] = mapped_column(Integer)
    available: Mapped[int] = mapped_column(Integer)

    train = relationship("Train")


# 4. BOOKING MODEL
class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    pnr: Mapped[str] = mapped_column(String(12), unique=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventories.id"))

    passenger_name: Mapped[str] = mapped_column(String(120))
    passenger_age: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(20), default="CONFIRMED")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    inventory = relationship("Inventory")
