import type { PatientStudy } from '../types/dicom.types';

const WEBSOCKET_URL = import.meta.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8080';

export interface WebSocketMessage {
  type: 'patient_added' | 'patient_updated' | 'patient_removed' | 'study_added' | 'study_updated' | 'connection_status' | 'error' | 'request_sync';
  payload: unknown;
  timestamp: string;
}

export interface ConnectionStatus {
  isConnected: boolean;
  orthancConnected: boolean;
  lastSync: string;
  patientCount: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private isConnecting = false;
  private eventListeners: Map<string, ((message: WebSocketMessage) => void)[]> = new Map();
  private connectionStatusCallbacks: ((status: ConnectionStatus) => void)[] = [];

  // Connect to WebSocket
  connect(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      try {
        this.isConnecting = true;
        this.ws = new WebSocket(WEBSOCKET_URL);

        this.ws.onopen = () => {
          console.log('WebSocket connected successfully');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          
          // Send initial connection message
          this.send({
            type: 'connection_status',
            payload: { status: 'connected' },
            timestamp: new Date().toISOString(),
          });

          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket connection closed:', event.code, event.reason);
          this.isConnecting = false;
          this.ws = null;
          
          // Notify connection status callbacks
          this.notifyConnectionStatus({
            isConnected: false,
            orthancConnected: false,
            lastSync: new Date().toISOString(),
            patientCount: 0,
          });

          // Attempt to reconnect if not a clean close
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          
          if (this.reconnectAttempts === 0) {
            reject(error);
          }
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  // Disconnect WebSocket
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
  }

  // Send message through WebSocket
  send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  // Subscribe to specific message types
  subscribe(messageType: string, callback: (message: WebSocketMessage) => void): () => void {
    if (!this.eventListeners.has(messageType)) {
      this.eventListeners.set(messageType, []);
    }
    
    this.eventListeners.get(messageType)!.push(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.eventListeners.get(messageType);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  // Subscribe to connection status updates
  onConnectionStatus(callback: (status: ConnectionStatus) => void): () => void {
    this.connectionStatusCallbacks.push(callback);

    // Return unsubscribe function
    return () => {
      const index = this.connectionStatusCallbacks.indexOf(callback);
      if (index > -1) {
        this.connectionStatusCallbacks.splice(index, 1);
      }
    };
  }

  // Get current connection state
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  // Handle incoming messages
  private handleMessage(message: WebSocketMessage): void {
    console.log('Received WebSocket message:', message);

    // Handle connection status messages
    if (message.type === 'connection_status' && message.payload) {
      this.notifyConnectionStatus(message.payload as ConnectionStatus);
    }

    // Notify subscribers
    const listeners = this.eventListeners.get(message.type);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(message);
        } catch (error) {
          console.error('Error in WebSocket message callback:', error);
        }
      });
    }

    // Notify all message listeners
    const allListeners = this.eventListeners.get('*');
    if (allListeners) {
      allListeners.forEach(callback => {
        try {
          callback(message);
        } catch (error) {
          console.error('Error in WebSocket all-message callback:', error);
        }
      });
    }
  }

  // Schedule reconnection with exponential backoff
  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    
    console.log(`Scheduling WebSocket reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectDelay}ms`);
    
    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect().catch(error => {
          console.error('WebSocket reconnection failed:', error);
        });
      }
    }, this.reconnectDelay);

    // Exponential backoff with jitter
    this.reconnectDelay = Math.min(
      this.reconnectDelay * 2 + Math.random() * 1000,
      30000 // Max 30 seconds
    );
  }

  // Notify connection status callbacks
  private notifyConnectionStatus(status: ConnectionStatus): void {
    this.connectionStatusCallbacks.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in connection status callback:', error);
      }
    });
  }

  // Request full sync
  requestSync(): void {
    this.send({
      type: 'request_sync',
      payload: {},
      timestamp: new Date().toISOString(),
    });
  }

  // Subscribe to patient events
  subscribeToPatientEvents(callbacks: {
    onPatientAdded?: (patient: PatientStudy) => void;
    onPatientUpdated?: (patient: PatientStudy) => void;
    onPatientRemoved?: (patientId: string) => void;
    onStudyAdded?: (study: PatientStudy) => void;
    onStudyUpdated?: (study: PatientStudy) => void;
  }): () => void {
    const unsubscribeFunctions: (() => void)[] = [];

    if (callbacks.onPatientAdded) {
      unsubscribeFunctions.push(
        this.subscribe('patient_added', (message) => {
          callbacks.onPatientAdded!(message.payload as PatientStudy);
        })
      );
    }

    if (callbacks.onPatientUpdated) {
      unsubscribeFunctions.push(
        this.subscribe('patient_updated', (message) => {
          callbacks.onPatientUpdated!(message.payload as PatientStudy);
        })
      );
    }

    if (callbacks.onPatientRemoved) {
      unsubscribeFunctions.push(
        this.subscribe('patient_removed', (message) => {
          const payload = message.payload as { patientId: string };
          callbacks.onPatientRemoved!(payload.patientId);
        })
      );
    }

    if (callbacks.onStudyAdded) {
      unsubscribeFunctions.push(
        this.subscribe('study_added', (message) => {
          callbacks.onStudyAdded!(message.payload as PatientStudy);
        })
      );
    }

    if (callbacks.onStudyUpdated) {
      unsubscribeFunctions.push(
        this.subscribe('study_updated', (message) => {
          callbacks.onStudyUpdated!(message.payload as PatientStudy);
        })
      );
    }

    // Return combined unsubscribe function
    return () => {
      unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
    };
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();