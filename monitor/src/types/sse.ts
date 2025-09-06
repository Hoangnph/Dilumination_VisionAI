/**
 * SSE Types and Interfaces
 * Clean separation of concerns for SSE functionality
 */

import { Session, PeopleMovement, AlertLog, RealtimeMetrics } from './database';

// SSE Message types
export interface SSEMessage {
  type: 'connection' | 'data' | 'error' | 'heartbeat' | 'test';
  data?: any;
  message?: string;
  error?: string;
  timestamp: string;
}

// SSE Connection states
export type SSEConnectionState = 'idle' | 'connecting' | 'connected' | 'error' | 'disconnected';

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
  connectionTimeout?: number;
}

// SSE Connection configuration
export interface SSEConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  heartbeatInterval: number;
}

// Database listener configuration
export interface DatabaseListenerConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  connectionTimeoutMillis: number;
  queryTimeout: number;
  maxRetries: number;
}

// SSE Event types
export interface SSEEventHandlers {
  onOpen: () => void;
  onMessage: (event: MessageEvent) => void;
  onError: (event: Event) => void;
  onClose: () => void;
}

// Database notification data
export interface DatabaseNotification {
  channel: string;
  payload: string;
  processId: number;
}

// SSE Stream controller
export interface SSEStreamController {
  enqueue: (chunk: Uint8Array) => void;
  close: () => void;
  error: (error: Error) => void;
}

// Typed SSE Data Structures
export interface SessionSSEData {
  table: 'sessions';
  action: 'INSERT' | 'UPDATE' | 'DELETE' | 'TEST';
  data: Session;
  old_data?: Session;
  timestamp: number;
}

export interface MovementSSEData {
  table: 'people_movements';
  action: 'INSERT' | 'UPDATE' | 'DELETE' | 'TEST';
  data: PeopleMovement;
  old_data?: PeopleMovement;
  timestamp: number;
}

export interface AlertSSEData {
  table: 'alert_logs';
  action: 'INSERT' | 'UPDATE' | 'DELETE' | 'TEST';
  data: AlertLog;
  old_data?: AlertLog;
  timestamp: number;
}

export interface MetricsSSEData {
  table: 'realtime_metrics';
  action: 'INSERT' | 'UPDATE' | 'DELETE' | 'TEST';
  data: RealtimeMetrics;
  old_data?: RealtimeMetrics;
  timestamp: number;
}

// Union type for all SSE data
export type SSEData = SessionSSEData | MovementSSEData | AlertSSEData | MetricsSSEData;

// Type guards for SSE data
export function isSessionSSEData(data: SSEData): data is SessionSSEData {
  return data.table === 'sessions';
}

export function isMovementSSEData(data: SSEData): data is MovementSSEData {
  return data.table === 'people_movements';
}

export function isAlertSSEData(data: SSEData): data is AlertSSEData {
  return data.table === 'alert_logs';
}

export function isMetricsSSEData(data: SSEData): data is MetricsSSEData {
  return data.table === 'realtime_metrics';
}
