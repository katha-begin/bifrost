"""
Value objects for the Asset domain.

This module defines immutable value objects used within the Asset domain.
"""

import uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any, NewType


# Type aliases for IDs to increase type safety
AssetId = NewType('AssetId', str)
VersionId = NewType('VersionId', str)
DependencyId = NewType('DependencyId', str)


def generate_asset_id() -> AssetId:
    """Generate a new unique asset ID."""
    return AssetId(str(uuid.uuid4()))


def generate_version_id() -> VersionId:
    """Generate a new unique version ID."""
    return VersionId(str(uuid.uuid4()))


def generate_dependency_id() -> DependencyId:
    """Generate a new unique dependency ID."""
    return DependencyId(str(uuid.uuid4()))


@dataclass(frozen=True)
class AssetMetadata:
    """Immutable metadata associated with an asset."""
    description: str = ""
    tags: tuple = ()
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        # Ensure properties is never None
        if self._properties is None:
            object.__setattr__(self, '_properties', {})
        
        # Convert any mutable collections to immutable ones
        if not isinstance(self.tags, tuple):
            object.__setattr__(self, 'tags', tuple(self.tags))
    
    def with_tag(self, tag: str) -> 'AssetMetadata':
        """Create a new metadata object with an additional tag."""
        return AssetMetadata(
            description=self.description,
            tags=(*self.tags, tag),
            properties=self.properties.copy()
        )
    
    def with_property(self, key: str, value: Any) -> 'AssetMetadata':
        """Create a new metadata object with an updated property."""
        new_properties = self.properties.copy()
        new_properties[key] = value
        return AssetMetadata(
            description=self.description,
            tags=self.tags,
            properties=new_properties
        )
    
    def with_description(self, description: str) -> 'AssetMetadata':
        """Create a new metadata object with an updated description."""
        return AssetMetadata(
            description=description,
            tags=self.tags,
            properties=self.properties.copy()
        )


@dataclass(frozen=True)
class FilePath:
    """Immutable representation of a file path."""
    path: str
    
    def __str__(self) -> str:
        return self.path
