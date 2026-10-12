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

## Reservation Latency Profiling

### Objective

Investigate why reservation endpoint latency increases under concurrent load. Now, the objective is to identify potential bottlenecks in database connection acquisition, query execution, row locking, and transaction commits without modifying the reservation logic.

#### Test 1 — Single-request baseline - One reservation request against an available seat.

| Metric | Result |
|---|---:|
| Event lookup | 2.51 ms |
| Seat lookup + lock query | 1.80 ms |
| Database commit | 11.42 ms |
| Total endpoint time | 17.32 ms |

**Observation:** The endpoint completed in approximately 17 ms in this run, establishing a local single-request reference point.

#### Test 2 — Concurrent reservations across multiple seats - One event with distinct available seats, with 5 and 10 concurrent requests.

| Requests | Successful reservations | Average client latency | Throughput |
|---:|---:|---:|---:|
| 5 | 5 | 46.11 ms | 14.98 RPS |
| 10 | 10 | 104.50 ms | 21.82 RPS |

The 10-request run reported P50 latency of 112.04 ms and P95 latency of 154.17 ms.

**Observation:** Latency increased with concurrency in these runs. These results are local measurements and may vary between runs.

#### Test 3 — Event lookup profiling - Added timing around the event query in `create_reservation()`.

**Observations:**
- Some concurrent runs reported event lookup times of approximately 80–197 ms.
- Other requests completed the same lookup in approximately 1–12 ms.
- The single-request event lookup was approximately 2.51 ms.

**Conclusion:** Event lookup time was highly variable under load. The measurements alone do not establish whether query execution, connection acquisition, or other scheduling overhead caused the variation.

#### Test 4 — SQLAlchemy connection pool inspection - Inspected the SQLAlchemy engine and sampled pool statistics during concurrent requests.

| Property | Observed value |
|---|---|
| Pool class | `QueuePool` |
| Base pool size | 5 |
| Checked-out connections during load | Up to 10 |
| Observed overflow connections | Up to 5 |

The default SQLAlchemy `QueuePool` configuration generally permits up to 10 overflow connections in addition to the base pool size, giving a maximum of 15 simultaneous connections under the default settings.

**Observation:** The pool expanded beyond its base size during concurrent bursts. The samples did not establish that the pool was exhausted.

#### Test 5 — Connection acquisition and connection lifecycle - Measured the time spent in `db.connection()` and temporarily logged SQLAlchemy connection creation and closure events.

**Observations:**
- Connection acquisition measurements reached approximately 80–214 ms in some concurrent runs.
- Multiple new database connections were created during bursts.
- Five connection-close events were observed in one run.
- Overflow connections may be closed when returned to the pool; closure events alone do not demonstrate a connection leak.

**Conclusion:** Connection acquisition and connection lifecycle warrant further investigation. However, the measured acquisition duration includes more than pure pool waiting time, so the root cause remains unconfirmed.

### Overall Findings

1. The reservation endpoint successfully processed the tested multi-seat workloads.
2. Earlier single-seat contention tests demonstrated the expected single-winner behavior for competing reservations.
3. Concurrent request latency was substantially higher than the single-request baseline in several runs.
4. Connection acquisition, query execution, and commit timings varied under load.
5. No definitive root cause for the latency increase has been established.

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