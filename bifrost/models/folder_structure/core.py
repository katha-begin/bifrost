#!/usr/bin/env python
# core.py - Core folder structure models
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class EntityType(Enum):
    """
    Type of production entity.
    
    This enumeration represents the different types of entities that can exist
    in a production pipeline, such as assets, shots, and sequences.
    """
    ASSET = "asset"
    SHOT = "shot"
    SEQUENCE = "sequence"
    EPISODE = "episode"
    SERIES = "series"
    PROJECT = "project"


class DataType(Enum):
    """
    Type of data storage.
    
    This enumeration represents the different categories of data that
    are separated in the production pipeline.
    """
    WORK = "work"           # Work-in-progress data
    PUBLISHED = "published"  # Published, validated data
    CACHE = "cache"          # Temporary, regeneratable data
    RENDER = "render"        # Render output data
    DELIVERABLE = "deliverable"  # Final deliverable data


@dataclass
class FolderTemplate:
    """
    Template for folder path construction.
    
    This class represents a template string that can be formatted with
    variables to create a file path.
    
    Attributes:
        template: A string with placeholders for variables
        variables: A list of variable names used in the template
    """
    template: str
    variables: List[str] = field(default_factory=list)
    
    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        return self.template.format(**kwargs)


@dataclass
class StudioMapping:
    """
    Mapping between different studio folder structures.
    
    This class represents a mapping between different studio folder structures,
    allowing for cross-studio synchronization despite different conventions.
    
    Attributes:
        name: Studio identifier
        asset_published_path: Template for published asset paths
        asset_work_path: Template for work-in-progress asset paths
        shot_published_path: Template for published shot paths
        shot_work_path: Template for work-in-progress shot paths
        render_path: Template for render output paths
        cache_path: Template for cache data paths
        deliverable_path: Template for deliverable paths
    """
    name: str
    asset_published_path: FolderTemplate
    asset_work_path: FolderTemplate
    shot_published_path: FolderTemplate
    shot_work_path: FolderTemplate
    render_path: Optional[FolderTemplate] = None
    cache_path: Optional[FolderTemplate] = None
    deliverable_path: Optional[FolderTemplate] = None
