from pydantic import BaseModel, Field
from typing import Optional


class DriverLocation(BaseModel):
    driver_id: str = Field(..., example="driver_001")
    driver_name: str = Field(..., example="Ravi Kumar")
    latitude: float = Field(..., ge=-90, le=90, example=13.0827)
    longitude: float = Field(..., ge=-180, le=180, example=80.2707)
    is_available: bool = Field(default=True)


class RideRequest(BaseModel):
    rider_id: str = Field(..., example="rider_42")
    pickup_lat: float = Field(..., ge=-90, le=90, example=13.0900)
    pickup_lon: float = Field(..., ge=-180, le=180, example=80.2750)
    active_requests: int = Field(
        default=1,
        ge=1,
        description="Number of concurrent ride requests in the area (used for surge pricing)"
    )


class MatchResponse(BaseModel):
    driver_id: str
    driver_name: str
    distance_km: float
    eta_minutes: int
    fare_estimate: float
    surge_multiplier: float
