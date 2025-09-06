#!/usr/bin/env node

/**
 * SSE Connection Test Script
 * Test SSE connections and verify functionality
 */

const { EventSource } = require('eventsource');

class SSETester {
  constructor() {
    this.baseUrl = 'http://localhost:3000';
    this.testResults = [];
  }

  async testBasicConnection() {
    console.log('🧪 Testing basic SSE connection...');
    
    return new Promise((resolve) => {
      const eventSource = new EventSource(`${this.baseUrl}/api/sse/sessions`);
      let messageCount = 0;
      let startTime = Date.now();

      eventSource.onopen = () => {
        console.log('✅ SSE connection opened');
        this.testResults.push({ test: 'Basic Connection', status: 'PASS', message: 'Connection opened' });
      };

      eventSource.onmessage = (event) => {
        messageCount++;
        const data = JSON.parse(event.data);
        console.log(`📨 Message ${messageCount}:`, {
          type: data.type,
          message: data.message,
          timestamp: data.timestamp
        });
        
        if (messageCount >= 3) {
          eventSource.close();
          const duration = Date.now() - startTime;
          console.log(`✅ Received ${messageCount} messages in ${duration}ms`);
          this.testResults.push({ 
            test: 'Message Reception', 
            status: 'PASS', 
            message: `Received ${messageCount} messages` 
          });
          resolve();
        }
      };

      eventSource.onerror = (error) => {
        console.error('❌ SSE connection error:', error);
        this.testResults.push({ test: 'Basic Connection', status: 'FAIL', message: 'Connection error' });
        eventSource.close();
        resolve();
      };

      // Timeout after 10 seconds
      setTimeout(() => {
        if (messageCount < 3) {
          console.log('⏰ Test timeout');
          eventSource.close();
          this.testResults.push({ test: 'Basic Connection', status: 'TIMEOUT', message: 'Test timeout' });
          resolve();
        }
      }, 10000);
    });
  }

  async testSessionFilteredConnection() {
    console.log('\n🧪 Testing SSE connection with session filter...');
    
    return new Promise((resolve) => {
      const sessionId = 'test-session-123';
      const eventSource = new EventSource(`${this.baseUrl}/api/sse/sessions?session_id=${sessionId}`);
      let messageCount = 0;
      let startTime = Date.now();

      eventSource.onopen = () => {
        console.log('✅ Filtered SSE connection opened');
        this.testResults.push({ test: 'Filtered Connection', status: 'PASS', message: 'Filtered connection opened' });
      };

      eventSource.onmessage = (event) => {
        messageCount++;
        const data = JSON.parse(event.data);
        console.log(`📨 Filtered Message ${messageCount}:`, {
          type: data.type,
          message: data.message,
          timestamp: data.timestamp
        });
        
        if (messageCount >= 2) {
          eventSource.close();
          const duration = Date.now() - startTime;
          console.log(`✅ Received ${messageCount} filtered messages in ${duration}ms`);
          this.testResults.push({ 
            test: 'Filtered Message Reception', 
            status: 'PASS', 
            message: `Received ${messageCount} filtered messages` 
          });
          resolve();
        }
      };

      eventSource.onerror = (error) => {
        console.error('❌ Filtered SSE connection error:', error);
        this.testResults.push({ test: 'Filtered Connection', status: 'FAIL', message: 'Filtered connection error' });
        eventSource.close();
        resolve();
      };

      // Timeout after 10 seconds
      setTimeout(() => {
        if (messageCount < 2) {
          console.log('⏰ Filtered test timeout');
          eventSource.close();
          this.testResults.push({ test: 'Filtered Connection', status: 'TIMEOUT', message: 'Filtered test timeout' });
          resolve();
        }
      }, 10000);
    });
  }

  async testAPIEndpoints() {
    console.log('\n🧪 Testing API endpoints...');
    
    try {
      // Test sessions API
      const sessionsResponse = await fetch(`${this.baseUrl}/api/sessions`);
      const sessionsData = await sessionsResponse.json();
      
      if (sessionsResponse.ok) {
        console.log('✅ Sessions API working:', {
          success: sessionsData.success,
          total: sessionsData.data?.total || 0
        });
        this.testResults.push({ test: 'Sessions API', status: 'PASS', message: 'API responding' });
      } else {
        console.error('❌ Sessions API error:', sessionsResponse.status);
        this.testResults.push({ test: 'Sessions API', status: 'FAIL', message: `HTTP ${sessionsResponse.status}` });
      }

      // Test dashboard stats API
      const statsResponse = await fetch(`${this.baseUrl}/api/dashboard/stats`);
      const statsData = await statsResponse.json();
      
      if (statsResponse.ok) {
        console.log('✅ Dashboard stats API working:', {
          success: statsData.success,
          totalSessions: statsData.data?.total_sessions || 0
        });
        this.testResults.push({ test: 'Dashboard Stats API', status: 'PASS', message: 'API responding' });
      } else {
        console.error('❌ Dashboard stats API error:', statsResponse.status);
        this.testResults.push({ test: 'Dashboard Stats API', status: 'FAIL', message: `HTTP ${statsResponse.status}` });
      }

    } catch (error) {
      console.error('❌ API test error:', error.message);
      this.testResults.push({ test: 'API Endpoints', status: 'FAIL', message: error.message });
    }
  }

  async testDatabaseConnection() {
    console.log('\n🧪 Testing database connection...');
    
    try {
      const response = await fetch(`${this.baseUrl}/api/debug`);
      const data = await response.json();
      
      if (response.ok && data.success) {
        console.log('✅ Database connection working:', {
          connected: data.database?.connected || false,
          sessions: data.database?.sessions || 0
        });
        this.testResults.push({ test: 'Database Connection', status: 'PASS', message: 'Database connected' });
      } else {
        console.error('❌ Database connection error');
        this.testResults.push({ test: 'Database Connection', status: 'FAIL', message: 'Database not connected' });
      }
    } catch (error) {
      console.error('❌ Database test error:', error.message);
      this.testResults.push({ test: 'Database Connection', status: 'FAIL', message: error.message });
    }
  }

  printResults() {
    console.log('\n📊 TEST RESULTS SUMMARY:');
    console.log('='.repeat(50));
    
    const passed = this.testResults.filter(r => r.status === 'PASS').length;
    const failed = this.testResults.filter(r => r.status === 'FAIL').length;
    const timeout = this.testResults.filter(r => r.status === 'TIMEOUT').length;
    
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`⏰ Timeout: ${timeout}`);
    console.log(`📊 Total: ${this.testResults.length}`);
    
    console.log('\n📋 DETAILED RESULTS:');
    this.testResults.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : '⏰';
      console.log(`${icon} ${result.test}: ${result.message}`);
    });
    
    if (failed === 0 && timeout === 0) {
      console.log('\n🎉 ALL TESTS PASSED! SSE is working correctly.');
    } else {
      console.log('\n⚠️ Some tests failed. Check the issues above.');
    }
  }

  async runAllTests() {
    console.log('🚀 Starting SSE Connection Tests...\n');
    
    await this.testAPIEndpoints();
    await this.testDatabaseConnection();
    await this.testBasicConnection();
    await this.testSessionFilteredConnection();
    
    this.printResults();
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  const tester = new SSETester();
  tester.runAllTests().catch(console.error);
}

module.exports = SSETester;
