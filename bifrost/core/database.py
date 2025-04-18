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

import psycopg2
from psycopg2.extras import RealDictCursor

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
            
        # Get database configuration
        self.db_type = get_config('database.type', 'sqlite')
        
        if self.db_type == 'sqlite':
            db_path = get_config('database.path')
            self._db_path = Path(db_path) if db_path else Path(os.getcwd()) / 'data' / 'bifrost.db'
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # PostgreSQL configuration
            self.db_host = os.getenv('DATABASE_HOST') or get_config('database.host', 'localhost')
            self.db_port = os.getenv('DATABASE_PORT') or get_config('database.port', 5432)
            self.db_name = os.getenv('DATABASE_NAME') or get_config('database.name', 'bifrost')
            self.db_user = os.getenv('DATABASE_USER') or get_config('database.user', 'bifrost_user')
            self.db_password = os.getenv('DATABASE_PASSWORD') or get_config('database.password', '')
        
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
                    is_assembly BOOLEAN NOT NULL DEFAULT FALSE,
                    thumbnail_path TEXT,
                    preview_path TEXT,
                    metadata TEXT
                )
                ''')
                
                # Asset types
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset_types (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    supports_assembly BOOLEAN NOT NULL DEFAULT FALSE,
                    metadata TEXT
                )
                ''')
                
                # Assembly components
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS assembly_components (
                    id TEXT PRIMARY KEY,
                    assembly_id TEXT NOT NULL,
                    component_asset_id TEXT NOT NULL,
                    transform TEXT,
                    override_parameters TEXT,
                    FOREIGN KEY (assembly_id) REFERENCES assets (id) ON DELETE CASCADE,
                    FOREIGN KEY (component_asset_id) REFERENCES assets (id) ON DELETE CASCADE
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
                
                # Series table (top-level show organization)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS series (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    description TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    modified_at TIMESTAMP NOT NULL,
                    modified_by TEXT
                )
                ''')
                
                # Episodes table 
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    series_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    description TEXT,
                    frame_start INTEGER NOT NULL,
                    frame_end INTEGER NOT NULL,
                    global_frame_start INTEGER,
                    global_frame_end INTEGER,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    modified_at TIMESTAMP NOT NULL,
                    modified_by TEXT,
                    metadata TEXT,
                    FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
                )
                ''')
                
                # Sequences table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS sequences (
                    id TEXT PRIMARY KEY,
                    episode_id TEXT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    description TEXT,
                    frame_start INTEGER NOT NULL,
                    frame_end INTEGER NOT NULL,
                    global_frame_start INTEGER,
                    global_frame_end INTEGER,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    modified_at TIMESTAMP NOT NULL,
                    modified_by TEXT,
                    metadata TEXT,
                    FOREIGN KEY (episode_id) REFERENCES episodes (id) ON DELETE SET NULL
                )
                ''')
                
                # Shots table with enhanced frame tracking
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
                    global_frame_start INTEGER,
                    global_frame_end INTEGER,
                    handle_pre INTEGER NOT NULL DEFAULT 0,
                    handle_post INTEGER NOT NULL DEFAULT 0,
                    thumbnail_path TEXT,
                    metadata TEXT,
                    FOREIGN KEY (sequence_id) REFERENCES sequences (id) ON DELETE CASCADE
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
                
                # Projects table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    project_code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    updated_at TIMESTAMP,
                    updated_by TEXT,
                    fps REAL NOT NULL DEFAULT 24.0,
                    resolution TEXT NOT NULL DEFAULT '1920x1080',
                    colorspace TEXT NOT NULL DEFAULT 'ACES',
                    metadata TEXT
                )
                ''')
                
                # Pipeline steps (departments)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_steps (
                    id TEXT PRIMARY KEY,
                    department_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    step_order INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    updated_at TIMESTAMP,
                    updated_by TEXT,
                    metadata TEXT
                )
                ''')
                
                # Pipeline step requirements
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_step_requirements (
                    id TEXT PRIMARY KEY,
                    pipeline_step_id TEXT NOT NULL,
                    required_department TEXT NOT NULL,
                    required_status TEXT NOT NULL DEFAULT 'approved',
                    FOREIGN KEY (pipeline_step_id) REFERENCES pipeline_steps (id) ON DELETE CASCADE
                )
                ''')
                
                # Pipeline step outputs
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_step_outputs (
                    id TEXT PRIMARY KEY,
                    pipeline_step_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    formats TEXT NOT NULL,
                    location TEXT NOT NULL,
                    FOREIGN KEY (pipeline_step_id) REFERENCES pipeline_steps (id) ON DELETE CASCADE
                )
                ''')
                
                # Pipeline workflows
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    updated_at TIMESTAMP,
                    updated_by TEXT,
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    metadata TEXT
                )
                ''')
                
                # Asset workflows
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset_workflows (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    sequence TEXT NOT NULL,
                    FOREIGN KEY (workflow_id) REFERENCES pipeline_workflows (id) ON DELETE CASCADE
                )
                ''')
                
                # Shot workflows
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS shot_workflows (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    shot_type TEXT NOT NULL,
                    sequence TEXT NOT NULL,
                    FOREIGN KEY (workflow_id) REFERENCES pipeline_workflows (id) ON DELETE CASCADE
                )
                ''')
                
                # Project pipeline configurations
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_pipeline_configs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    workflow_type TEXT NOT NULL DEFAULT 'default',
                    config TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
                ''')
                
                # Project custom department dependencies
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_department_overrides (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    department_id TEXT NOT NULL,
                    requires TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
                ''')
                
                # Project task template overrides
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_task_templates (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    department_id TEXT NOT NULL,
                    name_template TEXT,
                    description_template TEXT,
                    estimated_hours REAL,
                    priority TEXT,
                    status TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
                ''')
                
                # Tasks table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    assignee_id TEXT,
                    asset_id TEXT,
                    shot_id TEXT,
                    department_id TEXT,
                    due_date TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT NOT NULL,
                    estimated_hours REAL,
                    tags TEXT,
                    metadata TEXT,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE SET NULL,
                    FOREIGN KEY (shot_id) REFERENCES shots (id) ON DELETE SET NULL
                )
                ''')
                
                # Task dependencies
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    depends_on_task_id TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks (id) ON DELETE CASCADE
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
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    department TEXT,
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    preferences TEXT,
                    metadata TEXT
                )
                ''')
                
                # Roles table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    permissions TEXT NOT NULL
                )
                ''')
                
                # User roles junction table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_roles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role_id TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
                )
                ''')
                
                # Teams table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
                ''')
                
                # Team members junction table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_members (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT,
                    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
                ''')
                
                # Reviews table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    completed_at TIMESTAMP,
                    status TEXT NOT NULL,
                    metadata TEXT
                )
                ''')
                
                # Review items
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_items (
                    id TEXT PRIMARY KEY,
                    review_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    version_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    preview_path TEXT,
                    metadata TEXT,
                    FOREIGN KEY (review_id) REFERENCES reviews (id) ON DELETE CASCADE
                )
                ''')
                
                # Review notes
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_notes (
                    id TEXT PRIMARY KEY,
                    review_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    author TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    frame INTEGER,
                    timecode TEXT,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    attachments TEXT,
                    FOREIGN KEY (review_id) REFERENCES reviews (id) ON DELETE CASCADE
                )
                ''')
                
                # Activity log
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    changes TEXT,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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
            if self.db_type == 'sqlite':
                connection = sqlite3.connect(
                    self._db_path,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                )
                connection.row_factory = sqlite3.Row
            else:
                connection = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    cursor_factory=RealDictCursor
                )
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
                
                # Convert SQLite paramstyle (?) to PostgreSQL (%s) if needed
                if self.db_type != 'sqlite':
                    query = query.replace('?', '%s')
                
                cursor.execute(query, params)
                
                if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                    if self.db_type == 'sqlite':
                        results = [dict(row) for row in cursor.fetchall()]
                    else:
                        results = cursor.fetchall()
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
                # Convert SQLite paramstyle (?) to PostgreSQL (%s) if needed
                if self.db_type != 'sqlite':
                    query = query.replace('?', '%s')
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
