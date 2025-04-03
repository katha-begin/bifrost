"""
Domain events for the Asset domain.

This module defines events that represent important occurrences within the Asset domain.
These events can be published and subscribed to by different parts of the system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from bifrost.domains.asset.model.value_objects import AssetId, VersionId
from bifrost.domains.asset.model.enums import AssetStatus, VersionStatus, AssetType


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    occurred_on: datetime = None
    
    def __post_init__(self):
        if self.occurred_on is None:
            self.occurred_on = datetime.now()


@dataclass
class AssetCreated(DomainEvent):
    """Event raised when a new asset is created."""
    asset_id: AssetId
    name: str
    asset_type: AssetType
    status: AssetStatus


@dataclass
class AssetUpdated(DomainEvent):
    """Event raised when an asset's metadata is updated."""
    asset_id: AssetId
    name: Optional[str] = None
    status: Optional[AssetStatus] = None
    updated_fields: Dict[str, Any] = None


@dataclass
class AssetDeleted(DomainEvent):
    """Event raised when an asset is deleted."""
    asset_id: AssetId


@dataclass
class AssetVersionCreated(DomainEvent):
    """Event raised when a new asset version is created."""
    asset_id: AssetId
    version_id: VersionId
    version_number: int
    comment: str


@dataclass
class AssetVersionUpdated(DomainEvent):
    """Event raised when an asset version is updated."""
    asset_id: AssetId
    version_id: VersionId
    status: Optional[VersionStatus] = None
    comment: Optional[str] = None
    updated_fields: Dict[str, Any] = None


@dataclass
class AssetVersionPublished(DomainEvent):
    """Event raised when an asset version is published."""
    asset_id: AssetId
    version_id: VersionId
    version_number: int


@dataclass
class AssetVersionDeprecated(DomainEvent):
    """Event raised when an asset version is deprecated."""
    asset_id: AssetId
    version_id: VersionId
    reason: str


@dataclass
class AssetDependencyAdded(DomainEvent):
    """Event raised when a dependency is added between assets."""
    source_asset_id: AssetId
    target_asset_id: AssetId
    dependency_type: str
    is_required: bool


@dataclass
class AssetDependencyRemoved(DomainEvent):
    """Event raised when a dependency between assets is removed."""
    source_asset_id: AssetId
    target_asset_id: AssetId
