import uuid
from datetime import datetime
from pydantic import BaseModel

class ReservationCreate(BaseModel):
    user_id: uuid.UUID
    event_id: uuid.UUID
    seat_id: uuid.UUID

class ReservationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID
    seat_id: uuid.UUID
    status: str
    created_at: datetime
    expires_at: datetime | None
    class Config:
        from_attributes = True