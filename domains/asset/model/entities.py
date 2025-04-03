"""
Core domain entities for the Asset domain.

This module defines the primary entities that make up the Asset domain model,
including their attributes, relationships, and business logic.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Set

from bifrost.domains.asset.model.value_objects import (
    AssetId, VersionId, DependencyId, 
    AssetMetadata, FilePath,
    generate_asset_id, generate_version_id, generate_dependency_id
)
from bifrost.domains.asset.model.enums import (
    AssetStatus, VersionStatus, AssetType, DependencyType
)


class AssetVersion:
    """Entity representing a specific version of an asset."""
    
    def __init__(
        self,
        asset_id: AssetId,
        version_number: int,
        comment: str = "",
        status: VersionStatus = VersionStatus.WORK_IN_PROGRESS,
        created_at: Optional[datetime] = None,
        version_id: Optional[VersionId] = None,
        metadata: Optional[Dict[str, Any]] = None,
        file_path: Optional[FilePath] = None
    ):
        self.id = version_id or generate_version_id()
        self.asset_id = asset_id
        self.version_number = version_number
        self.comment = comment
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = self.created_at
        self.metadata = metadata or {}
        self.file_path = file_path
        self._dependencies: List[AssetDependency] = []
    
    @property
    def dependencies(self) -> List['AssetDependency']:
        """Return a copy of the dependencies to prevent direct modification."""
        return self._dependencies.copy()
    
    def add_dependency(
        self, 
        target_version_id: VersionId,
        dependency_type: DependencyType,
        is_required: bool = True
    ) -> 'AssetDependency':
        """Add a dependency to another asset version."""
        dependency = AssetDependency(
            source_id=self.id,
            target_id=target_version_id,
            dependency_type=dependency_type,
            is_required=is_required
        )
        self._dependencies.append(dependency)
        self.updated_at = datetime.now()
        return dependency
    
    def remove_dependency(self, target_version_id: VersionId) -> None:
        """Remove a dependency to another asset version."""
        self._dependencies = [
            dep for dep in self._dependencies 
            if dep.target_id != target_version_id
        ]
        self.updated_at = datetime.now()
    
    def publish(self) -> None:
        """Publish this version."""
        if self.status == VersionStatus.WORK_IN_PROGRESS:
            raise ValueError("Cannot publish a version that is still in progress.")
        
        if self.status == VersionStatus.PUBLISHED:
            return  # Already published
        
        self.status = VersionStatus.PUBLISHED
        self.updated_at = datetime.now()
    
    def deprecate(self) -> None:
        """Mark this version as deprecated."""
        if self.status == VersionStatus.DEPRECATED:
            return  # Already deprecated
        
        self.status = VersionStatus.DEPRECATED
        self.updated_at = datetime.now()
    
    def set_status(self, status: VersionStatus) -> None:
        """Update the status of this version."""
        if self.status == status:
            return  # No change
        
        self.status = status
        self.updated_at = datetime.now()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata value."""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def __eq__(self, other):
        if not isinstance(other, AssetVersion):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)


class AssetDependency:
    """Entity representing a dependency between assets or versions."""
    
    def __init__(
        self,
        source_id: VersionId,
        target_id: VersionId,
        dependency_type: DependencyType,
        is_required: bool = True,
        dependency_id: Optional[DependencyId] = None
    ):
        self.id = dependency_id or generate_dependency_id()
        self.source_id = source_id
        self.target_id = target_id
        self.dependency_type = dependency_type
        self.is_required = is_required
        self.created_at = datetime.now()
    
    def __eq__(self, other):
        if not isinstance(other, AssetDependency):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)


class Asset:
    """Root entity representing a digital asset in the system."""
    
    def __init__(
        self,
        name: str,
        asset_type: AssetType,
        status: AssetStatus = AssetStatus.DRAFT,
        created_at: Optional[datetime] = None,
        asset_id: Optional[AssetId] = None,
        metadata: Optional[AssetMetadata] = None
    ):
        self.id = asset_id or generate_asset_id()
        self.name = name
        self.asset_type = asset_type
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = self.created_at
        self.metadata = metadata or AssetMetadata()
        self._versions: List[AssetVersion] = []
    
    @property
    def versions(self) -> List[AssetVersion]:
        """Return a copy of the versions to prevent direct modification."""
        return self._versions.copy()
    
    @property
    def latest_version(self) -> Optional[AssetVersion]:
        """Return the latest version of this asset."""
        if not self._versions:
            return None
        
        return max(self._versions, key=lambda v: v.version_number)
    
    @property
    def latest_published_version(self) -> Optional[AssetVersion]:
        """Return the latest published version of this asset."""
        published_versions = [
            v for v in self._versions 
            if v.status == VersionStatus.PUBLISHED
        ]
        
        if not published_versions:
            return None
        
        return max(published_versions, key=lambda v: v.version_number)
    
    def create_version(self, comment: str = "") -> AssetVersion:
        """Create a new version of this asset."""
        next_version_number = 1
        if self._versions:
            next_version_number = max(v.version_number for v in self._versions) + 1
        
        version = AssetVersion(
            asset_id=self.id,
            version_number=next_version_number,
            comment=comment
        )
        
        self._versions.append(version)
        self.updated_at = datetime.now()
        
        return version
    
    def add_version(self, version: AssetVersion) -> None:
        """Add an existing version to this asset."""
        if version.asset_id != self.id:
            raise ValueError("Version does not belong to this asset.")
        
        existing_versions = {v.version_number for v in self._versions}
        if version.version_number in existing_versions:
            raise ValueError(f"Version {version.version_number} already exists.")
        
        self._versions.append(version)
        self.updated_at = datetime.now()
    
    def get_version(self, version_number: int) -> Optional[AssetVersion]:
        """Get a specific version by number."""
        for version in self._versions:
            if version.version_number == version_number:
                return version
        return None
    
    def get_version_by_id(self, version_id: VersionId) -> Optional[AssetVersion]:
        """Get a specific version by ID."""
        for version in self._versions:
            if version.id == version_id:
                return version
        return None
    
    def publish_version(self, version_id: VersionId) -> None:
        """Publish a specific version."""
        version = self.get_version_by_id(version_id)
        if not version:
            raise ValueError(f"Version with ID {version_id} not found.")
        
        version.publish()
        self.status = AssetStatus.PUBLISHED
        self.updated_at = datetime.now()
    
    def change_status(self, new_status: AssetStatus) -> None:
        """Change the status of this asset."""
        if self.status == new_status:
            return  # No change
        
        self.status = new_status
        self.updated_at = datetime.now()
    
    def __eq__(self, other):
        if not isinstance(other, Asset):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
