import { useEffect, useCallback, useRef } from 'react';
import { usePatientStore } from '../stores/patientStore';
import { orthancApiService } from '../services/orthancApi';
import { webSocketService } from '../services/websocketService';
import type { PatientStudy } from '../types/dicom.types';

const POLLING_INTERVAL = parseInt(import.meta.env.REACT_APP_POLLING_INTERVAL || '5000');

export interface UseOrthancSyncOptions {
  enablePolling?: boolean;
  enableWebSocket?: boolean;
  pollingInterval?: number;
  autoStart?: boolean;
}

export interface OrthancSyncStatus {
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  lastSync: Date | null;
  patientCount: number;
  webSocketConnected: boolean;
}

export function useOrthancSync(options: UseOrthancSyncOptions = {}) {
  const {
    enablePolling = true,
    enableWebSocket = true,
    pollingInterval = POLLING_INTERVAL,
    autoStart = true,
  } = options;

  const {
    patients,
    setPatients,
    addPatient,
    updatePatient,
    removePatient,
    setConnectionState,
    setLastSync,
    setLoading,
    setError,
    isLoading,
    error,
    lastSync,
    isConnected,
  } = usePatientStore();

  const pollingIntervalRef = useRef<NodeJS.Timeout>();
  const isActiveRef = useRef(false);
  const lastPatientCountRef = useRef(0);

  // Sync patients from Orthanc
  const syncPatients = useCallback(async (showLoading = true) => {
    if (!isActiveRef.current) return;

    try {
      if (showLoading) {
        setLoading(true);
      }
      setError(null);

      // Check Orthanc connection
      const connected = await orthancApiService.checkConnection();
      setConnectionState(connected);

      if (!connected) {
        throw new Error('Cannot connect to Orthanc server');
      }

      // Fetch all patient studies
      const allStudies = await orthancApiService.getAllPatientStudies();
      
      // Update store
      setPatients(allStudies);
      setLastSync(new Date());

      console.log(`Synced ${allStudies.length} patient studies from Orthanc`);

      // Detect new patients for notifications
      if (allStudies.length > lastPatientCountRef.current && lastPatientCountRef.current > 0) {
        const newPatients = allStudies.slice(lastPatientCountRef.current);
        newPatients.forEach(patient => {
          console.log('New patient detected:', patient.patientName);
          // You could add notification logic here
        });
      }
      
      lastPatientCountRef.current = allStudies.length;

    } catch (error) {
      console.error('Error syncing patients:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      setConnectionState(false);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, [setPatients, setLoading, setError, setConnectionState, setLastSync]);

  // Start polling
  const startPolling = useCallback(() => {
    if (!enablePolling || pollingIntervalRef.current) return;

    console.log(`Starting Orthanc polling every ${pollingInterval}ms`);
    
    // Initial sync
    syncPatients();

    // Set up interval
    pollingIntervalRef.current = setInterval(() => {
      syncPatients(false); // Don't show loading for background syncs
    }, pollingInterval);
  }, [enablePolling, pollingInterval, syncPatients]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      console.log('Stopping Orthanc polling');
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = undefined;
    }
  }, []);

  // Setup WebSocket connection
  const setupWebSocket = useCallback(() => {
    if (!enableWebSocket) return;

    console.log('Setting up WebSocket connection for real-time updates');

    // Connect to WebSocket
    webSocketService.connect().catch(error => {
      console.warn('WebSocket connection failed, falling back to polling only:', error);
    });

    // Subscribe to patient events
    const unsubscribePatientEvents = webSocketService.subscribeToPatientEvents({
      onPatientAdded: (patient: PatientStudy) => {
        console.log('Real-time: Patient added', patient.patientName);
        addPatient(patient);
      },
      onPatientUpdated: (patient: PatientStudy) => {
        console.log('Real-time: Patient updated', patient.patientName);
        updatePatient(patient.id, patient);
      },
      onPatientRemoved: (patientId: string) => {
        console.log('Real-time: Patient removed', patientId);
        removePatient(patientId);
      },
      onStudyAdded: (study: PatientStudy) => {
        console.log('Real-time: Study added', study.studyDescription);
        addPatient(study);
      },
      onStudyUpdated: (study: PatientStudy) => {
        console.log('Real-time: Study updated', study.studyDescription);
        updatePatient(study.id, study);
      },
    });

    // Subscribe to connection status
    const unsubscribeConnectionStatus = webSocketService.onConnectionStatus((status) => {
      console.log('WebSocket connection status:', status);
      setConnectionState(status.orthancConnected);
      if (status.lastSync) {
        setLastSync(new Date(status.lastSync));
      }
    });

    // Return cleanup function
    return () => {
      unsubscribePatientEvents();
      unsubscribeConnectionStatus();
    };
  }, [enableWebSocket, addPatient, updatePatient, removePatient, setConnectionState, setLastSync]);

  // Manual refresh
  const refresh = useCallback(async () => {
    await syncPatients(true);
  }, [syncPatients]);

  // Force full resync
  const forceResync = useCallback(async () => {
    console.log('Forcing full resync from Orthanc');
    if (enableWebSocket && webSocketService.isConnected()) {
      webSocketService.requestSync();
    }
    await syncPatients(true);
  }, [syncPatients, enableWebSocket]);

  // Start/stop sync
  const start = useCallback(() => {
    if (isActiveRef.current) return;
    
    console.log('Starting Orthanc synchronization');
    isActiveRef.current = true;
    
    if (enablePolling) {
      startPolling();
    }
    
    if (enableWebSocket) {
      setupWebSocket();
    }
  }, [startPolling, setupWebSocket, enablePolling, enableWebSocket]);

  const stop = useCallback(() => {
    if (!isActiveRef.current) return;
    
    console.log('Stopping Orthanc synchronization');
    isActiveRef.current = false;
    
    stopPolling();
    
    if (enableWebSocket) {
      webSocketService.disconnect();
    }
  }, [stopPolling, enableWebSocket]);

  // Auto-start effect
  useEffect(() => {
    if (autoStart) {
      start();
    }

    // Cleanup on unmount
    return () => {
      stop();
    };
  }, [autoStart, start, stop]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      stopPolling();
      if (enableWebSocket) {
        webSocketService.disconnect();
      }
    };
  }, [stopPolling, enableWebSocket]);

  // Return sync status and controls
  const status: OrthancSyncStatus = {
    isConnected,
    isLoading,
    error,
    lastSync,
    patientCount: patients.length,
    webSocketConnected: enableWebSocket ? webSocketService.isConnected() : false,
  };

  return {
    // Status
    status,
    patients,
    
    // Controls
    start,
    stop,
    refresh,
    forceResync,
    
    // Configuration
    isActive: isActiveRef.current,
    options: {
      enablePolling,
      enableWebSocket,
      pollingInterval,
      autoStart,
    },
  };
}