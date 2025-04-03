#!/usr/bin/env python
# shot.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class ShotStatus(Enum):
    """Enumeration of possible shot statuses in the production pipeline."""
    PLANNED = "planned"        # Shot is planned but not started
    IN_PROGRESS = "in_progress"  # Currently being worked on
    REVIEW = "review"          # Ready for review
    APPROVED = "approved"      # Approved but may need changes
    FINAL = "final"            # Final version
    LOCKED = "locked"          # Locked, cannot be changed
    OMITTED = "omitted"        # Shot has been cut from production


class Department(Enum):
    """Departments involved in shot production."""
    LAYOUT = "layout"
    ANIMATION = "animation"
    FX = "fx"
    LIGHTING = "lighting"
    COMPOSITING = "compositing"
    EDITORIAL = "editorial"
    AUDIO = "audio"
    ALL = "all"  # For global tasks/notes


@dataclass
class ShotTask:
    """Task associated with a shot."""
    id: str
    name: str
    description: str = ""
    department: Department = Department.ALL
    assigned_to: str = ""
    status: str = "pending"  # pending, in_progress, completed, etc.
    priority: int = 1  # 1 (lowest) to 5 (highest)
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks this depends on
    metadata: Dict = field(default_factory=dict)


@dataclass
class ShotNote:
    """Notes and feedback related to a shot."""
    id: str
    content: str
    author: str
    created_at: datetime = field(default_factory=datetime.now)
    department: Department = Department.ALL
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: str = ""
    attachments: List[Path] = field(default_factory=list)
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        for i, path in enumerate(self.attachments):
            if isinstance(path, str):
                self.attachments[i] = Path(path)
    
    def resolve(self, user: str) -> None:
        """Mark this note as resolved."""
        self.resolved = True
        self.resolved_at = datetime.now()
        self.resolved_by = user


@dataclass
class ShotVersion:
    """Represents a specific version of a shot."""
    version_number: int
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    comment: str = ""
    status: ShotStatus = ShotStatus.IN_PROGRESS
    filepath: Optional[Path] = None
    frame_range: tuple = (1, 1)  # (start_frame, end_frame)
    preview_path: Optional[Path] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.filepath, str):
            self.filepath = Path(self.filepath)
        if isinstance(self.preview_path, str):
            self.preview_path = Path(self.preview_path)


@dataclass
class Shot:
    """
    Represents a shot in the animation production pipeline.
    
    A shot is a continuous sequence of frames that is part of a sequence.
    """
    id: str
    code: str  # Shot code (e.g., "sq001_sh010")
    sequence_id: str  # ID of the parent sequence
    name: str = ""
    description: str = ""
    status: ShotStatus = ShotStatus.PLANNED
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    modified_at: datetime = field(default_factory=datetime.now)
    modified_by: str = ""
    frame_range: tuple = (1, 1)  # (start_frame, end_frame)
    handle_range: tuple = (0, 0)  # (pre_handles, post_handles)
    
    # References to assets used in this shot
    asset_ids: Set[str] = field(default_factory=set)
    
    # Shot management
    tasks: List[ShotTask] = field(default_factory=list)
    notes: List[ShotNote] = field(default_factory=list)
    versions: List[ShotVersion] = field(default_factory=list)
    
    # Visual references
    thumbnail_path: Optional[Path] = None
    
    # Additional metadata
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.thumbnail_path, str):
            self.thumbnail_path = Path(self.thumbnail_path)
    
    @property
    def duration(self) -> int:
        """Calculate the duration of the shot in frames."""
        start, end = self.frame_range
        return max(0, end - start + 1)
    
    @property
    def duration_with_handles(self) -> int:
        """Calculate the duration of the shot in frames, including handles."""
        start, end = self.frame_range
        pre, post = self.handle_range
        return max(0, (end + post) - (start - pre) + 1)
    
    @property
    def latest_version(self) -> Optional[ShotVersion]:
        """Return the latest version of this shot."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)
    
    @property
    def latest_approved_version(self) -> Optional[ShotVersion]:
        """Return the latest approved or final version of this shot."""
        approved_versions = [v for v in self.versions 
                            if v.status in (ShotStatus.APPROVED, ShotStatus.FINAL)]
        if not approved_versions:
            return None
        return max(approved_versions, key=lambda v: v.version_number)
    
    def add_version(self, version: ShotVersion) -> None:
        """Add a new version to this shot."""
        self.versions.append(version)
        self.modified_at = datetime.now()
    
    def add_task(self, task: ShotTask) -> None:
        """Add a task to this shot."""
        self.tasks.append(task)
        self.modified_at = datetime.now()
    
    def add_note(self, note: ShotNote) -> None:
        """Add a note to this shot."""
        self.notes.append(note)
        self.modified_at = datetime.now()
    
    def add_asset(self, asset_id: str) -> None:
        """Associate an asset with this shot."""
        self.asset_ids.add(asset_id)
        self.modified_at = datetime.now()
    
    def remove_asset(self, asset_id: str) -> bool:
        """Remove an asset association from this shot."""
        if asset_id in self.asset_ids:
            self.asset_ids.remove(asset_id)
            self.modified_at = datetime.now()
            return True
        return False
    
    def update_status(self, status: ShotStatus, updated_by: str) -> None:
        """Update the status of this shot."""
        self.status = status
        self.modified_by = updated_by
        self.modified_at = datetime.now()
    
    def update_frame_range(self, start_frame: int, end_frame: int) -> None:
        """Update the frame range of this shot."""
        self.frame_range = (start_frame, end_frame)
        self.modified_at = datetime.now()
