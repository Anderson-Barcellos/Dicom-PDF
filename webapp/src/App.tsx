import { useEffect } from 'react';
import ErrorBoundary from './components/Common/ErrorBoundary';
import Header from './components/Layout/Header';
import TabBar from './components/Layout/TabBar';
import MainContent from './components/Layout/MainContent';
import { useTabManager } from './hooks/useTabManager';
import { useOrthancSync } from './hooks/useOrthancSync';

function App() {
  const { handleKeyboardShortcut } = useTabManager();
  const { status } = useOrthancSync();

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      handleKeyboardShortcut(event);
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyboardShortcut]);

  return (
    <ErrorBoundary>
      <div className="medical-interface">
        {/* Header with connection status and controls */}
        <Header />
        
        {/* Tab bar with dynamic patient tabs */}
        <TabBar />
        
        {/* Main content area with patient tab or welcome screen */}
        <MainContent />
        
        {/* Optional: Connection status overlay for debugging */}
        {import.meta.env.DEV && (
          <div className="fixed bottom-4 right-4 p-2 bg-black bg-opacity-75 text-white text-xs rounded z-50">
            <div>Orthanc: {status.isConnected ? '✅' : '❌'}</div>
            <div>WebSocket: {status.webSocketConnected ? '✅' : '❌'}</div>
            <div>Patients: {status.patientCount}</div>
            {status.lastSync && (
              <div>Last sync: {status.lastSync.toLocaleTimeString()}</div>
            )}
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}

export default App;
