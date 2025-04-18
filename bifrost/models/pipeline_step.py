"""
Pipeline step models for the Bifrost system.
"""

from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator

from .task import TaskStatus, TaskPriority


class FileFormat(BaseModel):
    """File format produced by a pipeline step."""
    type: str
    formats: List[str]
    location: str


class DepartmentDependency(BaseModel):
    """Dependency on another department."""
    department: str
    status: str = "approved"  # Status required for dependency to be satisfied


class TaskTemplate(BaseModel):
    """Task template model for pipeline steps."""
    name_template: str
    description_template: Optional[str] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)


class PipelineStep(BaseModel):
    """Core pipeline step model representing a workflow stage."""
    id: UUID = Field(default_factory=uuid4)
    department_id: str = Field(min_length=1, max_length=50)  # Matches department ID in dependencies.yaml
    name: str = Field(min_length=3, max_length=50)
    description: str
    step_order: int = Field(ge=0)
    requires: List[DepartmentDependency] = Field(default_factory=list)
    produces: List[FileFormat] = Field(default_factory=list)
    task_template: Optional[TaskTemplate] = None
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True

    @validator('department_id')
    def department_id_must_be_valid(cls, v):
        """Ensure department_id follows the convention in dependencies.yaml."""
        valid_departments = {"concept", "modeling", "texture", "shading", "rigging", 
                             "layout", "animation", "fx", "lighting", "rendering", "comp"}
        if v not in valid_departments:
            raise ValueError(f"Department ID must be one of: {', '.join(valid_departments)}")
        return v


class PipelineStepCreate(BaseModel):
    """Model for creating a new pipeline step."""
    department_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=3, max_length=50)
    description: str
    step_order: int = Field(ge=0)
    requires: List[DepartmentDependency] = Field(default_factory=list)
    produces: List[FileFormat] = Field(default_factory=list)
    task_template: Optional[TaskTemplate] = None
    enabled: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('department_id')
    def department_id_must_be_valid(cls, v):
        """Ensure department_id follows the convention in dependencies.yaml."""
        valid_departments = {"concept", "modeling", "texture", "shading", "rigging", 
                             "layout", "animation", "fx", "lighting", "rendering", "comp"}
        if v not in valid_departments:
            raise ValueError(f"Department ID must be one of: {', '.join(valid_departments)}")
        return v


class PipelineStepUpdate(BaseModel):
    """Model for updating an existing pipeline step."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=50)
    description: Optional[str] = None
    step_order: Optional[int] = Field(default=None, ge=0)
    requires: Optional[List[DepartmentDependency]] = None
    produces: Optional[List[FileFormat]] = None
    task_template: Optional[TaskTemplate] = None
    enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowType(str, Enum):
    """Type of workflow."""
    DEFAULT = "default"
    LIGHTWEIGHT = "lightweight"
    CUSTOM = "custom"


class AssetWorkflow(BaseModel):
    """Pipeline workflow for an asset type."""
    asset_type: str  # character, prop, environment, etc.
    sequence: List[str]  # List of department IDs in sequence


class ShotWorkflow(BaseModel):
    """Pipeline workflow for a shot type."""
    shot_type: str  # standard, vfx_heavy, full_cg, etc.
    sequence: List[str]  # List of department IDs in sequence


class PipelineWorkflow(BaseModel):
    """Complete pipeline workflow configuration."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    type: WorkflowType = WorkflowType.DEFAULT
    description: str = ""
    asset_workflows: List[AssetWorkflow] = Field(default_factory=list)
    shot_workflows: List[ShotWorkflow] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    enabled: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True