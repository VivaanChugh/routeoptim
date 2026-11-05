"""Tests for solver handling of malformed input."""

import logging

from app.models import (
    DeliveryStop,
    OptimizationOptions,
    TimeWindow,
    VehicleConfig,
)
from app.services.vrp_solver import solve_vrp

TIME_MATRIX = [[0, 300, 600], [300, 0, 300], [600, 300, 0]]
DIST_MATRIX = [[0, 1000, 2000], [1000, 0, 1000], [2000, 1000, 0]]


def test_invalid_time_window_is_ignored_and_logged(caplog):
    """A malformed window must not crash the solve, and must be reported."""
    bad = TimeWindow.model_construct(earliest="not-a-time", latest="12:00")  # skips validation
    stops = [
        DeliveryStop(id="a", lat=43.66, lng=-79.39, name="A", service_time_minutes=5),
        DeliveryStop.model_construct(
            id="b", lat=43.67, lng=-79.40, name="B", service_time_minutes=5,
            demand=0, time_window=bad, priority=1, notes=None,
        ),
    ]

    with caplog.at_level(logging.WARNING):
        result = solve_vrp(
            depot=(43.65, -79.38),
            stops=stops,
            vehicles=VehicleConfig(start_time="09:00"),
            time_matrix=TIME_MATRIX,
            distance_matrix=DIST_MATRIX,
            options=OptimizationOptions(time_limit_seconds=1),
        )

    assert result["success"]
    assert "Invalid time window for stop 'b'" in caplog.text
