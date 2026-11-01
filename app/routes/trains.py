from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models import Train
from app.schemas.train import TrainCreate, TrainResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/trains", tags=["Trains"])


# PUBLIC: Search active trains
@router.get("/", response_model=list[TrainResponse])
def search_trains(
    source: str | None = None,
    destination: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Train).where(Train.active.is_(True))

    if source:
        query = query.where(Train.source.ilike(source.strip()))

    if destination:
        query = query.where(Train.destination.ilike(destination.strip()))

    return list(db.scalars(query.order_by(Train.train_number)).all())


# ADMIN: Add a new train
@router.post("/", response_model=TrainResponse, status_code=201)
def create_train(
    data: TrainCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")

    if data.source.strip().lower() == data.destination.strip().lower():
        raise HTTPException(400, "Source and destination must differ")

    train_data = data.model_dump()
    train_data["source"] = data.source.strip()
    train_data["destination"] = data.destination.strip()
    train_data["train_number"] = data.train_number.strip()
    train_data["train_name"] = data.train_name.strip()

    train = Train(**train_data)

    db.add(train)

    try:
        db.commit()
        db.refresh(train)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Train number already exists")

    return train


# ADMIN: Update train
@router.put("/{train_id}", response_model=TrainResponse)
def update_train(
    train_id: int,
    data: TrainCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")

    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(404, "Train not found")

    if data.source.strip().lower() == data.destination.strip().lower():
        raise HTTPException(400, "Source and destination must differ")

    train_data = data.model_dump()
    train_data["source"] = data.source.strip()
    train_data["destination"] = data.destination.strip()
    train_data["train_number"] = data.train_number.strip()
    train_data["train_name"] = data.train_name.strip()

    for key, value in train_data.items():
        setattr(train, key, value)

    try:
        db.commit()
        db.refresh(train)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Train number already exists")

    return train


# ADMIN: Activate or deactivate train
@router.patch("/{train_id}/status")
def update_train_status(
    train_id: int,
    active: bool,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")

    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(404, "Train not found")

    train.active = active
    db.commit()

    return {
        "message": "Train status updated",
        "train_id": train.id,
        "active": train.active,
    }
