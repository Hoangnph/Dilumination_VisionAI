/**
 * SSE Connection Service
 * Clean separation of SSE connection management
 */

import { SSEConfig, SSEConnectionState, SSEEventHandlers } from '@/types/sse';
import { getSSEConfig } from '@/config/sse';
import { SSEMessageService } from './sse-message.service';

export class SSEConnectionService {
  private eventSource: EventSource | null = null;
  private config: SSEConfig;
  private connectionState: SSEConnectionState = 'idle';
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private connectionTimeout: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isDestroyed: boolean = false;

  constructor(config?: Partial<SSEConfig>) {
    this.config = { ...getSSEConfig(), ...config };
  }

  /**
   * Connect to SSE endpoint
   */
  async connect(
    endpoint: string,
    handlers: SSEEventHandlers,
    options?: {
      sessionId?: string;
      resolved?: boolean;
      autoReconnect?: boolean;
    }
  ): Promise<void> {
    if (this.isDestroyed) {
      throw new Error('SSE connection service has been destroyed');
    }

    if (this.connectionState === 'connecting' || this.connectionState === 'connected') {
      // console.log('⚠️ SSE connection already in progress or connected');
      return;
    }

    this.connectionState = 'connecting';
    this._clearTimeouts();

    try {
      const url = this._buildUrl(endpoint, options);
      // console.log(`🔌 Connecting to SSE: ${url}`);
      
      this.eventSource = new EventSource(url);
      this._setupEventHandlers(handlers);
      this._setupConnectionTimeout();
      
    } catch (error) {
      this.connectionState = 'error';
      // console.error('❌ Failed to create SSE connection:', error);
      throw error;
    }
  }

  /**
   * Disconnect from SSE endpoint
   */
  disconnect(): void {
    this._clearTimeouts();
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    this.connectionState = 'disconnected';
    // console.log('🔌 SSE connection disconnected');
  }

  /**
   * Destroy the connection service
   */
  destroy(): void {
    this.isDestroyed = true;
    this.disconnect();
  }

  /**
   * Get current connection state
   */
  getConnectionState(): SSEConnectionState {
    return this.connectionState;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connectionState === 'connected' && 
           this.eventSource?.readyState === EventSource.OPEN;
  }

  /**
   * Get connection URL
   */
  getConnectionUrl(): string | null {
    return this.eventSource?.url || null;
  }

  /**
   * Get ready state
   */
  getReadyState(): number {
    return this.eventSource?.readyState || EventSource.CLOSED;
  }

  private _buildUrl(endpoint: string, options?: {
    sessionId?: string;
    resolved?: boolean;
  }): string {
    const url = new URL(endpoint, this.config.baseUrl);
    
    if (options?.sessionId) {
      url.searchParams.set('session_id', options.sessionId);
    }
    
    if (options?.resolved !== undefined) {
      url.searchParams.set('resolved', options.resolved.toString());
    }
    
    return url.toString();
  }

  private _setupEventHandlers(handlers: SSEEventHandlers): void {
    if (!this.eventSource) return;

    this.eventSource.onopen = () => {
      this.connectionState = 'connected';
      // console.log('✅ SSE connection established');
      handlers.onOpen();
    };

    this.eventSource.onmessage = (event) => {
      const message = SSEMessageService.parseMessage(event);
      if (message) {
        // console.log(`📨 SSE message received:`, message);
        handlers.onMessage(event);
      }
    };

    this.eventSource.onerror = (event) => {
      this.connectionState = 'error';
      // console.error('❌ SSE connection error:', {
      //   readyState: this.eventSource?.readyState,
      //   url: this.eventSource?.url,
      //   timestamp: new Date().toISOString(),
      // });
      handlers.onError(event);
    };
  }

  private _setupConnectionTimeout(): void {
    this.connectionTimeout = setTimeout(() => {
      if (this.connectionState === 'connecting') {
        // console.error('⏰ SSE connection timeout');
        this.connectionState = 'error';
        this.disconnect();
      }
    }, this.config.timeout);
  }

  private _clearTimeouts(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Setup auto-reconnect
   */
  setupAutoReconnect(
    endpoint: string,
    handlers: SSEEventHandlers,
    options?: {
      sessionId?: string;
      resolved?: boolean;
    }
  ): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectTimeout = setTimeout(() => {
      if (!this.isDestroyed && this.connectionState !== 'connected') {
        // console.log('🔄 Attempting to reconnect SSE...');
        this.connect(endpoint, handlers, { ...options, autoReconnect: true });
      }
    }, this.config.retryDelay);
  }
}
