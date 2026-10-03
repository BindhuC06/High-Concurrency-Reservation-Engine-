# High-Concurrency Reservation Engine

A backend reservation system designed to safely handle multiple users
competing for limited inventory.

The primary goal is to prevent double-booking under concurrent requests.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- HTTPX

## Architecture

Client → FastAPI → SQLAlchemy → PostgreSQL

## Core Concepts

- REST API design
- PostgreSQL transactions
- Row-level locking
- Reservation state management
- Concurrent request handling
- Load testing

## Reservation Flow

AVAILABLE → HELD → BOOKED
              ↓
          CANCELLED
              ↓
          AVAILABLE

A seat can only be successfully reserved by one concurrent request.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/events/` | Create event |
| GET | `/events/` | List events |
| POST | `/events/{id}/seats` | Add seat |
| GET | `/events/{id}/seats` | Get seats |
| POST | `/reservations/` | Hold seat |
| POST | `/reservations/{id}/confirm` | Confirm reservation |
| POST | `/reservations/{id}/cancel` | Cancel reservation |

## Concurrency

Reservations use PostgreSQL row-level locking:

```python
.with_for_update()
```

This prevents two concurrent requests from successfully reserving
the same seat.

Benchmark
Single-seat contention test:


| Requests | Success | Conflicts | Time(sec) | RPS |
|---:|---:|---:|---:|---:|
| 10 | 1 | 9 | 0.703 | 14.22 |
| 50 | 1 | 49 | 0.858 | 58.29 |
| 100 | 1 | 99 | 1.074 | 93.09 |
| 500 | 1 | 499 | 3.438 | 145.42 |


Result: Exactly one reservation succeeded in every test.
Note: These are local single-seat contention tests, not general
system throughput benchmarks.

Run Locally
```
backend\venv\Scripts\activate
cd backend
uvicorn app.main:app --reload
```

Swagger:
http://127.0.0.1:8000/docs

## Roadmap

- [x] Event & seat management
- [x] Reservation lifecycle
- [x] Concurrency protection
- [x] Concurrency benchmarks
- [ ] Realistic multi-seat load testing
- [ ] Latency metrics
- [ ] Redis
- [ ] Background workers
- [ ] Docker & CI/CD
- [ ] Cloud deployment
- [ ] Observability