"""
Value objects for the Folder Structure domain.

This module defines immutable value objects used within the Folder Structure domain.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from datetime import datetime

from .enums import VariableType, TokenType


@dataclass(frozen=True)
class TemplateVariable:
    """
    Immutable representation of a template variable.
    
    This value object represents a variable that can be used in a folder template.
    """
    name: str
    description: str = ""
    variable_type: VariableType = VariableType.STRING
    required: bool = True
    default_value: Optional[Any] = None
    allowed_values: List[Any] = field(default_factory=list)
    validation_pattern: Optional[str] = None
    
    def __post_init__(self):
        """Validate the variable after initialization."""
        # Check that name is valid
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', self.name):
            raise ValueError(f"Variable name must be uppercase with only letters, numbers, and underscores: {self.name}")
        
        # Validate default value based on type
        if self.default_value is not None:
            self._validate_value(self.default_value)
    
    def _validate_value(self, value: Any) -> bool:
        """
        Validate a value against this variable's constraints.
        
        Args:
            value: The value to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Check against allowed values if specified
        if self.allowed_values and value not in self.allowed_values:
            raise ValueError(f"Value '{value}' not in allowed values for {self.name}: {self.allowed_values}")
        
        # Check against validation pattern if specified
        if self.validation_pattern and isinstance(value, str):
            if not re.match(self.validation_pattern, value):
                raise ValueError(f"Value '{value}' does not match pattern '{self.validation_pattern}' for {self.name}")
        
        # Type-specific validation
        if self.variable_type == VariableType.INTEGER:
            if not isinstance(value, int):
                raise ValueError(f"Value '{value}' is not an integer for {self.name}")
                
        elif self.variable_type == VariableType.DATE:
            if not isinstance(value, (datetime, str)):
                raise ValueError(f"Value '{value}' is not a valid date for {self.name}")
                
        elif self.variable_type == VariableType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(f"Value '{value}' is not a boolean for {self.name}")
                
        elif self.variable_type == VariableType.ENUM:
            if not self.allowed_values:
                raise ValueError(f"Enum variable {self.name} must have allowed_values specified")
            # Already checked against allowed_values above
            
        return True
    
    def validate_value(self, value: Any) -> bool:
        """
        Public method to validate a value against this variable's constraints.
        
        Args:
            value: The value to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        return self._validate_value(value)


@dataclass(frozen=True)
class PathToken:
    """
    Immutable representation of a token in a template path.
    
    This value object represents a token that can appear in a path template,
    such as a literal string or a variable placeholder.
    """
    token_type: TokenType
    content: str
    position: Tuple[int, int] = (0, 0)  # (start, end) position in the template
    
    def __post_init__(self):
        """Validate the token after initialization."""
        # Ensure position is a tuple
        if not isinstance(self.position, tuple) or len(self.position) != 2:
            object.__setattr__(self, 'position', (0, 0))


@dataclass(frozen=True)
class TemplatePath:
    """
    Immutable representation of a parsed template path.
    
    This value object represents a folder template path that has been parsed
    into its component tokens for validation and evaluation.
    """
    raw_template: str
    tokens: List[PathToken] = field(default_factory=list)
    variables: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize the variables set based on tokens."""
        # Extract variable names from variable tokens
        var_names = set()
        for token in self.tokens:
            if token.token_type == TokenType.VARIABLE:
                var_names.add(token.content)
        
        # Update the variables set
        object.__setattr__(self, 'variables', frozenset(var_names))
    
    def contains_variable(self, variable_name: str) -> bool:
        """
        Check if this template contains a specific variable.
        
        Args:
            variable_name: The variable name to check for
            
        Returns:
            True if the variable is used in this template
        """
        return variable_name in self.variables
