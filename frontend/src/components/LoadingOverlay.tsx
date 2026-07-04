/**
 * Loading Overlay Component
 */

import { Loader2 } from 'lucide-react';

export default function LoadingOverlay() {
  return (
    <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-8 flex flex-col items-center gap-4">
        <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
        <div className="text-center">
          <h3 className="font-semibold text-lg text-gray-900 mb-1">
            Optimizing Route
          </h3>
          <p className="text-sm text-gray-600">
            Calculating optimal delivery sequence...
          </p>
        </div>
      </div>
    </div>
  );
}
