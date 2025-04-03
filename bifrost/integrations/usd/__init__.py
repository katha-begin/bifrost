"""
OpenUSD integration for Bifrost.

This module provides integration with OpenUSD (Universal Scene Description),
allowing Bifrost to work with USD files and leverage USD's powerful
composition and referencing capabilities.
"""

import logging
import os
import sys
from pathlib import Path

from ...core.config import get_config

logger = logging.getLogger(__name__)

# Check if USD is available
USD_AVAILABLE = False
try:
    from pxr import Usd, UsdGeom, Sdf, Ar
    USD_AVAILABLE = True
except ImportError:
    logger.warning("OpenUSD modules could not be imported. USD functionality will be disabled.")
    logger.warning("Install USD with: pip install usd-core")

# Set up USD environment variables from config if available
def setup_usd_environment():
    """Set up USD environment variables based on configuration."""
    if not USD_AVAILABLE:
        return False
    
    # Get USD configuration
    usd_enabled = get_config("usd.enabled", True)
    if not usd_enabled:
        logger.info("USD integration is disabled in configuration.")
        return False
    
    # Set environment variables
    usd_install_dir = get_config("usd.environment.USD_INSTALL_DIR", "")
    if usd_install_dir:
        os.environ["USD_INSTALL_DIR"] = str(usd_install_dir)
        
    plugin_paths = get_config("usd.environment.PXR_PLUGINPATH_NAME", "")
    if plugin_paths:
        os.environ["PXR_PLUGINPATH_NAME"] = str(plugin_paths)
    
    logger.info("USD environment variables configured.")
    return True

# Initialize USD support if available
if USD_AVAILABLE:
    setup_usd_environment()
    logger.info("OpenUSD integration initialized.")
