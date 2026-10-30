"""NAGARPAALAN AI — Geospatial calculation utilities."""

from __future__ import annotations

import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth in meters."""
    # Earth radius in meters
    r = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return r * c


def find_nearest_asset(lat: float, lon: float, assets: list[any], max_distance_m: float = 200.0):
    """Find the closest asset within max_distance_m."""
    closest_asset = None
    min_dist = float("inf")

    for asset in assets:
        dist = haversine_distance(lat, lon, asset.latitude, asset.longitude)
        if dist < min_dist and dist <= max_distance_m:
            min_dist = dist
            closest_asset = (asset, dist)

    return closest_asset
