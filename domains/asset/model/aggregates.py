"""
Domain aggregates for the Asset domain.

This module defines aggregates that group entities and enforce consistency boundaries.
Aggregates represent the primary access points for manipulating related entities.
"""

from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime

from bifrost.domains.asset.model.entities import Asset, AssetVersion, AssetDependency
from bifrost.domains.asset.model.value_objects import AssetId, VersionId, DependencyId
from bifrost.domains.asset.model.enums import AssetStatus, VersionStatus, DependencyType
from bifrost.domains.asset.model.exceptions import (
    AssetVersionNotFoundError, AssetStateError, DependencyError
)


class AssetAggregate:
    """
    Aggregate root for Asset and its related entities.
    
    This class enforces consistency rules across the Asset entity
    and its child entities (versions, dependencies).
    """
    
    def __init__(self, asset: Asset):
        self._asset = asset
        # Track domain events to be published
        self._events = []
    
    @property
    def asset(self) -> Asset:
        """Get the underlying asset entity."""
        return self._asset
    
    @property
    def events(self) -> List:
        """Get accumulated domain events."""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear accumulated domain events after publishing."""
        self._events = []
    
    def create_version(self, comment: str = "") -> AssetVersion:
        """Create a new version of the asset with business rule validation."""
        # Check if asset can have a new version (e.g., not ARCHIVED)
        if self._asset.status == AssetStatus.ARCHIVED:
            raise AssetStateError("Cannot create new versions for archived assets.")
        
        # Create the version through the entity
        version = self._asset.create_version(comment)
        
        # Record the event
        from bifrost.domains.asset.model.events import AssetVersionCreated
        event = AssetVersionCreated(
            asset_id=self._asset.id,
            version_id=version.id,
            version_number=version.version_number,
            comment=comment
        )
        self._events.append(event)
        
        return version
    
    def publish_version(self, version_id: VersionId) -> None:
        """Publish a version with validation of dependencies."""
        version = self._asset.get_version_by_id(version_id)
        if not version:
            raise AssetVersionNotFoundError(self._asset.id, version_id)
        
        # Check if all required dependencies are published
        self._validate_dependencies_for_publish(version)
        
        # Publish the version
        version.publish()
        
        # Update asset status
        self._asset.status = AssetStatus.PUBLISHED
        
        # Record the event
        from bifrost.domains.asset.model.events import AssetVersionPublished
        event = AssetVersionPublished(
            asset_id=self._asset.id,
            version_id=version.id,
            version_number=version.version_number
        )
        self._events.append(event)
    
    def _validate_dependencies_for_publish(self, version: AssetVersion) -> None:
        """Validate that all required dependencies are published."""
        for dependency in version.dependencies:
            if dependency.is_required:
                # In a real implementation, we would check if the target version
                # is published by querying the repository
                # For now, this is a placeholder for that logic
                pass  # Would raise DependencyError if validation fails
    
    def add_dependency(
        self,
        source_version_id: VersionId,
        target_version_id: VersionId,
        dependency_type: DependencyType,
        is_required: bool = True
    ) -> AssetDependency:
        """Add a dependency between versions with validation."""
        source_version = self._asset.get_version_by_id(source_version_id)
        if not source_version:
            raise AssetVersionNotFoundError(self._asset.id, source_version_id)
        
        # In a real implementation, we would validate that target_version_id exists
        # in the system by querying the repository
        
        # Add the dependency
        dependency = source_version.add_dependency(
            target_version_id=target_version_id,
            dependency_type=dependency_type,
            is_required=is_required
        )
        
        # Record the event
        from bifrost.domains.asset.model.events import AssetDependencyAdded
        event = AssetDependencyAdded(
            source_asset_id=self._asset.id,
            target_asset_id=target_version_id,  # This is simplified
            dependency_type=dependency_type.name,
            is_required=is_required
        )
        self._events.append(event)
        
        return dependency
