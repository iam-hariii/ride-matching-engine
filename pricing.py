BASE_FARE = 30.0          # Base fare in INR
RATE_PER_KM = 12.0        # INR per km
MAX_SURGE_MULTIPLIER = 3.0


def calculate_surge_price(
    num_drivers: int,
    num_requests: int,
    distance_km: float
) -> tuple[float, float]:
    """
    Compute surge multiplier based on real-time demand vs supply ratio.

    Surge logic:
      - demand_ratio = active_requests / available_drivers
      - ratio < 1.5  → no surge (1.0x)
      - ratio 1.5–3  → moderate surge (1.5x)
      - ratio 3–5    → high surge (2.0x)
      - ratio > 5    → peak surge (capped at 3.0x)

    Args:
        num_drivers   : Number of available drivers in the area
        num_requests  : Number of concurrent active ride requests
        distance_km   : Estimated trip distance

    Returns:
        Tuple of (surge_multiplier, estimated_fare_in_INR)
    """
    if num_drivers == 0:
        surge_multiplier = MAX_SURGE_MULTIPLIER
    else:
        demand_ratio = num_requests / num_drivers

        if demand_ratio < 1.5:
            surge_multiplier = 1.0
        elif demand_ratio < 3.0:
            surge_multiplier = 1.5
        elif demand_ratio < 5.0:
            surge_multiplier = 2.0
        else:
            surge_multiplier = MAX_SURGE_MULTIPLIER

    fare = (BASE_FARE + RATE_PER_KM * distance_km) * surge_multiplier
    return surge_multiplier, round(fare, 2)
