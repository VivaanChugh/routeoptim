/**
 * Main Map View component using React-Leaflet
 */

import { MapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents } from 'react-leaflet';
import { LatLngExpression, Icon } from 'leaflet';
import { useStore } from '../store';
import { ROUTE_COLORS } from '../types';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in React-Leaflet
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Map click handler component
function MapClickHandler() {
  const { depot, setDepot } = useStore();

  useMapEvents({
    click(e) {
      if (!depot) {
        setDepot({
          lat: e.latlng.lat,
          lng: e.latlng.lng,
          name: 'Main Depot',
        });
      }
    },
  });

  return null;
}

export default function MapView() {
  const { depot, stops, optimizationResult } = useStore();

  // Default center (Toronto)
  const center: LatLngExpression = depot
    ? [depot.lat, depot.lng]
    : [43.6532, -79.3832];

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
      className="z-0"
    >
      <TileLayer
        url={import.meta.env.VITE_MAP_TILE_URL || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'}
        attribution={import.meta.env.VITE_MAP_ATTRIBUTION || '&copy; OpenStreetMap'}
      />

      <MapClickHandler />

      {/* Depot Marker */}
      {depot && (
        <Marker position={[depot.lat, depot.lng]}>
          <Popup>
            <div className="font-semibold">🏢 {depot.name}</div>
            <div className="text-xs text-gray-600">Depot / Starting Location</div>
          </Popup>
        </Marker>
      )}

      {/* Stop Markers */}
      {stops.map((stop, index) => (
        <Marker key={stop.id} position={[stop.lat, stop.lng]}>
          <Popup>
            <div className="font-semibold">
              {index + 1}. {stop.name}
            </div>
            <div className="text-xs text-gray-600">
              Demand: {stop.demand} | Service: {stop.service_time_minutes} min
            </div>
            {stop.time_window && (
              <div className="text-xs text-gray-600">
                Window: {stop.time_window.earliest} - {stop.time_window.latest}
              </div>
            )}
          </Popup>
        </Marker>
      ))}

      {/* Optimized Routes */}
      {optimizationResult && optimizationResult.routes.map((route) => (
        <Polyline
          key={route.vehicle_id}
          positions={route.route_geometry as LatLngExpression[]}
          color={ROUTE_COLORS[route.vehicle_id % ROUTE_COLORS.length]}
          weight={4}
          opacity={0.7}
        />
      ))}
    </MapContainer>
  );
}
