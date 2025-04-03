#!/usr/bin/env python
# workflow.py - Workflow definition models
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class DepartmentDependency:
    """
    Dependency between departments.
    
    This class represents a dependency relationship where one department
    requires work from another department to be completed.
    
    Attributes:
        department: The department that is depended upon
        status: The required status of the dependent department's work
        version: Optional specific version required
    """
    department: str
    status: str = "approved"
    version: Optional[str] = None


@dataclass
class DepartmentOutput:
    """
    Output produced by a department.
    
    This class represents the type of output that a department produces,
    including the file formats and storage location.
    
    Attributes:
        type: The type of output (e.g., "model", "animation", etc.)
        format: List of file formats for this output
        location: Path template for where this output is stored
    """
    type: str
    format: List[str]
    location: str


@dataclass
class Department:
    """
    Department in the production pipeline.
    
    This class represents a department in the production pipeline,
    including its dependencies and outputs.
    
    Attributes:
        id: Department identifier
        name: Human-readable name
        requires: List of dependencies on other departments
        produces: List of outputs this department produces
    """
    id: str
    name: str
    requires: List[DepartmentDependency] = field(default_factory=list)
    produces: List[DepartmentOutput] = field(default_factory=list)


@dataclass
class Workflow:
    """
    Workflow definition for a production type.
    
    This class represents a workflow that defines how departments interact
    for different types of assets and shots.
    
    Attributes:
        name: Workflow identifier
        asset_types: Dictionary mapping asset types to department sequences
        shot_types: Dictionary mapping shot types to department sequences
    """
    name: str
    asset_types: Dict[str, Dict[str, List[str]]]
    shot_types: Dict[str, Dict[str, List[str]]]
