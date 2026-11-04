"""Regression tests for time-window waiting and service-time handling.

Scenario: start 09:00. Stop A is 5 min away (10 min service). Stop B is a further
5 min away with a window opening at 09:40, so the driver must wait.
"""

from app.models import (
    DeliveryStop,
    Location,
    OptimizationOptions,
    RouteOptimizationRequest,
    TimeWindow,
    VehicleConfig,
)
from app.services.optimization_service import OptimizationService
from app.services.vrp_solver import solve_vrp

# seconds / meters; node order: depot, A, B
TIME_MATRIX = [[0, 300, 600], [300, 0, 300], [600, 300, 0]]
DIST_MATRIX = [[0, 1000, 2000], [1000, 0, 1000], [2000, 1000, 0]]


def _stops():
    return [
        DeliveryStop(id="a", lat=43.66, lng=-79.39, name="A", service_time_minutes=10),
        DeliveryStop(
            id="b",
            lat=43.67,
            lng=-79.40,
            name="B",
            service_time_minutes=10,
            time_window=TimeWindow(earliest="09:40", latest="12:00"),
        ),
    ]


def _request(use_time_windows=True):
    return RouteOptimizationRequest(
        depot=Location(lat=43.65, lng=-79.38, name="Depot"),
        stops=_stops(),
        vehicles=VehicleConfig(start_time="09:00"),
        options=OptimizationOptions(use_time_windows=use_time_windows, time_limit_seconds=1),
    )


def _itinerary(request):
    service = OptimizationService.__new__(OptimizationService)  # skip OSRM client init
    coords = [(request.depot.lat, request.depot.lng)] + [(s.lat, s.lng) for s in request.stops]
    return service._build_itinerary(
        node_indices=[0, 1, 2, 0],
        node_times=[],
        node_distances=[0, 1000, 2000, 4000],
        request=request,
        coordinates=coords,
        time_matrix=TIME_MATRIX,
    )


def test_early_arrival_waits_for_window_to_open():
    a, b = _itinerary(_request())[1:3]

    assert (a.arrival_time, a.departure_time) == ("09:05", "09:15")
    # Leaves A at 09:15, arrives B at 09:20 -- before its 09:40 window opens.
    assert b.arrival_time == "09:20"
    assert b.waiting_time_minutes == 20
    assert b.service_start_time == "09:40"
    assert b.departure_time == "09:50"


def test_return_to_depot_follows_departure_from_last_stop():
    depot_end = _itinerary(_request())[-1]

    assert depot_end.arrival_time == "10:00"  # 09:50 + 10 min drive


def test_no_waiting_when_time_windows_disabled():
    b = _itinerary(_request(use_time_windows=False))[2]

    assert b.waiting_time_minutes == 0
    assert b.arrival_time == "09:20"
    assert b.departure_time == "09:30"


def test_solver_cumulative_time_includes_service_and_waiting():
    """The solver's clock must advance by service time, then wait for the window."""
    request = _request()
    result = solve_vrp(
        depot=(request.depot.lat, request.depot.lng),
        stops=request.stops,
        vehicles=request.vehicles,
        time_matrix=TIME_MATRIX,
        distance_matrix=DIST_MATRIX,
        options=request.options,
    )

    route = result["routes"][0]
    assert route["nodes"] == [0, 1, 2, 0]
    # A: 5 min drive. B: leave A at 15 min, arrive 20, wait until 40.
    assert route["times"][1] == 5 * 60
    assert route["times"][2] == 40 * 60
