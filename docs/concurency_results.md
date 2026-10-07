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

### Observation

The P50 latency was approximately 709 ms, while P95 and P99 were
approximately 858 ms and 875 ms respectively.

The relatively small difference between P95 and P99 indicates that the
tail latency did not increase dramatically under this workload.

These measurements were collected on a local development environment
and should be treated as a baseline rather than a production performance
claim.