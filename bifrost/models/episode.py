"""
Episode model for the Bifrost system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator


class EpisodeStatus(str, Enum):
    """Episode status enumeration."""
    PLANNING = "planning"
    BOARDING = "boarding"
    PRODUCTION = "production"
    POST = "post"
    DELIVERY = "delivery"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Episode(BaseModel):
    """
    Represents an episode in the animation production pipeline.
    
    An episode belongs to a series and contains sequences.
    """
    id: UUID = Field(default_factory=uuid4)
    series_id: UUID
    name: str
    code: str  # Episode code (e.g., "ep001")
    description: str = ""
    status: EpisodeStatus = EpisodeStatus.PLANNING
    
    # Frame tracking
    frame_start: int = 1001
    frame_end: int = 1001
    global_frame_start: Optional[int] = None
    global_frame_end: Optional[int] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    modified_by: str = ""
    metadata: Dict = Field(default_factory=dict)
    
    @validator('frame_end')
    def frame_end_greater_than_start(cls, v, values):
        """Validate that frame_end is greater than or equal to frame_start."""
        if 'frame_start' in values and v < values['frame_start']:
            raise ValueError('frame_end must be greater than or equal to frame_start')
        return v
    
    @validator('global_frame_end')
    def global_frame_end_greater_than_start(cls, v, values):
        """Validate that global_frame_end is greater than or equal to global_frame_start."""
        if (v is not None and 'global_frame_start' in values and 
                values['global_frame_start'] is not None and v < values['global_frame_start']):
            raise ValueError('global_frame_end must be greater than or equal to global_frame_start')
        return v
    
    class Config:
        orm_mode = True
    
    @property
    def duration(self) -> int:
        """Calculate the duration of the episode in frames."""
        return max(0, self.frame_end - self.frame_start + 1)
    
    @property
    def global_duration(self) -> Optional[int]:
        """Calculate the global duration of the episode in frames."""
        if self.global_frame_start is None or self.global_frame_end is None:
            return None
        return self.global_frame_end - self.global_frame_start + 1


class EpisodeCreate(BaseModel):
    """Model for creating a new episode."""
    series_id: UUID
    name: str
    code: str
    description: str = ""
    status: EpisodeStatus = EpisodeStatus.PLANNING
    frame_start: int = 1001
    frame_end: int = 1001
    global_frame_start: Optional[int] = None
    global_frame_end: Optional[int] = None
    metadata: Dict = Field(default_factory=dict)
    
    @validator('frame_end')
    def frame_end_greater_than_start(cls, v, values):
        """Validate that frame_end is greater than or equal to frame_start."""
        if 'frame_start' in values and v < values['frame_start']:
            raise ValueError('frame_end must be greater than or equal to frame_start')
        return v
    
    @validator('global_frame_end')
    def global_frame_end_greater_than_start(cls, v, values):
        """Validate that global_frame_end is greater than or equal to global_frame_start."""
        if (v is not None and 'global_frame_start' in values and 
                values['global_frame_start'] is not None and v < values['global_frame_start']):
            raise ValueError('global_frame_end must be greater than or equal to global_frame_start')
        return v


class EpisodeUpdate(BaseModel):
    """Model for updating an existing episode."""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[EpisodeStatus] = None
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    global_frame_start: Optional[int] = None
    global_frame_end: Optional[int] = None
    metadata: Optional[Dict] = None