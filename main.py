from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from models import RideRequest, DriverLocation, MatchResponse
from matching import find_nearest_driver
from cache import (
    register_driver, get_all_drivers,
    mark_driver_busy, mark_driver_available, init_redis
)
from pricing import calculate_surge_price

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield

app = FastAPI(
    title="Ride Matching Engine",
    description="Low-latency ride dispatch backend using FastAPI, Redis, and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/driver/register", summary="Register a driver with current location")
async def register(driver: DriverLocation):
    """
    Register or update a driver's location in Redis cache.
    Called periodically by the driver's mobile app (e.g. every 5 seconds).
    """
    await register_driver(driver)
    return {"status": "registered", "driver_id": driver.driver_id}


@app.post("/driver/available/{driver_id}", summary="Mark driver as available")
async def set_available(driver_id: str):
    await mark_driver_available(driver_id)
    return {"status": "available", "driver_id": driver_id}


@app.post("/ride/request", response_model=MatchResponse, summary="Request a ride")
async def request_ride(ride: RideRequest):
    """
    Core matching endpoint.
    - Fetches all available drivers from Redis cache
    - Finds the nearest driver using Haversine distance
    - Applies surge pricing based on demand density
    - Marks matched driver as busy
    Returns matched driver info and estimated fare.
    """
    drivers = await get_all_drivers()

    if not drivers:
        raise HTTPException(status_code=404, detail="No drivers available right now")

    matched_driver = find_nearest_driver(
        rider_lat=ride.pickup_lat,
        rider_lon=ride.pickup_lon,
        drivers=drivers
    )

    if not matched_driver:
        raise HTTPException(status_code=404, detail="No nearby drivers found")

    surge_multiplier, fare_estimate = calculate_surge_price(
        num_drivers=len(drivers),
        num_requests=ride.active_requests,
        distance_km=matched_driver["distance_km"]
    )

    await mark_driver_busy(matched_driver["driver_id"])

    return MatchResponse(
        driver_id=matched_driver["driver_id"],
        driver_name=matched_driver["driver_name"],
        distance_km=round(matched_driver["distance_km"], 2),
        eta_minutes=round(matched_driver["distance_km"] / 0.5),  # ~30 km/h city speed
        fare_estimate=fare_estimate,
        surge_multiplier=surge_multiplier
    )


@app.get("/drivers/available", summary="List all available drivers")
async def list_drivers():
    drivers = await get_all_drivers()
    return {"count": len(drivers), "drivers": drivers}


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}
