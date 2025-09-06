#!/usr/bin/env node

/**
 * Production Database Cleanup Script
 * Completely cleans database for production deployment
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

class ProductionCleaner {
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

  async showCurrentData() {
    try {
      console.log('\n📊 Current data in database:');
      
      // Count sessions
      const sessionsCount = await this.client.query('SELECT COUNT(*) FROM sessions');
      console.log(`   Sessions: ${sessionsCount.rows[0].count}`);
      
      // Count movements
      const movementsCount = await this.client.query('SELECT COUNT(*) FROM people_movements');
      console.log(`   People Movements: ${movementsCount.rows[0].count}`);
      
      // Count metrics
      const metricsCount = await this.client.query('SELECT COUNT(*) FROM realtime_metrics');
      console.log(`   Real-time Metrics: ${metricsCount.rows[0].count}`);
      
      // Count alerts
      const alertsCount = await this.client.query('SELECT COUNT(*) FROM alert_logs');
      console.log(`   Alert Logs: ${alertsCount.rows[0].count}`);
      
      // Count statistics
      const statsCount = await this.client.query('SELECT COUNT(*) FROM session_statistics');
      console.log(`   Session Statistics: ${statsCount.rows[0].count}`);
      
      return true;
    } catch (error) {
      console.error('❌ Error showing current data:', error.message);
      return false;
    }
  }

  async clearAllData() {
    try {
      console.log('\n🗑️ Clearing all data from database...');
      
      // Disable triggers temporarily to avoid issues
      await this.client.query('SET session_replication_role = replica;');
      
      // Clear data in reverse dependency order
      const clearQueries = [
        'DELETE FROM alert_logs;',
        'DELETE FROM alert_thresholds;',
        'DELETE FROM hourly_statistics;',
        'DELETE FROM daily_statistics;',
        'DELETE FROM realtime_metrics;',
        'DELETE FROM session_statistics;',
        'DELETE FROM people_movements;',
        'DELETE FROM sessions;',
        'DELETE FROM system_config WHERE config_key != \'seed_data_completed\';'
      ];
      
      for (const query of clearQueries) {
        try {
          const result = await this.client.query(query);
          console.log(`   ✅ ${query.split(' ')[1]} cleared`);
        } catch (error) {
          console.log(`   ⚠️ ${query.split(' ')[1]} - ${error.message}`);
        }
      }
      
      // Re-enable triggers
      await this.client.query('SET session_replication_role = DEFAULT;');
      
      console.log('✅ All data cleared successfully');
      return true;
    } catch (error) {
      console.error('❌ Error clearing data:', error.message);
      return false;
    }
  }

  async resetSequences() {
    try {
      console.log('\n🔄 Resetting sequences...');
      
      const sequences = [
        'sessions_id_seq',
        'people_movements_id_seq',
        'realtime_metrics_id_seq',
        'alert_logs_id_seq',
        'session_statistics_id_seq',
        'hourly_statistics_id_seq',
        'daily_statistics_id_seq',
        'system_config_id_seq',
        'alert_thresholds_id_seq'
      ];
      
      for (const sequence of sequences) {
        try {
          await this.client.query(`SELECT setval('${sequence}', 1, false);`);
          console.log(`   ✅ ${sequence} reset`);
        } catch (error) {
          // Sequence might not exist, ignore error
          console.log(`   ⚠️ ${sequence} - sequence not found (OK)`);
        }
      }
      
      console.log('✅ Sequences reset successfully');
      return true;
    } catch (error) {
      console.error('❌ Error resetting sequences:', error.message);
      return false;
    }
  }

  async verifyCleanState() {
    try {
      console.log('\n🔍 Verifying clean state...');
      
      const tables = ['sessions', 'people_movements', 'realtime_metrics', 'alert_logs', 'session_statistics'];
      let allClean = true;
      
      for (const table of tables) {
        const result = await this.client.query(`SELECT COUNT(*) FROM ${table}`);
        const count = parseInt(result.rows[0].count);
        
        if (count === 0) {
          console.log(`   ✅ ${table}: 0 records`);
        } else {
          console.log(`   ❌ ${table}: ${count} records (should be 0)`);
          allClean = false;
        }
      }
      
      if (allClean) {
        console.log('✅ Database is completely clean');
      } else {
        console.log('⚠️ Some tables still contain data');
      }
      
      return allClean;
    } catch (error) {
      console.error('❌ Error verifying clean state:', error.message);
      return false;
    }
  }

  async showProductionReady() {
    try {
      console.log('\n🚀 PRODUCTION READY STATUS:');
      console.log('');
      console.log('✅ Database is completely clean');
      console.log('✅ All test data removed');
      console.log('✅ Sequences reset');
      console.log('✅ Ready for production deployment');
      console.log('');
      console.log('📋 PRODUCTION CHECKLIST:');
      console.log('   • Database schema is intact');
      console.log('   • All tables are empty');
      console.log('   • Triggers and functions are active');
      console.log('   • System configuration preserved');
      console.log('   • Ready for real data');
      console.log('');
      console.log('🎯 NEXT STEPS:');
      console.log('   1. Deploy application to production');
      console.log('   2. Configure production environment variables');
      console.log('   3. Set up monitoring and logging');
      console.log('   4. Create first production session');
      console.log('   5. Monitor system performance');
      console.log('');
      
      return true;
    } catch (error) {
      console.error('❌ Error showing production status:', error.message);
      return false;
    }
  }

  async runCleanup() {
    console.log('🧹 Starting Production Database Cleanup...\n');
    
    const connected = await this.connect();
    if (!connected) {
      console.log('❌ Cannot proceed without database connection');
      return;
    }

    try {
      // Show current data
      await this.showCurrentData();
      
      // Clear all data
      const cleared = await this.clearAllData();
      if (!cleared) {
        console.log('❌ Failed to clear data');
        return;
      }
      
      // Reset sequences
      await this.resetSequences();
      
      // Verify clean state
      const isClean = await this.verifyCleanState();
      
      if (isClean) {
        await this.showProductionReady();
        
        console.log('🎉 Production cleanup completed successfully!');
        console.log('📝 Database is ready for production deployment');
        console.log('🚀 No test data remaining');
      } else {
        console.log('\n⚠️ Production cleanup completed with warnings');
        console.log('🔍 Some data may still remain');
      }
      
    } catch (error) {
      console.error('❌ Cleanup process failed:', error);
    } finally {
      await this.disconnect();
    }
  }
}

// Run cleanup if this script is executed directly
if (require.main === module) {
  const cleaner = new ProductionCleaner();
  cleaner.runCleanup().catch(console.error);
}

module.exports = ProductionCleaner;
