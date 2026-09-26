import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from datetime import datetime

class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column( # create/ generate a uuid when a new event is added
        primary_key=True,default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),nullable=False #false means if the field has not recived any value the input will be rejected
    )
    venue: Mapped[str] = mapped_column(
        String(200),nullable=False
    )
    start_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False
    )


'''
the model/event.py tells us how postgres stores the event data.
'''