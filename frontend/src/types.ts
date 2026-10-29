/**
 * Type definitions for the Route Optimizer application
 */

export interface Location {
  lat: number;
  lng: number;
  name: string;
}

export interface TimeWindow {
  earliest?: string; // HH:MM format
  latest?: string; // HH:MM format
}

export interface DeliveryStop {
  id: string;
  lat: number;
  lng: number;
  name: string;
  service_time_minutes: number;
  demand: number;
  time_window?: TimeWindow;
  priority: number;
  notes?: string;
}

export interface VehicleConfig {
  count: number;
  capacity: number;
  max_duration_minutes: number;
  start_time: string; // HH:MM format
}

export interface OptimizationOptions {
  time_limit_seconds: number;
  use_capacity_constraints: boolean;
  use_time_windows: boolean;
  allow_unassigned_stops: boolean;
  depot_return_required: boolean;
}

export interface RouteOptimizationRequest {
  depot: Location;
  stops: DeliveryStop[];
  vehicles: VehicleConfig;
  options: OptimizationOptions;
}

export interface StopItinerary {
  stop_id: string;
  stop_name: string;
  sequence: number;
  arrival_time: string;
  service_start_time?: string;
  departure_time: string;
  service_time_minutes: number;
  waiting_time_minutes?: number;
  cumulative_distance_km: number;
  cumulative_time_minutes: number;
  lat: number;
  lng: number;
}

export interface OptimizedRoute {
  vehicle_id: number;
  driver_name: string;
  stops: string[]; // stop IDs
  total_time_minutes: number;
  driving_time_minutes: number;
  service_time_minutes: number;
  waiting_time_minutes?: number;
  total_distance_km: number;
  total_demand: number;
  route_geometry: [number, number][]; // [lat, lng] pairs
  itinerary: StopItinerary[];
}

export interface RouteSummary {
  total_time_minutes: number;
  total_driver_time_minutes: number;
  total_driving_time_minutes: number;
  total_service_time_minutes: number;
  total_waiting_time_minutes?: number;
  completion_time_minutes: number;
  total_distance_km: number;
  time_saved_minutes?: number;
  percentage_improvement?: number;
  stops_assigned: number;
  stops_total: number;
  vehicles_used: number;
}

export interface RouteOptimizationResponse {
  success: boolean;
  routes: OptimizedRoute[];
  summary: RouteSummary;
  unassigned_stops: string[];
  warnings: string[];
  computation_time_seconds: number;
  timing_breakdown?: Record<string, number>;
  metadata: Record<string, unknown>;
}

export interface SampleScenario {
  name: string;
  description: string;
  depot: Location;
  stops: DeliveryStop[];
  vehicles: VehicleConfig;
}

export interface HealthResponse {
  status: string;
  version: string;
  osrm_available: boolean;
  redis_available: boolean;
}

export interface ApiConfig {
  max_stops: number;
  max_vehicles: number;
  min_stops: number;
  default_vehicle_capacity: number;
  default_service_time_minutes: number;
  osrm_available: boolean;
}

// UI State Types
export interface AppState {
  depot: Location | null;
  stops: DeliveryStop[];
  vehicles: VehicleConfig;
  options: OptimizationOptions;
  optimizationResult: RouteOptimizationResponse | null;
  isOptimizing: boolean;
  error: string | null;
  selectedScenario: string | null;
}

export const ROUTE_COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // purple
];

export const DEFAULT_VEHICLE_CONFIG: VehicleConfig = {
  count: 1,
  capacity: 100,
  max_duration_minutes: 480,
  start_time: '09:00',
};

export const DEFAULT_OPTIMIZATION_OPTIONS: OptimizationOptions = {
  time_limit_seconds: 5,  // Fast default for demos (1-5s is ideal)
  use_capacity_constraints: true,
  use_time_windows: true,
  allow_unassigned_stops: false,
  depot_return_required: true,
};
