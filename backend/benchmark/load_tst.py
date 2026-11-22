import asyncio
import httpx
import time
import statistics
import uuid
from datetime import datetime, timezone


BASE_URL = "http://127.0.0.1:8001"

TOTAL_SEATS = 100
TOTAL_REQUESTS = 500
CONCURRENCY = 50

async def create_benchmark_event(client):
    response = await client.post(
        f"{BASE_URL}/events/",
        json={
            "name": "Load Test Event",
            "venue": "Benchmark Event",
            "start_time": datetime.now(timezone.utc).isoformat()
        }
    )

    response.raise_for_status()
    return response.json()["id"]


async def create_benchmark_seats(client, event_id):
    seat_ids = []

    for i in range(TOTAL_SEATS):
        response = await client.post(
            f"{BASE_URL}/events/{event_id}/seats",
            json={"seat_number": f"L-{i + 1}"} #L1 L2....
        )

        response.raise_for_status()
        seat_ids.append(response.json()["id"])

    return seat_ids


async def reserve_seat(client, event_id, seat_id):
    payload = {
        "event_id": event_id,
        "seat_id": seat_id,
        "user_id": str(uuid.uuid4())
    }

    start = time.perf_counter()

    try:
        response = await client.post(
            f"{BASE_URL}/reservations/",
            json=payload
        )

        latency = (time.perf_counter() - start) * 1000

        return {
            "status": response.status_code,
            "latency": latency
        }

    except httpx.RequestError as error:
        latency = (time.perf_counter() - start) * 1000

        return {
            "status": "ERROR",
            "latency": latency,
            "error": str(error)
        }


async def run_benchmark():
    limits = httpx.Limits(
        max_connections=CONCURRENCY,
        max_keepalive_connections=CONCURRENCY
    )

    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:

        print("Creating benchmark event...")
        event_id = await create_benchmark_event(client)

        print("Creating seats...")
        seat_ids = await create_benchmark_seats(client, event_id)

        print(f"Created {TOTAL_SEATS} seats.")
        print(f"Sending {TOTAL_REQUESTS} requests...")

        # Distribute requests across all seats.
        seat_requests = [
            seat_ids[i % TOTAL_SEATS]
            for i in range(TOTAL_REQUESTS)
        ]

        start_time = time.perf_counter()

        semaphore = asyncio.Semaphore(CONCURRENCY)

        async def limited_request(seat_id):
            async with semaphore:
                return await reserve_seat(client, event_id, seat_id)

        results = await asyncio.gather(
            *[
                limited_request(seat_id)
                for seat_id in seat_requests
            ]
        )

        total_time = time.perf_counter() - start_time

    latencies = [r["latency"] for r in results]

    successful = sum(r["status"] == 200 for r in results)
    conflicts = sum(r["status"] == 409 for r in results)
    errors = sum(r["status"] not in (200, 409) for r in results)

    sorted_latencies = sorted(latencies)

    def percentile(values, percentile):
        index = int((percentile / 100) * len(values))
        index = min(index, len(values) - 1)
        return values[index]

    print("\n========== LOAD TEST RESULTS ==========")
    print(f"Total requests:      {TOTAL_REQUESTS}")
    print(f"Successful:          {successful}")
    print(f"Conflicts:          {conflicts}")
    print(f"Errors:             {errors}")
    print(f"Total time:         {total_time:.2f} seconds")
    print(f"Requests/sec:       {TOTAL_REQUESTS / total_time:.2f}")
    print(f"Average latency:    {statistics.mean(latencies):.2f} ms")
    print(f"P50 latency:        {percentile(sorted_latencies, 50):.2f} ms")
    print(f"P95 latency:        {percentile(sorted_latencies, 95):.2f} ms")
    print(f"P99 latency:        {percentile(sorted_latencies, 99):.2f} ms")
    print("=====================================")


if __name__ == "__main__":
    asyncio.run(run_benchmark())