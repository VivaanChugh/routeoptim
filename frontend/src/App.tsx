import { useEffect } from 'react';
import { useStore } from './store';
import MapView from './components/MapView';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ResultsPanel from './components/ResultsPanel';
import ErrorNotification from './components/ErrorNotification';
import LoadingOverlay from './components/LoadingOverlay';

function App() {
  const { error, isOptimizing } = useStore();

  useEffect(() => {
    // Check API health on mount
    const checkHealth = async () => {
      try {
        const { apiService } = await import('./api');
        await apiService.checkHealth();
      } catch (error) {
        console.error('API health check failed:', error);
      }
    };
    checkHealth();
  }, []);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar />

        {/* Map View */}
        <div className="flex-1 relative">
          <MapView />
          {isOptimizing && <LoadingOverlay />}
        </div>

        {/* Results Panel */}
        <ResultsPanel />
      </div>

      {/* Error Notification */}
      {error && <ErrorNotification />}
    </div>
  );
}

export default App;
