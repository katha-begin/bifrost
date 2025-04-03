#!/usr/bin/env python
# config.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for the Bifrost system.
    
    This class is responsible for loading, validating, and providing
    access to application configuration settings from YAML files.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """Initialize the configuration system."""
        # Skip if already initialized
        if getattr(self, '_initialized', False):
            return
            
        self._config_data = {}
        self._config_file = None
        
        # Default locations to look for config files
        self._config_locations = [
            # Current working directory
            Path(os.getcwd()) / 'bifrost_config.yaml',
            # User's home directory
            Path.home() / '.bifrost' / 'config.yaml',
            # Application directory
            Path(__file__).parent.parent.parent / 'config' / 'default_config.yaml',
        ]
        
        # Load configuration
        if config_file:
            self._config_file = Path(config_file)
            self._load_config(self._config_file)
        else:
            self._discover_and_load_config()
            
        self._initialized = True
    
    def _discover_and_load_config(self) -> None:
        """Find and load configuration from default locations."""
        # Check environment variable first
        env_config = os.environ.get('BIFROST_CONFIG')
        if env_config:
            config_path = Path(env_config)
            if config_path.exists():
                logger.info(f"Loading configuration from environment variable: {config_path}")
                self._config_file = config_path
                self._load_config(config_path)
                return
                
        # Try each location in order
        for location in self._config_locations:
            if location.exists():
                logger.info(f"Loading configuration from: {location}")
                self._config_file = location
                self._load_config(location)
                return
                
        # No config found, use empty config
        logger.warning("No configuration file found. Using default empty configuration.")
        self._config_data = {}
    
    def _load_config(self, config_path: Path) -> None:
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
                self._config_data = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded successfully from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config_data = {}
    
    def save(self, config_path: Optional[Path] = None) -> bool:
        """Save the current configuration to a file."""
        save_path = config_path or self._config_file
        
        if not save_path:
            logger.error("No path specified for saving configuration")
            return False
            
        try:
            # Create parent directories if they don't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.safe_dump(self._config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Supports nested keys using dot notation (e.g., 'database.host').
        """
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Supports nested keys using dot notation (e.g., 'database.host').
        """
        keys = key.split('.')
        data = self._config_data
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
            
        # Set the value
        data[keys[-1]] = value
    
    def get_all(self) -> Dict:
        """Get a copy of the entire configuration."""
        return self._config_data.copy()
    
    def merge(self, config_data: Dict) -> None:
        """Merge a dictionary of configuration values with the current config."""
        self._deep_merge(self._config_data, config_data)
    
    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """Recursively merge source dictionary into target dictionary."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def reset(self) -> None:
        """Reset the configuration to empty."""
        self._config_data = {}
        
    @property
    def config_file(self) -> Optional[Path]:
        """Get the path to the currently loaded configuration file."""
        return self._config_file


# Create a singleton instance
config = Config()

# Convenience function to get config values
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value by key."""
    return config.get(key, default)
