/**
 * SSE Configuration Service
 * Centralized configuration management for SSE functionality
 */

import { SSEConfig, DatabaseListenerConfig } from '@/types/sse';

// Default SSE configuration
export const DEFAULT_SSE_CONFIG: SSEConfig = {
  baseUrl: typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000',
  timeout: 60000, // 60 seconds
  retryAttempts: 3,
  retryDelay: 5000, // 5 seconds
  heartbeatInterval: 30000, // 30 seconds
};

// Default database listener configuration
export const DEFAULT_DB_CONFIG: DatabaseListenerConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'people_counter',
  user: process.env.DB_USER || 'people_counter_user',
  password: process.env.DB_PASSWORD || 'secure_password_123',
  connectionTimeoutMillis: 10000, // 10 seconds
  queryTimeout: 30000, // 30 seconds
  maxRetries: 3,
};

// Environment-specific configurations
export const getSSEConfig = (): SSEConfig => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  return {
    ...DEFAULT_SSE_CONFIG,
    timeout: isDevelopment ? 30000 : 60000, // Shorter timeout in dev
    retryAttempts: isDevelopment ? 2 : 3,
    retryDelay: isDevelopment ? 3000 : 5000,
  };
};

export const getDatabaseConfig = (): DatabaseListenerConfig => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  return {
    ...DEFAULT_DB_CONFIG,
    connectionTimeoutMillis: isDevelopment ? 5000 : 10000,
    queryTimeout: isDevelopment ? 15000 : 30000,
    maxRetries: isDevelopment ? 2 : 3,
  };
};

// SSE Endpoints configuration
export const SSE_ENDPOINTS = {
  SESSIONS: '/api/sse/sessions',
  MOVEMENTS: '/api/sse/movements',
  ALERTS: '/api/sse/alerts',
  METRICS: '/api/sse/metrics',
} as const;

// Database channels configuration
export const DB_CHANNELS = {
  SESSION_CHANGES: 'session_changes',
  MOVEMENT_CHANGES: 'movement_changes',
  ALERT_CHANGES: 'alert_changes',
  METRICS_CHANGES: 'metrics_changes',
} as const;
