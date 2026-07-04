"""Google OR-Tools Vehicle Routing Problem (VRP) solver service."""

import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from app.models import (
    DeliveryStop,
    VehicleConfig,
    OptimizationOptions,
    OptimizedRoute,
    StopItinerary,
)

logger = logging.getLogger(__name__)


class VRPSolver:
    """Vehicle Routing Problem solver using Google OR-Tools."""

    def __init__(
        self,
        depot_index: int,
        num_vehicles: int,
        vehicle_capacities: List[int],
        time_matrix: List[List[float]],  # seconds
        distance_matrix: List[List[float]],  # meters
        demands: List[int],
        service_times: List[int],  # minutes
        time_windows: List[Tuple[int, int]],  # (earliest_minutes, latest_minutes)
        options: OptimizationOptions,
    ):
        """
        Initialize VRP solver.

        Args:
            depot_index: Index of depot in matrices (usually 0)
            num_vehicles: Number of vehicles in fleet
            vehicle_capacities: Capacity of each vehicle
            time_matrix: Travel time matrix in seconds
            distance_matrix: Distance matrix in meters
            demands: Demand at each location (0 for depot)
            service_times: Service time at each location in minutes
            time_windows: Time window for each location (minutes from start)
            options: Optimization options
        """
        self.depot_index = depot_index
        self.num_vehicles = num_vehicles
        self.num_locations = len(time_matrix)
        self.vehicle_capacities = vehicle_capacities
        self.time_matrix = time_matrix
        self.distance_matrix = distance_matrix
        self.demands = demands
        self.service_times = service_times
        self.time_windows = time_windows
        self.options = options

        # Create routing model
        self.manager = pywrapcp.RoutingIndexManager(
            self.num_locations, self.num_vehicles, self.depot_index
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

        # Store solution
        self.solution: Optional[Any] = None

    def _create_time_callback(self, manager, time_matrix):
        """Create callback for travel time."""

        def time_callback(from_index: int, to_index: int) -> int:
            """Return travel time between two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(time_matrix[from_node][to_node])

        return time_callback

    def _create_distance_callback(self, manager, distance_matrix):
        """Create callback for distance."""

        def distance_callback(from_index: int, to_index: int) -> int:
            """Return distance between two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node])

        return distance_callback

    def _create_demand_callback(self, manager, demands):
        """Create callback for demand."""

        def demand_callback(from_index: int) -> int:
            """Return demand at node."""
            from_node = manager.IndexToNode(from_index)
            return demands[from_node]

        return demand_callback

    def solve(self) -> bool:
        """
        Solve the VRP.

        Returns:
            True if solution found, False otherwise
        """
        logger.info(
            f"Solving VRP with {self.num_locations} locations, "
            f"{self.num_vehicles} vehicles"
        )

        # Register time callback
        time_callback = self._create_time_callback(self.manager, self.time_matrix)
        time_callback_index = self.routing.RegisterTransitCallback(time_callback)

        # Set arc cost (primary objective: minimize time)
        self.routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)

        # Add time dimension (accounts for service time + travel time)
        time_dimension_name = "Time"
        max_time = 24 * 60 * 60  # 24 hours in seconds
        self.routing.AddDimension(
            time_callback_index,
            max_time,  # allow waiting time
            max_time,  # maximum time per vehicle
            False,  # don't force start cumul to zero
            time_dimension_name,
        )
        time_dimension = self.routing.GetDimensionOrDie(time_dimension_name)

        # Add time windows if enabled
        if self.options.use_time_windows and any(
            tw != (0, max_time) for tw in self.time_windows
        ):
            logger.info("Adding time window constraints")
            for location_idx in range(self.num_locations):
                if location_idx == self.depot_index:
                    continue
                index = self.manager.NodeToIndex(location_idx)
                earliest, latest = self.time_windows[location_idx]
                time_dimension.CumulVar(index).SetRange(
                    earliest * 60, latest * 60  # convert to seconds
                )

        # Add service time constraints
        for location_idx in range(self.num_locations):
            index = self.manager.NodeToIndex(location_idx)
            service_time_seconds = self.service_times[location_idx] * 60
            time_dimension.SetCumulVarSoftUpperBound(
                index, service_time_seconds, 100000
            )

        # Add capacity constraints if enabled
        if self.options.use_capacity_constraints and max(self.demands) > 0:
            logger.info("Adding capacity constraints")
            demand_callback = self._create_demand_callback(self.manager, self.demands)
            demand_callback_index = self.routing.RegisterUnaryTransitCallback(
                demand_callback
            )
            self.routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                0,  # null capacity slack
                self.vehicle_capacities,  # vehicle capacities
                True,  # start cumul to zero
                "Capacity",
            )

        # Add distance dimension (secondary objective)
        distance_callback = self._create_distance_callback(
            self.manager, self.distance_matrix
        )
        distance_callback_index = self.routing.RegisterTransitCallback(
            distance_callback
        )
        self.routing.AddDimension(
            distance_callback_index,
            0,  # no slack
            999999999,  # maximum distance
            True,  # start cumul to zero
            "Distance",
        )
        distance_dimension = self.routing.GetDimensionOrDie("Distance")
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Configure depot returns
        if self.options.depot_return_required:
            for vehicle_id in range(self.num_vehicles):
                self.routing.AddVariableMinimizedByFinalizer(
                    time_dimension.CumulVar(self.routing.Start(vehicle_id))
                )
                self.routing.AddVariableMinimizedByFinalizer(
                    time_dimension.CumulVar(self.routing.End(vehicle_id))
                )

        # Allow dropping nodes if constraints can't be satisfied
        if self.options.allow_unassigned_stops:
            penalty = 1000000  # high penalty for dropping nodes
            for node in range(1, self.num_locations):  # skip depot
                self.routing.AddDisjunction([self.manager.NodeToIndex(node)], penalty)

        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = self.options.time_limit_seconds
        search_parameters.log_search = self.options.time_limit_seconds > 30

        # Solve
        logger.info(f"Starting optimization (time limit: {self.options.time_limit_seconds}s)")
        self.solution = self.routing.SolveWithParameters(search_parameters)

        if self.solution:
            logger.info(f"Solution found! Objective value: {self.solution.ObjectiveValue()}")
            return True
        else:
            logger.warning("No solution found")
            return False

    def get_solution(self) -> Dict[str, Any]:
        """
        Extract solution details.

        Returns:
            Dictionary with routes, times, distances, etc.
        """
        if not self.solution:
            raise ValueError("No solution available. Call solve() first.")

        routes = []
        total_time = 0
        total_distance = 0
        time_dimension = self.routing.GetDimensionOrDie("Time")
        distance_dimension = self.routing.GetDimensionOrDie("Distance")
        unassigned = []

        # Check for unassigned nodes
        for node in range(self.num_locations):
            if node == self.depot_index:
                continue
            index = self.manager.NodeToIndex(node)
            if self.solution.Value(self.routing.NextVar(index)) == index:
                unassigned.append(node)

        # Extract routes for each vehicle
        for vehicle_id in range(self.num_vehicles):
            route_nodes = []
            route_times = []
            route_distances = []

            index = self.routing.Start(vehicle_id)
            route_distance = 0
            route_time = 0

            while not self.routing.IsEnd(index):
                node = self.manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                distance_var = distance_dimension.CumulVar(index)

                route_nodes.append(node)
                route_times.append(self.solution.Value(time_var))
                route_distances.append(self.solution.Value(distance_var))

                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))

            # Add final depot
            node = self.manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            distance_var = distance_dimension.CumulVar(index)

            route_nodes.append(node)
            route_times.append(self.solution.Value(time_var))
            route_distances.append(self.solution.Value(distance_var))

            route_time = route_times[-1] - route_times[0]
            route_distance = route_distances[-1]

            # Only include routes that visit at least one customer
            if len(route_nodes) > 2:  # More than just start and end depot
                routes.append(
                    {
                        "vehicle_id": vehicle_id,
                        "nodes": route_nodes,
                        "times": route_times,
                        "distances": route_distances,
                        "total_time_seconds": route_time,
                        "total_distance_meters": route_distance,
                    }
                )
                total_time += route_time
                total_distance += route_distance

        return {
            "routes": routes,
            "total_time_seconds": total_time,
            "total_distance_meters": total_distance,
            "unassigned_nodes": unassigned,
            "objective_value": self.solution.ObjectiveValue(),
        }


def solve_vrp(
    depot: Tuple[float, float],
    stops: List[DeliveryStop],
    vehicles: VehicleConfig,
    time_matrix: List[List[float]],
    distance_matrix: List[List[float]],
    options: OptimizationOptions,
) -> Dict[str, Any]:
    """
    Solve Vehicle Routing Problem.

    Args:
        depot: Depot (lat, lng)
        stops: List of delivery stops
        vehicles: Vehicle configuration
        time_matrix: Travel time matrix in seconds
        distance_matrix: Distance matrix in meters
        options: Optimization options

    Returns:
        Solution dictionary with routes and metrics
    """
    num_locations = len(stops) + 1  # stops + depot
    num_vehicles = vehicles.count

    # Prepare demands (depot has 0 demand)
    demands = [0] + [stop.demand for stop in stops]

    # Prepare service times (depot has 0 service time)
    service_times = [0] + [stop.service_time_minutes for stop in stops]

    # Prepare time windows
    # Convert time windows to minutes from start time
    start_time = datetime.strptime(vehicles.start_time, "%H:%M")
    max_duration_minutes = vehicles.max_duration_minutes

    time_windows = [(0, max_duration_minutes)]  # depot window

    for stop in stops:
        if stop.time_window and stop.time_window.earliest and stop.time_window.latest:
            try:
                earliest = datetime.strptime(stop.time_window.earliest, "%H:%M")
                latest = datetime.strptime(stop.time_window.latest, "%H:%M")

                earliest_minutes = int((earliest - start_time).total_seconds() / 60)
                latest_minutes = int((latest - start_time).total_seconds() / 60)

                time_windows.append((earliest_minutes, latest_minutes))
            except:
                # Invalid time window, use full range
                time_windows.append((0, max_duration_minutes))
        else:
            time_windows.append((0, max_duration_minutes))

    # Vehicle capacities
    vehicle_capacities = [vehicles.capacity] * num_vehicles

    # Create and solve VRP
    solver = VRPSolver(
        depot_index=0,
        num_vehicles=num_vehicles,
        vehicle_capacities=vehicle_capacities,
        time_matrix=time_matrix,
        distance_matrix=distance_matrix,
        demands=demands,
        service_times=service_times,
        time_windows=time_windows,
        options=options,
    )

    success = solver.solve()

    if not success:
        return {
            "success": False,
            "routes": [],
            "total_time_seconds": 0,
            "total_distance_meters": 0,
            "unassigned_nodes": [],
        }

    solution = solver.get_solution()
    solution["success"] = True
    return solution
