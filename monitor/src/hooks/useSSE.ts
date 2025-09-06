'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

// SSE Message types
export interface SSEMessage {
  type: 'connection' | 'data' | 'error' | 'heartbeat';
  data?: any;
  message?: string;
  error?: string;
  timestamp: string;
}

// SSE Hook options
export interface SSEOptions {
  sessionId?: string;
  resolved?: boolean;
  onMessage?: (message: SSEMessage) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

// Custom hook for SSE connections
export function useSSE(endpoint: string, options: SSEOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<SSEMessage | null>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const connectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  const {
    sessionId,
    resolved,
    onMessage,
    onError,
    onOpen,
    onClose,
    autoReconnect = false, // Disable auto-reconnect for debugging
    reconnectInterval = 5000
  } = options;

  // Build SSE URL with query parameters
  const buildSSEUrl = useCallback(() => {
    const url = new URL(endpoint, window.location.origin);
    
    if (sessionId) {
      url.searchParams.set('session_id', sessionId);
    }
    
    if (resolved !== undefined) {
      url.searchParams.set('resolved', resolved.toString());
    }
    
    return url.toString();
  }, [endpoint, sessionId, resolved]);

  // Connect to SSE
  const connect = useCallback(() => {
    if (eventSourceRef.current?.readyState === EventSource.OPEN) {
      return; // Already connected
    }

    setIsConnecting(true);
    setError(null);

    // Set connection timeout
    connectionTimeoutRef.current = setTimeout(() => {
      if (isMountedRef.current && !isConnected) {
        console.error(`SSE connection timeout for ${endpoint}`);
        setError('Connection timeout');
        setIsConnecting(false);
        setIsConnected(false);
        
        // Auto-reconnect on timeout
        if (autoReconnect && isMountedRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, reconnectInterval);
        }
      }
    }, 30000); // 30 second timeout

    try {
      const url = buildSSEUrl();
      console.log(`Connecting to SSE: ${url}`);
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log(`✅ SSE connected to ${endpoint}`);
        console.log(`✅ EventSource readyState: ${eventSource.readyState}`);
        console.log(`✅ EventSource URL: ${eventSource.url}`);
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
        
        // Clear connection timeout
        if (connectionTimeoutRef.current) {
          clearTimeout(connectionTimeoutRef.current);
          connectionTimeoutRef.current = null;
        }
        
        onOpen?.();
      };

      eventSource.onmessage = (event) => {
        console.log(`📨 SSE message received:`, event.data);
        console.log(`📨 Event type:`, event.type);
        console.log(`📨 Event lastEventId:`, event.lastEventId);
        try {
          const message: SSEMessage = JSON.parse(event.data);
          console.log(`📨 Parsed message:`, message);
          setLastMessage(message);
          onMessage?.(message);
        } catch (err) {
          console.error('❌ Error parsing SSE message:', err);
          setError('Failed to parse message');
        }
      };

      eventSource.onerror = (event) => {
        const errorMessage = `❌ SSE connection failed for ${endpoint}`;
        console.error(errorMessage, {
          readyState: eventSource.readyState,
          url: eventSource.url,
          timestamp: new Date().toISOString(),
          event: event
        });
        console.error(`❌ EventSource readyState: ${eventSource.readyState}`);
        console.error(`❌ EventSource URL: ${eventSource.url}`);
        setIsConnected(false);
        setIsConnecting(false);
        setError(errorMessage);
        onError?.(event);

        // Auto-reconnect if enabled
        if (autoReconnect && isMountedRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              console.log(`Attempting to reconnect to ${endpoint}...`);
              connect();
            }
          }, reconnectInterval);
        }
      };

    } catch (err) {
      console.error(`Failed to create SSE connection to ${endpoint}:`, err);
      setError(err instanceof Error ? err.message : 'Connection failed');
      setIsConnected(false);
      setIsConnecting(false);
      
      // Auto-reconnect on initial connection failure
      if (autoReconnect && isMountedRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            connect();
          }
        }, reconnectInterval);
      }
    }
  }, [endpoint, buildSSEUrl, onMessage, onError, onOpen, autoReconnect, reconnectInterval]);

  // Disconnect from SSE
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    onClose?.();
  }, [onClose]);

  // Reconnect manually
  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 100);
  }, [disconnect, connect]);

  // Auto-connect on mount
  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  // Reconnect when dependencies change
  useEffect(() => {
    if (isMountedRef.current) {
      reconnect();
    }
  }, [sessionId, resolved, reconnect]);

  return {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    connect,
    disconnect,
    reconnect
  };
}

// Specific hooks for different data types
export function useSessionsSSE(sessionId?: string) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch initial data
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/sessions?page=1&limit=100');
      const data = await response.json();
      if (data.success && data.data?.data) {
        setSessions(data.data.data);
      }
    } catch (error) {
      console.error('Error fetching initial sessions:', error);
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
    onMessage: (message) => {
      if (message.type === 'data' && message.data) {
        const { action, data } = message.data;
        
        setSessions(prevSessions => {
          switch (action) {
            case 'INSERT':
              // Check if session already exists to prevent duplicates
              const exists = prevSessions.some(session => session.id === data.id);
              if (exists) {
                console.log('Session already exists, skipping duplicate:', data.id);
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
    }
  });

  return { sessions, loading, isConnected, error, lastMessage, refetch: fetchInitialData };
}

export function useMovementsSSE(sessionId?: string) {
  const [movements, setMovements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/movements', {
    sessionId,
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
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/alerts', {
    sessionId,
    resolved,
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
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const { isConnected, error, lastMessage } = useSSE('/api/sse/metrics', {
    sessionId,
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
