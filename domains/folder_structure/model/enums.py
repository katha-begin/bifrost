"""
Enumerations for the Folder Structure domain.

This module defines the various enumeration types used within the Folder Structure domain.
"""

from enum import Enum, auto


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
    WORK = "work"               # Work-in-progress data
    PUBLISHED = "published"      # Published, validated data
    CACHE = "cache"              # Temporary, regeneratable data
    PUBLISHED_CACHE = "published_cache"  # Published, final cache data
    RENDER = "render"            # Render output data
    DELIVERABLE = "deliverable"  # Final deliverable data


class VariableType(Enum):
    """
    Type of template variable.
    
    This enumeration represents the different types of variables that 
    can be used in folder templates.
    """
    STRING = "string"           # Basic string variable
    INTEGER = "integer"         # Integer value
    ENUM = "enum"               # Value from a predefined set
    DATE = "date"               # Date value
    BOOLEAN = "boolean"         # Boolean value
    CONTEXT = "context"         # Value derived from context


class TemplateInheritance(Enum):
    """
    Inheritance mode for templates.
    
    This enumeration represents how a template inherits from its parent.
    """
    NONE = "none"               # No inheritance
    EXTEND = "extend"           # Extend parent template
    OVERRIDE = "override"       # Override parent template


class TokenType(Enum):
    """
    Type of token in a template path.
    
    This enumeration represents the different types of tokens that
    can appear in a template path.
    """
    LITERAL = "literal"         # Literal text
    VARIABLE = "variable"       # Variable placeholder
    EXPRESSION = "expression"   # Expression to evaluate
    CONDITION = "condition"     # Conditional section
