#!/usr/bin/env python
# review.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-14

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pathlib import Path

class ReviewStatus(Enum):
    """Enumeration of possible review statuses in the production pipeline."""
    PENDING = "pending"        # Scheduled but not started
    IN_PROGRESS = "in_progress"  # Currently being reviewed
    COMPLETED = "completed"    # Review finished
    CANCELED = "canceled"      # Review canceled
    REOPENED = "reopened"      # Review reopened after completion

class NoteStatus(Enum):
    """Enumeration of possible statuses for review notes."""
    OPEN = "open"              # Note needs to be addressed
    ADDRESSED = "addressed"    # Note has been addressed
    APPROVED = "approved"      # Changes approved
    REJECTED = "rejected"      # Changes rejected
    DEFERRED = "deferred"      # Addressing note deferred to later


@dataclass
class ReviewNote:
    """Note associated with a review item."""
    id: str
    review_id: str
    item_id: str  # Shot or asset ID
    author: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    frame: Optional[int] = None
    timecode: Optional[str] = None
    status: str = "open"
    metadata: Dict = field(default_factory=dict)
    attachments: List[Path] = field(default_factory=list)
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if self.attachments:
            for i, path in enumerate(self.attachments):
                if isinstance(path, str):
                    self.attachments[i] = Path(path)


@dataclass
class ReviewItem:
    """Item being reviewed (shot or asset)."""
    id: str
    review_id: str
    item_id: str  # Shot or asset ID
    item_type: str  # "shot" or "asset"
    version_id: str
    status: str = "pending"
    notes: List[ReviewNote] = field(default_factory=list)
    preview_path: Optional[Path] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.preview_path, str):
            self.preview_path = Path(self.preview_path)


@dataclass
class Review:
    """
    Review session for shots or assets.
    
    A review represents a collection of shots or assets to be reviewed,
    along with notes and feedback from reviewers.
    """
    id: str
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    completed_at: Optional[datetime] = None
    status: ReviewStatus = ReviewStatus.PENDING
    items: List[ReviewItem] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def add_item(self, item: ReviewItem) -> None:
        """Add an item to this review."""
        self.items.append(item)
    
    def add_note(self, item_id: str, note: ReviewNote) -> bool:
        """Add a note to a review item."""
        for item in self.items:
            if item.item_id == item_id:
                item.notes.append(note)
                return True
        return False
    
    def complete(self, completed_by: str) -> None:
        """Mark the review as completed."""
        self.status = ReviewStatus.COMPLETED
        self.completed_at = datetime.now()
        self.metadata["completed_by"] = completed_by
    
    def reopen(self, reopened_by: str) -> None:
        """Reopen a completed review."""
        self.status = ReviewStatus.REOPENED
        self.completed_at = None
        self.metadata["reopened_by"] = reopened_by
        self.metadata["reopened_at"] = datetime.now().isoformat()
