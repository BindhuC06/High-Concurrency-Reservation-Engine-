from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.dependencies import get_db

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

@router.get("/")
def get_events(db: Session = Depends(get_db)):
    return {"message": "Events endpoint working"}