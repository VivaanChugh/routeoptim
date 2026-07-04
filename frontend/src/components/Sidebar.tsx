/**
 * Sidebar for route configuration and controls
 */

import { Plus, Trash2, Play, RotateCcw, Download } from 'lucide-react';
import { useStore } from '../store';
import { useState } from 'react';

export default function Sidebar() {
  const {
    depot,
    stops,
    vehicles,
    options,
    setDepot,
    addStop,
    removeStop,
    clearStops,
    setVehicles,
    setOptions,
    optimizeRoute,
    isOptimizing,
    reset,
    loadScenario,
  } = useStore();

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleAddStop = () => {
    if (!depot) {
      alert('Please set a depot location first by clicking on the map');
      return;
    }

    // Add a stop near the depot with some random offset
    const newStop = {
      id: `stop-${Date.now()}`,
      lat: depot.lat + (Math.random() - 0.5) * 0.02,
      lng: depot.lng + (Math.random() - 0.5) * 0.02,
      name: `Stop ${stops.length + 1}`,
      service_time_minutes: 5,
      demand: Math.floor(Math.random() * 20) + 5,
      priority: 1,
    };

    addStop(newStop);
  };

  const handleLoadScenario = async (key: string) => {
    await loadScenario(key);
  };

  const handleExport = () => {
    const data = { depot, stops, vehicles, options };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'route-config.json';
    a.click();
  };

  return (
    <div className="w-96 bg-white border-r border-gray-200 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Sample Scenarios */}
        <div>
          <h3 className="text-lg font-semibold mb-3 text-gray-900">Quick Start</h3>
          <div className="space-y-2">
            <button
              onClick={() => handleLoadScenario('toronto')}
              className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="font-medium text-sm">Toronto Downtown</div>
              <div className="text-xs text-gray-600">10 stops, 2 drivers</div>
            </button>
            <button
              onClick={() => handleLoadScenario('waterloo')}
              className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="font-medium text-sm">Waterloo Tech</div>
              <div className="text-xs text-gray-600">15 stops, 1 driver</div>
            </button>
            <button
              onClick={() => handleLoadScenario('san_francisco')}
              className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="font-medium text-sm">San Francisco</div>
              <div className="text-xs text-gray-600">25 stops, 3 drivers</div>
            </button>
          </div>
        </div>

        {/* Depot Info */}
        <div>
          <h3 className="text-lg font-semibold mb-3 text-gray-900">Depot</h3>
          {depot ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="font-medium text-sm text-blue-900">{depot.name}</div>
              <div className="text-xs text-blue-700 mt-1">
                {depot.lat.toFixed(4)}, {depot.lng.toFixed(4)}
              </div>
              <button
                onClick={() => setDepot(null)}
                className="mt-2 text-xs text-blue-600 hover:text-blue-800"
              >
                Change Location
              </button>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-600">
              Click on the map to set depot location
            </div>
          )}
        </div>

        {/* Stops */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">
              Delivery Stops ({stops.length})
            </h3>
            <button
              onClick={handleAddStop}
              className="p-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              title="Add Stop"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto">
            {stops.map((stop, index) => (
              <div
                key={stop.id}
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 flex items-start justify-between"
              >
                <div className="flex-1">
                  <div className="font-medium text-sm">
                    {index + 1}. {stop.name}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    Demand: {stop.demand} | Service: {stop.service_time_minutes}m
                  </div>
                </div>
                <button
                  onClick={() => removeStop(stop.id)}
                  className="p-1 text-red-600 hover:text-red-800 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {stops.length > 0 && (
            <button
              onClick={clearStops}
              className="mt-2 w-full text-sm text-red-600 hover:text-red-800 transition-colors"
            >
              Clear All Stops
            </button>
          )}
        </div>

        {/* Vehicle Configuration */}
        <div>
          <h3 className="text-lg font-semibold mb-3 text-gray-900">Fleet Configuration</h3>
          <div className="space-y-3">
            <div>
              <label className="label">Number of Vehicles</label>
              <input
                type="number"
                min="1"
                max="5"
                value={vehicles.count}
                onChange={(e) => setVehicles({ count: parseInt(e.target.value) })}
                className="input w-full"
              />
            </div>
            <div>
              <label className="label">Vehicle Capacity</label>
              <input
                type="number"
                min="1"
                value={vehicles.capacity}
                onChange={(e) => setVehicles({ capacity: parseInt(e.target.value) })}
                className="input w-full"
              />
            </div>
            <div>
              <label className="label">Max Route Duration (minutes)</label>
              <input
                type="number"
                min="60"
                value={vehicles.max_duration_minutes}
                onChange={(e) =>
                  setVehicles({ max_duration_minutes: parseInt(e.target.value) })
                }
                className="input w-full"
              />
            </div>
          </div>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            {showAdvanced ? '▼' : '▶'} Advanced Options
          </button>

          {showAdvanced && (
            <div className="mt-3 space-y-3">
              <div>
                <label className="label">Solver Time Limit (seconds)</label>
                <input
                  type="number"
                  min="5"
                  max="300"
                  value={options.time_limit_seconds}
                  onChange={(e) =>
                    setOptions({ time_limit_seconds: parseInt(e.target.value) })
                  }
                  className="input w-full"
                />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={options.use_capacity_constraints}
                  onChange={(e) =>
                    setOptions({ use_capacity_constraints: e.target.checked })
                  }
                  className="rounded"
                />
                Use Capacity Constraints
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={options.use_time_windows}
                  onChange={(e) => setOptions({ use_time_windows: e.target.checked })}
                  className="rounded"
                />
                Use Time Windows
              </label>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="space-y-2 pt-4 border-t border-gray-200">
          <button
            onClick={optimizeRoute}
            disabled={isOptimizing || !depot || stops.length < 2}
            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            {isOptimizing ? 'Optimizing...' : 'Optimize Route'}
          </button>

          <div className="flex gap-2">
            <button
              onClick={handleExport}
              disabled={!depot || stops.length === 0}
              className="flex-1 btn-secondary flex items-center justify-center gap-2 text-sm disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={reset}
              className="flex-1 btn-secondary flex items-center justify-center gap-2 text-sm"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
