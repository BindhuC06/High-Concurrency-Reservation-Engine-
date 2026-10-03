# Concurrency Test Results

## Test Objective

Verify that multiple concurrent users cannot successfully reserve the same seat.

## Test Environment

- Backend: FastAPI
- Database: PostgreSQL
- Concurrency control: PostgreSQL row-level locking (`SELECT ... FOR UPDATE`)
- Test client: Python + HTTPX

## Results

| Concurrent Requests | Successful Reservations | Conflicts |
|---:|---:|---:|
| 10 | 1 | 9 |
| 50 | 1 | 49 |
| 100 | 1 | 99 |

## Invariant

For a single seat:

`successful reservations <= 1`

The invariant is successfully held for all tested concurrency levels.