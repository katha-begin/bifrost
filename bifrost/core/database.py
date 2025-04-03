#!/usr/bin/env python
# database.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .config import get_config

# Setup logger
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database management for the Bifrost system.
    
    This provides a simple interface for database operations with support
    for SQLite initially, with a path for scaling to PostgreSQL later.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """Initialize the database connection."""
        # Skip if already initialized
        if getattr(self, '_initialized', False):
            return
            
        # Determine database path
        self._db_path = None
        if db_path:
            self._db_path = Path(db_path)
        else:
            config_db_path = get_config('database.path')
            if config_db_path:
                # Get path from config
                self._db_path = Path(config_db_path)
            else:
                # Use default path
                self._db_path = Path(os.getcwd()) / 'data' / 'bifrost.db'
        
        # Ensure directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        self._initialized = True
        
    def _initialize_database(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        logger.info(f"Initializing database at {self._db_path}")
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Assets table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT NOT NULL,
                    modified_at TIMESTAMP NOT NULL,
                    modified_by TEXT,
                    description TEXT,
                    status TEXT NOT NULL,
                    thumbnail_path TEXT,
                    preview_path TEXT,
                    metadata TEXT
                )
                ''')
                
                # Asset versions
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset_versions (
                    id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    comment TEXT,
                    file_path TEXT,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                )
                ''')
                
                # Asset tags
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset_tags (
                    id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    color TEXT,
                    description TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                )
                ''')
                
                # Asset dependencies
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset_dependencies (
                    id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    dependent_asset_id TEXT NOT NULL,
                    dependency_type TEXT NOT NULL,
                    optional BOOLEAN NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE,
                    FOREIGN KEY (dependent_asset_id) REFERENCES assets (id) ON DELETE CASCADE
                )
                ''')
                
                # Shots table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shots (
                    id TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    sequence_id TEXT NOT NULL,
                    name TEXT,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    modified_at TIMESTAMP NOT NULL,
                    modified_by TEXT,
                    frame_start INTEGER NOT NULL,
                    frame_end INTEGER NOT NULL,
                    handle_pre INTEGER NOT NULL,
                    handle_post INTEGER NOT NULL,
                    thumbnail_path TEXT,
                    metadata TEXT
                )
                ''')
                
                # Shot versions
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shot_versions (
                    id TEXT PRIMARY KEY,
                    shot_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    comment TEXT,
                    status TEXT NOT NULL,
                    filepath TEXT,
                    frame_start INTEGER NOT NULL,
                    frame_end INTEGER NOT NULL,
                    preview_path TEXT,
                    metadata TEXT,
                    FOREIGN KEY (shot_id) REFERENCES shots (id) ON DELETE CASCADE
                )
                ''')
                
                # Shot-Asset relationships
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shot_assets (
                    shot_id TEXT NOT NULL,
                    asset_id TEXT NOT NULL,
                    PRIMARY KEY (shot_id, asset_id),
                    FOREIGN KEY (shot_id) REFERENCES shots (id) ON DELETE CASCADE,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                )
                ''')
                
                # Shot tasks
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shot_tasks (
                    id TEXT PRIMARY KEY,
                    shot_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    department TEXT NOT NULL,
                    assigned_to TEXT,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    due_date TIMESTAMP,
                    completed_at TIMESTAMP,
                    estimated_hours REAL,
                    actual_hours REAL,
                    metadata TEXT,
                    FOREIGN KEY (shot_id) REFERENCES shots (id) ON DELETE CASCADE
                )
                ''')
                
                # Shot notes
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shot_notes (
                    id TEXT PRIMARY KEY,
                    shot_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    department TEXT NOT NULL,
                    resolved BOOLEAN NOT NULL,
                    resolved_at TIMESTAMP,
                    resolved_by TEXT,
                    attachments TEXT,
                    FOREIGN KEY (shot_id) REFERENCES shots (id) ON DELETE CASCADE
                )
                ''')
                
                # Users table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    department TEXT,
                    role TEXT,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    is_active BOOLEAN NOT NULL,
                    metadata TEXT
                )
                ''')
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with context management."""
        connection = None
        try:
            connection = sqlite3.connect(
                self._db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            connection.row_factory = sqlite3.Row
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SQL query and return the results as a list of dictionaries."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                    results = [dict(row) for row in cursor.fetchall()]
                    return results
                else:
                    conn.commit()
                    return []
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute a SQL query with multiple parameter sets."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
        except Exception as e:
            logger.error(f"Batch query execution error: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def get_by_id(self, table: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Get a record by its ID."""
        query = f"SELECT * FROM {table} WHERE id = ?"
        results = self.execute(query, (id_value,))
        return results[0] if results else None
    
    def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Insert a record into a table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        self.execute(query, tuple(data.values()))
        return data.get('id')
    
    def update(self, table: str, id_value: str, data: Dict[str, Any]) -> bool:
        """Update a record by its ID."""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        
        params = list(data.values()) + [id_value]
        self.execute(query, tuple(params))
        return True
    
    def delete(self, table: str, id_value: str) -> bool:
        """Delete a record by its ID."""
        query = f"DELETE FROM {table} WHERE id = ?"
        self.execute(query, (id_value,))
        return True
    
    def serialize_json(self, obj: Any) -> str:
        """Serialize an object to JSON for storage."""
        return json.dumps(obj)
    
    def deserialize_json(self, json_str: str) -> Any:
        """Deserialize JSON from storage."""
        if not json_str:
            return None
        return json.loads(json_str)


# Create a singleton instance
db = DatabaseManager()
