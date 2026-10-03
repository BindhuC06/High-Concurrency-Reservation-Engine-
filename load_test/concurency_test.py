import uuid,time,httpx,asyncio

URL = "http://127.0.0.1:8000/reservations/"

EVENT_ID = "90f0c8b3-724f-4d0e-be32-57fae5cb468e"
SEAT_ID = "d42eee5b-bd3d-46e7-a097-677da982ae42"

NUMBER_OF_REQUESTS = 100
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
    async with httpx.AsyncClient() as client:
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

    print("Total requests:", len(results))
    print("Successful reservations:", len(successful))
    print("Conflicts:", len(conflicts))
    print(f"Total time : {end_time-start_time:.4f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())