"""
Folder structure domain models.

This module contains the domain models for the Folder Structure domain.
"""

from .enums import EntityType, DataType
from .value_objects import TemplatePath, TemplateVariable
from .entities import FolderTemplate, TemplateGroup, StudioMapping
from .exceptions import (
    TemplateError, VariableResolutionError, InvalidTemplateError,
    PathResolutionError, ContextError
)

__all__ = [
    'EntityType',
    'DataType',
    'TemplatePath',
    'TemplateVariable',
    'FolderTemplate',
    'TemplateGroup',
    'StudioMapping',
    'TemplateError',
    'VariableResolutionError',
    'InvalidTemplateError',
    'PathResolutionError',
    'ContextError'
]
