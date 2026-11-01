from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models import Train, Inventory
from app.schemas.inventory import InventoryCreate, InventoryResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ADMIN: Add seat inventory for a train
@router.post("/", response_model=InventoryResponse, status_code=201)
def create_inventory(
    data: InventoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")

    train = db.get(Train, data.train_id)

    if not train or not train.active:
        raise HTTPException(404, "Active train not found")

    if data.journey_date < date.today():
        raise HTTPException(400, "Journey date cannot be in the past")

    inventory = Inventory(
        train_id=data.train_id,
        journey_date=data.journey_date,
        travel_class=data.travel_class,
        capacity=data.capacity,
        available=data.capacity,
    )

    db.add(inventory)

    try:
        db.commit()
        db.refresh(inventory)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409, "Inventory already exists for this train, date and class"
        )

    return inventory


# PUBLIC: Check seat availability
@router.get("/", response_model=list[InventoryResponse])
def check_availability(
    train_id: int = Query(gt=0),
    journey_date: date = Query(),
    db: Session = Depends(get_db),
):
    if journey_date < date.today():
        raise HTTPException(400, "Journey date cannot be in the past")

    train = db.get(Train, train_id)

    if not train or not train.active:
        raise HTTPException(404, "Active train not found")

    query = select(Inventory).where(
        Inventory.train_id == train_id, Inventory.journey_date == journey_date
    )

    return list(db.scalars(query).all())
