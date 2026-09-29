from app.db.database import Base, engine
from app.models.event import Event
from app.models.seats import Seat

def init_db():
    Base.metadata.create_all(bind=engine) # create all-doesnt modify existing tables....only creates ner ones.

if __name__ == "__main__":
    init_db()