/**
 * Error Notification Component
 */

import { X, AlertCircle } from 'lucide-react';
import { useStore } from '../store';
import { useEffect } from 'react';

export default function ErrorNotification() {
  const { error } = useStore((state) => ({ error: state.error }));
  const clearError = () => useStore.setState({ error: null });

  useEffect(() => {
    if (error) {
      // Auto-clear error after 10 seconds
      const timeout = setTimeout(() => {
        clearError();
      }, 10000);

      return () => clearTimeout(timeout);
    }
  }, [error]);

  if (!error) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-md fade-in">
      <div className="bg-red-50 border border-red-200 rounded-lg shadow-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-red-900 text-sm mb-1">Error</h4>
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button
            onClick={clearError}
            className="text-red-600 hover:text-red-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
