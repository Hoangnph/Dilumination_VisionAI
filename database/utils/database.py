# Database Connection and Session Management
# Production-ready database connection handling

import asyncio
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config.settings import db_config

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
        
        try:
            # Create synchronous engine
            self.engine = create_engine(
                db_config.connection_string,
                poolclass=QueuePool,
                pool_size=db_config.pool_min,
                max_overflow=db_config.pool_max - db_config.pool_min,
                pool_timeout=db_config.pool_timeout,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
                echo=False,  # Set to True for SQL debugging
            )
            
            # Create async engine
            self.async_engine = create_async_engine(
                db_config.async_connection_string,
                pool_size=db_config.pool_min,
                max_overflow=db_config.pool_max - db_config.pool_min,
                pool_timeout=db_config.pool_timeout,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )
            
            # Create session factories
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self._initialized = True
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get synchronous database session"""
        if not self._initialized:
            self.initialize()
        
        return self.SessionLocal()
    
    def get_async_session(self) -> AsyncSession:
        """Get asynchronous database session"""
        if not self._initialized:
            self.initialize()
        
        return self.AsyncSessionLocal()
    
    @asynccontextmanager
    async def async_session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for database sessions"""
        session = self.get_async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def session_scope(self):
        """Synchronous context manager for database sessions"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.async_session_scope() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_connection_info(self) -> dict:
        """Get database connection information"""
        try:
            async with self.async_session_scope() as session:
                # Get database version
                version_result = await session.execute(text("SELECT version()"))
                version = version_result.scalar()
                
                # Get connection count
                conn_result = await session.execute(text(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                ))
                active_connections = conn_result.scalar()
                
                # Get database size
                size_result = await session.execute(text(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                ))
                db_size = size_result.scalar()
                
                return {
                    "version": version,
                    "active_connections": active_connections,
                    "database_size": db_size,
                    "pool_size": db_config.pool_max,
                    "host": db_config.host,
                    "port": db_config.port,
                    "database": db_config.database
                }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
        if self.async_engine:
            asyncio.create_task(self.async_engine.dispose())
        logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Dependency functions for FastAPI
def get_db() -> Session:
    """Dependency for getting database session"""
    with db_manager.session_scope() as session:
        yield session

async def get_async_db() -> AsyncSession:
    """Dependency for getting async database session"""
    async with db_manager.async_session_scope() as session:
        yield session

# Utility functions
async def init_database():
    """Initialize database tables"""
    from .models import Base
    
    try:
        async with db_manager.async_session_scope() as session:
            # Create all tables
            async with db_manager.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

async def drop_database():
    """Drop all database tables (use with caution!)"""
    from .models import Base
    
    try:
        async with db_manager.async_session_scope() as session:
            async with db_manager.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
            logger.warning("Database tables dropped successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to drop database: {e}")
        return False

# Export
__all__ = [
    'DatabaseManager',
    'db_manager',
    'get_db',
    'get_async_db',
    'init_database',
    'drop_database'
]
