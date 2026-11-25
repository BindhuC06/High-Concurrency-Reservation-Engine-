# High-Concurrency Reservation System

A FastAPI backend for reserving limited event seats. The project focuses on one core problem: safely handling simultaneous attempts to reserve the same seat.

## What it demonstrates

- A REST API for events, seats, and reservations
- PostgreSQL with SQLAlchemy
- Transactional reservation handling and row-level locking
- Reservation lifecycle management
- Concurrent load testing and latency investigation

## Architecture

```text
Client → FastAPI → SQLAlchemy → PostgreSQL
```

## Reservation flow

```text
AVAILABLE → HELD → BOOKED
               └→ CANCELLED → AVAILABLE
```

The exact transition rules depend on the reservation lifecycle implemented by the API. A seat should only become available again when the reservation is cancelled or otherwise released according to that logic.

## Concurrency approach

The reservation path uses PostgreSQL row-level locking through SQLAlchemy's `with_for_update()` when checking and updating a seat. This serializes competing transactions for a locked seat. The availability check and reservation state change must remain inside the same transaction for the lock to protect the operation correctly.

## Technology

- Python
- FastAPI and Uvicorn
- PostgreSQL
- SQLAlchemy
- Pydantic
- HTTPX for API/load testing

## Run locally

### Prerequisites

- Python installed
- PostgreSQL running and a database created for the project

### Setup

From the repository root, create and activate a virtual environment, then install the backend requirements:

```powershell
py -m venv backend\venv
backend\venv\Scripts\Activate.ps1
python -m pip install -r backend\requirement.txt
```

Configure the database connection using the environment settings expected by the application. Do not commit credentials. Then start the API:

```powershell
cd backend
uvicorn app.main:app --reload
```

Interactive API documentation is available at [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

> Database creation, schema initialization/migrations, and the required environment variable names are not documented here yet. Add the exact commands and names used by the project so a new contributor can follow this section from a clean checkout.

## Benchmarks

These measurements were collected in local development. They are useful as correctness and behavior observations for the tested setup; they are not production capacity claims. Results can vary with hardware, database configuration, and server settings.

### Single-seat contention

Concurrent attempts competed for one seat. Each reported run produced one successful reservation and conflicts for the remaining attempts.

| Requests | Successful | Conflicts | Duration | Throughput |
|---:|---:|---:|---:|---:|
| 10 | 1 | 9 | 0.703 s | 14.22 req/s |
| 50 | 1 | 49 | 0.858 s | 58.29 req/s |
| 100 | 1 | 99 | 1.074 s | 93.09 req/s |
| 500 | 1 | 499 | 3.438 s | 145.42 req/s |

### Multiple-seat load run

The recorded run created 100 seats and sent 500 reservation requests. The request concurrency setting and request-to-seat distribution were not recorded in the available output, so they should be added to make this run reproducible.

| Metric | Result |
|---|---:|
| Total requests | 500 |
| Successful reservations | 100 |
| HTTP 409 conflicts | 400 |
| Unexpected errors | 0 |
| Duration | 7.37 s |
| Throughput | 67.89 req/s |
| Average client latency | 704.96 ms |
| P50 client latency | 504.93 ms |
| P95 client latency | 2,032.19 ms |
| P99 client latency | 3,625.61 ms |

The counts are consistent with one successful reservation per available seat and conflicts for the other attempts. Confirming that every distinct seat was reserved exactly once requires checking the resulting seat/reservation records or an explicit assertion in the benchmark.

## Latency investigation

Local profiling compared a single request with concurrent requests and sampled database query, commit, and connection behavior. The measurements showed higher and more variable client latency under concurrency, but did not identify a definitive root cause.

| Scenario | Requests | Successful | Average client latency | Throughput |
|---|---:|---:|---:|---:|
| Single-request baseline | 1 | 1 | 17.32 ms total endpoint time | — |
| Concurrent requests across distinct seats | 5 | 5 | 46.11 ms | 14.98 req/s |
| Concurrent requests across distinct seats | 10 | 10 | 104.50 ms | 21.82 req/s |

In the 10-request run, P50 was 112.04 ms and P95 was 154.17 ms. Event lookup, connection acquisition, and commit timings varied across runs. Pool samples showed a `QueuePool` with a base size of 5 and up to 10 checked-out connections (including up to 5 overflow connections in the observed run). These observations point to areas for further investigation; they do not establish pool exhaustion or a specific bottleneck.

## Roadmap

- [x] Event and seat management
- [x] Reservation lifecycle
- [x] Concurrency protection
- [x] Single-seat contention benchmarks
- [x] Multi-seat load run
- [x] Latency measurements
- [ ] Redis
- [ ] Background workers
- [ ] Docker and CI
- [ ] Cloud deployment
- [ ] Observability