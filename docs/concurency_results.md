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

### For a single seat:

`successful reservations <= 1`

The invariant is successfully held for all tested concurrency levels.


| Requests | Successful | Conflicts | Total Time (s) | Requests/sec |
|----------|------------|-----------|----------------|--------------|
| 10       | 1          | 9         | 0.703          | 14.22        |
| 50       | 1          | 49        | 0.858          | 58.29        |
| 100      | 1          | 99        | 1.074          | 93.09        |
| 500      | 1          | 499       | 3.438          | 145.42       |

### Observation

Across all contention tests, exactly one reservation succeeded
while all other concurrent attempts were rejected.

This confirms that the reservation endpoint preserves the
single-booking invariant under concurrent access.

The 500-request test initially encountered an HTTP client
connection-pool timeout. Increasing the HTTPX connection pool
allowed the full benchmark to execute successfully.


### Multi-seat concurrency

100 users → 10 seats
→ 10 successes
→ 90 conflicts

| Requests | Seats | Successful | Conflicts | Time | RPS |
|---:|---:|---:|---:|---:|---:|
| 100 | 10 | **10** | **90** | 1.6255s | **61.52** |