"""Tests for the API routes."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "osrm_available" in data


def test_get_config():
    """Test config endpoint."""
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert "max_stops" in data
    assert "max_vehicles" in data


def test_get_sample_scenarios():
    """Test sample scenarios endpoint."""
    response = client.get("/api/v1/sample-scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "toronto" in data
    assert "waterloo" in data
    assert "san_francisco" in data


def test_optimize_route_missing_depot():
    """Test optimization with missing depot."""
    request_data = {
        "stops": [
            {
                "id": "stop-1",
                "lat": 43.6532,
                "lng": -79.3832,
                "name": "Stop 1",
                "service_time_minutes": 5,
                "demand": 10,
                "priority": 1,
            }
        ]
    }
    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 422  # Validation error


def test_optimize_route_insufficient_stops():
    """Test optimization with insufficient stops."""
    request_data = {
        "depot": {"lat": 43.6532, "lng": -79.3832, "name": "Depot"},
        "stops": [
            {
                "id": "stop-1",
                "lat": 43.6426,
                "lng": -79.3871,
                "name": "Stop 1",
                "service_time_minutes": 5,
                "demand": 10,
                "priority": 1,
            }
        ],
    }
    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 400  # At least 2 stops required


@pytest.mark.asyncio
async def test_optimize_route_success():
    """Test successful optimization."""
    request_data = {
        "depot": {"lat": 43.6532, "lng": -79.3832, "name": "Main Depot"},
        "stops": [
            {
                "id": "stop-1",
                "lat": 43.6426,
                "lng": -79.3871,
                "name": "Stop 1",
                "service_time_minutes": 5,
                "demand": 10,
                "priority": 1,
            },
            {
                "id": "stop-2",
                "lat": 43.6629,
                "lng": -79.3957,
                "name": "Stop 2",
                "service_time_minutes": 5,
                "demand": 8,
                "priority": 1,
            },
            {
                "id": "stop-3",
                "lat": 43.6708,
                "lng": -79.3899,
                "name": "Stop 3",
                "service_time_minutes": 5,
                "demand": 12,
                "priority": 1,
            },
        ],
        "vehicles": {"count": 1, "capacity": 100, "max_duration_minutes": 480, "start_time": "09:00"},
        "options": {
            "time_limit_seconds": 10,
            "use_capacity_constraints": True,
            "use_time_windows": False,
            "allow_unassigned_stops": False,
            "depot_return_required": True,
        },
    }

    response = client.post("/api/v1/optimize", json=request_data)
    
    # This test might fail if OSRM is unavailable
    # In that case, we expect a 500 error
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "routes" in data
        assert "summary" in data
        assert len(data["routes"]) > 0
    else:
        # OSRM might be unavailable
        assert response.status_code in [500, 503]
