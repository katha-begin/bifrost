"""
Sequence model for the Bifrost system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator


class SequenceStatus(str, Enum):
    """Sequence status enumeration."""
    PLANNING = "planning"
    BOARDING = "boarding"
    LAYOUT = "layout"
    PRODUCTION = "production"
    FINALING = "finaling"
    APPROVED = "approved"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Sequence(BaseModel):
    """
    Represents a sequence in the animation production pipeline.
    
    A sequence belongs to an episode and contains shots.
    """
    id: UUID = Field(default_factory=uuid4)
    episode_id: Optional[UUID] = None  # Optional because some sequences might not be part of an episode
    name: str
    code: str  # Sequence code (e.g., "sq001")
    description: str = ""
    status: SequenceStatus = SequenceStatus.PLANNING
    
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
        """Calculate the duration of the sequence in frames."""
        return max(0, self.frame_end - self.frame_start + 1)
    
    @property
    def global_duration(self) -> Optional[int]:
        """Calculate the global duration of the sequence in frames."""
        if self.global_frame_start is None or self.global_frame_end is None:
            return None
        return self.global_frame_end - self.global_frame_start + 1


class SequenceCreate(BaseModel):
    """Model for creating a new sequence."""
    episode_id: Optional[UUID] = None
    name: str
    code: str
    description: str = ""
    status: SequenceStatus = SequenceStatus.PLANNING
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


class SequenceUpdate(BaseModel):
    """Model for updating an existing sequence."""
    episode_id: Optional[UUID] = None
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SequenceStatus] = None
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    global_frame_start: Optional[int] = None
    global_frame_end: Optional[int] = None
    metadata: Optional[Dict] = None