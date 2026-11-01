from pydantic import BaseModel, Field, ConfigDict


class TrainCreate(BaseModel):
    train_number: str = Field(min_length=1, max_length=10)
    train_name: str = Field(min_length=2, max_length=120)
    source: str
    destination: str
    departure_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    arrival_time: str = Field(pattern=r"^\d{2}:\d{2}$")


class TrainResponse(TrainCreate):
    id: int
    active: bool

    model_config = ConfigDict(from_attributes=True)
