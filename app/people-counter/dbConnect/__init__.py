"""
Database Connection Module for People Counter
Clean, production-ready database integration
"""

from .db_connection import PeopleCounterDB, create_db_connection, get_db_instance
from .logging_integration import PeopleCounterLogger

__all__ = [
    'PeopleCounterDB',
    'create_db_connection', 
    'get_db_instance',
    'PeopleCounterLogger'
]
