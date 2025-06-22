import React from 'react';
import { useOrthancSync } from '../../hooks/useOrthancSync';

interface HeaderProps {
  className?: string;
}

export default function Header({ className = '' }: HeaderProps) {
  const { status, refresh } = useOrthancSync();

  const handleSettingsClick = () => {
    // TODO: Open settings modal
    console.log('Settings clicked');
  };

  const handleHelpClick = () => {
    // TODO: Open help/documentation
    console.log('Help clicked');
  };

  return (
    <header className={`medical-header ${className}`}>
      <div className="flex items-center gap-4">
        <div className="medical-logo">
          🏥 Orthanc Medical Dashboard
        </div>
        
        <div className="flex items-center gap-2">
          {/* Connection Status */}
          <div className={`status-indicator ${
            status.isConnected 
              ? 'status-completed' 
              : status.isLoading 
                ? 'status-processing' 
                : 'status-error'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              status.isConnected 
                ? 'bg-green-400' 
                : status.isLoading
                  ? 'bg-blue-400 animate-pulse'
                  : 'bg-red-400'
            }`} />
            {status.isConnected ? 'Connected' : status.isLoading ? 'Connecting...' : 'Disconnected'}
          </div>

          {/* Patient Count */}
          <div className="text-sm text-blue-200">
            {status.patientCount} {status.patientCount === 1 ? 'patient' : 'patients'}
          </div>

          {/* Last Sync */}
          {status.lastSync && (
            <div className="text-xs text-blue-300">
              Last sync: {status.lastSync.toLocaleTimeString()}
            </div>
          )}

          {/* WebSocket Status */}
          {status.webSocketConnected && (
            <div className="status-indicator status-completed">
              <div className="w-2 h-2 rounded-full bg-green-400" />
              Real-time
            </div>
          )}
        </div>
      </div>

      <div className="medical-header-actions">
        {/* Refresh Button */}
        <button
          onClick={refresh}
          disabled={status.isLoading}
          className="action-button"
          title="Refresh patient data"
        >
          <svg 
            className={`w-4 h-4 ${status.isLoading ? 'animate-spin' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
            />
          </svg>
          {status.isLoading ? 'Syncing...' : 'Refresh'}
        </button>

        {/* Error Display */}
        {status.error && (
          <div 
            className="status-indicator status-error cursor-pointer" 
            title={status.error}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" 
              />
            </svg>
            Error
          </div>
        )}

        {/* Settings Button */}
        <button
          onClick={handleSettingsClick}
          className="action-button"
          title="Settings"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" 
            />
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
            />
          </svg>
        </button>

        {/* Help Button */}
        <button
          onClick={handleHelpClick}
          className="action-button"
          title="Help"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
        </button>
      </div>
    </header>
  );
}