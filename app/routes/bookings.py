import secrets
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models import Train, Inventory, Booking
from app.schemas.booking import BookingCreate, BookingResponse
from app.routes.auth import get_current_user


router = APIRouter(prefix="/bookings", tags=["Bookings"])


# CUSTOMER: Book a train ticket
@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    data: BookingCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    # 1. Validate journey date
    if data.journey_date < date.today():
        raise HTTPException(400, "Journey date cannot be in the past")

    # 2. Check whether train exists and is active
    train = db.get(Train, data.train_id)

    if not train or not train.active:
        raise HTTPException(404, "Active train not found")

    # 3. Find matching inventory
    inventory = db.scalar(
        select(Inventory).where(
            Inventory.train_id == data.train_id,
            Inventory.journey_date == data.journey_date,
            Inventory.travel_class == data.travel_class,
        )
    )

    if not inventory:
        raise HTTPException(404, "Seat inventory not found for this train and date")

    # 4. Generate a unique PNR
    pnr = None

    for _ in range(5):
        candidate = str(secrets.randbelow(10**10)).zfill(10)

        existing = db.scalar(select(Booking.id).where(Booking.pnr == candidate))

        if existing is None:
            pnr = candidate
            break

    if pnr is None:
        raise HTTPException(500, "Could not generate PNR. Please try again.")

    # 5. Atomically reduce available seats
    result = db.execute(
        update(Inventory)
        .where(Inventory.id == inventory.id, Inventory.available > 0)
        .values(available=Inventory.available - 1)
    )

    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "No seats available")

    # 6. Create booking
    booking = Booking(
        pnr=pnr,
        user_id=user.id,
        inventory_id=inventory.id,
        passenger_name=data.passenger_name.strip(),
        passenger_age=data.passenger_age,
        status="CONFIRMED",
    )

    db.add(booking)

    # 7. Save booking and seat reduction together
    try:
        db.commit()
        db.refresh(booking)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Booking could not be completed. Please try again.")

    return booking


# CUSTOMER: View my bookings
@router.get("/my-bookings", response_model=list[BookingResponse])
def get_my_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    bookings = db.scalars(
        select(Booking)
        .where(Booking.user_id == user.id)
        .order_by(Booking.created_at.desc())
    ).all()

    return list(bookings)


# CUSTOMER: View a booking using PNR
@router.get("/{pnr}", response_model=BookingResponse)
def get_booking(
    pnr: str, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    booking = db.scalar(
        select(Booking).where(Booking.pnr == pnr, Booking.user_id == user.id)
    )

    if not booking:
        raise HTTPException(404, "Booking not found")

    return booking


# CUSTOMER: Cancel a booking
@router.patch("/{pnr}/cancel")
def cancel_booking(
    pnr: str, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    # 1. Find booking belonging to logged-in customer
    booking = db.scalar(
        select(Booking).where(Booking.pnr == pnr, Booking.user_id == user.id)
    )

    if not booking:
        raise HTTPException(404, "Booking not found")

    # 2. Change status only if currently confirmed
    result = db.execute(
        update(Booking)
        .where(Booking.id == booking.id, Booking.status == "CONFIRMED")
        .values(status="CANCELLED")
    )

    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Booking is already cancelled or cannot be cancelled")

    # 3. Restore one seat to inventory
    seat_result = db.execute(
        update(Inventory)
        .where(
            Inventory.id == booking.inventory_id,
            Inventory.available < Inventory.capacity,
        )
        .values(available=Inventory.available + 1)
    )

    if seat_result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Could not restore seat inventory")

    # 4. Save cancellation and seat restoration together
    db.commit()

    return {
        "message": "Booking cancelled successfully",
        "pnr": pnr,
        "status": "CANCELLED",
    }
