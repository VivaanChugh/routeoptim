"""Main optimization service that coordinates OSRM and OR-Tools."""

import logging
import time
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta

from app.models import (
    RouteOptimizationRequest,
    RouteOptimizationResponse,
    OptimizedRoute,
    StopItinerary,
    RouteSummary,
    DeliveryStop,
    Location,
)
from app.services.osrm_service import get_osrm_service
from app.services.vrp_solver import solve_vrp

logger = logging.getLogger(__name__)


class OptimizationService:
    """Main service for route optimization."""

    def __init__(self):
        """Initialize optimization service."""
        self.osrm_service = get_osrm_service()

    async def optimize_route(
        self, request: RouteOptimizationRequest
    ) -> RouteOptimizationResponse:
        """
        Optimize delivery route.

        Args:
            request: Route optimization request

        Returns:
            Optimization response with routes and metrics
        """
        start_time = time.time()
        warnings = []
        
        # Track timing breakdown
        timing_breakdown = {}
        timing_start = time.time()

        try:
            # Step 1: Prepare coordinates (depot + stops)
            coordinates = self._prepare_coordinates(request)
            logger.info(f"Optimizing route with {len(coordinates)} locations")
            timing_breakdown["coordinates_prep"] = time.time() - timing_start

            # Step 2: Get travel time matrix from OSRM
            logger.info("Fetching travel time matrix from OSRM...")
            timing_start = time.time()
            time_matrix, distance_matrix = await self.osrm_service.get_travel_time_matrix(
                coordinates
            )
            timing_breakdown["osrm_matrix_fetch"] = time.time() - timing_start

            # Step 3: Solve VRP with OR-Tools
            logger.info("Solving VRP with OR-Tools...")
            timing_start = time.time()
            vrp_solution = solve_vrp(
                depot=(request.depot.lat, request.depot.lng),
                stops=request.stops,
                vehicles=request.vehicles,
                time_matrix=time_matrix,
                distance_matrix=distance_matrix,
                options=request.options,
            )
            timing_breakdown["vrp_solver"] = time.time() - timing_start

            if not vrp_solution.get("success"):
                raise Exception("VRP solver failed to find a solution")

            # Step 4: Get route geometries from OSRM
            logger.info("Fetching route geometries from OSRM...")
            timing_start = time.time()
            optimized_routes = await self._build_optimized_routes(
                vrp_solution=vrp_solution,
                request=request,
                coordinates=coordinates,
            )
            timing_breakdown["geometry_fetch"] = time.time() - timing_start

            # Step 5: Build response
            computation_time = time.time() - start_time

            # Calculate unassigned stops
            unassigned_node_indices = vrp_solution.get("unassigned_nodes", [])
            unassigned_stop_ids = [
                request.stops[idx - 1].id
                for idx in unassigned_node_indices
                if idx > 0
            ]

            if unassigned_stop_ids:
                warnings.append(
                    f"{len(unassigned_stop_ids)} stops could not be assigned due to constraints"
                )

            # Calculate summary with proper timing breakdown
            stops_assigned = len(request.stops) - len(unassigned_stop_ids)
            
            # Calculate total driving, service, and waiting time across all routes
            total_driving_time_minutes = sum(route.driving_time_minutes for route in optimized_routes)
            total_service_time_minutes = sum(route.service_time_minutes for route in optimized_routes)
            total_waiting_time_minutes = sum(route.waiting_time_minutes for route in optimized_routes)
            
            # Total driver time = sum of all routes (all drivers working)
            total_driver_time_minutes = sum(route.total_time_minutes for route in optimized_routes)
            
            # Completion time (makespan) = max of all route total times (when last driver finishes)
            completion_time_minutes = max(
                (route.total_time_minutes for route in optimized_routes),
                default=0.0
            )
            
            # Total distance across all routes
            total_distance_km = sum(route.total_distance_km for route in optimized_routes)

            summary = RouteSummary(
                total_time_minutes=total_driver_time_minutes,  # Deprecated field
                total_driver_time_minutes=total_driver_time_minutes,
                total_distance_km=total_distance_km,
                stops_assigned=stops_assigned,
                stops_total=len(request.stops),
                vehicles_used=len(optimized_routes),
                total_driving_time_minutes=total_driving_time_minutes,
                total_service_time_minutes=total_service_time_minutes,
                total_waiting_time_minutes=total_waiting_time_minutes,
                completion_time_minutes=completion_time_minutes,
            )

            response = RouteOptimizationResponse(
                success=True,
                routes=optimized_routes,
                summary=summary,
                unassigned_stops=unassigned_stop_ids,
                warnings=warnings,
                computation_time_seconds=computation_time,
                timing_breakdown=timing_breakdown,
                metadata={
                    "osrm_base_url": self.osrm_service.base_url,
                    "solver_time_limit": request.options.time_limit_seconds,
                    "vrp_objective_value": vrp_solution.get("objective_value", 0),
                },
            )

            logger.info(
                f"Optimization completed in {computation_time:.2f}s - "
                f"{len(optimized_routes)} routes, {stops_assigned}/{len(request.stops)} stops assigned"
            )

            return response

        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            raise

    def _prepare_coordinates(
        self, request: RouteOptimizationRequest
    ) -> List[Tuple[float, float]]:
        """Prepare coordinate list: [depot, stop1, stop2, ...]"""
        coordinates = [(request.depot.lat, request.depot.lng)]
        coordinates.extend((stop.lat, stop.lng) for stop in request.stops)
        return coordinates

    async def _build_optimized_routes(
        self,
        vrp_solution: Dict[str, Any],
        request: RouteOptimizationRequest,
        coordinates: List[Tuple[float, float]],
    ) -> List[OptimizedRoute]:
        """
        Build OptimizedRoute objects with geometries and itineraries.

        Args:
            vrp_solution: Solution from VRP solver
            request: Original request
            coordinates: List of all coordinates [depot, stops...]

        Returns:
            List of OptimizedRoute objects
        """
        optimized_routes = []

        for route_data in vrp_solution["routes"]:
            vehicle_id = route_data["vehicle_id"]
            node_indices = route_data["nodes"]
            node_times = route_data["times"]  # cumulative seconds
            node_distances = route_data["distances"]  # cumulative meters

            # Get stop IDs in order (excluding depot at start/end)
            stop_ids = []
            for node_idx in node_indices[1:-1]:  # Skip first and last depot
                if node_idx > 0:  # 0 is depot
                    stop_ids.append(request.stops[node_idx - 1].id)

            # Get route coordinates for OSRM geometry
            route_coordinates = [coordinates[idx] for idx in node_indices]

            # Fetch route geometry from OSRM
            try:
                route_segment = await self.osrm_service.get_route_geometry(
                    route_coordinates
                )
                geometry = route_segment.geometry
            except Exception as e:
                logger.warning(f"Failed to get route geometry: {e}, using straight lines")
                geometry = [[lat, lng] for lat, lng in route_coordinates]

            # Build itinerary
            itinerary = self._build_itinerary(
                node_indices=node_indices,
                node_times=node_times,
                node_distances=node_distances,
                request=request,
                coordinates=coordinates,
            )

            # Calculate total service time for this route
            total_service_time_minutes = sum(
                request.stops[idx - 1].service_time_minutes
                for idx in node_indices[1:-1]
                if idx > 0
            )
            
            # Calculate total waiting time from itinerary
            total_waiting_time_minutes = sum(stop.waiting_time_minutes for stop in itinerary)
            
            # Calculate driving time (total time from OR-Tools is driving time only)
            driving_time_minutes = route_data["total_time_seconds"] / 60
            
            # Total time for route = driving + service + waiting
            total_time_minutes = driving_time_minutes + total_service_time_minutes + total_waiting_time_minutes

            # Calculate total demand for this route
            total_demand = sum(
                request.stops[idx - 1].demand
                for idx in node_indices[1:-1]
                if idx > 0
            )

            optimized_route = OptimizedRoute(
                vehicle_id=vehicle_id,
                driver_name=f"Driver {vehicle_id + 1}",
                stops=stop_ids,
                total_time_minutes=total_time_minutes,
                total_distance_km=route_data["total_distance_meters"] / 1000,
                total_demand=total_demand,
                route_geometry=geometry,
                itinerary=itinerary,
                driving_time_minutes=driving_time_minutes,
                service_time_minutes=total_service_time_minutes,
                waiting_time_minutes=total_waiting_time_minutes,
            )

            optimized_routes.append(optimized_route)

        return optimized_routes

    def _build_itinerary(
        self,
        node_indices: List[int],
        node_times: List[float],  # cumulative seconds from OR-Tools (includes driving + waiting)
        node_distances: List[float],  # cumulative meters
        request: RouteOptimizationRequest,
        coordinates: List[Tuple[float, float]],
    ) -> List[StopItinerary]:
        """Build stop-by-stop itinerary with proper service time accumulation."""
        itinerary = []
        start_time = datetime.strptime(request.vehicles.start_time, "%H:%M")
        
        # Track cumulative service time as we go through stops
        cumulative_service_minutes = 0

        for seq, (node_idx, cum_time, cum_distance) in enumerate(
            zip(node_indices, node_times, node_distances)
        ):
            # Get stop details
            if node_idx == 0:
                # Depot
                stop_id = "depot"
                stop_name = request.depot.name
                service_time = 0
                time_window_start = None
            else:
                stop = request.stops[node_idx - 1]
                stop_id = stop.id
                stop_name = stop.name
                service_time = stop.service_time_minutes
                # Extract time window from nested object
                time_window_start = stop.time_window.earliest if stop.time_window else None

            # Arrival time = start + OR-Tools cumulative time + cumulative service time
            # OR-Tools time includes driving + any waiting for time windows
            arrival_time = start_time + timedelta(seconds=cum_time) + timedelta(minutes=cumulative_service_minutes)
            
            # Check if there's waiting time by comparing to time window
            waiting_time = 0
            service_start_time = arrival_time
            
            if time_window_start and request.options.use_time_windows:
                try:
                    # Parse time window on the same date as arrival_time
                    window_hour, window_minute = map(int, time_window_start.split(":"))
                    window_start = arrival_time.replace(hour=window_hour, minute=window_minute, second=0, microsecond=0)
                    
                    # If we arrive before window opens, there's waiting
                    if arrival_time < window_start:
                        waiting_time = int((window_start - arrival_time).total_seconds() / 60)
                        service_start_time = window_start
                except (ValueError, AttributeError):
                    pass  # Invalid time window format, skip waiting
            
            # Departure time = when service finishes
            departure_time = service_start_time + timedelta(minutes=service_time)

            lat, lng = coordinates[node_idx]

            itinerary.append(
                StopItinerary(
                    stop_id=stop_id,
                    stop_name=stop_name,
                    sequence=seq,
                    arrival_time=arrival_time.strftime("%H:%M"),
                    service_start_time=service_start_time.strftime("%H:%M") if waiting_time > 0 else "",
                    departure_time=departure_time.strftime("%H:%M"),
                    service_time_minutes=service_time,
                    waiting_time_minutes=waiting_time,
                    cumulative_distance_km=cum_distance / 1000,
                    cumulative_time_minutes=int((cum_time / 60) + cumulative_service_minutes + waiting_time),
                    lat=lat,
                    lng=lng,
                )
            )
            
            # Add this stop's service time to cumulative
            cumulative_service_minutes += service_time

        return itinerary


# Singleton instance
_optimization_service: Optional[OptimizationService] = None


def get_optimization_service() -> OptimizationService:
    """Get or create optimization service singleton."""
    global _optimization_service
    if _optimization_service is None:
        _optimization_service = OptimizationService()
    return _optimization_service
