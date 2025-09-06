#!/usr/bin/env node

/**
 * SSE Connection Test Script
 * Tests the SSE timeout fixes and connection stability
 */

const EventSource = require('eventsource');

class SSETester {
  constructor() {
    this.baseUrl = 'http://localhost:3000';
    this.testResults = [];
    this.connections = [];
  }

  async runTests() {
    console.log('🧪 Starting SSE Connection Tests...\n');
    
    try {
      await this.testBasicConnection();
      await this.testMultipleConnections();
      await this.testConnectionTimeout();
      await this.testReconnection();
      
      this.printResults();
    } catch (error) {
      console.error('❌ Test suite failed:', error);
    }
  }

  async testBasicConnection() {
    console.log('📡 Test 1: Basic SSE Connection');
    
    return new Promise((resolve) => {
      const startTime = Date.now();
      const eventSource = new EventSource(`${this.baseUrl}/api/sse/sessions`);
      
      eventSource.onopen = () => {
        const connectionTime = Date.now() - startTime;
        this.testResults.push({
          test: 'Basic Connection',
          status: 'PASS',
          connectionTime: `${connectionTime}ms`,
          message: 'Connection established successfully'
        });
        console.log(`✅ Connection established in ${connectionTime}ms`);
        eventSource.close();
        resolve();
      };

      eventSource.onerror = (error) => {
        this.testResults.push({
          test: 'Basic Connection',
          status: 'FAIL',
          error: error.message || 'Connection failed',
          message: 'Failed to establish connection'
        });
        console.log('❌ Connection failed');
        eventSource.close();
        resolve();
      };

      // Timeout after 10 seconds
      setTimeout(() => {
        this.testResults.push({
          test: 'Basic Connection',
          status: 'TIMEOUT',
          message: 'Connection timeout after 10s'
        });
        console.log('⏰ Connection timeout');
        eventSource.close();
        resolve();
      }, 10000);
    });
  }

  async testMultipleConnections() {
    console.log('\n📡 Test 2: Multiple Connections');
    
    const connectionPromises = [];
    
    for (let i = 0; i < 3; i++) {
      connectionPromises.push(this.createConnection(i));
    }
    
    const results = await Promise.allSettled(connectionPromises);
    const successCount = results.filter(r => r.status === 'fulfilled').length;
    
    this.testResults.push({
      test: 'Multiple Connections',
      status: successCount === 3 ? 'PASS' : 'PARTIAL',
      successCount: `${successCount}/3`,
      message: `${successCount} out of 3 connections successful`
    });
    
    console.log(`✅ ${successCount}/3 connections successful`);
  }

  async createConnection(id) {
    return new Promise((resolve, reject) => {
      const eventSource = new EventSource(`${this.baseUrl}/api/sse/sessions`);
      
      eventSource.onopen = () => {
        console.log(`  ✅ Connection ${id + 1} established`);
        setTimeout(() => {
          eventSource.close();
          resolve();
        }, 2000);
      };

      eventSource.onerror = () => {
        console.log(`  ❌ Connection ${id + 1} failed`);
        eventSource.close();
        reject(new Error(`Connection ${id + 1} failed`));
      };

      setTimeout(() => {
        eventSource.close();
        reject(new Error(`Connection ${id + 1} timeout`));
      }, 5000);
    });
  }

  async testConnectionTimeout() {
    console.log('\n📡 Test 3: Connection Timeout (60s)');
    
    return new Promise((resolve) => {
      const startTime = Date.now();
      const eventSource = new EventSource(`${this.baseUrl}/api/sse/sessions`);
      
      eventSource.onopen = () => {
        console.log('✅ Connection established, waiting for timeout...');
      };

      eventSource.onerror = (error) => {
        const elapsed = Date.now() - startTime;
        this.testResults.push({
          test: 'Connection Timeout',
          status: elapsed >= 60000 ? 'PASS' : 'FAIL',
          elapsed: `${elapsed}ms`,
          message: elapsed >= 60000 ? 'Timeout occurred after 60s' : 'Premature timeout'
        });
        console.log(`⏰ Connection error after ${elapsed}ms`);
        eventSource.close();
        resolve();
      };

      // Wait for timeout
      setTimeout(() => {
        const elapsed = Date.now() - startTime;
        this.testResults.push({
          test: 'Connection Timeout',
          status: 'PASS',
          elapsed: `${elapsed}ms`,
          message: 'Connection maintained for 60s+'
        });
        console.log(`✅ Connection maintained for ${elapsed}ms`);
        eventSource.close();
        resolve();
      }, 65000);
    });
  }

  async testReconnection() {
    console.log('\n📡 Test 4: Reconnection Logic');
    
    return new Promise((resolve) => {
      let reconnectCount = 0;
      const eventSource = new EventSource(`${this.baseUrl}/api/sse/sessions`);
      
      eventSource.onopen = () => {
        console.log('✅ Initial connection established');
        
        // Simulate connection drop after 5 seconds
        setTimeout(() => {
          console.log('🔄 Simulating connection drop...');
          eventSource.close();
        }, 5000);
      };

      eventSource.onerror = () => {
        reconnectCount++;
        console.log(`🔄 Reconnection attempt ${reconnectCount}`);
        
        if (reconnectCount >= 3) {
          this.testResults.push({
            test: 'Reconnection Logic',
            status: 'PASS',
            reconnectCount: reconnectCount,
            message: 'Reconnection logic working correctly'
          });
          console.log('✅ Reconnection logic working');
          eventSource.close();
          resolve();
        }
      };

      setTimeout(() => {
        this.testResults.push({
          test: 'Reconnection Logic',
          status: 'TIMEOUT',
          message: 'Reconnection test timeout'
        });
        console.log('⏰ Reconnection test timeout');
        eventSource.close();
        resolve();
      }, 30000);
    });
  }

  printResults() {
    console.log('\n📊 TEST RESULTS SUMMARY');
    console.log('='.repeat(50));
    
    this.testResults.forEach(result => {
      const status = result.status === 'PASS' ? '✅' : 
                   result.status === 'FAIL' ? '❌' : 
                   result.status === 'PARTIAL' ? '⚠️' : '⏰';
      
      console.log(`${status} ${result.test}: ${result.message}`);
      if (result.connectionTime) console.log(`   Connection Time: ${result.connectionTime}`);
      if (result.successCount) console.log(`   Success Rate: ${result.successCount}`);
      if (result.elapsed) console.log(`   Elapsed Time: ${result.elapsed}`);
      if (result.reconnectCount) console.log(`   Reconnect Count: ${result.reconnectCount}`);
    });
    
    const passCount = this.testResults.filter(r => r.status === 'PASS').length;
    const totalCount = this.testResults.length;
    
    console.log('\n🎯 OVERALL RESULT:');
    console.log(`   Passed: ${passCount}/${totalCount} tests`);
    console.log(`   Success Rate: ${Math.round((passCount / totalCount) * 100)}%`);
    
    if (passCount === totalCount) {
      console.log('🎉 All tests passed! SSE fixes are working correctly.');
    } else {
      console.log('⚠️ Some tests failed. Please check the implementation.');
    }
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  const tester = new SSETester();
  tester.runTests().catch(console.error);
}

module.exports = SSETester;
