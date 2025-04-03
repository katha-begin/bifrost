#!/usr/bin/env python
# bifrost_host.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

# Import OpenAssetIO modules if available
ASSETIO_AVAILABLE = False
try:
    from openassetio import Context, HostInterface, TraitsData
    from openassetio.access import PolicyAccess
    from openassetio import constants, hostApi, log
    from openassetio.hostApi import Manager, ManagerFactory, ManagerInterface
    
    ASSETIO_AVAILABLE = True
except ImportError:
    logging.warning("OpenAssetIO modules could not be imported. AssetIO functionality will be disabled.")

from ...core.config import get_config
from .uri_mapper import AssetUriMapper

# Setup logger
logger = logging.getLogger(__name__)

class BifrostHostInterface:
    """
    Manages communication with the OpenAssetIO system.
    
    This class provides host-side communication with OpenAssetIO, allowing
    Bifrost to resolve assets via the OpenAssetIO interface. This is particularly
    useful when integrating with DCC tools.
    """
    
    def __init__(self):
        """Initialize the host interface."""
        self.manager = None
        self.initialized = False
        
        # Check if OpenAssetIO is available
        if not ASSETIO_AVAILABLE:
            logger.warning("BifrostHostInterface initialized but OpenAssetIO is not available.")
            return
            
        # Check if enabled in configuration
        self.enabled = get_config("assetio.enabled", True)
        if not self.enabled:
            logger.info("OpenAssetIO integration is disabled in configuration.")
            return
        
        # Configure Manager settings
        self.manager_id = get_config("assetio.manager", "org.bifrost.assetmanager")
        self.fallback_manager_id = get_config("assetio.fallback_manager", "org.openassetio.test.manager")
        self.host_name = get_config("assetio.host_name", "Bifrost Asset Manager")
        self.host_version = get_config("assetio.host_version", "0.1.0")
        
    def initialize(self):
        """
        Initialize the OpenAssetIO system.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if not ASSETIO_AVAILABLE or not self.enabled:
            return False
            
        if self.initialized:
            return True
            
        try:
            # Create a manager factory
            factory = ManagerFactory()
            
            # Get registered managers
            managers = factory.identifiers()
            logger.debug(f"Available OpenAssetIO managers: {managers}")
            
            # Find our manager or another preferred one
            manager_id = self.manager_id
            if manager_id not in managers:
                if self.fallback_manager_id in managers:
                    logger.warning(f"Primary manager {manager_id} not found, using fallback {self.fallback_manager_id}")
                    manager_id = self.fallback_manager_id
                elif managers:
                    logger.warning(f"Preferred managers not found, using first available: {managers[0]}")
                    manager_id = managers[0]
                else:
                    logger.error("No OpenAssetIO managers available")
                    return False
            
            # Create the manager
            self.manager = factory.createManager(manager_id)
            if not self.manager:
                logger.error(f"Failed to create OpenAssetIO manager: {manager_id}")
                return False
                
            # Initialize the manager
            host_session = self._create_host_session()
            if not self.manager.initialize({}, host_session):
                logger.error("Failed to initialize OpenAssetIO manager")
                return False
                
            self.initialized = True
            logger.info(f"OpenAssetIO initialized with manager: {manager_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing OpenAssetIO: {e}")
            return False
    
    def resolve_asset_path(self, asset_uri: str) -> Optional[Path]:
        """
        Resolve an asset URI to a file path.
        
        Args:
            asset_uri: OpenAssetIO URI string
            
        Returns:
            Path to the asset's file, or None if not found
        """
        if not self.initialized and not self.initialize():
            return None
            
        try:
            # Create context
            context = Context()
            
            # Create entity reference
            entity_reference = self.manager.createEntityReference(asset_uri)
            
            # Create trait set for locatable content
            trait_set = ["locatableContent"]
            
            # Resolve the reference
            results = self.manager.resolve([entity_reference], trait_set, context)
            
            if not results or not results[0]:
                logger.warning(f"Failed to resolve URI: {asset_uri}")
                return None
                
            # Extract the location from the result
            location = results[0].get("location")
            if not location:
                logger.warning(f"No location found for URI: {asset_uri}")
                return None
                
            return Path(location)
            
        except Exception as e:
            logger.error(f"Error resolving asset URI: {e}")
            return None
    
    def get_version(self, asset_uri: str) -> Optional[int]:
        """
        Get the version number for an asset URI.
        
        Args:
            asset_uri: OpenAssetIO URI string
            
        Returns:
            Version number or None if not found
        """
        if not self.initialized and not self.initialize():
            return None
            
        try:
            # Create context
            context = Context()
            
            # Create entity reference
            entity_reference = self.manager.createEntityReference(asset_uri)
            
            # Create trait set for versioned content
            trait_set = ["versionedContent"]
            
            # Resolve the reference
            results = self.manager.resolve([entity_reference], trait_set, context)
            
            if not results or not results[0]:
                logger.warning(f"Failed to resolve URI: {asset_uri}")
                return None
                
            # Extract the version from the result
            version = results[0].get("version")
            if not version:
                logger.warning(f"No version found for URI: {asset_uri}")
                return None
                
            return int(version)
            
        except Exception as e:
            logger.error(f"Error getting version for asset URI: {e}")
            return None
    
    def get_entity_info(self, asset_uri: str) -> Optional[Dict]:
        """
        Get complete information for an entity.
        
        Args:
            asset_uri: OpenAssetIO URI string
            
        Returns:
            Dictionary of entity information or None if not found
        """
        if not self.initialized and not self.initialize():
            return None
            
        try:
            # Create context
            context = Context()
            
            # Create entity reference
            entity_reference = self.manager.createEntityReference(asset_uri)
            
            # Create trait set for all available traits
            trait_set = [
                "locatableContent",
                "versionedContent",
                "defaultName",
                "defaultThumbnail",
                "managementPolicy"
            ]
            
            # Resolve the reference
            results = self.manager.resolve([entity_reference], trait_set, context)
            
            if not results or not results[0]:
                logger.warning(f"Failed to resolve URI: {asset_uri}")
                return None
                
            return results[0]
            
        except Exception as e:
            logger.error(f"Error getting info for asset URI: {e}")
            return None
    
    def get_relationships(self, asset_uri: str) -> Optional[List]:
        """
        Get relationships for an entity.
        
        Args:
            asset_uri: OpenAssetIO URI string
            
        Returns:
            List of relationships or None if not found
        """
        if not self.initialized and not self.initialize():
            return None
            
        try:
            # Create context
            context = Context()
            
            # Create entity reference
            entity_reference = self.manager.createEntityReference(asset_uri)
            
            # Define relationship traits
            relationship_traits = ["dependencies", "references"]
            
            # Get entity with relationships
            entities, relationships = self.manager.getWithRelationships(
                [entity_reference], relationship_traits, context)
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error getting relationships for asset URI: {e}")
            return None
    
    def create_entity_reference(self, asset_id: str) -> Optional[str]:
        """
        Create an entity reference from an asset ID.
        
        Args:
            asset_id: Bifrost asset ID
            
        Returns:
            OpenAssetIO URI string
        """
        uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        return f"{uri_scheme}:///assets/{asset_id}"
    
    def is_valid_entity_reference(self, uri: str) -> bool:
        """
        Check if a string is a valid entity reference.
        
        Args:
            uri: String to check
            
        Returns:
            True if valid, False otherwise
        """
        return AssetUriMapper.is_valid_uri(uri)
    
    def _create_host_session(self):
        """
        Create a host session for the manager.
        
        Returns:
            Host session dictionary
        """
        return {
            "hostIdentifier": "org.bifrost.host",
            "hostName": self.host_name,
            "hostVersion": self.host_version
        }

# Create a singleton instance
bifrost_host = BifrostHostInterface()
