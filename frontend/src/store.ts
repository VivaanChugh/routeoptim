/**
 * Zustand store for global application state
 */

import { create } from 'zustand';
import {
  Location,
  DeliveryStop,
  VehicleConfig,
  OptimizationOptions,
  RouteOptimizationResponse,
  DEFAULT_VEHICLE_CONFIG,
  DEFAULT_OPTIMIZATION_OPTIONS,
} from './types';
import { apiService } from './api';

interface AppStore {
  // State
  depot: Location | null;
  stops: DeliveryStop[];
  vehicles: VehicleConfig;
  options: OptimizationOptions;
  optimizationResult: RouteOptimizationResponse | null;
  isOptimizing: boolean;
  error: string | null;
  selectedScenario: string | null;

  // Actions
  setDepot: (depot: Location | null) => void;
  addStop: (stop: DeliveryStop) => void;
  updateStop: (stopId: string, updates: Partial<DeliveryStop>) => void;
  removeStop: (stopId: string) => void;
  clearStops: () => void;
  setVehicles: (vehicles: Partial<VehicleConfig>) => void;
  setOptions: (options: Partial<OptimizationOptions>) => void;
  optimizeRoute: () => Promise<void>;
  clearOptimization: () => void;
  loadScenario: (scenarioKey: string) => Promise<void>;
  reset: () => void;
}

export const useStore = create<AppStore>((set, get) => ({
  // Initial State
  depot: null,
  stops: [],
  vehicles: DEFAULT_VEHICLE_CONFIG,
  options: DEFAULT_OPTIMIZATION_OPTIONS,
  optimizationResult: null,
  isOptimizing: false,
  error: null,
  selectedScenario: null,

  // Actions
  setDepot: (depot) => set({ depot, optimizationResult: null }),

  addStop: (stop) =>
    set((state) => ({
      stops: [...state.stops, stop],
      optimizationResult: null,
    })),

  updateStop: (stopId, updates) =>
    set((state) => ({
      stops: state.stops.map((stop) => (stop.id === stopId ? { ...stop, ...updates } : stop)),
      optimizationResult: null,
    })),

  removeStop: (stopId) =>
    set((state) => ({
      stops: state.stops.filter((stop) => stop.id !== stopId),
      optimizationResult: null,
    })),

  clearStops: () => set({ stops: [], optimizationResult: null }),

  setVehicles: (vehicles) =>
    set((state) => ({
      vehicles: { ...state.vehicles, ...vehicles },
      optimizationResult: null,
    })),

  setOptions: (options) =>
    set((state) => ({
      options: { ...state.options, ...options },
      optimizationResult: null,
    })),

  optimizeRoute: async () => {
    const state = get();

    if (!state.depot) {
      set({ error: 'Please set a depot location' });
      return;
    }

    if (state.stops.length < 2) {
      set({ error: 'Please add at least 2 delivery stops' });
      return;
    }

    set({ isOptimizing: true, error: null });

    try {
      const request = {
        depot: state.depot,
        stops: state.stops,
        vehicles: state.vehicles,
        options: state.options,
      };

      const result = await apiService.optimizeRoute(request);

      set({
        optimizationResult: result,
        isOptimizing: false,
        error: null,
      });
    } catch (error: any) {
      set({
        isOptimizing: false,
        error: error.message || 'Optimization failed',
      });
    }
  },

  clearOptimization: () => set({ optimizationResult: null }),

  loadScenario: async (scenarioKey) => {
    try {
      const scenarios = await apiService.getSampleScenarios();
      const scenario = scenarios[scenarioKey];

      if (!scenario) {
        throw new Error('Scenario not found');
      }

      set({
        depot: scenario.depot,
        stops: scenario.stops,
        vehicles: scenario.vehicles,
        optimizationResult: null,
        selectedScenario: scenarioKey,
        error: null,
      });
    } catch (error: any) {
      set({ error: error.message || 'Failed to load scenario' });
    }
  },

  reset: () =>
    set({
      depot: null,
      stops: [],
      vehicles: DEFAULT_VEHICLE_CONFIG,
      options: DEFAULT_OPTIMIZATION_OPTIONS,
      optimizationResult: null,
      isOptimizing: false,
      error: null,
      selectedScenario: null,
    }),
}));
