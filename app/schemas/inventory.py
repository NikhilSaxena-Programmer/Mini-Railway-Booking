from datetime import date

from pydantic import BaseModel, Field, ConfigDict


class InventoryCreate(BaseModel):
    train_id: int = Field(gt=0)
    journey_date: date
    travel_class: str = Field(pattern=r"^(SL|3A|2A|1A|CC|2S)$")
    capacity: int = Field(gt=0, le=10000)


class InventoryResponse(BaseModel):
    id: int
    train_id: int
    journey_date: date
    travel_class: str
    capacity: int
    available: int

    model_config = ConfigDict(from_attributes=True)
