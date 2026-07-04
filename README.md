# Last-Mile Route Optimizer

A production-grade web application that helps delivery drivers find the fastest route through multiple delivery stops using real road travel times and advanced constraint optimization.

## 🎯 Problem Statement

Traditional route planning relies on manual ordering or simple straight-line distance calculations, which don't account for:
- Real road networks and traffic patterns
- One-way streets and turn restrictions
- Vehicle capacity constraints
- Delivery time windows
- Multiple driver coordination

This application solves the **Vehicle Routing Problem (VRP)** using:
- **Google OR-Tools** for constraint programming and optimization
- **OSRM (Open Source Routing Machine)** for real-world driving time matrices
- **Leaflet.js** for interactive map visualization

## 🚀 Key Features

### Core Routing
- ✅ Interactive map with draggable delivery stops
- ✅ 10-25 delivery stops per route
- ✅ Real driving time matrix from OSRM/OpenStreetMap
- ✅ Optimized route calculation using OR-Tools VRP solver
- ✅ Visual route display with actual road paths (not straight lines)

### Advanced Logistics
- 🚚 **Multi-Driver Support**: Optimize routes for 1-5 vehicles simultaneously
- 📍 **Depot Location**: Set a starting/ending point for all drivers
- ⏱️ **Service Time**: Configure time spent at each delivery stop
- 🕐 **Time Windows**: Set delivery time constraints per stop
- 📦 **Capacity Constraints**: Vehicle capacity limits and package demands
- ⚠️ **Constraint Handling**: Show unassigned stops when constraints can't be satisfied
- 📊 **Route Comparison**: Compare manual vs optimized routes
- 🌍 **Sample Scenarios**: Pre-configured routes for Toronto, Waterloo, San Francisco

### User Experience
- 📤 Export/share optimized routes
- 💾 Save and load route configurations
- 📈 Real-time metrics: distance, time, savings
- 🎨 Clean, modern UI with loading and empty states
- 🗺️ Stop-by-stop itinerary with ETAs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + Leaflet.js + Tailwind CSS            │
│  - Interactive map with draggable stops                     │
│  - Route visualization with road paths                      │
│  - Constraint configuration UI                              │
│  - Results dashboard with metrics                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
                       │ JSON
┌──────────────────────┴──────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  - Route optimization endpoint                              │
│  - OSRM integration for travel times                        │
│  - OR-Tools VRP solver                                      │
│  - Input validation with Pydantic                           │
│  - Redis caching for OSRM responses                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼─────────┐
│  OSRM Service  │           │  PostgreSQL DB   │
│  (Routing API) │           │  (Route Storage) │
└────────────────┘           └──────────────────┘
```

## 🧮 Why OSRM Instead of Euclidean Distance?

**Euclidean (straight-line) distance** assumes:
- Direct paths between points (ignoring roads)
- Constant travel speed
- No terrain or traffic considerations

**OSRM (Open Source Routing Machine)** provides:
- ✅ Real road network routing
- ✅ Actual driving distances and times
- ✅ Turn-by-turn route geometry
- ✅ Consideration of road types, speed limits, one-way streets
- ✅ More accurate time estimates (15-30% improvement over Euclidean)

**Example**: Two points 5km apart "as the crow flies" might require 8km of actual driving through a city's road network.

## 🔧 How OR-Tools Solves the VRP

Google OR-Tools uses a **constraint programming** approach:

1. **Problem Modeling**:
   - Nodes: Depot + all delivery stops
   - Arcs: Travel times between all node pairs (from OSRM)
   - Vehicles: Driver count, capacity, start/end depot

2. **Constraints**:
   - Each stop visited exactly once
   - Vehicle capacity not exceeded
   - Time windows respected
   - Routes start and end at depot

3. **Objective Function**:
   - Minimize total travel time across all vehicles
   - Secondary: Minimize total distance

4. **Solving Strategy**:
   - Local search with guided local search meta-heuristic
   - Path cheapest arc heuristic for initial solution
   - Configurable time limit (default: 30 seconds)

5. **Output**:
   - Optimized stop sequence per vehicle
   - Total time and distance
   - Estimated time savings vs baseline

## 📦 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Leaflet.js** for map visualization
- **React-Leaflet** for React integration
- **Tailwind CSS** for styling
- **Axios** for API calls
- **Zustand** for state management

### Backend
- **FastAPI** (Python 3.10+)
- **Google OR-Tools** (VRP solver)
- **httpx** for async OSRM API calls
- **Pydantic** for data validation
- **Redis** for caching (optional)
- **PostgreSQL** for route storage (optional)

### External Services
- **OSRM** (self-hosted or public API)
- **OpenStreetMap** (map tiles)

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Docker** (optional, for Redis/PostgreSQL)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run the development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Optional: Docker Setup

```bash
# Run the entire stack with Docker Compose
docker-compose up -d

# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Redis: localhost:6379
# PostgreSQL: localhost:5432
```

## 🎮 Usage

### 1. Select Starting Depot
Click on the map to set your depot/starting location, or use a sample scenario.

### 2. Add Delivery Stops
- Click "Add Stop" and place markers on the map
- Drag markers to adjust positions
- Add stop names and optional constraints:
  - Service time (minutes)
  - Time window (earliest/latest delivery time)
  - Package demand (weight/volume)

### 3. Configure Vehicle Fleet
- Set number of drivers (1-5)
- Configure vehicle capacity
- Set max route duration

### 4. Optimize Route
Click "Optimize Route" to solve the VRP:
- Backend fetches OSRM travel time matrix
- OR-Tools calculates optimal routes
- Results display in 2-5 seconds

### 5. View Results
- **Map View**: Color-coded routes per driver with sequence numbers
- **Metrics Panel**: Total time, distance, savings
- **Itinerary**: Stop-by-stop breakdown with ETAs
- **Comparison**: Side-by-side manual vs optimized

### 6. Export & Share
- Export route to JSON
- Generate shareable link
- Print driver itineraries

## 📊 Sample Scenarios

### Toronto Downtown Deliveries
- 20 stops across downtown core
- 2 drivers
- Morning delivery windows (9 AM - 12 PM)
- Depot: CN Tower area

### Waterloo Tech Corridor
- 15 stops (universities + tech companies)
- 1 driver
- Standard capacity constraints
- Depot: Conestoga Mall

### San Francisco Hills
- 25 stops with elevation challenges
- 3 drivers
- Mixed time windows
- Depot: Fisherman's Wharf

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

## 🔑 Environment Variables

### Backend (.env)
```bash
OSRM_BASE_URL=http://router.project-osrm.org
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost:5432/routeoptim
OSRM_CACHE_TTL=3600
OR_TOOLS_TIME_LIMIT=30
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

## 🎯 Performance Optimization

1. **OSRM Caching**: Travel time matrices cached in Redis (1-hour TTL)
2. **OR-Tools Time Limit**: 30-second max for large problems
3. **Lazy Loading**: Map tiles and route geometry loaded on demand
4. **Debouncing**: Map interactions debounced to reduce API calls
5. **Code Splitting**: Frontend chunks split for faster initial load

## 🛠️ API Documentation

### POST /api/v1/optimize
Optimize a delivery route.

**Request Body**:
```json
{
  "depot": {"lat": 43.6532, "lng": -79.3832, "name": "Main Depot"},
  "stops": [
    {
      "id": "stop-1",
      "lat": 43.6426,
      "lng": -79.3871,
      "name": "Customer A",
      "service_time_minutes": 5,
      "demand": 10,
      "time_window": {"earliest": "09:00", "latest": "12:00"}
    }
  ],
  "vehicles": {
    "count": 2,
    "capacity": 100,
    "max_duration_minutes": 480
  },
  "options": {
    "time_limit_seconds": 30
  }
}
```

**Response**:
```json
{
  "routes": [
    {
      "vehicle_id": 0,
      "stops": ["depot", "stop-1", "stop-3", "depot"],
      "total_time_minutes": 120,
      "total_distance_km": 45.2,
      "route_geometry": "...",
      "itinerary": [...]
    }
  ],
  "summary": {
    "total_time_minutes": 240,
    "total_distance_km": 85.5,
    "time_saved_minutes": 45,
    "percentage_improvement": 18.75
  },
  "unassigned_stops": []
}
```

## 📝 Future Enhancements

- [ ] Real-time traffic integration
- [ ] Driver break time constraints
- [ ] Priority/urgency levels per stop
- [ ] Mobile app for drivers
- [ ] Live GPS tracking
- [ ] Historical route analytics
- [ ] Machine learning for demand prediction
- [ ] Multi-day route planning

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 👨‍💻 Author

Built by Vivaan Chugh

## 🙏 Acknowledgments

- Google OR-Tools team for the optimization library
- OSRM Project for routing data
- OpenStreetMap contributors
- React and FastAPI communities

---

**Note**: This is a portfolio/resume project demonstrating full-stack development, optimization algorithms, and production-grade software engineering practices.
