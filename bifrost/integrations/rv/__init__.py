"""
OpenRV integration for Bifrost.

This module provides integration with OpenRV for media playback and review.
"""

import logging
import os
from typing import Dict, List, Optional

from ...core.config import get_config
from .rv_service import RVService

__all__ = ['RVService']

logger = logging.getLogger(__name__)

# Check if RV is available
RV_AVAILABLE = False
rv_binary = get_config("review.rv_binary_path", "rv")
try:
    import subprocess
    result = subprocess.run([rv_binary, "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        RV_AVAILABLE = True
        logger.info(f"OpenRV detected: {result.stdout.strip()}")
    else:
        logger.warning(f"OpenRV command '{rv_binary}' failed. Review functionality will be limited.")
except Exception as e:
    logger.warning(f"Failed to check for OpenRV: {e}. Review functionality will be limited.")

# Configure RV environment if available
if RV_AVAILABLE:
    # Get RV plugin directory from config
    rv_plugin_dir = get_config("review.rv_plugin_dir", None)
    if rv_plugin_dir:
        os.environ["RV_PLUGIN_PATH"] = str(rv_plugin_dir)
    
    # Get RV package directory from config
    rv_package_dir = get_config("review.rv_package_dir", None)
    if rv_package_dir:
        os.environ["RV_PACKAGE_PATH"] = str(rv_package_dir)
        
    logger.info("OpenRV environment configured")
