#!/usr/bin/env node

/**
 * Create Test Session Script
 * Create a test session to verify SSE functionality
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

async function createTestSession() {
  const client = new Client(dbConfig);
  
  try {
    console.log('🔌 Connecting to database...');
    await client.connect();
    console.log('✅ Database connected successfully');

    // Create a test session
    const sessionData = {
      session_name: 'SSE Test Session',
      input_source: 'test_camera',
      status: 'active',
      created_at: new Date().toISOString(),
    };

    console.log('📝 Creating test session...');
    const insertQuery = `
      INSERT INTO sessions (session_name, input_source, status, created_at)
      VALUES ($1, $2, $3, $4)
      RETURNING id, session_name, input_source, status, created_at
    `;

    const result = await client.query(insertQuery, [
      sessionData.session_name,
      sessionData.input_source,
      sessionData.status,
      sessionData.created_at
    ]);

    const session = result.rows[0];
    console.log('✅ Test session created:', {
      id: session.id,
      name: session.session_name,
      source: session.input_source,
      status: session.status,
      created: session.created_at
    });

    // Create some test movements
    console.log('📝 Creating test movements...');
    const movements = [
      { direction: 'in', timestamp: new Date(Date.now() - 30000).toISOString() },
      { direction: 'out', timestamp: new Date(Date.now() - 20000).toISOString() },
      { direction: 'in', timestamp: new Date(Date.now() - 10000).toISOString() },
    ];

    for (const movement of movements) {
      const movementQuery = `
        INSERT INTO people_movements (session_id, person_id, movement_direction, movement_time)
        VALUES ($1, $2, $3, $4)
        RETURNING id, movement_direction, movement_time
      `;
      
      const movementResult = await client.query(movementQuery, [
        session.id,
        Math.floor(Math.random() * 1000), // Random person_id
        movement.direction,
        movement.timestamp
      ]);
      
      console.log(`✅ Movement created:`, {
        id: movementResult.rows[0].id,
        direction: movementResult.rows[0].movement_direction,
        timestamp: movementResult.rows[0].movement_time
      });
    }

    console.log('🎉 Test data created successfully!');
    console.log('📊 Session ID:', session.id);
    console.log('🔗 You can now test SSE with this session ID');

    return session.id;

  } catch (error) {
    console.error('❌ Error creating test session:', error);
    throw error;
  } finally {
    await client.end();
    console.log('🔌 Database disconnected');
  }
}

// Run if this script is executed directly
if (require.main === module) {
  createTestSession().catch(console.error);
}

module.exports = createTestSession;
