#!/usr/bin/env python
# setup_dependencies.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02
#
# This script helps set up external dependencies required by Bifrost,
# particularly for OpenUSD and OpenAssetIO which may need additional
# configuration beyond pip installation.

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup_dependencies")

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))


def check_python_version():
    """Check if the Python version is compatible."""
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 9):
        logger.error("Python 3.9 or higher is required.")
        return False
    return True


def setup_usd():
    """Set up OpenUSD dependencies."""
    logger.info("Setting up OpenUSD dependencies...")
    
    system = platform.system()
    
    if system == "Linux":
        try:
            logger.info("Installing system dependencies for USD on Linux...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", 
                           "libgl1-mesa-dev", "libglu1-mesa-dev", 
                           "libxi-dev", "libxrandr-dev"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing USD system dependencies: {e}")
            logger.warning("You may need to install these packages manually.")
        except FileNotFoundError:
            logger.warning("Could not run apt-get. You may need to install the required packages manually.")
    
    elif system == "Windows":
        logger.info("No additional system packages required for USD on Windows.")
    
    elif system == "Darwin":  # macOS
        try:
            logger.info("Installing system dependencies for USD on macOS...")
            subprocess.run(["brew", "install", "boost", "python"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing USD dependencies with homebrew: {e}")
            logger.warning("You may need to install these packages manually.")
        except FileNotFoundError:
            logger.warning("Could not run brew. You may need to install Homebrew and required packages manually.")
    
    # Install usd-core via pip
    try:
        logger.info("Installing USD Python package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "usd-core>=23.11.0"], check=True)
        logger.info("USD Python package installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing USD Python package: {e}")
        return False
    
    # Verify USD installation
    try:
        logger.info("Verifying USD installation...")
        # Try to import USD modules
        import_cmd = "from pxr import Usd, UsdGeom, Sdf, Ar; print('USD import successful')"
        result = subprocess.run([sys.executable, "-c", import_cmd], 
                               capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            logger.info("USD verification successful")
        else:
            logger.error(f"USD verification failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error verifying USD installation: {e}")
        return False
    
    return True


def setup_openassetio():
    """Set up OpenAssetIO dependencies."""
    logger.info("Setting up OpenAssetIO dependencies...")
    
    # Install openassetio via pip
    try:
        logger.info("Installing OpenAssetIO Python package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openassetio>=1.0.0b1"], check=True)
        logger.info("OpenAssetIO Python package installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing OpenAssetIO Python package: {e}")
        return False
    
    # Verify OpenAssetIO installation
    try:
        logger.info("Verifying OpenAssetIO installation...")
        # Try to import OpenAssetIO modules
        import_cmd = "import openassetio; print('OpenAssetIO import successful')"
        result = subprocess.run([sys.executable, "-c", import_cmd], 
                               capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            logger.info("OpenAssetIO verification successful")
        else:
            logger.error(f"OpenAssetIO verification failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error verifying OpenAssetIO installation: {e}")
        return False
    
    return True


def update_environment():
    """Update environment variables if needed."""
    logger.info("Updating environment variables...")
    
    # Create a .env file with environment variables
    env_file = parent_dir / ".env"
    
    with open(env_file, "w") as f:
        f.write("# Environment variables for Bifrost\n")
        f.write("# Generated by setup_dependencies.py\n\n")
        
        # Add USD-related environment variables
        f.write("# USD environment variables\n")
        f.write("USD_INSTALL_DIR=\n")  # User should fill this in if needed
        
        # Add OpenAssetIO-related environment variables
        f.write("\n# OpenAssetIO environment variables\n")
        f.write("OPENASSETIO_PLUGIN_PATH=\n")  # User should fill this in if needed
    
    logger.info(f"Created environment file at {env_file}")
    logger.info("Please edit this file with your specific environment variables if needed.")
    
    return True


def main():
    """Main entry point for the script."""
    logger.info("Starting Bifrost dependencies setup...")
    
    if not check_python_version():
        return 1
    
    # Install pip packages from requirements.txt
    try:
        logger.info("Installing dependencies from requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", 
                       str(parent_dir / "requirements.txt")], check=True)
        logger.info("Basic dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing basic dependencies: {e}")
        return 1
    
    # Set up USD
    if not setup_usd():
        logger.warning("USD setup incomplete. Some features may not work correctly.")
    
    # Set up OpenAssetIO
    if not setup_openassetio():
        logger.warning("OpenAssetIO setup incomplete. Some features may not work correctly.")
    
    # Update environment
    update_environment()
    
    logger.info("Dependencies setup complete!")
    logger.info("You can now run Bifrost with USD and OpenAssetIO support.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
