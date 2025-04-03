"""
Folder structure models for Bifrost.

This module provides data models for representing production folder
structures, including support for episodic content, asset management,
and cross-studio synchronization.
"""

from .core import EntityType, DataType, FolderTemplate, StudioMapping
from .project import Series, Episode, SequenceInfo, ShotInfo
from .workflow import Department, DepartmentDependency, DepartmentOutput, Workflow

__all__ = [
    'EntityType',
    'DataType',
    'FolderTemplate',
    'StudioMapping',
    'Series',
    'Episode',
    'SequenceInfo',
    'ShotInfo',
    'Department',
    'DepartmentDependency',
    'DepartmentOutput',
    'Workflow'
]
