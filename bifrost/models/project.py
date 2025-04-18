"""
Project model for the Bifrost system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, root_validator

from bifrost.models.pipeline_step import WorkflowType, AssetWorkflow, ShotWorkflow


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DepartmentOverride(BaseModel):
    """Override for department dependencies in a project."""
    requires: List[Dict[str, Any]] = Field(default_factory=list)


class TaskTemplateOverride(BaseModel):
    """Override for task templates in a project."""
    name_template: Optional[str] = None
    description_template: Optional[str] = None
    estimated_hours: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class ProjectPipelineConfig(BaseModel):
    """Project-specific pipeline configuration."""
    workflow_type: WorkflowType = WorkflowType.DEFAULT
    custom_department_dependencies: Dict[str, DepartmentOverride] = Field(default_factory=dict)
    asset_workflows: Dict[str, AssetWorkflow] = Field(default_factory=dict)
    shot_workflows: Dict[str, ShotWorkflow] = Field(default_factory=dict)


class Project(BaseModel):
    """Core project model representing a production project."""
    id: UUID = Field(default_factory=uuid4)
    project_code: str = Field(min_length=2, max_length=20)
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    # Pipeline configuration
    pipeline_config: Optional[ProjectPipelineConfig] = None
    task_templates: Dict[str, TaskTemplateOverride] = Field(default_factory=dict)
    
    # Project metadata
    fps: float = 24.0
    resolution: str = "1920x1080"
    colorspace: str = "ACES"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class ProjectCreate(BaseModel):
    """Model for creating a new project."""
    project_code: str = Field(min_length=2, max_length=20)
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Pipeline configuration
    pipeline_config: Optional[ProjectPipelineConfig] = None
    task_templates: Dict[str, TaskTemplateOverride] = Field(default_factory=dict)
    
    # Project metadata
    fps: float = 24.0
    resolution: str = "1920x1080"
    colorspace: str = "ACES"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    """Model for updating an existing project."""
    project_code: Optional[str] = Field(default=None, min_length=2, max_length=20)
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Pipeline configuration
    pipeline_config: Optional[ProjectPipelineConfig] = None
    task_templates: Optional[Dict[str, TaskTemplateOverride]] = None
    
    # Project metadata
    fps: Optional[float] = None
    resolution: Optional[str] = None
    colorspace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None