#!/usr/bin/env python3
"""
People Counter Database Migration Manager
Production-ready migration system for PostgreSQL
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add database directory to path
sys.path.append(str(Path(__file__).parent))

from config.settings import db_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migrations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationManager:
    """Database migration manager"""
    
    def __init__(self):
        self.engine = None
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.seeds_dir = Path(__file__).parent / "seeds"
        self.migrations_table = "migration_history"
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(
                db_config.async_connection_string,
                echo=False
            )
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    async def create_migrations_table(self):
        """Create migrations tracking table"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    checksum VARCHAR(64),
                    execution_time_ms INTEGER
                )
            """))
            logger.info("Migrations table created/verified")
    
    def get_migration_files(self) -> List[Path]:
        """Get sorted list of migration files"""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        migration_files = sorted([
            f for f in self.migrations_dir.glob("*.sql")
            if f.name[0].isdigit()  # Only files starting with numbers
        ])
        
        logger.info(f"Found {len(migration_files)} migration files")
        return migration_files
    
    def get_seed_files(self) -> List[Path]:
        """Get sorted list of seed files"""
        if not self.seeds_dir.exists():
            logger.warning(f"Seeds directory not found: {self.seeds_dir}")
            return []
        
        seed_files = sorted([
            f for f in self.seeds_dir.glob("*.sql")
            if f.name[0].isdigit()  # Only files starting with numbers
        ])
        
        logger.info(f"Found {len(seed_files)} seed files")
        return seed_files
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(f"""
                    SELECT migration_name FROM {self.migrations_table}
                    ORDER BY applied_at
                """))
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    async def apply_migration(self, migration_file: Path) -> bool:
        """Apply a single migration"""
        migration_name = migration_file.name
        start_time = datetime.now()
        
        try:
            logger.info(f"Applying migration: {migration_name}")
            
            # Read migration file
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.md5(migration_sql.encode()).hexdigest()
            
            # Apply migration - use psycopg2 for complex SQL
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            conn = psycopg2.connect(
                host=db_config.host,
                port=db_config.port,
                database=db_config.database,
                user=db_config.username,
                password=db_config.password
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            try:
                cursor.execute(migration_sql)
                cursor.close()
                conn.close()
            except Exception as e:
                cursor.close()
                conn.close()
                raise e
            
            # Record migration
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            async with self.engine.begin() as conn:
                await conn.execute(text(f"""
                    INSERT INTO {self.migrations_table} 
                    (migration_name, checksum, execution_time_ms)
                    VALUES (:name, :checksum, :time)
                """), {
                    "name": migration_name,
                    "checksum": checksum,
                    "time": execution_time
                })
            
            logger.info(f"Migration {migration_name} applied successfully in {execution_time}ms")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_name}: {e}")
            return False
    
    async def apply_seed(self, seed_file: Path) -> bool:
        """Apply a seed file"""
        seed_name = seed_file.name
        
        try:
            logger.info(f"Applying seed: {seed_name}")
            
            # Read seed file
            with open(seed_file, 'r', encoding='utf-8') as f:
                seed_sql = f.read()
            
            # Apply seed - use psycopg2 for complex SQL
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            conn = psycopg2.connect(
                host=db_config.host,
                port=db_config.port,
                database=db_config.database,
                user=db_config.username,
                password=db_config.password
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            try:
                cursor.execute(seed_sql)
                cursor.close()
                conn.close()
            except Exception as e:
                cursor.close()
                conn.close()
                raise e
            
            logger.info(f"Seed {seed_name} applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply seed {seed_name}: {e}")
            return False
    
    async def run_migrations(self, apply_seeds: bool = True) -> bool:
        """Run all pending migrations"""
        try:
            await self.create_migrations_table()
            
            # Get migration files and applied migrations
            migration_files = self.get_migration_files()
            applied_migrations = await self.get_applied_migrations()
            
            # Filter pending migrations
            pending_migrations = [
                f for f in migration_files
                if f.name not in applied_migrations
            ]
            
            if not pending_migrations:
                logger.info("No pending migrations found")
            else:
                logger.info(f"Found {len(pending_migrations)} pending migrations")
                
                # Apply pending migrations
                for migration_file in pending_migrations:
                    success = await self.apply_migration(migration_file)
                    if not success:
                        logger.error(f"Migration failed: {migration_file.name}")
                        return False
            
            # Apply seeds if requested
            if apply_seeds:
                seed_files = self.get_seed_files()
                for seed_file in seed_files:
                    success = await self.apply_seed(seed_file)
                    if not success:
                        logger.warning(f"Seed failed: {seed_file.name}")
            
            logger.info("All migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False
    
    async def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a specific migration (manual process)"""
        logger.warning(f"Rollback requested for: {migration_name}")
        logger.warning("Rollback is not automated. Please restore from backup.")
        return False
    
    async def get_migration_status(self) -> dict:
        """Get migration status"""
        try:
            await self.create_migrations_table()
            
            migration_files = self.get_migration_files()
            applied_migrations = await self.get_applied_migrations()
            
            status = {
                "total_migrations": len(migration_files),
                "applied_migrations": len(applied_migrations),
                "pending_migrations": len(migration_files) - len(applied_migrations),
                "migration_files": [f.name for f in migration_files],
                "applied_migrations_list": applied_migrations,
                "pending_migrations_list": [
                    f.name for f in migration_files
                    if f.name not in applied_migrations
                ]
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="People Counter Database Migration Manager")
    parser.add_argument("command", choices=["migrate", "status", "rollback"], 
                       help="Migration command to execute")
    parser.add_argument("--migration", help="Migration name for rollback")
    parser.add_argument("--no-seeds", action="store_true", 
                       help="Skip applying seed data")
    
    args = parser.parse_args()
    
    migration_manager = MigrationManager()
    
    try:
        await migration_manager.initialize()
        
        if args.command == "migrate":
            success = await migration_manager.run_migrations(apply_seeds=not args.no_seeds)
            sys.exit(0 if success else 1)
            
        elif args.command == "status":
            status = await migration_manager.get_migration_status()
            print("\nMigration Status:")
            print(f"Total migrations: {status.get('total_migrations', 0)}")
            print(f"Applied migrations: {status.get('applied_migrations', 0)}")
            print(f"Pending migrations: {status.get('pending_migrations', 0)}")
            
            if status.get('pending_migrations_list'):
                print("\nPending migrations:")
                for migration in status['pending_migrations_list']:
                    print(f"  - {migration}")
            
        elif args.command == "rollback":
            if not args.migration:
                print("Error: --migration required for rollback")
                sys.exit(1)
            success = await migration_manager.rollback_migration(args.migration)
            sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        sys.exit(1)
    
    finally:
        await migration_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
