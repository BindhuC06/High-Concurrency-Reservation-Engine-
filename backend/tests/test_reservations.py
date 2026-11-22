import asyncio
import os
import uuid
from datetime import datetime, timezone
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.event import Event
from app.models.seats import Seat
from app.models.reservation import Reservation


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL or "reservation_test_db" not in TEST_DATABASE_URL.lower():
    raise RuntimeError("Refusing to run against a non-test database.")

engine = create_engine(TEST_DATABASE_URL)
SessionLocalTest = sessionmaker(bind=engine, autoflush=False, autocommit=False)

BASE_URL = "http://127.0.0.1:8001"


def create_available_seat():
    db = SessionLocalTest()
    try:
        event = Event(
            name="Concurrency Test Event",
            venue="Test Venue",
            start_time=datetime.now(timezone.utc),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        seat = Seat(
            event_id=event.id,
            seat_number=f"T-{uuid.uuid4().hex[:8]}",
            status="AVAILABLE",
        )
        db.add(seat)
        db.commit()
        db.refresh(seat)
        event_id = event.id
        seat_id = seat.id
        return event_id, seat_id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_event_with_seats(number_of_seats=10):
    db = SessionLocalTest()
    try:
        event = Event(
            name="Multi Seat Concurrency Test",
            venue="Test Venue",
            start_time=datetime.now(timezone.utc),
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        seats = []

        for i in range(number_of_seats):
            seat = Seat(
                event_id=event.id,
                seat_number=f"M-{i + 1}",
                status="AVAILABLE",
            )
            seats.append(seat)

        db.add_all(seats)
        db.commit()

        for seat in seats:
            db.refresh(seat)

        return event.id, [seat.id for seat in seats]

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

async def send_reservation(client, event_id, seat_id):
    payload = {
        "event_id": str(event_id),
        "seat_id": str(seat_id),
        "user_id": str(uuid.uuid4()),
    }
    response = await client.post("/reservations/", json=payload)
    #event not found error was observed
    # if response.status_code == 404:
    #     print("404 RESPONSE:", response.text)
    return response.status_code


async def run_same_seat_test():
    event_id, seat_id = create_available_seat()

    limits = httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
    )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        limits=limits,
        timeout=30.0,
    ) as client:
        statuses = await asyncio.gather(
            *[
                send_reservation(client, event_id, seat_id)
                for _ in range(10)
            ]
        )

    assert statuses.count(200) == 1, statuses
    assert statuses.count(409) == 9, statuses


def test_concurrent_requests_for_same_seat():
    asyncio.run(run_same_seat_test())

async def run_multiple_seats_test():
    event_id, seat_ids = create_event_with_seats(10)

    limits = httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
    )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        limits=limits,
        timeout=30.0,
    ) as client:

        statuses = await asyncio.gather(
            *[
                send_reservation(client, event_id, seat_id)
                for seat_id in seat_ids
            ]
        )

    assert statuses.count(200) == 10, statuses


def test_concurrent_requests_for_different_seats():
    asyncio.run(run_multiple_seats_test())

async def run_stress_test():
    event_id, seat_id = create_available_seat()

    total_requests = 50

    limits = httpx.Limits(
        max_connections=50,
        max_keepalive_connections=20,
    )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        limits=limits,
        timeout=30.0,
    ) as client:

        statuses = await asyncio.gather(
            *[
                send_reservation(client, event_id, seat_id)
                for _ in range(total_requests)
            ]
        )

    # Verify API responses
    assert statuses.count(200) == 1, statuses
    assert statuses.count(409) == 49, statuses

    # Verify database invariants
    db = SessionLocalTest()

    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()

        reservations = (
            db.query(Reservation)
            .filter(Reservation.seat_id == seat_id)
            .all()
        )

        assert seat is not None
        assert seat.status == "HELD"

        assert len(reservations) == 1
        assert reservations[0].status == "HELD"

    finally:
        db.close()

def test_stress_same_seat():
    asyncio.run(run_stress_test())