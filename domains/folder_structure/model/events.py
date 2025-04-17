"""
Domain events for the Folder Structure domain.

This module defines events that represent important occurrences within the Folder Structure domain.
These events can be published and subscribed to by different parts of the system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    occurred_on: datetime = None
    
    def __post_init__(self):
        if self.occurred_on is None:
            self.occurred_on = datetime.now()


@dataclass
class TemplateGroupCreated(DomainEvent):
    """Event raised when a new template group is created."""
    group_name: str
    description: str = ""


@dataclass
class TemplateGroupUpdated(DomainEvent):
    """Event raised when a template group is updated."""
    group_name: str
    description: Optional[str] = None


@dataclass
class TemplateGroupDeleted(DomainEvent):
    """Event raised when a template group is deleted."""
    group_name: str


@dataclass
class TemplateCreated(DomainEvent):
    """Event raised when a new template is created in a group."""
    group_name: str
    template_name: str
    description: str = ""
    parent_name: Optional[str] = None


@dataclass
class TemplateUpdated(DomainEvent):
    """Event raised when a template is updated."""
    group_name: str
    template_name: str
    updated_fields: Optional[Dict[str, Any]] = None


@dataclass
class TemplateDeleted(DomainEvent):
    """Event raised when a template is deleted from a group."""
    group_name: str
    template_name: str


@dataclass
class TemplateVariableAdded(DomainEvent):
    """Event raised when a variable is added to a template."""
    group_name: str
    template_name: str
    variable_name: str
    variable_type: str


@dataclass
class TemplateVariableUpdated(DomainEvent):
    """Event raised when a template variable is updated."""
    group_name: str
    template_name: str
    variable_name: str
    updated_fields: Dict[str, Any]


@dataclass
class TemplateVariableRemoved(DomainEvent):
    """Event raised when a variable is removed from a template."""
    group_name: str
    template_name: str
    variable_name: str


@dataclass
class StudioMappingCreated(DomainEvent):
    """Event raised when a new studio mapping is created."""
    studio_name: str
    description: str = ""


@dataclass
class StudioMappingUpdated(DomainEvent):
    """Event raised when a studio mapping is updated."""
    studio_name: str
    updated_fields: Dict[str, Any]


@dataclass
class StudioMappingDeleted(DomainEvent):
    """Event raised when a studio mapping is deleted."""
    studio_name: str


@dataclass
class MappingTemplateSet(DomainEvent):
    """Event raised when a template is set for a specific entity and data type in a mapping."""
    studio_name: str
    entity_type: str
    data_type: str
    template_name: Optional[str] = None


@dataclass
class PathResolved(DomainEvent):
    """Event raised when a path is successfully resolved."""
    studio_name: str
    entity_type: str
    data_type: str
    entity_name: str
    resolved_path: str
    context: Dict[str, Any]


@dataclass
class PathResolutionFailed(DomainEvent):
    """Event raised when path resolution fails."""
    studio_name: str
    entity_type: str
    data_type: str
    entity_name: str
    reason: str
    context: Dict[str, Any]


@dataclass
class FolderStructureCreated(DomainEvent):
    """Event raised when a folder structure is created on disk."""
    path: str
    created_by: str = ""


@dataclass
class FolderStructureSynchronized(DomainEvent):
    """Event raised when a folder structure is synchronized."""
    source_path: str
    target_path: str
    changes_count: int = 0
