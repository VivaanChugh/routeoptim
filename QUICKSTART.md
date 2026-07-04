# 🚀 Quick Start Guide

Get the Last-Mile Route Optimizer running in 5 minutes!

## Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/routeoptim.git
cd routeoptim

# Run setup script
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Start backend
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

#### Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start frontend
npm run dev
```

Frontend runs at `http://localhost:5173`

### Option 3: Docker (Easiest)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## First Steps

1. **Open the app**: Navigate to `http://localhost:5173`

2. **Load a sample scenario**: Click on "Toronto Downtown" or another sample

3. **Optimize the route**: Click the "Optimize Route" button

4. **View results**: See optimized routes on the map and in the results panel

## Troubleshooting

### Backend won't start

- Check Python version: `python3 --version` (needs 3.10+)
- Check if virtual environment is activated
- Check if port 8000 is available

### Frontend won't start

- Check Node version: `node --version` (needs 18+)
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check if port 5173 is available

### OSRM connection issues

The app uses the public OSRM server by default. If you experience issues:
- Check your internet connection
- The public OSRM server might be rate-limiting
- Consider running your own OSRM server for production use

### Dependencies installation fails

**Backend (Python)**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Install build tools (on Ubuntu/Debian)
sudo apt-get install python3-dev gcc g++

# Install build tools (on macOS)
xcode-select --install
```

**Frontend (Node.js)**:
```bash
# Clear npm cache
npm cache clean --force

# Try with legacy peer deps
npm install --legacy-peer-deps
```

## Testing the API

### Check API health
```bash
curl http://localhost:8000/api/v1/health
```

### View API documentation
Open `http://localhost:8000/docs` in your browser

## Development Tips

### Backend Hot Reload
The backend automatically reloads when you save Python files (when using `--reload` flag).

### Frontend Hot Reload
The frontend automatically reloads when you save TypeScript/React files.

### API Base URL
If you need to change the backend URL, update `frontend/.env`:
```
VITE_API_BASE_URL=http://your-backend-url:8000/api/v1
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [API documentation](http://localhost:8000/docs)
- Try creating custom routes
- Experiment with different constraints
- Check out the [Contributing Guide](CONTRIBUTING.md)

## Common Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload          # Start with hot reload
python -m pytest tests/ -v             # Run tests
black .                                # Format code
ruff .                                 # Lint code

# Frontend
cd frontend
npm run dev                            # Start dev server
npm run build                          # Build for production
npm run preview                        # Preview production build
npm run lint                           # Lint code
npm run format                         # Format code

# Docker
docker-compose up                      # Start all services
docker-compose up -d                   # Start in background
docker-compose down                    # Stop all services
docker-compose logs -f backend         # View backend logs
docker-compose logs -f frontend        # View frontend logs
```

## Need Help?

- 📖 Read the [full README](README.md)
- 🐛 [Report an issue](https://github.com/yourusername/routeoptim/issues)
- 💬 [Ask a question](https://github.com/yourusername/routeoptim/discussions)

---

**Happy optimizing! 🚚📦🗺️**
