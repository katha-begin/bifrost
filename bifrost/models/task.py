"""
Task domain models for the Bifrost system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Core task model representing a work item."""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=3, max_length=100)
    description: str
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    assignee_id: Optional[UUID] = None
    asset_id: Optional[UUID] = None
    shot_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    tags: List[str] = Field(default_factory=list)
    dependencies: List[UUID] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    """Model for creating a new task."""
    name: str = Field(min_length=3, max_length=100)
    description: str
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    assignee_id: Optional[UUID] = None
    asset_id: Optional[UUID] = None
    shot_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    tags: List[str] = Field(default_factory=list)
    dependencies: List[UUID] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[UUID] = None
    asset_id: Optional[UUID] = None
    shot_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    dependencies: Optional[List[UUID]] = None
    metadata: Optional[Dict[str, Any]] = None