from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.db.dependencies import get_db
from app.schema.event import EventResponse, EventCreate
from app.models.event import Event
from app.models.seats import Seat
from app.schema.seat import SeatCreate, SeatResponse
import uuid

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

@router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    new_event = Event(
        name=event.name,
        venue=event.venue,
        start_time=event.start_time
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event

@router.get("/", response_model=list[EventResponse])
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events

@router.post("/{event_id}/seats", response_model=SeatResponse)
def create_seat(
    event_id: uuid.UUID,
    seat: SeatCreate,
    db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    new_seat = Seat(
        event_id=event_id,
        seat_number=seat.seat_number
    )

    db.add(new_seat)
    db.commit()
    db.refresh(new_seat)
    return new_seat

@router.get("/{event_id}/seats", response_model=list[SeatResponse])
def get_seats(
    event_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    seats = db.query(Seat).filter(
        Seat.event_id == event_id
    ).all()

    return seats