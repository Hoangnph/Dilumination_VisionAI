#!/usr/bin/env node

/**
 * Database Connection Test Script
 * Tests database connection and creates test sessions
 */

const { Client } = require('pg');

// Database configuration
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'people_counter',
  user: process.env.DB_USER || 'people_counter_user',
  password: process.env.DB_PASSWORD || 'secure_password_123',
  connectionTimeoutMillis: 10000,
  query_timeout: 30000,
};

class DatabaseTester {
  constructor() {
    this.client = null;
  }

  async connect() {
    try {
      console.log('🔌 Connecting to database...');
      this.client = new Client(dbConfig);
      await this.client.connect();
      console.log('✅ Database connected successfully');
      return true;
    } catch (error) {
      console.error('❌ Database connection failed:', error.message);
      return false;
    }
  }

  async disconnect() {
    if (this.client) {
      await this.client.end();
      console.log('🔌 Database disconnected');
    }
  }

  async testConnection() {
    try {
      const result = await this.client.query('SELECT NOW() as current_time');
      console.log('✅ Database query successful:', result.rows[0].current_time);
      return true;
    } catch (error) {
      console.error('❌ Database query failed:', error.message);
      return false;
    }
  }

  async checkTables() {
    try {
      console.log('\n📋 Checking database tables...');
      
      // Check if sessions table exists
      const sessionsCheck = await this.client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_schema = 'public' 
          AND table_name = 'sessions'
        );
      `);
      
      if (sessionsCheck.rows[0].exists) {
        console.log('✅ Sessions table exists');
        
        // Count sessions
        const countResult = await this.client.query('SELECT COUNT(*) FROM sessions');
        const sessionCount = parseInt(countResult.rows[0].count);
        console.log(`📊 Total sessions in database: ${sessionCount}`);
        
        if (sessionCount === 0) {
          console.log('⚠️ No sessions found in database');
          return false;
        } else {
          // Show recent sessions
          const recentSessions = await this.client.query(`
            SELECT id, session_name, status, start_time, created_at 
            FROM sessions 
            ORDER BY created_at DESC 
            LIMIT 5
          `);
          
          console.log('\n📝 Recent sessions:');
          recentSessions.rows.forEach((session, index) => {
            console.log(`  ${index + 1}. ${session.session_name} (${session.status}) - ${session.start_time}`);
          });
        }
      } else {
        console.log('❌ Sessions table does not exist');
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('❌ Error checking tables:', error.message);
      return false;
    }
  }

  async createTestSessions() {
    try {
      console.log('\n🆕 Creating test sessions...');
      
      const testSessions = [
        {
          session_name: 'Live Demo Session',
          input_source: 'camera://0',
          status: 'active',
          fps: 30.0,
          resolution_width: 640,
          resolution_height: 480
        },
        {
          session_name: 'Video Processing Session',
          input_source: 'utils/data/tests/test_1.mp4',
          status: 'completed',
          fps: 25.5,
          resolution_width: 1280,
          resolution_height: 720
        },
        {
          session_name: 'Stream Analysis Session',
          input_source: 'rtsp://192.168.1.100:554/stream',
          status: 'active',
          fps: 20.0,
          resolution_width: 1920,
          resolution_height: 1080
        }
      ];

      for (const session of testSessions) {
        const insertQuery = `
          INSERT INTO sessions (
            session_name,
            input_source,
            status,
            fps,
            resolution_width,
            resolution_height,
            confidence_threshold,
            skip_frames,
            max_disappeared,
            max_distance
          ) VALUES ($1, $2, $3, $4, $5, $6, 0.3, 3, 15, 80)
          RETURNING id, session_name, status
        `;
        
        const result = await this.client.query(insertQuery, [
          session.session_name,
          session.input_source,
          session.status,
          session.fps,
          session.resolution_width,
          session.resolution_height
        ]);
        
        console.log(`✅ Created session: ${result.rows[0].session_name} (${result.rows[0].status})`);
      }
      
      return true;
    } catch (error) {
      console.error('❌ Error creating test sessions:', error.message);
      return false;
    }
  }

  async testAPIEndpoint() {
    try {
      console.log('\n🌐 Testing API endpoint...');
      
      // Test the sessions API query
      const query = `
        SELECT * FROM sessions 
        ORDER BY created_at DESC 
        LIMIT 10 OFFSET 0
      `;
      
      const result = await this.client.query(query);
      
      console.log(`✅ API query successful: ${result.rows.length} sessions found`);
      
      if (result.rows.length > 0) {
        console.log('\n📝 Sessions from API query:');
        result.rows.forEach((session, index) => {
          console.log(`  ${index + 1}. ${session.session_name} (${session.status}) - ${session.created_at}`);
        });
      }
      
      return true;
    } catch (error) {
      console.error('❌ API endpoint test failed:', error.message);
      return false;
    }
  }

  async runTests() {
    console.log('🧪 Starting Database Tests...\n');
    
    const connected = await this.connect();
    if (!connected) {
      console.log('❌ Cannot proceed without database connection');
      return;
    }

    try {
      await this.testConnection();
      const tablesExist = await this.checkTables();
      
      if (!tablesExist) {
        console.log('⚠️ Creating test sessions...');
        await this.createTestSessions();
        await this.checkTables();
      }
      
      await this.testAPIEndpoint();
      
      console.log('\n🎉 All tests completed successfully!');
      
    } catch (error) {
      console.error('❌ Test suite failed:', error);
    } finally {
      await this.disconnect();
    }
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  const tester = new DatabaseTester();
  tester.runTests().catch(console.error);
}

module.exports = DatabaseTester;
