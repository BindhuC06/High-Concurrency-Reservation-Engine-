from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schema.event import EventResponse, EventCreate
from app.models.event import Event

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