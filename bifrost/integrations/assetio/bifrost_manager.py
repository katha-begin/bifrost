#!/usr/bin/env python
# bifrost_manager.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Import OpenAssetIO modules if available
ASSETIO_AVAILABLE = False
try:
    from openassetio import Context, HostInterface, TraitsData
    from openassetio.access import PolicyAccess
    from openassetio import constants, hostApi, log, managerApi
    from openassetio.hostApi import Manager, ManagerFactory, ManagerInterface
    from openassetio.managerApi import EntityReference, HostSession
    from openassetio.managerApi.hosting import ManagerImplementationFactory
    
    ASSETIO_AVAILABLE = True
except ImportError:
    logging.warning("OpenAssetIO modules could not be imported. AssetIO functionality will be disabled.")

from ...core.config import get_config
from ...services.asset_service import asset_service

# Setup logger
logger = logging.getLogger(__name__)

class BifrostManagerInterface:
    """
    Implementation of the OpenAssetIO Manager interface for Bifrost.
    
    This class provides the bridge between OpenAssetIO and Bifrost,
    allowing other applications to interact with Bifrost assets via
    the OpenAssetIO standard interface.
    """
    
    def __init__(self):
        """Initialize the manager interface."""
        if not ASSETIO_AVAILABLE:
            logger.warning("BifrostManagerInterface initialized but OpenAssetIO is not available.")
            return
            
        self.enabled = get_config("assetio.enabled", True)
        if not self.enabled:
            logger.info("OpenAssetIO integration is disabled in configuration.")
            return
            
        self.uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        self._host_session = None
        
        logger.info("BifrostManagerInterface initialized.")
    
    def identifier(self):
        """Return the unique identifier for this manager."""
        return "org.bifrost.assetmanager"
        
    def displayName(self):
        """Return the human-readable name for this manager."""
        return "Bifrost Asset Manager"
        
    def info(self):
        """Return information about this manager."""
        return {
            "version": "0.1.0",
            "hostVersion": "1.0.0",
            "vendor": "Bifrost Team",
            "website": "https://github.com/your-organization/bifrost"
        }
        
    def initialize(self, managerSettings, hostSession):
        """
        Initialize the manager.
        
        Args:
            managerSettings: Settings for the manager
            hostSession: Information about the host application
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self._host_session = hostSession
        return True
        
    def uninitialize(self):
        """Uninitialize the manager."""
        self._host_session = None
        return True
        
    def capabilities(self):
        """Return the capabilities of this manager."""
        return {
            "entityReferenceIdentification": True,
            "entityReferencesPublishing": True,
            "entityReferencesEmbeddedVersions": True,
            "fileLocations": True,
            "resolutionTracking": True
        }
        
    def entityExists(self, entityRefs, context, hostSession):
        """
        Check if entities exist in the manager.
        
        Args:
            entityRefs: List of entity references to check
            context: Context for the operation
            hostSession: Information about the host application
            
        Returns:
            List of boolean values indicating if each entity exists
        """
        results = []
        
        for ref in entityRefs:
            # Extract asset ID from the entity reference
            asset_id = self._extract_asset_id(ref)
            if not asset_id:
                results.append(False)
                continue
                
            # Check if asset exists
            asset = asset_service.get_asset(asset_id)
            results.append(asset is not None)
            
        return results
        
    def resolve(self, entityRefs, traitSet, context, hostSession):
        """
        Resolve entities to their data.
        
        Args:
            entityRefs: List of entity references to resolve
            traitSet: Set of traits to resolve
            context: Context for the operation
            hostSession: Information about the host application
            
        Returns:
            List of resolved data (dictionaries) for each entity
        """
        results = []
        
        for ref in entityRefs:
            # Extract asset ID from the entity reference
            asset_id = self._extract_asset_id(ref)
            if not asset_id:
                results.append({})
                continue
                
            # Get asset
            asset = asset_service.get_asset(asset_id)
            if not asset or not asset.latest_version:
                results.append({})
                continue
                
            # Map traits to asset data
            result = {}
            
            # Handle different trait sets
            if "locatableContent" in traitSet:
                # Return path to the asset's content
                result["location"] = str(asset.latest_version.file_path)
                
            if "versionedContent" in traitSet:
                # Return version information
                result["version"] = str(asset.latest_version.version_number)
                result["versionInfo"] = {
                    "created": str(asset.latest_version.created_at),
                    "createdBy": asset.latest_version.created_by,
                    "comment": asset.latest_version.comment
                }
                
            if "defaultName" in traitSet:
                # Return the default name for display
                result["name"] = asset.name
                
            if "defaultThumbnail" in traitSet:
                # Return thumbnail path if available
                if asset.thumbnail_path:
                    result["thumbnail"] = str(asset.thumbnail_path)
                    
            if "managementPolicy" in traitSet:
                # Define what users are allowed to do with this asset
                result["managementPolicy"] = {
                    "canUpdate": True,
                    "canDelete": True,
                    "canModifyRelationships": True
                }
                
            results.append(result)
            
        return results
    
    def getWithRelationships(self, entityRefs, relationshipTraits, context, hostSession):
        """
        Get entities with their relationships.
        
        Args:
            entityRefs: List of entity references to get
            relationshipTraits: Traits for relationships to include
            context: Context for the operation
            hostSession: Information about the host application
            
        Returns:
            Tuple with (entities, relationships)
        """
        entities = []
        relationships = []
        
        for ref in entityRefs:
            # Extract asset ID from the entity reference
            asset_id = self._extract_asset_id(ref)
            if not asset_id:
                continue
                
            # Get asset
            asset = asset_service.get_asset(asset_id)
            if not asset:
                continue
                
            # Add entity
            entity = {
                "reference": ref,
                "traits": {
                    "defaultName": {
                        "name": asset.name
                    },
                    "defaultDescription": {
                        "description": asset.description or ""
                    }
                }
            }
            entities.append(entity)
            
            # Add relationships
            if "dependencies" in relationshipTraits:
                for dep in asset.dependencies:
                    dep_entity_ref = self._create_entity_reference(dep.dependent_asset_id)
                    relationship = {
                        "fromEntity": ref,
                        "toEntity": dep_entity_ref,
                        "traits": {
                            "dependency": {
                                "type": dep.dependency_type,
                                "optional": dep.optional
                            }
                        }
                    }
                    relationships.append(relationship)
        
        return (entities, relationships)
    
    def register(self, entities, managementPolicy, context, hostSession):
        """
        Register new entities with the manager.
        
        Args:
            entities: List of entities to register
            managementPolicy: Management policy for the entities
            context: Context for the operation
            hostSession: Information about the host application
            
        Returns:
            List of registered entity references
        """
        # This is a simplified implementation - a real implementation would
        # create assets based on the provided entity data
        return []
    
    def _extract_asset_id(self, entity_ref):
        """
        Extract asset ID from an entity reference.
        
        Args:
            entity_ref: OpenAssetIO entity reference
            
        Returns:
            Asset ID or None if the reference is not valid
        """
        # Entity references look like: bifrost:///assets/{asset_id}
        uri = entity_ref.toString()
        if not uri.startswith(f"{self.uri_scheme}:///assets/"):
            return None
            
        return uri.split("/")[-1]
    
    def _create_entity_reference(self, asset_id):
        """
        Create an entity reference from an asset ID.
        
        Args:
            asset_id: Bifrost asset ID
            
        Returns:
            OpenAssetIO entity reference
        """
        uri = f"{self.uri_scheme}:///assets/{asset_id}"
        return EntityReference(uri)
