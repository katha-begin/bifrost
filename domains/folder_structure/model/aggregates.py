"""
Domain aggregates for the Folder Structure domain.

This module defines aggregates that group entities and enforce consistency boundaries.
Aggregates represent the primary access points for manipulating related entities.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime

from .entities import FolderTemplate, TemplateGroup, StudioMapping
from .value_objects import TemplateVariable
from .enums import EntityType, DataType, TemplateInheritance
from .exceptions import (
    TemplateError, InvalidTemplateError, StudioMappingError
)


class TemplateGroupAggregate:
    """
    Aggregate root for TemplateGroup and its related entities.
    
    This class enforces consistency rules across the TemplateGroup entity
    and its child entities (templates).
    """
    
    def __init__(self, template_group: TemplateGroup):
        """
        Initialize with a TemplateGroup entity.
        
        Args:
            template_group: The TemplateGroup entity to manage
        """
        self._template_group = template_group
        # Track domain events to be published
        self._events = []
        
    @property
    def template_group(self) -> TemplateGroup:
        """Get the underlying TemplateGroup entity."""
        return self._template_group
    
    @property
    def events(self) -> List:
        """Get accumulated domain events."""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear accumulated domain events after publishing."""
        self._events = []
        
    def create_template(
        self,
        name: str,
        template: str,
        description: str = "",
        variables: Optional[Dict[str, TemplateVariable]] = None,
        parent_name: Optional[str] = None,
        inheritance_mode: TemplateInheritance = TemplateInheritance.NONE
    ) -> FolderTemplate:
        """
        Create a new template in this group.
        
        Args:
            name: The name of the template
            template: The template string
            description: Optional description of the template
            variables: Optional dictionary of variables
            parent_name: Optional name of the parent template
            inheritance_mode: How to inherit from the parent
            
        Returns:
            The newly created template
            
        Raises:
            ValueError: If a template with the same name already exists
            KeyError: If the parent template doesn't exist
            InvalidTemplateError: If the template is invalid
        """
        # Check if template name already exists
        if name in self._template_group.templates:
            raise ValueError(f"Template '{name}' already exists in group '{self._template_group.name}'")
        
        # Get parent template if specified
        parent = None
        if parent_name:
            if parent_name not in self._template_group.templates:
                raise KeyError(f"Parent template '{parent_name}' not found in group '{self._template_group.name}'")
            parent = self._template_group.templates[parent_name]
        
        # Create the template
        template_entity = FolderTemplate(
            name=name,
            template=template,
            description=description,
            variables=variables,
            parent=parent,
            inheritance_mode=inheritance_mode
        )
        
        # Validate the template
        try:
            template_entity.validate()
        except InvalidTemplateError as e:
            raise InvalidTemplateError(template, f"Template validation failed: {e}")
        
        # Add template to the group
        self._template_group.add_template(template_entity)
        
        # Record domain event
        from .events import TemplateCreated
        self._events.append(TemplateCreated(
            group_name=self._template_group.name,
            template_name=name
        ))
        
        return template_entity
    
    def update_template(
        self,
        name: str,
        template: Optional[str] = None,
        description: Optional[str] = None,
        variables: Optional[Dict[str, TemplateVariable]] = None,
        parent_name: Optional[str] = None,
        inheritance_mode: Optional[TemplateInheritance] = None
    ) -> FolderTemplate:
        """
        Update an existing template in this group.
        
        Args:
            name: The name of the template to update
            template: Optional new template string
            description: Optional new description
            variables: Optional new dictionary of variables
            parent_name: Optional new parent template name
            inheritance_mode: Optional new inheritance mode
            
        Returns:
            The updated template
            
        Raises:
            KeyError: If the template or parent template doesn't exist
            InvalidTemplateError: If the updated template is invalid
        """
        # Get the template to update
        if name not in self._template_group.templates:
            raise KeyError(f"Template '{name}' not found in group '{self._template_group.name}'")
        
        template_entity = self._template_group.templates[name]
        
        # Update template string if provided
        if template is not None:
            template_entity.raw_template = template
            template_entity.parsed_template = template_entity._parse_template(template)
        
        # Update description if provided
        if description is not None:
            template_entity.description = description
        
        # Update variables if provided
        if variables is not None:
            # Remove existing variables
            template_entity.variables.clear()
            
            # Add new variables
            for var_name, var in variables.items():
                template_entity.add_variable(var)
            
            # Extract required variables from template
            for var_name in template_entity.parsed_template.variables:
                if var_name not in template_entity.variables:
                    # Create a default variable
                    template_entity.add_variable(TemplateVariable(name=var_name))
        
        # Update parent and inheritance mode if provided
        if parent_name is not None:
            if parent_name:
                if parent_name not in self._template_group.templates:
                    raise KeyError(f"Parent template '{parent_name}' not found in group '{self._template_group.name}'")
                parent = self._template_group.templates[parent_name]
            else:
                parent = None
            
            template_entity.parent = parent
        
        if inheritance_mode is not None:
            template_entity.inheritance_mode = inheritance_mode
        
        # Validate the updated template
        try:
            template_entity.validate()
        except InvalidTemplateError as e:
            raise InvalidTemplateError(template_entity.raw_template, f"Template validation failed: {e}")
        
        # Update timestamp
        template_entity.updated_at = datetime.now()
        self._template_group.updated_at = datetime.now()
        
        # Record domain event
        from .events import TemplateUpdated
        self._events.append(TemplateUpdated(
            group_name=self._template_group.name,
            template_name=name
        ))
        
        return template_entity
    
    def delete_template(self, name: str) -> None:
        """
        Delete a template from this group.
        
        Args:
            name: The name of the template to delete
            
        Raises:
            KeyError: If the template doesn't exist
            ValueError: If the template is used as a parent by other templates
        """
        # Check if template exists
        if name not in self._template_group.templates:
            raise KeyError(f"Template '{name}' not found in group '{self._template_group.name}'")
        
        # Check if the template is used as a parent
        for template in self._template_group.templates.values():
            if template.parent and template.parent.name == name:
                raise ValueError(f"Template '{name}' cannot be deleted as it is used as a parent by '{template.name}'")
        
        # Delete template
        self._template_group.remove_template(name)
        
        # Record domain event
        from .events import TemplateDeleted
        self._events.append(TemplateDeleted(
            group_name=self._template_group.name,
            template_name=name
        ))


class StudioMappingAggregate:
    """
    Aggregate root for StudioMapping and its related entities.
    
    This class enforces consistency rules across the StudioMapping entity
    and its child entities (templates).
    """
    
    def __init__(self, studio_mapping: StudioMapping):
        """
        Initialize with a StudioMapping entity.
        
        Args:
            studio_mapping: The StudioMapping entity to manage
        """
        self._studio_mapping = studio_mapping
        # Track domain events to be published
        self._events = []
        
    @property
    def studio_mapping(self) -> StudioMapping:
        """Get the underlying StudioMapping entity."""
        return self._studio_mapping
    
    @property
    def events(self) -> List:
        """Get accumulated domain events."""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear accumulated domain events after publishing."""
        self._events = []
        
    def set_template(
        self,
        entity_type: EntityType,
        data_type: DataType,
        template: FolderTemplate
    ) -> None:
        """
        Set a template for a specific entity and data type.
        
        Args:
            entity_type: The type of entity (ASSET, SHOT, etc.)
            data_type: The type of data (WORK, PUBLISHED, etc.)
            template: The template to set
            
        Raises:
            InvalidTemplateError: If the template is invalid
        """
        # Validate the template
        try:
            template.validate()
        except InvalidTemplateError as e:
            raise InvalidTemplateError(template.raw_template, f"Template validation failed: {e}")
        
        # Set the template
        self._studio_mapping.set_template_for_entity(entity_type, data_type, template)
        
        # Record domain event
        from .events import MappingTemplateSet
        self._events.append(MappingTemplateSet(
            studio_name=self._studio_mapping.name,
            entity_type=entity_type.value,
            data_type=data_type.value
        ))
        
    def validate(self) -> None:
        """
        Validate the studio mapping.
        
        Raises:
            StudioMappingError: If validation fails
        """
        errors = self._studio_mapping.validate()
        if errors:
            error_messages = [f"{name}: {message}" for name, message in errors]
            raise StudioMappingError(
                self._studio_mapping.name,
                f"Validation failed: {', '.join(error_messages)}"
            )
