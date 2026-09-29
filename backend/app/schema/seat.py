import uuid
from pydantic import BaseModel

class SeatCreate(BaseModel):
    seat_number: str

class SeatResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    seat_number: str
    class Config:
        from_attributes = True