/**
 * Results Panel - Shows optimization results and metrics
 */

import { useStore } from '../store';
import { Clock, MapPin, Truck, X } from 'lucide-react';
import { ROUTE_COLORS } from '../types';

export default function ResultsPanel() {
  const { optimizationResult, clearOptimization } = useStore();

  if (!optimizationResult) return null;

  const { routes, summary, unassigned_stops, warnings, computation_time_seconds } =
    optimizationResult;

  return (
    <div className="w-96 bg-white border-l border-gray-200 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Optimization Results</h3>
          <button
            onClick={clearOptimization}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Summary Metrics */}
        <div className="space-y-3">
          {/* Primary Metrics */}
          <div className="grid grid-cols-2 gap-3">
            <div className="card bg-blue-50 border border-blue-200">
              <div className="flex items-center gap-2 text-blue-700 mb-1">
                <Clock className="w-4 h-4" />
                <span className="text-xs font-medium">Completion Time</span>
              </div>
              <div className="text-2xl font-bold text-blue-900">
                {Math.round(summary.completion_time_minutes)} min
              </div>
              <div className="text-xs text-blue-600 mt-1">
                When last driver finishes
              </div>
            </div>

            <div className="card bg-indigo-50 border border-indigo-200">
              <div className="flex items-center gap-2 text-indigo-700 mb-1">
                <Clock className="w-4 h-4" />
                <span className="text-xs font-medium">Total Driver Time</span>
              </div>
              <div className="text-2xl font-bold text-indigo-900">
                {Math.round(summary.total_driver_time_minutes || summary.total_time_minutes)} min
              </div>
              <div className="text-xs text-indigo-600 mt-1">
                All drivers combined
              </div>
            </div>

            <div className="card bg-green-50 border border-green-200">
              <div className="flex items-center gap-2 text-green-700 mb-1">
                <MapPin className="w-4 h-4" />
                <span className="text-xs font-medium">Distance</span>
              </div>
              <div className="text-2xl font-bold text-green-900">
                {summary.total_distance_km.toFixed(1)} km
              </div>
            </div>

            <div className="card bg-purple-50 border border-purple-200">
              <div className="flex items-center gap-2 text-purple-700 mb-1">
                <Truck className="w-4 h-4" />
                <span className="text-xs font-medium">Summary</span>
              </div>
              <div className="text-xs text-purple-900 space-y-0.5">
                <div className="font-bold">Vehicles: {summary.vehicles_used}/{summary.vehicles_used}</div>
                <div className="font-bold">Stops: {summary.stops_assigned}/{summary.stops_total}</div>
                {unassigned_stops.length > 0 && (
                  <div className="text-red-600 font-medium">Dropped: {unassigned_stops.length}</div>
                )}
              </div>
            </div>
          </div>

          {/* Time Breakdown */}
          <div className="card bg-gray-50">
            <div className="text-xs font-medium text-gray-700 mb-2">Time Breakdown</div>
            <div className="space-y-1 text-xs text-gray-600">
              <div className="flex justify-between">
                <span>Driving:</span>
                <span className="font-medium">{Math.round(summary.total_driving_time_minutes)} min</span>
              </div>
              <div className="flex justify-between">
                <span>Service:</span>
                <span className="font-medium">{Math.round(summary.total_service_time_minutes)} min</span>
              </div>
              {(summary.total_waiting_time_minutes ?? 0) > 0 && (
                <div className="flex justify-between">
                  <span>Waiting:</span>
                  <span className="font-medium">{Math.round(summary.total_waiting_time_minutes ?? 0)} min</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Computation Time */}
        <div className="text-xs text-gray-600">
          {optimizationResult.timing_breakdown ? (
            <div className="space-y-1">
              <div>Optimized in {computation_time_seconds.toFixed(2)}s:</div>
              <div className="pl-3 space-y-0.5 text-gray-500">
                {optimizationResult.timing_breakdown.osrm_matrix_fetch && (
                  <div>• Matrix fetch: {optimizationResult.timing_breakdown.osrm_matrix_fetch.toFixed(2)}s</div>
                )}
                {optimizationResult.timing_breakdown.vrp_solver && (
                  <div>• Solver: {optimizationResult.timing_breakdown.vrp_solver.toFixed(2)}s</div>
                )}
                {optimizationResult.timing_breakdown.geometry_fetch && (
                  <div>• Route geometry: {optimizationResult.timing_breakdown.geometry_fetch.toFixed(2)}s</div>
                )}
              </div>
            </div>
          ) : (
            `Optimized in ${computation_time_seconds.toFixed(2)} seconds`
          )}
        </div>

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="font-medium text-sm text-yellow-900 mb-1">⚠️ Warnings</div>
            {warnings.map((warning, idx) => (
              <div key={idx} className="text-xs text-yellow-800 mt-1">
                • {warning}
              </div>
            ))}
          </div>
        )}

        {/* Unassigned Stops */}
        {unassigned_stops.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="font-medium text-sm text-red-900 mb-1">
              ❌ Unassigned Stops
            </div>
            {unassigned_stops.map((stopId) => (
              <div key={stopId} className="text-xs text-red-800 mt-1">
                • {stopId}
              </div>
            ))}
          </div>
        )}

        {/* Route Details */}
        <div>
          <h4 className="font-semibold text-sm mb-3 text-gray-900">Route Details</h4>
          <div className="space-y-4">
            {routes.map((route) => (
              <div
                key={route.vehicle_id}
                className="border rounded-lg p-3"
                style={{ borderColor: ROUTE_COLORS[route.vehicle_id % ROUTE_COLORS.length] }}
              >
                <div
                  className="font-medium text-sm mb-2"
                  style={{ color: ROUTE_COLORS[route.vehicle_id % ROUTE_COLORS.length] }}
                >
                  {route.driver_name}
                </div>

                <div className="text-xs text-gray-600 space-y-1 mb-2">
                  <div>⏱️ Route Duration: {Math.round(route.total_time_minutes)} min</div>
                  <div className="pl-4 text-gray-500">
                    Driving: {Math.round(route.driving_time_minutes)}m | 
                    Service: {Math.round(route.service_time_minutes)}m
                    {route.waiting_time_minutes && route.waiting_time_minutes > 0 && 
                      ` | Wait: ${Math.round(route.waiting_time_minutes)}m`}
                  </div>
                  <div>📍 Distance: {route.total_distance_km.toFixed(1)} km</div>
                  <div>📦 Demand: {route.total_demand} units</div>
                  <div>🛑 Stops: {route.stops.length}</div>
                </div>

                {/* Itinerary */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-xs font-medium text-gray-700 mb-2">Itinerary</div>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {route.itinerary.map((stop) => (
                      <div key={stop.stop_id} className="flex items-start gap-2">
                        <div
                          className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                          style={{
                            backgroundColor:
                              ROUTE_COLORS[route.vehicle_id % ROUTE_COLORS.length],
                          }}
                        >
                          {stop.sequence}
                        </div>
                        <div className="flex-1">
                          <div className="text-xs font-medium text-gray-900">
                            {stop.stop_name}
                          </div>
                          <div className="text-xs text-gray-600">
                            {stop.waiting_time_minutes && stop.waiting_time_minutes > 0 ? (
                              <>
                                Arrival: {stop.arrival_time} | Wait: {stop.waiting_time_minutes}m
                                <br />
                                Service Start: {stop.service_start_time} | Service: {stop.service_time_minutes}m | Departure: {stop.departure_time}
                              </>
                            ) : (
                              <>
                                Arrival: {stop.arrival_time} | Service: {stop.service_time_minutes}m | Departure: {stop.departure_time}
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
