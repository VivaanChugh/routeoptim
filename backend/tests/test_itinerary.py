"""Offline unit tests for itinerary timing (no OSRM / solver required)."""

from app.models import (
    DeliveryStop,
    Location,
    OptimizationOptions,
    RouteOptimizationRequest,
    VehicleConfig,
)
from app.services.optimization_service import OptimizationService


def _service() -> OptimizationService:
    # Bypass __init__ so no OSRM client is created.
    return OptimizationService.__new__(OptimizationService)


def _request(use_time_windows: bool = False) -> RouteOptimizationRequest:
    return RouteOptimizationRequest(
        depot=Location(lat=43.65, lng=-79.38, name="Depot"),
        stops=[
            DeliveryStop(id="a", lat=43.66, lng=-79.39, name="A", service_time_minutes=10),
            DeliveryStop(id="b", lat=43.67, lng=-79.40, name="B", service_time_minutes=5),
        ],
        vehicles=VehicleConfig(start_time="09:00"),
        options=OptimizationOptions(use_time_windows=use_time_windows),
    )


# Leg travel times in seconds: depot->A 10 min, A->B 15 min, B->depot 10 min.
TIME_MATRIX = [[0, 600, 1500], [600, 0, 900], [600, 900, 0]]


def _build(request: RouteOptimizationRequest):
    coords = [(request.depot.lat, request.depot.lng)] + [
        (s.lat, s.lng) for s in request.stops
    ]
    return _service()._build_itinerary(
        node_indices=[0, 1, 2, 0],
        node_times=[],
        node_distances=[0, 1000, 2000, 3000],
        request=request,
        coordinates=coords,
        time_matrix=TIME_MATRIX,
    )


def test_service_time_accumulates_across_stops():
    """Each stop's arrival must include service time spent at earlier stops."""
    itinerary = _build(_request())

    assert [s.arrival_time for s in itinerary] == ["09:00", "09:10", "09:35", "09:50"]
    assert [s.departure_time for s in itinerary] == ["09:00", "09:20", "09:40", "09:50"]
    assert all(s.waiting_time_minutes == 0 for s in itinerary)


def test_sequence_and_ids_follow_route_order():
    itinerary = _build(_request())

    assert [s.sequence for s in itinerary] == [0, 1, 2, 3]
    assert [s.stop_id for s in itinerary] == ["depot", "a", "b", "depot"]


def test_cumulative_distance_is_reported_in_km():
    itinerary = _build(_request())

    assert [s.cumulative_distance_km for s in itinerary] == [0, 1, 2, 3]
