import uuid,time,httpx,asyncio, sys

URL = "http://127.0.0.1:8000/reservations/"

EVENT_ID = "90f0c8b3-724f-4d0e-be32-57fae5cb468e"
SEAT_ID = "2815e8dd-adad-463a-b71a-8d405a5b3cbd"

NUMBER_OF_REQUESTS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
async def reserve_seat(client, user_id):
    payload = {
        "user_id": str(user_id),
        "event_id": EVENT_ID,
        "seat_id": SEAT_ID
    }
    response = await client.post(URL, json=payload)

    return response.status_code, response.json()


async def main():
    start_time =time.perf_counter()

    limits = httpx.Limits(
        max_connections=1000,
        max_keepalive_connections=100
    )
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = [
            reserve_seat(client, uuid.uuid4())
            for _ in range(NUMBER_OF_REQUESTS)
        ]
        results = await asyncio.gather(*tasks)

    end_time=time.perf_counter()

    successful = [
        result for result in results
        if result[0] == 200
    ]

    conflicts = [
        result for result in results
        if result[0] == 409
    ]
    total_time=end_time-start_time
    requests_per_second=len(results)/total_time

    print("Total requests:", len(results))
    print("Successful reservations:", len(successful))
    print("Conflicts:", len(conflicts))
    print(f"Total time : {total_time:.4f} seconds.")
    print(f"requests per second : {requests_per_second:.4f}.")

if __name__ == "__main__":
    asyncio.run(main())