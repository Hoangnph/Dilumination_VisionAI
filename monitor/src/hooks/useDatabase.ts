'use client';

import { useState, useEffect, useCallback } from 'react';
import { databaseService } from '@/lib/database';
import { 
  Session, 
  PeopleMovement, 
  RealtimeMetrics, 
  AlertLog, 
  DashboardStats,
  PaginatedResponse,
  TimeSeriesData
} from '@/types/database';

// Custom hook for sessions
export function useSessions(page: number = 1, limit: number = 10) {
  const [sessions, setSessions] = useState<PaginatedResponse<Session> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // console.log('Fetching sessions...');
      const response = await databaseService.getSessions(page, limit);
      // console.log('Sessions response:', response);
      
      if (response.success && response.data) {
        // console.log('Setting sessions data:', response.data);
        setSessions(response.data);
      } else {
        // console.error('Failed to fetch sessions:', response.error);
        setError(response.error || 'Failed to fetch sessions');
      }
    } catch (err) {
      // console.error('Error in fetchSessions:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [page, limit]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return { sessions, loading, error, refetch: fetchSessions };
}

// Custom hook for active sessions
export function useActiveSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActiveSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await databaseService.getActiveSessions();
      
      if (response.success && response.data) {
        setSessions(response.data);
      } else {
        setError(response.error || 'Failed to fetch active sessions');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActiveSessions();
    
    // Poll for updates every 20 seconds (further reduced frequency)
    const interval = setInterval(fetchActiveSessions, 20000);
    return () => clearInterval(interval);
  }, [fetchActiveSessions]);

  return { sessions, loading, error, refetch: fetchActiveSessions };
}

// Custom hook for movements
export function useMovements(sessionId?: string, page: number = 1, limit: number = 50) {
  const [movements, setMovements] = useState<PaginatedResponse<PeopleMovement> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMovements = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await databaseService.getMovements(sessionId, page, limit);
      
      if (response.success && response.data) {
        setMovements(response.data);
      } else {
        setError(response.error || 'Failed to fetch movements');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [sessionId, page, limit]);

  useEffect(() => {
    fetchMovements();
  }, [fetchMovements]);

  return { movements, loading, error, refetch: fetchMovements };
}

// Custom hook for real-time metrics
export function useRealtimeMetrics(sessionId?: string) {
  const [metrics, setMetrics] = useState<RealtimeMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await databaseService.getRealtimeMetrics(sessionId);
      
      if (response.success && response.data) {
        setMetrics(response.data);
      } else {
        setError(response.error || 'Failed to fetch metrics');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchMetrics();
    
    // Poll for updates every 10 seconds for real-time data (further reduced frequency)
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  return { metrics, loading, error, refetch: fetchMetrics };
}

// Custom hook for dashboard stats
export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await databaseService.getDashboardStats();
      
      if (response.success && response.data) {
        setStats(response.data);
      } else {
        setError(response.error || 'Failed to fetch dashboard stats');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    
    // Poll for updates every 15 seconds (reduced frequency)
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
}

// Custom hook for alerts
export function useAlerts(sessionId?: string, resolved?: boolean, page: number = 1, limit: number = 20) {
  const [alerts, setAlerts] = useState<PaginatedResponse<AlertLog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await databaseService.getAlerts(sessionId, resolved, page, limit);
      
      if (response.success && response.data) {
        setAlerts(response.data);
      } else {
        setError(response.error || 'Failed to fetch alerts');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [sessionId, resolved, page, limit]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return { alerts, loading, error, refetch: fetchAlerts };
}

// Custom hook for time series data
export function useTimeSeriesData(sessionId: string, hours: number = 24) {
  const [data, setData] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await databaseService.getMetricsHistory(sessionId, hours);
      
      if (response.success && response.data) {
        setData(response.data);
      } else {
        setError(response.error || 'Failed to fetch time series data');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [sessionId, hours]);

  useEffect(() => {
    if (sessionId) {
      fetchData();
    }
  }, [fetchData, sessionId]);

  return { data, loading, error, refetch: fetchData };
}
