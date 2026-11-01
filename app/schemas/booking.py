from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict


class BookingCreate(BaseModel):
    train_id: int = Field(gt=0)
    journey_date: date
    travel_class: str = Field(pattern=r"^(SL|3A|2A|1A|CC|2S)$")
    passenger_name: str = Field(min_length=2, max_length=120)
    passenger_age: int = Field(ge=1, le=120)


class BookingResponse(BaseModel):
    id: int
    pnr: str
    user_id: int
    inventory_id: int
    passenger_name: str
    passenger_age: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingDetailsResponse(BookingResponse):
    train_name: str
    train_number: str
    journey_date: date
    travel_class: str
