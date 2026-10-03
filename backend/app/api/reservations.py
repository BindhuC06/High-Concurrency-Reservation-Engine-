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
        Seat.event_id == reservation.event_id).with_for_update().first()

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

@router.post("/{reservation_id}/confirm", response_model=ReservationResponse)
def confirm_reservation(
    reservation_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    if reservation.status != "HELD":
        raise HTTPException(
            status_code=409,
            detail="Reservation cannot be confirmed"
        )

    if reservation.expires_at and reservation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=409,
            detail="Reservation hold has expired"
        )

    seat = db.query(Seat).filter(
        Seat.id == reservation.seat_id
    ).first()

    if seat is None:
        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )

    seat.status = "BOOKED"
    reservation.status = "CONFIRMED"

    db.commit()
    db.refresh(reservation)

    return reservation

@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
def cancel_reservation(
    reservation_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    if reservation.status != "HELD":
        raise HTTPException(
            status_code=409,
            detail="Reservation cannot be cancelled"
        )

    seat = db.query(Seat).filter(Seat.id == reservation.seat_id).first()

    if seat is None:
        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )

    seat.status = "AVAILABLE"
    reservation.status = "CANCELLED"
    db.commit()
    db.refresh(reservation)

    return reservation