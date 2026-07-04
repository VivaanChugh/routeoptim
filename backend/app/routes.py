"""API routes."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models import (
    RouteOptimizationRequest,
    RouteOptimizationResponse,
    ErrorResponse,
    HealthResponse,
)
from app.services import get_optimization_service, get_osrm_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create router
api_router = APIRouter()


@api_router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Checks:
    - API availability
    - OSRM service connectivity
    """
    osrm_service = get_osrm_service()
    osrm_available = await osrm_service.check_availability()

    return HealthResponse(
        status="healthy" if osrm_available else "degraded",
        version=settings.app_version,
        osrm_available=osrm_available,
        redis_available=False,  # TODO: Implement Redis check
    )


@api_router.post("/optimize", response_model=RouteOptimizationResponse)
async def optimize_route(request: RouteOptimizationRequest):
    """
    Optimize delivery route.

    This endpoint:
    1. Validates input (depot, stops, constraints)
    2. Fetches real driving time matrix from OSRM
    3. Solves Vehicle Routing Problem with OR-Tools
    4. Returns optimized routes with geometries and itineraries

    Args:
        request: Route optimization request with depot, stops, vehicles, and options

    Returns:
        Optimized routes with metrics, geometries, and itineraries

    Raises:
        HTTPException: If optimization fails or constraints are invalid
    """
    try:
        # Validate request
        if len(request.stops) < settings.min_stops:
            raise HTTPException(
                status_code=400,
                detail=f"At least {settings.min_stops} stops required",
            )

        if len(request.stops) > settings.max_stops:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {settings.max_stops} stops allowed",
            )

        if request.vehicles.count > settings.max_vehicles:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {settings.max_vehicles} vehicles allowed",
            )

        # Optimize route
        optimization_service = get_optimization_service()
        response = await optimization_service.optimize_route(request)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}",
        )


@api_router.get("/sample-scenarios")
async def get_sample_scenarios() -> Dict[str, Any]:
    """
    Get sample delivery scenarios for different cities.

    Returns:
        Dictionary of sample scenarios (Toronto, Waterloo, San Francisco)
    """
    scenarios = {
        "toronto": {
            "name": "Toronto Downtown Deliveries",
            "description": "20 stops across downtown core with time windows",
            "depot": {
                "lat": 43.6426,
                "lng": -79.3871,
                "name": "CN Tower Distribution Center",
            },
            "stops": [
                {
                    "id": "tor-1",
                    "lat": 43.6532,
                    "lng": -79.3832,
                    "name": "Union Station",
                    "service_time_minutes": 5,
                    "demand": 10,
                },
                {
                    "id": "tor-2",
                    "lat": 43.6629,
                    "lng": -79.3957,
                    "name": "City Hall",
                    "service_time_minutes": 5,
                    "demand": 8,
                },
                {
                    "id": "tor-3",
                    "lat": 43.6677,
                    "lng": -79.3948,
                    "name": "Dundas Square",
                    "service_time_minutes": 7,
                    "demand": 12,
                    "time_window": {"earliest": "09:00", "latest": "11:00"},
                },
                {
                    "id": "tor-4",
                    "lat": 43.6708,
                    "lng": -79.3899,
                    "name": "Ryerson University",
                    "service_time_minutes": 5,
                    "demand": 15,
                },
                {
                    "id": "tor-5",
                    "lat": 43.6533,
                    "lng": -79.3756,
                    "name": "St. Lawrence Market",
                    "service_time_minutes": 10,
                    "demand": 20,
                    "time_window": {"earliest": "08:00", "latest": "10:00"},
                },
                {
                    "id": "tor-6",
                    "lat": 43.6481,
                    "lng": -79.3773,
                    "name": "Distillery District",
                    "service_time_minutes": 8,
                    "demand": 10,
                },
                {
                    "id": "tor-7",
                    "lat": 43.6465,
                    "lng": -79.3744,
                    "name": "Corktown",
                    "service_time_minutes": 5,
                    "demand": 8,
                },
                {
                    "id": "tor-8",
                    "lat": 43.6579,
                    "lng": -79.3873,
                    "name": "Eaton Centre",
                    "service_time_minutes": 10,
                    "demand": 25,
                    "time_window": {"earliest": "10:00", "latest": "12:00"},
                },
                {
                    "id": "tor-9",
                    "lat": 43.6668,
                    "lng": -79.3815,
                    "name": "Church-Wellesley Village",
                    "service_time_minutes": 5,
                    "demand": 12,
                },
                {
                    "id": "tor-10",
                    "lat": 43.6565,
                    "lng": -79.3799,
                    "name": "Yonge-Dundas",
                    "service_time_minutes": 6,
                    "demand": 10,
                },
            ],
            "vehicles": {"count": 2, "capacity": 100, "max_duration_minutes": 300},
        },
        "waterloo": {
            "name": "Waterloo Tech Corridor",
            "description": "15 stops across Waterloo tech companies and universities",
            "depot": {
                "lat": 43.4643,
                "lng": -80.5204,
                "name": "Conestoga Mall Distribution",
            },
            "stops": [
                {
                    "id": "wat-1",
                    "lat": 43.4723,
                    "lng": -80.5449,
                    "name": "University of Waterloo",
                    "service_time_minutes": 10,
                    "demand": 20,
                },
                {
                    "id": "wat-2",
                    "lat": 43.4734,
                    "lng": -80.5378,
                    "name": "Wilfrid Laurier University",
                    "service_time_minutes": 8,
                    "demand": 15,
                },
                {
                    "id": "wat-3",
                    "lat": 43.4516,
                    "lng": -80.4925,
                    "name": "Google Kitchener",
                    "service_time_minutes": 5,
                    "demand": 10,
                    "time_window": {"earliest": "09:00", "latest": "11:00"},
                },
                {
                    "id": "wat-4",
                    "lat": 43.4501,
                    "lng": -80.4959,
                    "name": "Communitech Hub",
                    "service_time_minutes": 7,
                    "demand": 12,
                },
                {
                    "id": "wat-5",
                    "lat": 43.4553,
                    "lng": -80.4897,
                    "name": "Shopify Waterloo",
                    "service_time_minutes": 5,
                    "demand": 8,
                },
                {
                    "id": "wat-6",
                    "lat": 43.4615,
                    "lng": -80.5213,
                    "name": "Uptown Waterloo",
                    "service_time_minutes": 6,
                    "demand": 10,
                },
                {
                    "id": "wat-7",
                    "lat": 43.4589,
                    "lng": -80.5125,
                    "name": "Waterloo Town Square",
                    "service_time_minutes": 8,
                    "demand": 15,
                },
            ],
            "vehicles": {"count": 1, "capacity": 100, "max_duration_minutes": 240},
        },
        "san_francisco": {
            "name": "San Francisco Hills Challenge",
            "description": "25 stops across SF with elevation and time constraints",
            "depot": {
                "lat": 37.8080,
                "lng": -122.4177,
                "name": "Fisherman's Wharf Depot",
            },
            "stops": [
                {
                    "id": "sf-1",
                    "lat": 37.7749,
                    "lng": -122.4194,
                    "name": "Downtown SF",
                    "service_time_minutes": 5,
                    "demand": 10,
                },
                {
                    "id": "sf-2",
                    "lat": 37.7955,
                    "lng": -122.4030,
                    "name": "North Beach",
                    "service_time_minutes": 6,
                    "demand": 12,
                },
                {
                    "id": "sf-3",
                    "lat": 37.8024,
                    "lng": -122.4058,
                    "name": "Telegraph Hill",
                    "service_time_minutes": 8,
                    "demand": 8,
                    "time_window": {"earliest": "09:00", "latest": "11:00"},
                },
                {
                    "id": "sf-4",
                    "lat": 37.7937,
                    "lng": -122.4078,
                    "name": "Chinatown",
                    "service_time_minutes": 7,
                    "demand": 15,
                },
                {
                    "id": "sf-5",
                    "lat": 37.7858,
                    "lng": -122.4364,
                    "name": "Presidio",
                    "service_time_minutes": 5,
                    "demand": 10,
                },
                {
                    "id": "sf-6",
                    "lat": 37.7694,
                    "lng": -122.4862,
                    "name": "Golden Gate Park",
                    "service_time_minutes": 10,
                    "demand": 20,
                    "time_window": {"earliest": "10:00", "latest": "14:00"},
                },
                {
                    "id": "sf-7",
                    "lat": 37.7599,
                    "lng": -122.4148,
                    "name": "Mission District",
                    "service_time_minutes": 6,
                    "demand": 12,
                },
                {
                    "id": "sf-8",
                    "lat": 37.7694,
                    "lng": -122.4632,
                    "name": "Inner Sunset",
                    "service_time_minutes": 5,
                    "demand": 8,
                },
            ],
            "vehicles": {"count": 3, "capacity": 80, "max_duration_minutes": 360},
        },
    }

    return scenarios


@api_router.get("/config")
async def get_config() -> Dict[str, Any]:
    """
    Get API configuration and limits.

    Returns:
        Configuration settings
    """
    return {
        "max_stops": settings.max_stops,
        "max_vehicles": settings.max_vehicles,
        "min_stops": settings.min_stops,
        "default_vehicle_capacity": settings.default_vehicle_capacity,
        "default_service_time_minutes": settings.default_service_time_minutes,
        "osrm_available": True,
    }
