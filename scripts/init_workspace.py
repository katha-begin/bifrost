#!/usr/bin/env python
# init_workspace.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import from the package
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from bifrost.core.config import config
from bifrost.core.database import db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_directory(path, name):
    """Create a directory if it doesn't exist."""
    dir_path = Path(path)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"{name} directory created at: {dir_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating {name} directory: {e}")
        return False


def initialize_workspace():
    """Initialize the Bifrost workspace."""
    logger.info("Initializing Bifrost workspace...")
    
    # Determine root directory
    root_dir = parent_dir
    logger.info(f"Using root directory: {root_dir}")
    
    # Create data directory
    data_dir = root_dir / "data"
    if not create_directory(data_dir, "Data"):
        return False
    
    # Create assets directory
    assets_dir = data_dir / "assets"
    if not create_directory(assets_dir, "Assets"):
        return False
    
    # Create logs directory
    logs_dir = root_dir / "logs"
    if not create_directory(logs_dir, "Logs"):
        return False
    
    # Create temp directory
    temp_dir = root_dir / "temp"
    if not create_directory(temp_dir, "Temporary files"):
        return False
    
    # Set up configuration
    try:
        # Create default configuration
        default_config = {
            "database": {
                "type": "sqlite",
                "path": str(data_dir / "bifrost.db")
            },
            "storage": {
                "local": {
                    "root_path": str(assets_dir)
                }
            },
            "log": {
                "level": "INFO",
                "path": str(logs_dir / "bifrost.log")
            },
            "ui": {
                "theme": "dark",
                "language": "en"
            }
        }
        
        # Merge with existing config (if any)
        config.merge(default_config)
        
        # Save configuration
        config_dir = root_dir / "config"
        config_file = config_dir / "config.yaml"
        if not create_directory(config_dir, "Configuration"):
            return False
        
        config.save(config_file)
        logger.info(f"Configuration saved to: {config_file}")
    
    except Exception as e:
        logger.error(f"Error setting up configuration: {e}")
        return False
    
    # Initialize database
    try:
        # Database initialization happens automatically when importing db
        logger.info(f"Database initialized at: {db._db_path}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
    
    logger.info("Bifrost workspace initialized successfully!")
    return True


def main():
    """Script entry point."""
    try:
        if initialize_workspace():
            print("Bifrost workspace initialized successfully!")
            print(f"Root directory: {parent_dir}")
            return 0
        else:
            print("Failed to initialize Bifrost workspace.")
            return 1
    except Exception as e:
        logger.exception("Unexpected error during initialization")
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
