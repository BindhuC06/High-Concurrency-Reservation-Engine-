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

## Benchmark

### Single-seat contention

500 concurrent requests competing for the same seat:

| Requests | Successful | Conflicts | Total Time | Requests/sec |
|---:|---:|---:|---:|---:|
| 10 | 1 | 9 | 0.703s | 14.22 |
| 50 | 1 | 49 | 0.858s | 58.29 |
| 100 | 1 | 99 | 1.074s | 93.09 |
| 500 | 1 | 499 | 3.438s | 145.42 |

**Result:** Exactly one reservation succeeded in every test, confirming that
the same seat cannot be successfully reserved by multiple concurrent users.

### Multi-seat concurrency

100 concurrent requests distributed across 10 seats:

| Requests | Seats | Successful | Conflicts | Total Time | Requests/sec |
|---:|---:|---:|---:|---:|---:|
| 100 | 10 | 10 | 90 | 1.6255s | 61.52 |

### Latency

100 concurrent requests distributed across 10 seats:

| Metric | Result |
|---|---:|
| Total requests | 100 |
| Successful | 10 |
| Conflicts | 90 |
| Throughput | 68.20 req/s |
| Average latency | 705.66 ms |
| P50 latency | 709.35 ms |
| P95 latency | 858.22 ms |
| P99 latency | 875.23 ms |

> These are local development benchmarks. The contention tests measure
> concurrency correctness and behavior under resource contention, not
> production system capacity.

Result: Exactly one reservation succeeded in every test.

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
- [x] Realistic multi-seat load testing
- [x] Latency metrics
- [ ] Redis
- [ ] Background workers
- [ ] Docker & CI/CD
- [ ] Cloud deployment
- [ ] Observability