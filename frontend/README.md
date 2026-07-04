# Frontend - Last-Mile Route Optimizer

React + TypeScript frontend for the Last-Mile Route Optimizer.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Leaflet.js** + React-Leaflet for maps
- **Zustand** for state management
- **Axios** for API calls
- **Lucide React** for icons

## Setup

### Install Dependencies

```bash
npm install
```

### Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Adjust the API URL if needed:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── MapView.tsx
│   ├── ResultsPanel.tsx
│   ├── ErrorNotification.tsx
│   └── LoadingOverlay.tsx
├── api.ts              # API service
├── store.ts            # Zustand store
├── types.ts            # TypeScript types
├── index.css           # Global styles
├── main.tsx            # Entry point
└── App.tsx             # Main app component
```

## Features

- 🗺️ Interactive map with Leaflet.js
- 📍 Drag-and-drop depot and stop markers
- 🚚 Multi-vehicle route optimization
- ⏱️ Time window constraints
- 📦 Capacity constraints
- 📊 Real-time metrics and visualization
- 💾 Export route configurations
- 🎨 Responsive, modern UI

## Development

### Code Formatting

```bash
npm run format
```

### Linting

```bash
npm run lint
```

## License

MIT
