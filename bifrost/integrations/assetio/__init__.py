"""
OpenAssetIO integration for Bifrost.

This module provides integration with OpenAssetIO, allowing Bifrost to interact
with various asset management systems and digital content creation tools
through a standardized interface.
"""

import logging
import os
import sys
from pathlib import Path

from ...core.config import get_config

logger = logging.getLogger(__name__)

# Check if OpenAssetIO is available
ASSETIO_AVAILABLE = False
try:
    import openassetio
    ASSETIO_AVAILABLE = True
except ImportError:
    logger.warning("OpenAssetIO modules could not be imported. AssetIO functionality will be disabled.")
    logger.warning("Install OpenAssetIO with: pip install openassetio")

# Set up OpenAssetIO environment variables from config if available
def setup_assetio_environment():
    """Set up OpenAssetIO environment variables based on configuration."""
    if not ASSETIO_AVAILABLE:
        return False
    
    # Get OpenAssetIO configuration
    assetio_enabled = get_config("assetio.enabled", True)
    if not assetio_enabled:
        logger.info("OpenAssetIO integration is disabled in configuration.")
        return False
    
    # Set environment variables
    plugin_path = get_config("assetio.environment.OPENASSETIO_PLUGIN_PATH", "")
    if plugin_path:
        os.environ["OPENASSETIO_PLUGIN_PATH"] = str(plugin_path)
    
    logger.info("OpenAssetIO environment variables configured.")
    return True

# Initialize OpenAssetIO support if available
if ASSETIO_AVAILABLE:
    setup_assetio_environment()
    logger.info("OpenAssetIO integration initialized.")
