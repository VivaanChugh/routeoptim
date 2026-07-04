"""OSRM (Open Source Routing Machine) integration service."""

import asyncio
import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class RouteSegment:
    """A route segment between two points."""

    distance_meters: float
    duration_seconds: float
    geometry: List[List[float]]  # List of [lat, lng] coordinates


class OSRMService:
    """Service for interacting with OSRM API."""

    def __init__(self):
        """Initialize OSRM service."""
        self.base_url = settings.osrm_base_url.rstrip("/")
        self.profile = settings.osrm_profile
        self.timeout = settings.osrm_timeout

    async def get_travel_time_matrix(
        self, coordinates: List[Tuple[float, float]]
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Get travel time and distance matrices between all coordinate pairs.

        Args:
            coordinates: List of (lat, lng) tuples

        Returns:
            Tuple of (time_matrix_seconds, distance_matrix_meters)
            Both are 2D lists where matrix[i][j] is travel from i to j

        Raises:
            Exception: If OSRM API call fails
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates required")

        if len(coordinates) > 100:
            logger.warning(f"Large matrix requested: {len(coordinates)} points")

        # OSRM table API expects lng,lat format (GeoJSON order)
        coords_str = ";".join(f"{lng},{lat}" for lat, lng in coordinates)
        url = f"{self.base_url}/table/v1/{self.profile}/{coords_str}"

        params = {
            "annotations": "duration,distance",
            "generate_hints": "false",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Requesting OSRM table for {len(coordinates)} points")
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("code") != "Ok":
                    error_msg = data.get("message", "Unknown OSRM error")
                    raise Exception(f"OSRM API error: {error_msg}")

                # Extract matrices
                durations = data.get("durations", [])
                distances = data.get("distances", [])

                if not durations or not distances:
                    raise Exception("OSRM returned empty matrices")

                # Validate matrix dimensions
                n = len(coordinates)
                if len(durations) != n or len(distances) != n:
                    raise Exception("OSRM matrix dimensions mismatch")

                for row in durations + distances:
                    if len(row) != n:
                        raise Exception("OSRM matrix row length mismatch")

                logger.info(
                    f"Successfully retrieved {n}x{n} travel time/distance matrix"
                )
                return durations, distances

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling OSRM: {e}")
            raise Exception(f"Failed to connect to OSRM service: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting OSRM matrix: {e}")
            raise

    async def get_route_geometry(
        self, coordinates: List[Tuple[float, float]], overview: str = "full"
    ) -> RouteSegment:
        """
        Get detailed route geometry between ordered waypoints.

        Args:
            coordinates: List of (lat, lng) tuples in route order
            overview: "full", "simplified", or "false"

        Returns:
            RouteSegment with distance, duration, and geometry

        Raises:
            Exception: If OSRM API call fails
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates required")

        # OSRM route API expects lng,lat format
        coords_str = ";".join(f"{lng},{lat}" for lat, lng in coordinates)
        url = f"{self.base_url}/route/v1/{self.profile}/{coords_str}"

        params = {
            "overview": overview,
            "geometries": "geojson",
            "steps": "false",
            "continue_straight": "false",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("code") != "Ok":
                    error_msg = data.get("message", "Unknown OSRM error")
                    raise Exception(f"OSRM API error: {error_msg}")

                routes = data.get("routes", [])
                if not routes:
                    raise Exception("OSRM returned no routes")

                route = routes[0]
                distance = route.get("distance", 0)  # meters
                duration = route.get("duration", 0)  # seconds

                # Extract geometry (GeoJSON format: [lng, lat])
                geometry_coords = route.get("geometry", {}).get("coordinates", [])
                # Convert to [lat, lng] for Leaflet
                geometry = [[lat, lng] for lng, lat in geometry_coords]

                return RouteSegment(
                    distance_meters=distance,
                    duration_seconds=duration,
                    geometry=geometry,
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling OSRM route API: {e}")
            raise Exception(f"Failed to get route from OSRM: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting OSRM route: {e}")
            raise

    async def check_availability(self) -> bool:
        """
        Check if OSRM service is available.

        Returns:
            True if OSRM is reachable, False otherwise
        """
        try:
            # Simple health check with minimal coordinates
            test_coords = [(43.6532, -79.3832), (43.6426, -79.3871)]
            await self.get_travel_time_matrix(test_coords)
            return True
        except Exception as e:
            logger.error(f"OSRM availability check failed: {e}")
            return False

    async def get_multi_route_geometries(
        self, route_coordinates: List[List[Tuple[float, float]]]
    ) -> List[RouteSegment]:
        """
        Get route geometries for multiple routes in parallel.

        Args:
            route_coordinates: List of routes, each a list of (lat, lng) tuples

        Returns:
            List of RouteSegment objects, one per route
        """
        tasks = [
            self.get_route_geometry(coords) for coords in route_coordinates
        ]
        return await asyncio.gather(*tasks)


# Singleton instance
_osrm_service: Optional[OSRMService] = None


def get_osrm_service() -> OSRMService:
    """Get or create OSRM service singleton."""
    global _osrm_service
    if _osrm_service is None:
        _osrm_service = OSRMService()
    return _osrm_service
