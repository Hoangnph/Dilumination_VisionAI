/**
 * Clean SSE Hook
 * Refactored useSSE hook using clean architecture principles
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { SSEConnectionService } from '@/services/sse-connection.service';
import { SSEMessageService } from '@/services/sse-message.service';
import { SSEOptions, SSEMessage, SSEConnectionState } from '@/types/sse';
import { Session, PeopleMovement, AlertLog, RealtimeMetrics } from '@/types/database';

export function useSSE(endpoint: string, options: SSEOptions = {}) {
  // State management
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<SSEMessage | null>(null);
  const [connectionState, setConnectionState] = useState<SSEConnectionState>('idle');
  
  // Refs for cleanup
  const connectionServiceRef = useRef<SSEConnectionService | null>(null);
  const isMountedRef = useRef(true);

  const {
    sessionId,
    resolved,
    onMessage,
    onError,
    onOpen,
    onClose,
    autoReconnect = false,
    reconnectInterval = 5000,
    connectionTimeout = 60000
  } = options;

  // Initialize connection service
  useEffect(() => {
    connectionServiceRef.current = new SSEConnectionService({
      timeout: connectionTimeout,
      retryDelay: reconnectInterval,
    });

    return () => {
      if (connectionServiceRef.current) {
        connectionServiceRef.current.destroy();
      }
    };
  }, [connectionTimeout, reconnectInterval]);

  // Connect to SSE
  const connect = useCallback(async () => {
    if (!connectionServiceRef.current || !isMountedRef.current) {
      return;
    }

    const service = connectionServiceRef.current;

    // Check if already connected
    if (service.isConnected()) {
      // console.log('✅ SSE already connected, skipping');
      return;
    }

    // Check if already connecting
    if (service.getConnectionState() === 'connecting') {
      // console.log('⏳ SSE connection already in progress');
      return;
    }

    setIsConnecting(true);
    setError(null);
    setConnectionState('connecting');

    try {
      await service.connect(endpoint, {
        onOpen: () => {
          if (!isMountedRef.current) return;
          
          setIsConnected(true);
          setIsConnecting(false);
          setError(null);
          setConnectionState('connected');
          // console.log('✅ SSE connection established');
          onOpen?.();
        },
        onMessage: (event) => {
          if (!isMountedRef.current) return;
          
          const message = SSEMessageService.parseMessage(event);
          if (message) {
            setLastMessage(message);
            onMessage?.(message);
          }
        },
        onError: (event) => {
          if (!isMountedRef.current) return;
          
          setIsConnected(false);
          setIsConnecting(false);
          setConnectionState('error');
          setError('SSE connection failed');
          // console.error('❌ SSE connection error:', event);
          onError?.(event);

          // Setup auto-reconnect if enabled
          if (autoReconnect && isMountedRef.current) {
            service.setupAutoReconnect(endpoint, {
              onOpen: () => {
                if (!isMountedRef.current) return;
                setIsConnected(true);
                setIsConnecting(false);
                setError(null);
                setConnectionState('connected');
                onOpen?.();
              },
              onMessage: (event) => {
                if (!isMountedRef.current) return;
                const message = SSEMessageService.parseMessage(event);
                if (message) {
                  setLastMessage(message);
                  onMessage?.(message);
                }
              },
              onError: (event) => {
                if (!isMountedRef.current) return;
                setIsConnected(false);
                setIsConnecting(false);
                setConnectionState('error');
                setError('SSE connection failed');
                onError?.(event);
              },
              onClose: () => {
                if (!isMountedRef.current) return;
                setIsConnected(false);
                setIsConnecting(false);
                setConnectionState('disconnected');
                onClose?.();
              }
            }, { sessionId, resolved });
          }
        },
        onClose: () => {
          if (!isMountedRef.current) return;
          
          setIsConnected(false);
          setIsConnecting(false);
          setConnectionState('disconnected');
          onClose?.();
        }
      }, { sessionId, resolved });

    } catch (err) {
      if (!isMountedRef.current) return;
      
      const errorMessage = err instanceof Error ? err.message : 'Connection failed';
      setError(errorMessage);
      setIsConnected(false);
      setIsConnecting(false);
      setConnectionState('error');
      // console.error('❌ SSE connection failed:', err);
    }
  }, [endpoint, sessionId, resolved, onMessage, onError, onOpen, onClose, autoReconnect, reconnectInterval, connectionTimeout]);

  // Disconnect from SSE
  const disconnect = useCallback(() => {
    if (connectionServiceRef.current) {
      connectionServiceRef.current.disconnect();
      setIsConnected(false);
      setIsConnecting(false);
      setConnectionState('disconnected');
      onClose?.();
    }
  }, [onClose]);

  // Reconnect manually
  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 100);
  }, [disconnect, connect]);

  // Auto-connect on mount
  useEffect(() => {
    isMountedRef.current = true;
    
    // Small delay to ensure previous connections are cleaned up
    const connectTimeout = setTimeout(() => {
      if (isMountedRef.current) {
        connect();
      }
    }, 100);

    return () => {
      isMountedRef.current = false;
      clearTimeout(connectTimeout);
      disconnect();
    };
  }, [connect, disconnect]);

  // Reconnect when dependencies change
  useEffect(() => {
    if (isMountedRef.current) {
      reconnect();
    }
  }, [sessionId, resolved, reconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (connectionServiceRef.current) {
        connectionServiceRef.current.destroy();
      }
    };
  }, []);

  return {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    connectionState,
    connect,
    disconnect,
    reconnect,
    // Additional utility methods
    getConnectionUrl: () => connectionServiceRef.current?.getConnectionUrl() || null,
    getReadyState: () => connectionServiceRef.current?.getReadyState() || EventSource.CLOSED,
  };
}

// Specific hooks for different data types
export function useSessionsSSE(sessionId?: string) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch initial data
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/sessions?page=1&limit=100');
      const data = await response.json();
      if (data.success && data.data?.data) {
        setSessions(data.data.data);
      } else {
        // If no data or empty data, clear sessions
        setSessions([]);
      }
    } catch (error) {
      // console.error('Error fetching initial sessions:', error);
      // On error, clear sessions to avoid stale data
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch initial data on mount
  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/sessions', {
    sessionId,
    autoReconnect: true,
    onMessage: (message) => {
      if (message.type === 'data' && message.data) {
        const { action, data } = message.data;
        
        setSessions(prevSessions => {
          switch (action) {
            case 'INSERT':
              // Check if session already exists to prevent duplicates
              const exists = prevSessions.some(session => session.id === data.id);
              if (exists) {
                // console.log('Session already exists, skipping duplicate:', data.id);
                return prevSessions;
              }
              return [...prevSessions, data];
            case 'UPDATE':
              return prevSessions.map(session => 
                session.id === data.id ? { ...session, ...data } : session
              );
            case 'DELETE':
              return prevSessions.filter(session => session.id !== data.id);
            default:
              return prevSessions;
          }
        });
      }
    },
    onError: (error) => {
      // console.error('SSE connection error in useSessionsSSE:', error);
      // On SSE error, refetch data to ensure consistency
      fetchInitialData();
    }
  });

  return { sessions, loading, isConnected, error, lastMessage, refetch: fetchInitialData };
}

export function useMovementsSSE(sessionId?: string) {
  const [movements, setMovements] = useState<PeopleMovement[]>([]);
  const [loading, setLoading] = useState(true);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/movements', {
    sessionId,
    autoReconnect: true,
    onMessage: (message) => {
      if (message.type === 'data' && message.data) {
        const { action, data } = message.data;
        
        setMovements(prevMovements => {
          switch (action) {
            case 'INSERT':
              return [...prevMovements, data];
            case 'UPDATE':
              return prevMovements.map(movement => 
                movement.id === data.id ? { ...movement, ...data } : movement
              );
            case 'DELETE':
              return prevMovements.filter(movement => movement.id !== data.id);
            default:
              return prevMovements;
          }
        });
        setLoading(false);
      }
    }
  });

  return { movements, loading, isConnected, error, lastMessage };
}

export function useAlertsSSE(sessionId?: string, resolved?: boolean) {
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/alerts', {
    sessionId,
    resolved,
    autoReconnect: true,
    onMessage: (message) => {
      if (message.type === 'data' && message.data) {
        const { action, data } = message.data;
        
        setAlerts(prevAlerts => {
          switch (action) {
            case 'INSERT':
              return [...prevAlerts, data];
            case 'UPDATE':
              return prevAlerts.map(alert => 
                alert.id === data.id ? { ...alert, ...data } : alert
              );
            case 'DELETE':
              return prevAlerts.filter(alert => alert.id !== data.id);
            default:
              return prevAlerts;
          }
        });
        setLoading(false);
      }
    }
  });

  return { alerts, loading, isConnected, error, lastMessage };
}

export function useMetricsSSE(sessionId?: string) {
  const [metrics, setMetrics] = useState<RealtimeMetrics[]>([]);
  const [loading, setLoading] = useState(true);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/metrics', {
    sessionId,
    autoReconnect: true,
    onMessage: (message) => {
      if (message.type === 'data' && message.data) {
        const { action, data } = message.data;
        
        setMetrics(prevMetrics => {
          switch (action) {
            case 'INSERT':
              return [...prevMetrics, data];
            case 'UPDATE':
              return prevMetrics.map(metric => 
                metric.id === data.id ? { ...metric, ...data } : metric
              );
            case 'DELETE':
              return prevMetrics.filter(metric => metric.id !== data.id);
            default:
              return prevMetrics;
          }
        });
        setLoading(false);
      }
    }
  });

  return { metrics, loading, isConnected, error, lastMessage };
}
