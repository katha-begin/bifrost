"""
Enumerations for the Asset domain.

This module defines the various enumeration types used within the Asset domain.
"""

from enum import Enum, auto


class AssetStatus(Enum):
    """Status of an asset in the system."""
    DRAFT = auto()
    IN_PROGRESS = auto()
    REVIEW = auto()
    APPROVED = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()
    DEPRECATED = auto()


class VersionStatus(Enum):
    """Status of an asset version."""
    WORK_IN_PROGRESS = auto()
    REVIEW = auto()
    APPROVED = auto()
    PUBLISHED = auto()
    DEPRECATED = auto()


class AssetType(Enum):
    """Type of asset that defines its purpose and behavior."""
    MODEL = auto()
    TEXTURE = auto()
    SHADER = auto()
    RIG = auto()
    ANIMATION = auto()
    EFFECT = auto()
    SCENE = auto()
    LIGHTING = auto()
    CAMERA = auto()
    AUDIO = auto()
    COMPOSITE = auto()
    OTHER = auto()


class DependencyType(Enum):
    """Type of dependency between assets or versions."""
    REFERENCES = auto()      # Simple reference
    IMPORTS = auto()         # Imports data
    DERIVES_FROM = auto()    # Derived work
    REQUIRES = auto()        # Requires to function
    COMPOSED_OF = auto()     # Contains as component
