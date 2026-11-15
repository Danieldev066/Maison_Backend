from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, menu, orders, reservations, restaurant
from app.core.config import get_settings

app = FastAPI(
    title="MAISON Restaurant API",
    version="1.0.0",
    description="Shared REST API for Flutter, website and staff dashboard. Prices in integer KGS (som).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(restaurant.router, prefix="/api/v1")
app.include_router(menu.router, prefix="/api/v1")
app.include_router(reservations.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
