#!/usr/bin/env python
# traits.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-03

"""
Extended OpenAssetIO trait support for Bifrost.

This module provides utilities for working with OpenAssetIO traits in Bifrost,
including trait conversion, validation, and discovery.
"""

import logging
from typing import Dict, List, Optional, Set, Any, Tuple, Union

# Import OpenAssetIO modules if available
ASSETIO_AVAILABLE = False
try:
    from openassetio import Context, TraitsData
    from openassetio.trait import TraitBase, TraitsDef
    ASSETIO_AVAILABLE = True
except ImportError:
    logging.warning("OpenAssetIO modules could not be imported. AssetIO functionality will be disabled.")

from ...core.config import get_config

# Setup logger
logger = logging.getLogger(__name__)


class BifrostTraitHandler:
    """
    Manages OpenAssetIO traits for Bifrost assets.
    
    This class provides utilities for converting between Bifrost asset attributes
    and OpenAssetIO traits, as well as discovering and validating traits.
    """
    
    # Define standard trait sets used by Bifrost
    STANDARD_TRAIT_SETS = {
        "basic": [
            "locatableContent",
            "defaultName"
        ],
        "versioned": [
            "locatableContent",
            "defaultName",
            "versionedContent"
        ],
        "media": [
            "locatableContent",
            "defaultName",
            "versionedContent",
            "mediaSource",
            "thumbnailable"
        ],
        "publish": [
            "locatableContent",
            "defaultName",
            "versionedContent",
            "publishableContent",
            "managementPolicy"
        ],
        "full": [
            "locatableContent",
            "defaultName",
            "versionedContent",
            "mediaSource",
            "thumbnailable",
            "previewable",
            "publishableContent",
            "managementPolicy",
            "relationshipManagement",
            "metadataQuerying",
            "statusTracking"
        ]
    }
    
    def __init__(self):
        """Initialize the trait handler."""
        self.enabled = ASSETIO_AVAILABLE and get_config("assetio.enabled", True)
        
        # A mapping from Bifrost asset attributes to trait properties
        self.asset_to_trait_map = {
            # Basic traits
            "name": ("defaultName", "name"),
            "description": ("defaultDescription", "description"),
            "path": ("locatableContent", "location"),
            
            # Versioned content
            "version_number": ("versionedContent", "version"),
            "created_at": ("versionedContent", "versionInfo.created"),
            "created_by": ("versionedContent", "versionInfo.createdBy"),
            "comment": ("versionedContent", "versionInfo.comment"),
            
            # Media traits
            "media_type": ("mediaSource", "mediaType"),
            "duration": ("mediaSource", "duration"),
            "frame_rate": ("mediaSource", "frameRate"),
            "width": ("mediaSource", "width"),
            "height": ("mediaSource", "height"),
            
            # Thumbnail traits
            "thumbnail_path": ("thumbnailable", "thumbnail"),
            "thumbnail_size": ("thumbnailable", "thumbnailSize"),
            
            # Preview traits
            "preview_path": ("previewable", "preview"),
            "preview_type": ("previewable", "previewType"),
            
            # Management traits
            "status": ("statusTracking", "status"),
            "tags": ("metadataQuerying", "tags"),
            "publish_status": ("publishableContent", "publishStatus"),
            
            # Policy traits
            "can_update": ("managementPolicy", "managementPolicy.canUpdate"),
            "can_delete": ("managementPolicy", "managementPolicy.canDelete"),
        }
        
        # A mapping from trait properties to Bifrost asset attributes (reverse of above)
        self.trait_to_asset_map = self._build_reverse_map()
        
        # Custom trait handlers for complex conversions
        self.custom_trait_handlers = {
            "relationshipManagement": self._handle_relationship_trait,
        }
        
    def _build_reverse_map(self) -> Dict[Tuple[str, str], str]:
        """
        Build a reverse mapping from trait properties to asset attributes.
        
        Returns:
            A dictionary mapping (trait_name, property_path) to asset_attribute
        """
        reverse_map = {}
        
        for asset_attr, (trait_name, prop_path) in self.asset_to_trait_map.items():
            reverse_map[(trait_name, prop_path)] = asset_attr
            
        return reverse_map
    
    def discover_traits(self, asset: Any) -> Set[str]:
        """
        Discover the OpenAssetIO traits supported by a Bifrost asset.
        
        Args:
            asset: A Bifrost asset object
            
        Returns:
            A set of trait names supported by the asset
        """
        if not self.enabled:
            return set()
            
        traits = set()
        
        # Group asset attributes by trait
        trait_coverage = {}
        
        for asset_attr, (trait_name, _) in self.asset_to_trait_map.items():
            if not hasattr(asset, asset_attr):
                continue
                
            value = getattr(asset, asset_attr)
            if value is not None:
                trait_coverage.setdefault(trait_name, []).append(asset_attr)
                
        # Add traits that have at least one property covered
        for trait_name, covered_attrs in trait_coverage.items():
            traits.add(trait_name)
            
        # Add custom trait handlers if applicable
        for trait_name, handler in self.custom_trait_handlers.items():
            if handler(asset, None, is_discovery=True):
                traits.add(trait_name)
                
        return traits
    
    def asset_to_traits_data(self, asset: Any, trait_set: List[str]) -> Dict[str, Any]:
        """
        Convert a Bifrost asset to OpenAssetIO traits data.
        
        Args:
            asset: A Bifrost asset object
            trait_set: List of trait names to include
            
        Returns:
            A dictionary of trait data compatible with OpenAssetIO
        """
        if not self.enabled or not asset:
            return {}
            
        result = {}
        
        # Expand any standard trait sets
        expanded_traits = self._expand_trait_set(trait_set)
        
        # Process direct mappings
        for asset_attr, (trait_name, prop_path) in self.asset_to_trait_map.items():
            if trait_name not in expanded_traits:
                continue
                
            if not hasattr(asset, asset_attr):
                continue
                
            value = getattr(asset, asset_attr)
            if value is not None:
                self._set_nested_value(result, trait_name, prop_path, value)
                
        # Process custom traits
        for trait_name in expanded_traits:
            if trait_name in self.custom_trait_handlers:
                self.custom_trait_handlers[trait_name](asset, result)
                
        return result
    
    def traits_data_to_asset(self, traits_data: Dict[str, Any], asset: Any) -> Any:
        """
        Update a Bifrost asset from OpenAssetIO traits data.
        
        Args:
            traits_data: Dictionary of trait data from OpenAssetIO
            asset: A Bifrost asset object to update
            
        Returns:
            The updated asset object
        """
        if not self.enabled or not traits_data or not asset:
            return asset
            
        # Process direct mappings
        for (trait_name, prop_path), asset_attr in self.trait_to_asset_map.items():
            if trait_name not in traits_data:
                continue
                
            value = self._get_nested_value(traits_data, trait_name, prop_path)
            if value is not None:
                setattr(asset, asset_attr, value)
                
        # Process custom traits
        for trait_name, handler in self.custom_trait_handlers.items():
            if trait_name in traits_data:
                handler(asset, traits_data, is_import=True)
                
        return asset
    
    def _expand_trait_set(self, trait_set: List[str]) -> Set[str]:
        """
        Expand a trait set by resolving standard trait set names.
        
        Args:
            trait_set: List of trait names, potentially including standard sets
            
        Returns:
            Set of expanded trait names
        """
        expanded = set()
        
        for trait in trait_set:
            if trait in self.STANDARD_TRAIT_SETS:
                # It's a standard trait set, expand it
                expanded.update(self.STANDARD_TRAIT_SETS[trait])
            else:
                # It's an individual trait
                expanded.add(trait)
                
        return expanded
    
    def _set_nested_value(self, result: Dict[str, Any], trait_name: str, prop_path: str, value: Any) -> None:
        """
        Set a value in a nested dictionary structure based on a dot-separated path.
        
        Args:
            result: The dictionary to update
            trait_name: The top-level trait name
            prop_path: Dot-separated path for the property
            value: The value to set
        """
        if trait_name not in result:
            result[trait_name] = {}
            
        if "." not in prop_path:
            # Simple case, direct property
            result[trait_name][prop_path] = value
            return
            
        # Complex case with nested properties
        current = result[trait_name]
        parts = prop_path.split(".")
        
        # Navigate to the right level
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            
        # Set the value at the final level
        current[parts[-1]] = value
    
    def _get_nested_value(self, data: Dict[str, Any], trait_name: str, prop_path: str) -> Any:
        """
        Get a value from a nested dictionary structure based on a dot-separated path.
        
        Args:
            data: The dictionary to read from
            trait_name: The top-level trait name
            prop_path: Dot-separated path for the property
            
        Returns:
            The value at the specified path, or None if not found
        """
        if trait_name not in data:
            return None
            
        if "." not in prop_path:
            # Simple case, direct property
            return data[trait_name].get(prop_path)
            
        # Complex case with nested properties
        current = data[trait_name]
        parts = prop_path.split(".")
        
        # Navigate to the right level
        for part in parts[:-1]:
            if part not in current:
                return None
            current = current[part]
            
        # Get the value at the final level
        return current.get(parts[-1])
    
    def _handle_relationship_trait(self, asset: Any, result: Optional[Dict[str, Any]], 
                                 is_discovery: bool = False, is_import: bool = False) -> Union[bool, None]:
        """
        Handle the relationshipManagement trait.
        
        This custom handler deals with asset dependencies and relationships.
        
        Args:
            asset: A Bifrost asset object
            result: Dictionary to update with trait data
            is_discovery: True if being called during trait discovery
            is_import: True if being called during import from traits data
            
        Returns:
            Boolean for discovery, None otherwise
        """
        # For discovery, check if asset has dependencies
        if is_discovery:
            return hasattr(asset, 'dependencies') and bool(getattr(asset, 'dependencies', []))
            
        # For export (to traits data)
        if not is_import and result is not None:
            if not hasattr(asset, 'dependencies') or not asset.dependencies:
                return
                
            # Convert dependencies to relationship traits
            relationships = []
            
            for dep in asset.dependencies:
                relationship = {
                    "type": dep.dependency_type or "default",
                    "targetId": str(dep.dependent_asset_id),
                    "optional": bool(dep.optional),
                    "metadata": {}
                }
                
                # Add any additional metadata
                if hasattr(dep, 'metadata') and dep.metadata:
                    relationship["metadata"] = dep.metadata
                    
                relationships.append(relationship)
                
            result["relationshipManagement"] = {
                "relationships": relationships
            }
            
        # For import (from traits data)
        if is_import and result is not None and hasattr(asset, 'set_dependencies'):
            if "relationshipManagement" not in result:
                return
                
            relationships_data = result["relationshipManagement"].get("relationships", [])
            if not relationships_data:
                return
                
            # Will need a proper implementation based on how Bifrost handles dependencies
            # This is a placeholder that would need to be completed:
            # dependencies = []
            # for rel_data in relationships_data:
            #     dependency = DependencyModel(
            #         dependent_asset_id=rel_data["targetId"],
            #         dependency_type=rel_data["type"],
            #         optional=rel_data.get("optional", False),
            #         metadata=rel_data.get("metadata", {})
            #     )
            #     dependencies.append(dependency)
            # 
            # asset.set_dependencies(dependencies)
            
            logger.info(f"Imported {len(relationships_data)} relationships for asset {asset.id}")

    def validate_traits_data(self, traits_data: Dict[str, Any], required_traits: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that traits data contains all required traits.
        
        Args:
            traits_data: Dictionary of trait data to validate
            required_traits: List of trait names that are required
            
        Returns:
            Tuple of (success, missing_traits)
        """
        if not self.enabled:
            return (False, required_traits)
            
        # Expand any standard trait sets in the required traits
        expanded_required = self._expand_trait_set(required_traits)
        
        # Check for missing traits
        missing = []
        for trait in expanded_required:
            if trait not in traits_data:
                missing.append(trait)
                
        return (len(missing) == 0, missing)


# Create a singleton instance
trait_handler = BifrostTraitHandler()
