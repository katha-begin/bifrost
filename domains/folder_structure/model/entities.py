"""
Domain entities for the Folder Structure domain.

This module defines the primary entities that make up the Folder Structure domain model,
including their attributes, relationships, and business logic.
"""

import re
import string
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple

from .enums import EntityType, DataType, VariableType, TemplateInheritance, TokenType
from .value_objects import TemplateVariable, TemplatePath, PathToken
from .exceptions import (
    InvalidTemplateError, VariableResolutionError, PathResolutionError,
    TemplateParsingError, ContextError
)


class FolderTemplate:
    """
    Entity representing a template for folder path construction.
    
    This entity represents a template string that can be formatted with variables
    to create a file path, with support for inheritance, conditional sections, 
    and variable validation.
    """
    
    def __init__(
        self,
        name: str,
        template: str,
        description: str = "",
        variables: Optional[Dict[str, TemplateVariable]] = None,
        parent: Optional['FolderTemplate'] = None,
        inheritance_mode: TemplateInheritance = TemplateInheritance.NONE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.raw_template = template
        self.parent = parent
        self.inheritance_mode = inheritance_mode
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        
        # Parse the template
        self.parsed_template = self._parse_template(template)
        
        # Initialize variables dictionary
        self.variables: Dict[str, TemplateVariable] = {}
        
        # Add provided variables
        if variables:
            for var_name, var in variables.items():
                self.add_variable(var)
        
        # Extract required variables from template if not provided
        for var_name in self.parsed_template.variables:
            if var_name not in self.variables:
                # Create a default variable
                self.add_variable(TemplateVariable(name=var_name))
    
    def _parse_template(self, template: str) -> TemplatePath:
        """
        Parse a template string into a TemplatePath object.
        
        Args:
            template: The template string to parse
            
        Returns:
            A TemplatePath object with the parsed tokens
            
        Raises:
            TemplateParsingError: If the template cannot be parsed
        """
        tokens = []
        current_pos = 0
        remaining = template
        
        # Simple regex to find variable placeholders
        pattern = r'{([A-Z_][A-Z0-9_]*)}'
        
        while remaining:
            # Find the next variable placeholder
            match = re.search(pattern, remaining)
            
            if not match:
                # No more variables, add the rest as a literal token
                if remaining:
                    token = PathToken(
                        token_type=TokenType.LITERAL,
                        content=remaining,
                        position=(current_pos, current_pos + len(remaining))
                    )
                    tokens.append(token)
                break
            
            # Add the text before the variable as a literal token
            if match.start() > 0:
                literal = remaining[:match.start()]
                token = PathToken(
                    token_type=TokenType.LITERAL,
                    content=literal,
                    position=(current_pos, current_pos + len(literal))
                )
                tokens.append(token)
                current_pos += len(literal)
            
            # Add the variable as a variable token
            var_name = match.group(1)
            var_token = PathToken(
                token_type=TokenType.VARIABLE,
                content=var_name,
                position=(current_pos + match.start(), current_pos + match.end())
            )
            tokens.append(var_token)
            
            # Update positions
            current_pos += match.end()
            remaining = remaining[match.end():]
        
        return TemplatePath(
            raw_template=template,
            tokens=tokens
        )
    
    def add_variable(self, variable: TemplateVariable) -> None:
        """
        Add a variable to this template.
        
        Args:
            variable: The variable to add
            
        Raises:
            ValueError: If a variable with the same name already exists
        """
        if variable.name in self.variables:
            raise ValueError(f"Variable '{variable.name}' already exists in template '{self.name}'")
        
        self.variables[variable.name] = variable
        self.updated_at = datetime.now()
    
    def remove_variable(self, variable_name: str) -> None:
        """
        Remove a variable from this template.
        
        Args:
            variable_name: The name of the variable to remove
            
        Raises:
            ValueError: If the variable is used in the template
            KeyError: If the variable doesn't exist
        """
        if variable_name not in self.variables:
            raise KeyError(f"Variable '{variable_name}' not found in template '{self.name}'")
        
        if self.parsed_template.contains_variable(variable_name):
            raise ValueError(f"Cannot remove variable '{variable_name}' as it is used in template '{self.name}'")
        
        del self.variables[variable_name]
        self.updated_at = datetime.now()
    
    def update_variable(self, variable: TemplateVariable) -> None:
        """
        Update a variable in this template.
        
        Args:
            variable: The updated variable
            
        Raises:
            KeyError: If the variable doesn't exist
        """
        if variable.name not in self.variables:
            raise KeyError(f"Variable '{variable.name}' not found in template '{self.name}'")
        
        self.variables[variable.name] = variable
        self.updated_at = datetime.now()
    
    def validate(self) -> bool:
        """
        Validate the template structure and variables.
        
        Returns:
            True if valid, raises exceptions otherwise
            
        Raises:
            InvalidTemplateError: If the template is invalid
        """
        # Check for missing required variables
        for var_name in self.parsed_template.variables:
            if var_name not in self.variables:
                raise InvalidTemplateError(
                    self.raw_template,
                    f"Variable '{var_name}' is used but not defined"
                )
        
        # No validation errors found
        return True
    
    def format(self, **kwargs) -> str:
        """
        Format the template with provided variables.
        
        Args:
            **kwargs: Variable values to use for formatting
            
        Returns:
            Formatted path string
            
        Raises:
            VariableResolutionError: If a required variable is missing
            ValueError: If a variable value is invalid
        """
        # Check for missing required variables
        for var_name, var in self.variables.items():
            if var.required and var_name not in kwargs and var.default_value is None:
                raise VariableResolutionError(var_name, self.raw_template)
        
        # Apply default values for missing variables
        format_args = {}
        for var_name, var in self.variables.items():
            if var_name in kwargs:
                # Validate the provided value
                try:
                    var.validate_value(kwargs[var_name])
                    format_args[var_name] = kwargs[var_name]
                except ValueError as e:
                    raise ValueError(f"Invalid value for '{var_name}': {e}")
            elif var.default_value is not None:
                format_args[var_name] = var.default_value
        
        # Add any additional variables not defined in the template
        for var_name, value in kwargs.items():
            if var_name not in format_args:
                format_args[var_name] = value
        
        # Format the template using the arguments
        try:
            # Use string.Formatter to identify missing keys first
            required_keys = set()
            for _, arg_name, _, _ in string.Formatter().parse(self.raw_template):
                if arg_name is not None:
                    required_keys.add(arg_name)
            
            # Check for missing keys
            missing_keys = required_keys - set(format_args.keys())
            if missing_keys:
                raise VariableResolutionError(
                    next(iter(missing_keys)),
                    self.raw_template
                )
                
            path = self.raw_template.format(**format_args)
            return path
        except KeyError as e:
            var_name = str(e).strip("'")
            raise VariableResolutionError(var_name, self.raw_template)
        except Exception as e:
            raise InvalidTemplateError(self.raw_template, str(e))
    
    def get_effective_template(self) -> str:
        """
        Get the effective template string, considering inheritance.
        
        Returns:
            The effective template string after inheritance is applied
        """
        if not self.parent or self.inheritance_mode == TemplateInheritance.NONE:
            return self.raw_template
            
        if self.inheritance_mode == TemplateInheritance.OVERRIDE:
            return self.raw_template
            
        if self.inheritance_mode == TemplateInheritance.EXTEND:
            parent_template = self.parent.get_effective_template()
            return f"{parent_template}/{self.raw_template}"
            
        # Default to using this template's raw value
        return self.raw_template


class TemplateGroup:
    """
    Entity representing a group of related templates.
    
    This entity represents a collection of templates that are related to each other,
    such as all templates for a specific studio or project.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        templates: Optional[Dict[str, FolderTemplate]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.templates: Dict[str, FolderTemplate] = templates or {}
    
    def add_template(self, template: FolderTemplate) -> None:
        """
        Add a template to this group.
        
        Args:
            template: The template to add
            
        Raises:
            ValueError: If a template with the same name already exists
        """
        if template.name in self.templates:
            raise ValueError(f"Template '{template.name}' already exists in group '{self.name}'")
        
        self.templates[template.name] = template
        self.updated_at = datetime.now()
    
    def remove_template(self, template_name: str) -> None:
        """
        Remove a template from this group.
        
        Args:
            template_name: The name of the template to remove
            
        Raises:
            KeyError: If the template doesn't exist
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found in group '{self.name}'")
        
        del self.templates[template_name]
        self.updated_at = datetime.now()
    
    def get_template(self, template_name: str) -> FolderTemplate:
        """
        Get a template by name.
        
        Args:
            template_name: The name of the template to get
            
        Returns:
            The template
            
        Raises:
            KeyError: If the template doesn't exist
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found in group '{self.name}'")
        
        return self.templates[template_name]
    
    def validate_all(self) -> List[Tuple[str, str]]:
        """
        Validate all templates in this group.
        
        Returns:
            List of (template_name, error_message) tuples for invalid templates
        """
        errors = []
        for name, template in self.templates.items():
            try:
                template.validate()
            except InvalidTemplateError as e:
                errors.append((name, str(e)))
        
        return errors


class StudioMapping:
    """
    Entity representing a mapping between different studio folder structures.
    
    This entity represents a mapping between different studio folder structures,
    allowing for cross-studio synchronization despite different conventions.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        asset_published_path: Optional[FolderTemplate] = None,
        asset_work_path: Optional[FolderTemplate] = None,
        shot_published_path: Optional[FolderTemplate] = None,
        shot_work_path: Optional[FolderTemplate] = None,
        render_path: Optional[FolderTemplate] = None,
        cache_path: Optional[FolderTemplate] = None,
        asset_published_cache_path: Optional[FolderTemplate] = None,
        shot_published_cache_path: Optional[FolderTemplate] = None,
        deliverable_path: Optional[FolderTemplate] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.asset_published_path = asset_published_path
        self.asset_work_path = asset_work_path
        self.shot_published_path = shot_published_path
        self.shot_work_path = shot_work_path
        self.render_path = render_path
        self.cache_path = cache_path
        self.asset_published_cache_path = asset_published_cache_path
        self.shot_published_cache_path = shot_published_cache_path
        self.deliverable_path = deliverable_path
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
    
    def get_template_for_entity(
        self,
        entity_type: EntityType,
        data_type: DataType
    ) -> Optional[FolderTemplate]:
        """
        Get the template for a specific entity and data type.
        
        Args:
            entity_type: The type of entity (ASSET, SHOT, etc.)
            data_type: The type of data (WORK, PUBLISHED, etc.)
            
        Returns:
            The template or None if not defined
        """
        if entity_type == EntityType.ASSET:
            if data_type == DataType.PUBLISHED:
                return self.asset_published_path
            elif data_type == DataType.WORK:
                return self.asset_work_path
            elif data_type == DataType.RENDER:
                return self.render_path
            elif data_type == DataType.CACHE:
                return self.cache_path
            elif data_type == DataType.PUBLISHED_CACHE:
                return self.asset_published_cache_path
            elif data_type == DataType.DELIVERABLE:
                return self.deliverable_path
        elif entity_type == EntityType.SHOT:
            if data_type == DataType.PUBLISHED:
                return self.shot_published_path
            elif data_type == DataType.WORK:
                return self.shot_work_path
            elif data_type == DataType.RENDER:
                return self.render_path
            elif data_type == DataType.CACHE:
                return self.cache_path
            elif data_type == DataType.PUBLISHED_CACHE:
                return self.shot_published_cache_path
            elif data_type == DataType.DELIVERABLE:
                return self.deliverable_path
        
        return None
    
    def set_template_for_entity(
        self,
        entity_type: EntityType,
        data_type: DataType,
        template: FolderTemplate
    ) -> None:
        """
        Set the template for a specific entity and data type.
        
        Args:
            entity_type: The type of entity (ASSET, SHOT, etc.)
            data_type: The type of data (WORK, PUBLISHED, etc.)
            template: The template to set
        """
        if entity_type == EntityType.ASSET:
            if data_type == DataType.PUBLISHED:
                self.asset_published_path = template
            elif data_type == DataType.WORK:
                self.asset_work_path = template
            elif data_type == DataType.RENDER:
                self.render_path = template
            elif data_type == DataType.CACHE:
                self.cache_path = template
            elif data_type == DataType.PUBLISHED_CACHE:
                self.asset_published_cache_path = template
            elif data_type == DataType.DELIVERABLE:
                self.deliverable_path = template
        elif entity_type == EntityType.SHOT:
            if data_type == DataType.PUBLISHED:
                self.shot_published_path = template
            elif data_type == DataType.WORK:
                self.shot_work_path = template
            elif data_type == DataType.RENDER:
                self.render_path = template
            elif data_type == DataType.CACHE:
                self.cache_path = template
            elif data_type == DataType.PUBLISHED_CACHE:
                self.shot_published_cache_path = template
            elif data_type == DataType.DELIVERABLE:
                self.deliverable_path = template
        
        self.updated_at = datetime.now()
    
    def validate(self) -> List[Tuple[str, str]]:
        """
        Validate all templates in this mapping.
        
        Returns:
            List of (template_name, error_message) tuples for invalid templates
        """
        errors = []
        
        # Required templates
        if not self.asset_published_path:
            errors.append(("asset_published_path", "Template is required but not defined"))
        if not self.asset_work_path:
            errors.append(("asset_work_path", "Template is required but not defined"))
        if not self.shot_published_path:
            errors.append(("shot_published_path", "Template is required but not defined"))
        if not self.shot_work_path:
            errors.append(("shot_work_path", "Template is required but not defined"))
        
        # Validate defined templates
        templates = [
            ("asset_published_path", self.asset_published_path),
            ("asset_work_path", self.asset_work_path),
            ("shot_published_path", self.shot_published_path),
            ("shot_work_path", self.shot_work_path),
            ("render_path", self.render_path),
            ("cache_path", self.cache_path),
            ("asset_published_cache_path", self.asset_published_cache_path),
            ("shot_published_cache_path", self.shot_published_cache_path),
            ("deliverable_path", self.deliverable_path)
        ]
        
        for name, template in templates:
            if template:
                try:
                    template.validate()
                except InvalidTemplateError as e:
                    errors.append((name, str(e)))
        
        return errors
