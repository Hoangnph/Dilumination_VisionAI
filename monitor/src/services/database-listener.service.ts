/**
 * Database Listener Service
 * Clean separation of database listening functionality
 */

import { Client } from 'pg';
import { DatabaseListenerConfig, DatabaseNotification } from '@/types/sse';
import { getDatabaseConfig } from '@/config/sse';

export class DatabaseListenerService {
  private client: Client | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private isConnected: boolean = false;
  private config: DatabaseListenerConfig;
  private connectionPromise: Promise<void> | null = null;

  constructor(config?: Partial<DatabaseListenerConfig>) {
    this.config = { ...getDatabaseConfig(), ...config };
  }

  /**
   * Connect to database with retry logic
   */
  async connect(): Promise<void> {
    if (this.isConnected && this.client) {
      return;
    }

    // Prevent multiple simultaneous connection attempts
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = this._connectWithRetry();
    return this.connectionPromise;
  }

  private async _connectWithRetry(): Promise<void> {
    let retries = this.config.maxRetries;
    
    while (retries > 0) {
      try {
        await this._attemptConnection();
        this.isConnected = true;
        this.connectionPromise = null;
        // console.log('✅ Database listener connected successfully');
        return;
      } catch (error) {
        retries--;
        // console.error(`❌ Database connection failed (${this.config.maxRetries - retries}/${this.config.maxRetries}):`, error);
        
        if (retries === 0) {
          this.isConnected = false;
          this.client = null;
          this.connectionPromise = null;
          throw new Error(`Failed to connect to database after ${this.config.maxRetries} attempts: ${error}`);
        }
        
        // Exponential backoff
        const delay = this.config.connectionTimeoutMillis * (this.config.maxRetries - retries);
        await this._delay(delay);
      }
    }
  }

  private async _attemptConnection(): Promise<void> {
    this.client = new Client({
      host: this.config.host,
      port: this.config.port,
      database: this.config.database,
      user: this.config.user,
      password: this.config.password,
      connectionTimeoutMillis: this.config.connectionTimeoutMillis,
      query_timeout: this.config.queryTimeout,
    });

    // Set max listeners to prevent memory leak warning
    this.client.setMaxListeners(50);
    
    // Connect with timeout
    const connectPromise = this.client.connect();
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Connection timeout')), this.config.connectionTimeoutMillis);
    });
    
    await Promise.race([connectPromise, timeoutPromise]);
  }

  private async _delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Disconnect from database
   */
  async disconnect(): Promise<void> {
    if (!this.isConnected || !this.client) {
      return;
    }
    
    try {
      await this.client.end();
      this.isConnected = false;
      this.client = null;
      this.connectionPromise = null;
      // console.log('🔌 Database listener disconnected');
    } catch (error) {
      // console.error('❌ Failed to disconnect from database:', error);
    }
  }

  /**
   * Listen to database channel
   */
  async listen(channel: string, callback: (data: any) => void): Promise<void> {
    await this.connect();
    
    if (!this.client) {
      throw new Error('Database client not available');
    }
    
    // Add callback to listeners
    if (!this.listeners.has(channel)) {
      this.listeners.set(channel, new Set());
    }
    this.listeners.get(channel)!.add(callback);

    // Start listening if this is the first listener for this channel
    if (this.listeners.get(channel)!.size === 1) {
      await this.client.query(`LISTEN ${channel}`);
      // console.log(`👂 Started listening to channel: ${channel}`);
    }

    // Handle notifications
    this.client.on('notification', (msg: DatabaseNotification) => {
      if (msg.channel === channel) {
        try {
          const data = JSON.parse(msg.payload || '{}');
          const callbacks = this.listeners.get(channel);
          if (callbacks) {
            callbacks.forEach(cb => cb(data));
          }
        } catch (error) {
          // console.error('❌ Error parsing notification payload:', error);
        }
      }
    });
  }

  /**
   * Stop listening to database channel
   */
  async unlisten(channel: string, callback: (data: any) => void): Promise<void> {
    const callbacks = this.listeners.get(channel);
    if (callbacks) {
      callbacks.delete(callback);
      
      // Stop listening if no more callbacks
      if (callbacks.size === 0) {
        if (this.client) {
          await this.client.query(`UNLISTEN ${channel}`);
        }
        this.listeners.delete(channel);
        // console.log(`🔇 Stopped listening to channel: ${channel}`);
      }
    }
  }

  /**
   * Get connection status
   */
  get connected(): boolean {
    return this.isConnected;
  }

  /**
   * Get active listeners count for a channel
   */
  getListenerCount(channel: string): number {
    return this.listeners.get(channel)?.size || 0;
  }

  /**
   * Get all active channels
   */
  getActiveChannels(): string[] {
    return Array.from(this.listeners.keys());
  }

  /**
   * Get client for direct queries (use with caution)
   */
  getClient(): Client | null {
    return this.client;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      if (!this.client) {
        return false;
      }
      
      await this.client.query('SELECT 1');
      return true;
    } catch (error) {
      // console.error('❌ Database health check failed:', error);
      return false;
    }
  }
}

// Singleton instance
export const databaseListenerService = new DatabaseListenerService();
