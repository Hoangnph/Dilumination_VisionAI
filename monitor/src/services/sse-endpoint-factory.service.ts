/**
 * SSE Endpoint Factory Service
 * Centralized factory for creating SSE endpoints with consistent behavior
 */

import { NextRequest } from 'next/server';
import { databaseListenerService } from '@/services/database-listener.service';
import { SSEMessageService } from '@/services/sse-message.service';
import { DB_CHANNELS } from '@/config/sse';
import { SSEData, isSessionSSEData, isMovementSSEData, isAlertSSEData, isMetricsSSEData } from '@/types/sse';

// SSE Response helper
export function createSSEResponse(stream: ReadableStream) {
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Cache-Control, Content-Type',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'X-Accel-Buffering': 'no', // Disable nginx buffering
    },
  });
}

// Base SSE handler
export class SSEHandler {
  private encoder = new TextEncoder();
  private isClosed = false;
  private lastMessageTime = 0;
  private messageThrottleMs = 1000; // Increased to 1 second between messages
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private debounceTimeout: NodeJS.Timeout | null = null;
  private pendingData: SSEData | null = null;
  private lastSentDataHash: string | null = null;

  constructor(
    private controller: ReadableStreamDefaultController,
    private channel: string,
    private filterCallback?: (data: SSEData) => boolean
  ) {}

  async start(): Promise<void> {
    try {
      // Send initial connection message
      await this.sendMessage(SSEMessageService.createConnectionMessage(this.channel));
      
      // Send test message
      await this.sendMessage(SSEMessageService.createTestMessage(`Connected to ${this.channel}`));
      
      // Setup heartbeat
      this.setupHeartbeat();
      
      // Setup database listener
      await this.setupDatabaseListener();
      
    } catch (error) {
      // console.error(`❌ Error starting SSE handler for ${this.channel}:`, error);
      await this.sendMessage(SSEMessageService.createErrorMessage(
        `Failed to start ${this.channel} listener`,
        { error: error instanceof Error ? error.message : 'Unknown error' }
      ));
    }
  }

  private async sendMessage(message: any): Promise<void> {
    if (this.isClosed || !this.controller) {
      return;
    }
    
    try {
      const encodedMessage = this.encoder.encode(SSEMessageService.encodeMessage(message));
      this.controller.enqueue(encodedMessage);
    } catch (error) {
      // Controller might be closed, mark as closed and ignore
      if (error instanceof Error && (
        error.message.includes('already closed') || 
        error.message.includes('Invalid state')
      )) {
        this.isClosed = true;
      }
    }
  }

  private setupHeartbeat(): void {
    this.heartbeatInterval = setInterval(async () => {
      if (!this.isClosed && this.controller) {
        await this.sendMessage(SSEMessageService.createHeartbeatMessage());
      }
    }, 30000); // 30 seconds
  }

  private async setupDatabaseListener(): Promise<void> {
    const handleDataChange = async (data: SSEData) => {
      // Apply filter if provided
      if (this.filterCallback && !this.filterCallback(data)) {
        return;
      }

      // Store the latest data
      this.pendingData = data;

      // Clear existing debounce timeout
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }

      // Set new debounce timeout
      this.debounceTimeout = setTimeout(async () => {
        if (this.pendingData && !this.isClosed) {
          // Create hash to check for duplicates
          const dataHash = JSON.stringify({
            table: this.pendingData.table,
            action: this.pendingData.action,
            id: this.pendingData.data?.id,
            updated_at: this.pendingData.data?.updated_at
          });

          // Skip if same data was already sent
          if (this.lastSentDataHash === dataHash) {
            this.pendingData = null;
            return;
          }

          // Additional throttling check
          const now = Date.now();
          if (now - this.lastMessageTime < this.messageThrottleMs) {
            return;
          }
          this.lastMessageTime = now;
          this.lastSentDataHash = dataHash;

          await this.sendMessage(SSEMessageService.createDataMessage(this.pendingData));
          this.pendingData = null;
        }
      }, 500); // 500ms debounce delay
    };

    // Start listening with retry logic
    let retries = 3;
    while (retries > 0) {
      try {
        await databaseListenerService.listen(this.channel, handleDataChange);
        // console.log(`✅ [${this.channel}] Database listener started successfully`);
        return;
      } catch (error) {
        retries--;
        // console.error(`❌ [${this.channel}] Error starting listener (${3 - retries}/3):`, error);
        
        if (retries === 0) {
          await this.sendMessage(SSEMessageService.createErrorMessage(
            `Failed to start ${this.channel} listener after 3 attempts`,
            { error: error instanceof Error ? error.message : 'Unknown error' }
          ));
        } else {
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }
  }

  async cleanup(): Promise<void> {
    this.isClosed = true;
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    if (this.debounceTimeout) {
      clearTimeout(this.debounceTimeout);
      this.debounceTimeout = null;
    }
    
    try {
      await databaseListenerService.unlisten(this.channel, () => {});
      this.controller.close();
    } catch (error) {
      // console.error(`❌ Error cleaning up ${this.channel}:`, error);
    }
  }
}

// SSE Endpoint Factory
export class SSEEndpointFactory {
  /**
   * Create a generic SSE endpoint handler
   */
  static createEndpoint(
    channel: string,
    endpointName: string,
    filterCallback?: (data: SSEData, searchParams: URLSearchParams) => boolean
  ) {
    return async function GET(request: NextRequest) {
      const { searchParams } = new URL(request.url);
      const sessionId = searchParams.get('session_id');
      const resolved = searchParams.get('resolved');

      // console.log(`[SSE ${endpointName}] Client connected. Session ID filter: ${sessionId || 'none'}, Resolved filter: ${resolved || 'none'}`);

      const stream = new ReadableStream({
        async start(controller) {
          const handler = new SSEHandler(
            controller,
            channel,
            filterCallback ? (data: any) => filterCallback(data, searchParams) : undefined
          );

          await handler.start();

          // Handle client disconnect
          request.signal.addEventListener('abort', async () => {
            // console.log(`[SSE ${endpointName}] Client disconnected (abort signal)`);
            await handler.cleanup();
          });
        }
      });

      return createSSEResponse(stream);
    };
  }

  /**
   * Create sessions SSE endpoint
   */
  static createSessionsEndpoint() {
    return this.createEndpoint(
      DB_CHANNELS.SESSION_CHANGES,
      'Sessions',
      (data: SSEData, searchParams: URLSearchParams) => {
        const sessionId = searchParams.get('session_id');
        return !sessionId || (isSessionSSEData(data) && data.data?.id === sessionId);
      }
    );
  }

  /**
   * Create movements SSE endpoint
   */
  static createMovementsEndpoint() {
    return this.createEndpoint(
      DB_CHANNELS.MOVEMENT_CHANGES,
      'Movements',
      (data: SSEData, searchParams: URLSearchParams) => {
        const sessionId = searchParams.get('session_id');
        return !sessionId || (isMovementSSEData(data) && data.data?.session_id === sessionId);
      }
    );
  }

  /**
   * Create alerts SSE endpoint
   */
  static createAlertsEndpoint() {
    return this.createEndpoint(
      DB_CHANNELS.ALERT_CHANGES,
      'Alerts',
      (data: SSEData, searchParams: URLSearchParams) => {
        const sessionId = searchParams.get('session_id');
        const resolved = searchParams.get('resolved');

        // Filter by session_id if provided
        if (sessionId && (!isAlertSSEData(data) || data.data?.session_id !== sessionId)) {
          return false;
        }

        // Filter by resolved status if provided
        if (resolved !== null && (!isAlertSSEData(data) || data.data?.is_resolved !== (resolved === 'true'))) {
          return false;
        }

        return true;
      }
    );
  }

  /**
   * Create metrics SSE endpoint
   */
  static createMetricsEndpoint() {
    return this.createEndpoint(
      DB_CHANNELS.METRICS_CHANGES,
      'Metrics',
      (data: SSEData, searchParams: URLSearchParams) => {
        const sessionId = searchParams.get('session_id');
        return !sessionId || (isMetricsSSEData(data) && data.data?.session_id === sessionId);
      }
    );
  }

  /**
   * Create OPTIONS handler for CORS
   */
  static createOptionsHandler() {
    return async function OPTIONS() {
      return new Response(null, {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Cache-Control, Content-Type',
        },
      });
    };
  }
}
