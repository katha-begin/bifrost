"""
Asset service for the Asset domain.

This module provides services for managing assets in the Bifrost system,
implementing the application layer functionality for the Asset domain.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Set, Tuple

from ..model.aggregates import AssetAggregate
from ..model.entities import Asset, AssetVersion, AssetDependency
from ..model.value_objects import (
    AssetId, VersionId, DependencyId, AssetMetadata, FilePath,
    generate_asset_id, generate_version_id, generate_dependency_id
)
from ..model.enums import AssetStatus, VersionStatus, AssetType, DependencyType
from ..model.exceptions import (
    AssetNotFoundError, AssetVersionNotFoundError, AssetStateError, 
    DependencyError, RepositoryError
)
from ..repository.asset_repository import AssetRepository
from bifrost.core.event_bus import EventBus

# Setup logger
logger = logging.getLogger(__name__)


class AssetService:
    """
    Service for managing assets in the Bifrost system.
    
    This service provides methods for creating, retrieving, updating, 
    and deleting assets, as well as managing asset versions and dependencies.
    """
    
    def __init__(self, repository: AssetRepository, event_bus: EventBus):
        """
        Initialize the asset service.
        
        Args:
            repository: The asset repository to use.
            event_bus: The event bus for publishing domain events.
        """
        self._repository = repository
        self._event_bus = event_bus
    
    def create_asset(self, 
                    name: str,
                    asset_type: AssetType,
                    description: str = "",
                    tags: list = None,
                    properties: Dict[str, Any] = None,
                    status: AssetStatus = AssetStatus.DRAFT) -> AssetId:
        """
        Create a new asset in the system.
        
        Args:
            name: The name of the asset
            asset_type: The type of asset
            description: Optional description of the asset
            tags: Optional list of tags
            properties: Optional additional metadata properties
            status: Initial status of the asset (default: DRAFT)
            
        Returns:
            The ID of the newly created Asset
            
        Raises:
            RepositoryError: If there's an error saving the asset
        """
        try:
            # Create metadata
            metadata = AssetMetadata(
                description=description,
                tags=tuple(tags or []),
                properties=properties or {}
            )
            
            # Create asset entity
            asset = Asset(
                name=name,
                asset_type=asset_type,
                status=status,
                metadata=metadata
            )
            
            # Create aggregate
            aggregate = AssetAggregate(asset)
            
            # Save to repository
            self._repository.save(aggregate)
            
            # Publish domain events
            for event in aggregate.events:
                self._event_bus.publish(event)
            
            # Clear events after publishing
            aggregate.clear_events()
            
            return asset.id
            
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            raise RepositoryError(f"Failed to create asset: {e}")
    
    def get_asset(self, asset_id: AssetId) -> Asset:
        """
        Retrieve an asset by its ID.
        
        Args:
            asset_id: The unique ID of the asset
            
        Returns:
            The Asset object
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
        """
        aggregate = self._repository.get_by_id(asset_id)
        if not aggregate:
            raise AssetNotFoundError(asset_id)
        
        return aggregate.asset
    
    def update_asset(self, 
                     asset_id: AssetId, 
                     name: Optional[str] = None,
                     description: Optional[str] = None,
                     status: Optional[AssetStatus] = None,
                     tags: Optional[list] = None,
                     properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Update an asset's properties.
        
        Args:
            asset_id: The ID of the asset to update
            name: New name (if provided)
            description: New description (if provided)
            status: New status (if provided)
            tags: New tags (if provided)
            properties: New metadata properties (if provided)
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
            RepositoryError: If there's an error saving the asset
        """
        # Get the asset aggregate
        aggregate = self._repository.get_by_id(asset_id)
        if not aggregate:
            raise AssetNotFoundError(asset_id)
        
        asset = aggregate.asset
        
        # Update properties if provided
        if name is not None:
            asset.name = name
        
        if status is not None:
            asset.change_status(status)
        
        # Update metadata
        if description is not None or tags is not None or properties is not None:
            current_metadata = asset.metadata
            
            # Create new metadata with updated values
            new_metadata = AssetMetadata(
                description=description if description is not None else current_metadata.description,
                tags=tuple(tags) if tags is not None else current_metadata.tags,
                properties=properties if properties is not None else current_metadata.properties
            )
            
            # Update asset's metadata
            object.__setattr__(asset, 'metadata', new_metadata)
        
        # Save changes
        self._repository.save(aggregate)
        
        # Publish domain events
        for event in aggregate.events:
            self._event_bus.publish(event)
        
        # Clear events after publishing
        aggregate.clear_events()
    
    def delete_asset(self, asset_id: AssetId) -> None:
        """
        Delete an asset from the system.
        
        Args:
            asset_id: The ID of the asset to delete
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
            RepositoryError: If there's an error deleting the asset
        """
        # Check if asset exists
        if not self._repository.exists(asset_id):
            raise AssetNotFoundError(asset_id)
        
        # Delete the asset
        success = self._repository.delete(asset_id)
        if not success:
            raise RepositoryError(f"Failed to delete asset with ID {asset_id}")
    
    def create_version(self, 
                       asset_id: AssetId, 
                       file_path: Optional[str] = None,
                       comment: str = "") -> VersionId:
        """
        Create a new version for an asset.
        
        Args:
            asset_id: The ID of the asset to version
            file_path: Path to the version file (optional)
            comment: Comment describing the version changes
            
        Returns:
            The ID of the newly created version
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
            AssetStateError: If the asset cannot have a new version
            RepositoryError: If there's an error saving the version
        """
        # Get the asset aggregate
        aggregate = self._repository.get_by_id(asset_id)
        if not aggregate:
            raise AssetNotFoundError(asset_id)
        
        # Create file path value object if path provided
        file_path_vo = FilePath(file_path) if file_path else None
        
        # Create the version through the aggregate
        version = aggregate.create_version(comment)
        
        # Set file path if provided
        if file_path_vo:
            object.__setattr__(version, 'file_path', file_path_vo)
        
        # Save changes
        self._repository.save(aggregate)
        
        # Publish domain events
        for event in aggregate.events:
            self._event_bus.publish(event)
        
        # Clear events after publishing
        aggregate.clear_events()
        
        return version.id
    
    def publish_version(self, asset_id: AssetId, version_id: VersionId) -> None:
        """
        Publish a specific version of an asset.
        
        Args:
            asset_id: The ID of the asset
            version_id: The ID of the version to publish
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
            AssetVersionNotFoundError: If the version doesn't exist
            DependencyError: If the version has unpublished required dependencies
            RepositoryError: If there's an error saving the changes
        """
        # Get the asset aggregate
        aggregate = self._repository.get_by_id(asset_id)
        if not aggregate:
            raise AssetNotFoundError(asset_id)
        
        # Publish the version through the aggregate
        try:
            aggregate.publish_version(version_id)
        except AssetVersionNotFoundError:
            raise AssetVersionNotFoundError(asset_id, version_id)
        
        # Save changes
        self._repository.save(aggregate)
        
        # Publish domain events
        for event in aggregate.events:
            self._event_bus.publish(event)
        
        # Clear events after publishing
        aggregate.clear_events()
    
    def add_dependency(self, 
                       source_asset_id: AssetId,
                       source_version_id: VersionId,
                       target_asset_id: AssetId,
                       target_version_id: VersionId,
                       dependency_type: DependencyType,
                       is_required: bool = True) -> None:
        """
        Add a dependency between two asset versions.
        
        Args:
            source_asset_id: ID of the asset that will have a dependency
            source_version_id: ID of the specific version that has the dependency
            target_asset_id: ID of the asset being depended on
            target_version_id: ID of the specific version being depended on
            dependency_type: Type of dependency
            is_required: Whether this dependency is required for publishing
            
        Raises:
            AssetNotFoundError: If either asset doesn't exist
            AssetVersionNotFoundError: If either version doesn't exist
            RepositoryError: If there's an error saving the dependency
        """
        # Check if source asset and version exist
        source_aggregate = self._repository.get_by_id(source_asset_id)
        if not source_aggregate:
            raise AssetNotFoundError(source_asset_id)
        
        # Check if target asset and version exist
        target_aggregate = self._repository.get_by_id(target_asset_id)
        if not target_aggregate:
            raise AssetNotFoundError(target_asset_id)
        
        # Check if target version exists
        target_version = self._repository.get_version(target_version_id)
        if not target_version:
            raise AssetVersionNotFoundError(target_asset_id, target_version_id)
        
        # Add the dependency through the aggregate
        try:
            dependency = source_aggregate.add_dependency(
                source_version_id=source_version_id,
                target_version_id=target_version_id,
                dependency_type=dependency_type,
                is_required=is_required
            )
        except AssetVersionNotFoundError:
            raise AssetVersionNotFoundError(source_asset_id, source_version_id)
        
        # Save changes
        self._repository.save(source_aggregate)
        
        # Publish domain events
        for event in source_aggregate.events:
            self._event_bus.publish(event)
        
        # Clear events after publishing
        source_aggregate.clear_events()
    
    def remove_dependency(self, 
                          source_asset_id: AssetId, 
                          source_version_id: VersionId,
                          target_version_id: VersionId) -> None:
        """
        Remove a dependency between two asset versions.
        
        Args:
            source_asset_id: ID of the asset that has the dependency
            source_version_id: ID of the specific version that has the dependency
            target_version_id: ID of the version being depended on
            
        Raises:
            AssetNotFoundError: If the source asset doesn't exist
            AssetVersionNotFoundError: If the source version doesn't exist
            RepositoryError: If there's an error saving the changes
        """
        # Get the source asset aggregate
        source_aggregate = self._repository.get_by_id(source_asset_id)
        if not source_aggregate:
            raise AssetNotFoundError(source_asset_id)
        
        # Get the source version
        source_version = source_aggregate.asset.get_version_by_id(source_version_id)
        if not source_version:
            raise AssetVersionNotFoundError(source_asset_id, source_version_id)
        
        # Remove the dependency
        source_version.remove_dependency(target_version_id)
        
        # Save changes
        self._repository.save(source_aggregate)
        
        # Create and publish domain event
        from ..model.events import AssetDependencyRemoved
        event = AssetDependencyRemoved(
            source_asset_id=source_asset_id,
            target_asset_id=target_version_id,  # This is simplified
        )
        self._event_bus.publish(event)
    
    def get_dependencies(self, asset_id: AssetId, version_id: VersionId) -> List[Tuple[AssetId, VersionId]]:
        """
        Get all dependencies for a specific asset version.
        
        Args:
            asset_id: The ID of the asset
            version_id: The ID of the version
            
        Returns:
            List of tuples (asset_id, version_id) that this version depends on
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
            AssetVersionNotFoundError: If the version doesn't exist
        """
        # Check if asset exists
        if not self._repository.exists(asset_id):
            raise AssetNotFoundError(asset_id)
        
        # Get the version dependencies
        dependent_ids = self._repository.get_dependencies(version_id)
        
        # For each dependency, get the asset ID
        # This is a simplified implementation. In a real system,
        # we would need to query the repository to get the asset ID for each version.
        return [(AssetId("unknown"), version_id) for version_id in dependent_ids]
    
    def get_dependents(self, asset_id: AssetId, version_id: VersionId) -> List[Tuple[AssetId, VersionId]]:
        """
        Get all dependents for a specific asset version.
        
        Args:
            asset_id: The ID of the asset
            version_id: The ID of the version
            
        Returns:
            List of tuples (asset_id, version_id) that depend on this version
            
        Raises:
            AssetNotFoundError: If the asset doesn't exist
            AssetVersionNotFoundError: If the version doesn't exist
        """
        # Check if asset exists
        if not self._repository.exists(asset_id):
            raise AssetNotFoundError(asset_id)
        
        # Get the version dependents
        dependent_ids = self._repository.get_dependents(version_id)
        
        # For each dependent, get the asset ID
        # This is a simplified implementation. In a real system,
        # we would need to query the repository to get the asset ID for each version.
        return [(AssetId("unknown"), version_id) for version_id in dependent_ids]
    
    def search_assets(self, 
                     query: str = "", 
                     asset_type: Optional[AssetType] = None,
                     status: Optional[AssetStatus] = None,
                     tags: List[str] = None,
                     created_by: str = None,
                     limit: int = 100,
                     offset: int = 0) -> List[Asset]:
        """
        Search for assets based on various criteria.
        
        Args:
            query: Text search term for name and description
            asset_type: Filter by asset type
            status: Filter by status
            tags: Filter by tags (list of tag names)
            created_by: Filter by creator
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of matching Asset objects
        """
        # Use repository search method
        aggregates = self._repository.search(
            query=query,
            asset_type=asset_type,
            status=status,
            tags=tags,
            created_by=created_by,
            limit=limit,
            offset=offset
        )
        
        # Extract assets from aggregates
        return [aggregate.asset for aggregate in aggregates]

# This can be used to create a singleton instance in a module-level variable
# asset_service = AssetService(repository, event_bus)
