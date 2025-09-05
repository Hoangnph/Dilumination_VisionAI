#!/usr/bin/env python3
"""
People Counter Database API Server
Production-ready FastAPI server for database operations
"""

import asyncio
import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add database directory to path
sys.path.append(str(Path(__file__).parent))

from api.main import app
from config.settings import app_config

# Configure logging
logging.basicConfig(
    level=getattr(logging, app_config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database/logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the API server"""
    logger.info("Starting People Counter Database API Server")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=app_config.log_level.lower(),
        access_log=True,
        reload=app_config.debug
    )

if __name__ == "__main__":
    main()
