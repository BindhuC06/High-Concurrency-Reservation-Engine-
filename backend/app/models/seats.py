import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Seat(Base):
    __tablename__ = "seats"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id"),
        nullable=False
    )
    seat_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    status: Mapped[str] = mapped_column( # Held Available and Reserved
        String(20),
        default="AVAILABLE",
        nullable=False
    )