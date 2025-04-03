#!/usr/bin/env python
# asset.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pathlib import Path


class AssetType(Enum):
    """Enumeration of possible asset types in an animation pipeline."""
    CHARACTER = "character"
    PROP = "prop"
    ENVIRONMENT = "environment"
    FX = "fx"
    LIGHTING = "lighting"
    MATERIAL = "material"
    RIG = "rig"
    TEXTURE = "texture"
    ANIMATION = "animation"
    OTHER = "other"


class AssetStatus(Enum):
    """Enumeration of possible asset statuses in the production pipeline."""
    CONCEPT = "concept"        # Initial idea stage
    IN_PROGRESS = "in_progress"  # Currently being worked on
    REVIEW = "review"          # Ready for review
    APPROVED = "approved"      # Approved but not final
    FINAL = "final"            # Final version
    ARCHIVED = "archived"      # No longer in active use
    DEPRECATED = "deprecated"  # Replaced by newer asset


@dataclass
class AssetTag:
    """Tags for categorizing and filtering assets."""
    name: str
    color: str = "#808080"  # Default gray color
    description: str = ""


@dataclass
class AssetVersion:
    """Represents a specific version of an asset."""
    version_number: int
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    comment: str = ""
    file_path: Path = None
    status: AssetStatus = AssetStatus.IN_PROGRESS
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)


@dataclass
class AssetDependency:
    """Represents a dependency between assets."""
    dependent_asset_id: str  # ID of the asset that depends on this one
    dependency_type: str  # Type of dependency (reference, import, etc.)
    optional: bool = False  # Whether this dependency is optional


@dataclass
class Asset:
    """
    Represents a production asset in the animation pipeline.
    
    An asset is any digital content used in the production, such as 
    characters, props, environments, textures, etc.
    """
    id: str
    name: str
    asset_type: AssetType
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    modified_at: datetime = field(default_factory=datetime.now)
    modified_by: str = ""
    description: str = ""
    status: AssetStatus = AssetStatus.CONCEPT
    tags: List[AssetTag] = field(default_factory=list)
    versions: List[AssetVersion] = field(default_factory=list)
    dependencies: List[AssetDependency] = field(default_factory=list)
    dependents: List[AssetDependency] = field(default_factory=list)
    thumbnail_path: Optional[Path] = None
    preview_path: Optional[Path] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.thumbnail_path, str):
            self.thumbnail_path = Path(self.thumbnail_path)
        if isinstance(self.preview_path, str):
            self.preview_path = Path(self.preview_path)
    
    @property
    def latest_version(self) -> Optional[AssetVersion]:
        """Return the latest version of this asset if any versions exist."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)
    
    @property
    def latest_approved_version(self) -> Optional[AssetVersion]:
        """Return the latest approved or final version of this asset."""
        approved_versions = [v for v in self.versions 
                             if v.status in (AssetStatus.APPROVED, AssetStatus.FINAL)]
        if not approved_versions:
            return None
        return max(approved_versions, key=lambda v: v.version_number)
    
    def add_version(self, version: AssetVersion) -> None:
        """Add a new version to this asset."""
        self.versions.append(version)
        self.modified_at = datetime.now()
    
    def add_dependency(self, asset_id: str, dependency_type: str, optional: bool = False) -> None:
        """Add a dependency on another asset."""
        dependency = AssetDependency(
            dependent_asset_id=asset_id,
            dependency_type=dependency_type,
            optional=optional
        )
        self.dependencies.append(dependency)
    
    def add_tag(self, tag_name: str, color: str = "#808080", description: str = "") -> None:
        """Add a tag to this asset."""
        tag = AssetTag(name=tag_name, color=color, description=description)
        self.tags.append(tag)
    
    def update_status(self, status: AssetStatus, updated_by: str) -> None:
        """Update the status of this asset."""
        self.status = status
        self.modified_by = updated_by
        self.modified_at = datetime.now()
