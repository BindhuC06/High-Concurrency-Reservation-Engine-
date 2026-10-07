import uuid,time,httpx,asyncio, sys
import statistics

URL = "http://127.0.0.1:8000/reservations/"

EVENT_ID = "f4bb7867-df41-45c4-84e4-a7153e6f09c7"
SEAT_IDS = [
    "7f19d792-08d6-4946-8acb-024929171c40",
    "7d45ea09-1796-4cd1-872a-4e161d60ca0e",
    "2ef2b927-0ae8-4f01-8ce8-dd1313b6f613",
    "cb4bd9c7-af17-4363-bda8-01ceebf4d8fb",
    "600984a8-7a00-4437-8f4f-1324043b2fb1",
    "26d759e1-7962-42e7-9fea-f84c8c4cb0a9",
    "95f3ed31-aa64-4799-ad9a-d36457051917",
    "c6cb9100-2227-4077-ac2b-093aaffae24e",
    "4892e6ed-f837-4b25-a9f1-d6052a0cc657",
    "beb89f05-4a04-4f9b-8ec5-7f2d5fdcc1fd"
]

NUMBER_OF_REQUESTS = int(sys.argv[1]) if len(sys.argv) > 1 else 10

async def reserve_seat(client, user_id, seat_id):
    payload = {
        "user_id": str(user_id),
        "event_id": EVENT_ID,
        "seat_id": seat_id
    }
    start = time.perf_counter()
    response = await client.post(URL, json=payload)
    end = time.perf_counter()
    latency = end - start
    return response.status_code, response.json(), latency

def percentile(data, p):
    k = (len(data) - 1) * p
    f = int(k)
    c = f + 1

    if c >= len(data):
        return data[f]

    return data[f] + (k - f) * (data[c] - data[f])

async def main():
    start_time =time.perf_counter()

    limits = httpx.Limits(
        max_connections=1000,
        max_keepalive_connections=100
    )
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = [
            reserve_seat(
                client,
                uuid.uuid4(),
                SEAT_IDS[i % len(SEAT_IDS)]
            )for i in range(NUMBER_OF_REQUESTS)
        ]
        results = await asyncio.gather(*tasks)

    end_time=time.perf_counter()

    successful = [ result for result in results if result[0] == 200]
    conflicts = [ result for result in results if result[0] == 409]
    latencies = [ result[2] for result in results]

    total_time=end_time-start_time
    requests_per_second=len(results)/total_time
    latencies.sort()

    p50 = statistics.median(latencies)
    average_latency = statistics.mean(latencies)
    p95 = percentile(latencies, 0.95)
    p99 = percentile(latencies, 0.99)

    print("Total requests:", len(results))
    print("Successful reservations:", len(successful))
    print("Conflicts:", len(conflicts))
    print(f"Total time : {total_time:.4f} seconds.")
    print(f"requests per second : {requests_per_second:.4f}.")
    print(f"Average latency : {average_latency * 1000:.2f} ms")
    print(f"P50 latency     : {p50 * 1000:.2f} ms")
    print(f"P95 latency     : {p95 * 1000:.2f} ms")
    print(f"P99 latency     : {p99 * 1000:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main())