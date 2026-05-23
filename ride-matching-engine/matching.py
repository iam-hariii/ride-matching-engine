import math
from typing import Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    Uses the Haversine formula — accurate for short to medium distances.

    Args:
        lat1, lon1: Rider's coordinates
        lat2, lon2: Driver's coordinates

    Returns:
        Distance in kilometres
    """
    R = 6371  # Earth's radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_nearest_driver(
    rider_lat: float,
    rider_lon: float,
    drivers: list[dict],
    max_radius_km: float = 10.0
) -> Optional[dict]:
    """
    Find the closest available driver to the rider's pickup location.

    Args:
        rider_lat, rider_lon : Rider's pickup coordinates
        drivers              : List of available driver dicts from Redis cache
        max_radius_km        : Only consider drivers within this radius (default 10 km)

    Returns:
        Nearest driver dict with added 'distance_km' key, or None if no match found
    """
    nearest = None
    min_distance = float("inf")

    for driver in drivers:
        distance = haversine_distance(
            rider_lat, rider_lon,
            float(driver["latitude"]),
            float(driver["longitude"])
        )

        if distance < max_radius_km and distance < min_distance:
            min_distance = distance
            nearest = {**driver, "distance_km": distance}

    return nearest
