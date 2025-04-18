"""
Series model for the Bifrost system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class SeriesStatus(str, Enum):
    """Series status enumeration."""
    PLANNING = "planning"
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Series(BaseModel):
    """Top-level series model representing a production series."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    code: str = Field(min_length=2, max_length=20)
    description: str = ""
    status: SeriesStatus = SeriesStatus.PLANNING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    modified_by: str = ""
    
    # Series metadata
    season_number: Optional[int] = None
    episode_count: Optional[int] = None
    total_duration: Optional[int] = None  # Total duration in frames
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class SeriesCreate(BaseModel):
    """Model for creating a new series."""
    name: str
    code: str = Field(min_length=2, max_length=20)
    description: str = ""
    status: SeriesStatus = SeriesStatus.PLANNING
    season_number: Optional[int] = None
    episode_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SeriesUpdate(BaseModel):
    """Model for updating an existing series."""
    name: Optional[str] = None
    code: Optional[str] = Field(default=None, min_length=2, max_length=20)
    description: Optional[str] = None
    status: Optional[SeriesStatus] = None
    season_number: Optional[int] = None
    episode_count: Optional[int] = None
    total_duration: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None