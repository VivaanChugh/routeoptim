"""Data models and schemas."""

from datetime import time
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Location(BaseModel):
    """Geographic location."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    name: str = Field(..., min_length=1, max_length=100, description="Location name")


class TimeWindow(BaseModel):
    """Delivery time window constraint."""

    earliest: Optional[str] = Field(None, description="Earliest delivery time (HH:MM)")
    latest: Optional[str] = Field(None, description="Latest delivery time (HH:MM)")

    @field_validator("earliest", "latest")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format."""
        if v is None:
            return v
        try:
            # Parse time to validate format
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time range")
            return v
        except Exception:
            raise ValueError("Time must be in HH:MM format")


class DeliveryStop(BaseModel):
    """A delivery stop location with constraints."""

    id: str = Field(..., description="Unique stop identifier")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    name: str = Field(..., min_length=1, max_length=100, description="Stop name")
    service_time_minutes: int = Field(
        default=5, ge=0, le=120, description="Service time in minutes"
    )
    demand: int = Field(
        default=0, ge=0, le=1000, description="Package demand (weight/volume units)"
    )
    time_window: Optional[TimeWindow] = Field(
        None, description="Delivery time window"
    )
    priority: int = Field(
        default=1, ge=1, le=5, description="Priority level (1=low, 5=urgent)"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Additional notes"
    )


class VehicleConfig(BaseModel):
    """Vehicle fleet configuration."""

    count: int = Field(
        default=1, ge=1, le=5, description="Number of vehicles/drivers"
    )
    capacity: int = Field(
        default=100, ge=1, le=10000, description="Vehicle capacity (weight/volume units)"
    )
    max_duration_minutes: int = Field(
        default=480, ge=60, le=960, description="Maximum route duration in minutes"
    )
    start_time: str = Field(
        default="09:00", description="Route start time (HH:MM)"
    )

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: str) -> str:
        """Validate start time format."""
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time range")
            return v
        except Exception:
            raise ValueError("Start time must be in HH:MM format")


class OptimizationOptions(BaseModel):
    """Optimization solver options."""

    time_limit_seconds: int = Field(
        default=10, ge=1, le=300, description="Solver time limit"
    )
    use_capacity_constraints: bool = Field(
        default=True, description="Enable capacity constraints"
    )
    use_time_windows: bool = Field(
        default=True, description="Enable time window constraints"
    )
    allow_unassigned_stops: bool = Field(
        default=False, description="Allow stops to be unassigned if constraints can't be met"
    )
    depot_return_required: bool = Field(
        default=True, description="Require vehicles to return to depot"
    )


class RouteOptimizationRequest(BaseModel):
    """Request to optimize a delivery route."""

    depot: Location = Field(..., description="Starting depot location")
    stops: List[DeliveryStop] = Field(
        ..., min_length=2, max_length=25, description="Delivery stops"
    )
    vehicles: VehicleConfig = Field(
        default_factory=VehicleConfig, description="Vehicle configuration"
    )
    options: OptimizationOptions = Field(
        default_factory=OptimizationOptions, description="Optimization options"
    )

    @model_validator(mode='after')
    def validate_stops(self) -> 'RouteOptimizationRequest':
        """Validate stop constraints."""
        if len(self.stops) < 2:
            raise ValueError("At least 2 stops required")
        if len(self.stops) > 25:
            raise ValueError("Maximum 25 stops allowed")
        
        # Check for duplicate IDs
        stop_ids = [stop.id for stop in self.stops]
        if len(stop_ids) != len(set(stop_ids)):
            raise ValueError("Duplicate stop IDs found")
        
        return self


class StopItinerary(BaseModel):
    """Itinerary details for a single stop."""

    stop_id: str
    stop_name: str
    sequence: int
    arrival_time: str  # HH:MM format
    service_start_time: str = ""  # HH:MM format (if waiting due to time window)
    departure_time: str  # HH:MM format
    service_time_minutes: int
    waiting_time_minutes: int = 0  # Time spent waiting for time window
    cumulative_distance_km: float
    cumulative_time_minutes: int
    lat: float
    lng: float


class OptimizedRoute(BaseModel):
    """Optimized route for a single vehicle."""

    vehicle_id: int
    driver_name: str = Field(default="")
    stops: List[str]  # Stop IDs in order
    total_time_minutes: float  # Total route time (driving + service + waiting)
    driving_time_minutes: float  # Driving time only
    service_time_minutes: float  # Service time only
    waiting_time_minutes: float = 0.0  # Waiting time for time windows
    total_distance_km: float
    total_demand: int
    route_geometry: List[List[float]]  # List of [lat, lng] coordinates
    itinerary: List[StopItinerary]


class RouteSummary(BaseModel):
    """Summary of optimization results."""

    total_time_minutes: float  # Total driver time (sum of all routes) - DEPRECATED, use total_driver_time_minutes
    total_driver_time_minutes: float  # Total driver time (sum of all routes)
    total_driving_time_minutes: float  # Total driving time only
    total_service_time_minutes: float  # Total service time only
    total_waiting_time_minutes: float = 0.0  # Total waiting time for time windows
    completion_time_minutes: float  # Makespan (longest route)
    total_distance_km: float
    time_saved_minutes: Optional[float] = None
    percentage_improvement: Optional[float] = None
    stops_assigned: int
    stops_total: int
    vehicles_used: int


class RouteOptimizationResponse(BaseModel):
    """Response from route optimization."""

    success: bool
    routes: List[OptimizedRoute]
    summary: RouteSummary
    unassigned_stops: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    computation_time_seconds: float
    timing_breakdown: Dict[str, float] = Field(default_factory=dict)  # Timing details
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    osrm_available: bool
    redis_available: bool = False
