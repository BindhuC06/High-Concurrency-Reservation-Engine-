from fastapi import FastAPI

from app.api.events import router as events_router

app = FastAPI(
    title="Reservation Engine",
    description="A high-concurrency reservation system",
    version="0.1.0"
)

app.include_router(events_router)