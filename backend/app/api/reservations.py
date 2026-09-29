import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.event import Event
from app.models.seats import Seat
from app.models.reservation import Reservation
from app.schema.reservation import ReservationCreate, ReservationResponse

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)

@router.post("/", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == reservation.event_id).first()
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    seat = db.query(Seat).filter(
        Seat.id == reservation.seat_id,
        Seat.event_id == reservation.event_id).first()

    if seat is None:
        raise HTTPException(
            status_code=404,
            detail="Seat not found for this event"
        )

    if seat.status != "AVAILABLE":
        raise HTTPException(
            status_code=409,
            detail="Seat is not available"
        )
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    seat.status = "HELD"

    new_reservation = Reservation(
        user_id=reservation.user_id,
        event_id=reservation.event_id,
        seat_id=reservation.seat_id,
        status="HELD",
        expires_at=expires_at
    )

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    return new_reservation