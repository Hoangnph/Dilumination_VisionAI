/**
 * SSE Message Service
 * Handles creation, encoding, and parsing of SSE messages
 */

import { SSEMessage } from '@/types/sse';

export class SSEMessageService {
  /**
   * Create a new SSE message
   */
  static createMessage(
    type: SSEMessage['type'],
    data?: any,
    message?: string,
    error?: string
  ): SSEMessage {
    return {
      type,
      data,
      message,
      error,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Encode SSE message for transmission
   */
  static encodeMessage(message: SSEMessage): string {
    return `data: ${JSON.stringify(message)}\n\n`;
  }

  /**
   * Parse incoming SSE message
   */
  static parseMessage(event: MessageEvent): SSEMessage | null {
    try {
      const data = JSON.parse(event.data);
      
      // Validate message structure
      if (!data.type || !data.timestamp) {
        console.warn('Invalid SSE message structure:', data);
        return null;
      }
      
      return data as SSEMessage;
    } catch (error) {
      console.error('Failed to parse SSE message:', error);
      return null;
    }
  }

  /**
   * Create connection message
   */
  static createConnectionMessage(endpoint: string): SSEMessage {
    return this.createMessage(
      'connection',
      { endpoint },
      `Connected to ${endpoint}`
    );
  }

  /**
   * Create heartbeat message
   */
  static createHeartbeatMessage(): SSEMessage {
    return this.createMessage('heartbeat', null, 'Heartbeat');
  }

  /**
   * Create error message
   */
  static createErrorMessage(error: string, details?: any): SSEMessage {
    return this.createMessage('error', details, 'Error occurred', error);
  }

  /**
   * Create data message
   */
  static createDataMessage(data: any, message?: string): SSEMessage {
    return this.createMessage('data', data, message);
  }

  /**
   * Create test message
   */
  static createTestMessage(message: string = 'Test message'): SSEMessage {
    return this.createMessage('test', { message }, message);
  }

  /**
   * Validate message type
   */
  static isValidMessageType(type: string): type is SSEMessage['type'] {
    return ['connection', 'data', 'error', 'heartbeat', 'test'].includes(type);
  }

  /**
   * Get message priority for logging
   */
  static getMessagePriority(message: SSEMessage): 'low' | 'medium' | 'high' {
    switch (message.type) {
      case 'error':
        return 'high';
      case 'connection':
      case 'data':
        return 'medium';
      case 'heartbeat':
      case 'test':
        return 'low';
      default:
        return 'low';
    }
  }
}
