"""
Folder structure service for the Folder Structure domain.

This module provides services for managing folder structures in the Bifrost system,
implementing the application layer functionality for the Folder Structure domain.
"""

import os
import logging
import re
import string
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from ..model.aggregates import TemplateGroupAggregate, StudioMappingAggregate
from ..model.entities import TemplateGroup, StudioMapping, FolderTemplate
from ..model.value_objects import TemplateVariable
from ..model.enums import EntityType, DataType, VariableType, TemplateInheritance
from ..model.exceptions import (
    TemplateError, InvalidTemplateError, VariableResolutionError,
    PathResolutionError, ContextError, StudioMappingError, RepositoryError
)
from ..repository.folder_structure_repository import FolderStructureRepository
from bifrost.core.event_bus import EventBus
from bifrost.core.config import get_config

# Setup logger
logger = logging.getLogger(__name__)


class FolderStructureService:
    """
    Service for managing folder structures in the Bifrost system.
    
    This service provides methods for creating, retrieving, and manipulating
    folder structure templates and studio mappings, as well as resolving paths
    and creating folder structures on disk.
    """
    
    def __init__(self, repository: FolderStructureRepository, event_bus: EventBus):
        """
        Initialize the folder structure service.
        
        Args:
            repository: The folder structure repository to use.
            event_bus: The event bus for publishing domain events.
        """
        self._repository = repository
        self._event_bus = event_bus
        
        # Load configurations
        self.project_root = get_config("project.root_path", "")
        self.studio_name = get_config("project.studio_name", "main_studio")
        
        logger.info(f"Folder structure service initialized with project root: {self.project_root}")
    
    # Template Group Methods
    
    def create_template_group(self, name: str, description: str = "") -> str:
        """
        Create a new template group.
        
        Args:
            name: The name of the template group
            description: Optional description of the template group
            
        Returns:
            The name of the newly created template group
            
        Raises:
            ValueError: If a template group with the same name already exists
            RepositoryError: If there's an error saving the template group
        """
        try:
            # Check if template group already exists
            existing_group = self._repository.get_template_group_by_name(name)
            if existing_group:
                raise ValueError(f"Template group '{name}' already exists")
            
            # Create template group entity
            template_group = TemplateGroup(
                name=name,
                description=description
            )
            
            # Create aggregate
            aggregate = TemplateGroupAggregate(template_group)
            
            # Save to repository
            self._repository.save_template_group(aggregate)
            
            # Publish domain events
            from ..model.events import TemplateGroupCreated
            self._event_bus.publish(TemplateGroupCreated(
                group_name=name,
                description=description
            ))
            
            return name
            
        except RepositoryError as e:
            logger.error(f"Error creating template group: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating template group: {e}")
            raise RepositoryError(f"Failed to create template group: {e}")
    
    def get_template_group(self, name: str) -> TemplateGroup:
        """
        Retrieve a template group by its name.
        
        Args:
            name: The name of the template group
            
        Returns:
            The template group
            
        Raises:
            ValueError: If the template group doesn't exist
        """
        aggregate = self._repository.get_template_group_by_name(name)
        if not aggregate:
            raise ValueError(f"Template group '{name}' not found")
        
        return aggregate.template_group
    
    def list_template_groups(self) -> List[str]:
        """
        List all template group names.
        
        Returns:
            A list of template group names
        """
        return self._repository.list_template_groups()
    
    def delete_template_group(self, name: str) -> None:
        """
        Delete a template group.
        
        Args:
            name: The name of the template group to delete
            
        Raises:
            ValueError: If the template group doesn't exist
            RepositoryError: If there's an error deleting the template group
        """
        # Check if template group exists
        aggregate = self._repository.get_template_group_by_name(name)
        if not aggregate:
            raise ValueError(f"Template group '{name}' not found")
        
        # Delete from repository
        success = self._repository.delete_template_group(name)
        if not success:
            raise RepositoryError(f"Failed to delete template group '{name}'")
        
        # Publish domain event
        from ..model.events import TemplateGroupDeleted
        self._event_bus.publish(TemplateGroupDeleted(
            group_name=name
        ))
    
    # Template Methods
    
    def create_template(
        self,
        group_name: str,
        template_name: str,
        template_string: str,
        description: str = "",
        variables: Optional[Dict[str, Dict[str, Any]]] = None,
        parent_name: Optional[str] = None,
        inheritance_mode: str = "none"
    ) -> FolderTemplate:
        """
        Create a new template in a template group.
        
        Args:
            group_name: The name of the template group
            template_name: The name of the new template
            template_string: The template string
            description: Optional description of the template
            variables: Optional dictionary of variables with their properties
            parent_name: Optional name of the parent template
            inheritance_mode: How to inherit from the parent ("none", "extend", "override")
            
        Returns:
            The newly created template
            
        Raises:
            ValueError: If the template group doesn't exist or the template name already exists
            InvalidTemplateError: If the template is invalid
            RepositoryError: If there's an error saving the template
        """
        try:
            # Get the template group
            aggregate = self._repository.get_template_group_by_name(group_name)
            if not aggregate:
                raise ValueError(f"Template group '{group_name}' not found")
            
            # Convert variables dictionary to TemplateVariable objects
            template_variables = None
            if variables:
                template_variables = {}
                for var_name, var_props in variables.items():
                    variable = TemplateVariable(
                        name=var_name,
                        description=var_props.get("description", ""),
                        variable_type=VariableType(var_props.get("type", "string")),
                        required=var_props.get("required", True),
                        default_value=var_props.get("default_value"),
                        allowed_values=var_props.get("allowed_values", []),
                        validation_pattern=var_props.get("validation_pattern")
                    )
                    template_variables[var_name] = variable
            
            # Convert inheritance mode string to enum
            inheritance_enum = TemplateInheritance(inheritance_mode)
            
            # Create the template through the aggregate
            template = aggregate.create_template(
                name=template_name,
                template=template_string,
                description=description,
                variables=template_variables,
                parent_name=parent_name,
                inheritance_mode=inheritance_enum
            )
            
            # Save the updated aggregate
            self._repository.save_template_group(aggregate)
            
            # Publish domain events
            for event in aggregate.events:
                self._event_bus.publish(event)
            
            # Clear events after publishing
            aggregate.clear_events()
            
            return template
            
        except (ValueError, InvalidTemplateError) as e:
            logger.error(f"Error creating template: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise RepositoryError(f"Failed to create template: {e}")
    
    def update_template(
        self,
        group_name: str,
        template_name: str,
        template_string: Optional[str] = None,
        description: Optional[str] = None,
        variables: Optional[Dict[str, Dict[str, Any]]] = None,
        parent_name: Optional[str] = None,
        inheritance_mode: Optional[str] = None
    ) -> FolderTemplate:
        """
        Update an existing template in a template group.
        
        Args:
            group_name: The name of the template group
            template_name: The name of the template to update
            template_string: Optional new template string
            description: Optional new description
            variables: Optional new dictionary of variables
            parent_name: Optional new parent template name
            inheritance_mode: Optional new inheritance mode
            
        Returns:
            The updated template
            
        Raises:
            ValueError: If the template group or template doesn't exist
            InvalidTemplateError: If the updated template is invalid
            RepositoryError: If there's an error saving the template
        """
        try:
            # Get the template group
            aggregate = self._repository.get_template_group_by_name(group_name)
            if not aggregate:
                raise ValueError(f"Template group '{group_name}' not found")
            
            # Convert variables dictionary to TemplateVariable objects
            template_variables = None
            if variables:
                template_variables = {}
                for var_name, var_props in variables.items():
                    variable = TemplateVariable(
                        name=var_name,
                        description=var_props.get("description", ""),
                        variable_type=VariableType(var_props.get("type", "string")),
                        required=var_props.get("required", True),
                        default_value=var_props.get("default_value"),
                        allowed_values=var_props.get("allowed_values", []),
                        validation_pattern=var_props.get("validation_pattern")
                    )
                    template_variables[var_name] = variable
            
            # Convert inheritance mode string to enum if provided
            inheritance_enum = None
            if inheritance_mode:
                inheritance_enum = TemplateInheritance(inheritance_mode)
            
            # Update the template through the aggregate
            template = aggregate.update_template(
                name=template_name,
                template=template_string,
                description=description,
                variables=template_variables,
                parent_name=parent_name,
                inheritance_mode=inheritance_enum
            )
            
            # Save the updated aggregate
            self._repository.save_template_group(aggregate)
            
            # Publish domain events
            for event in aggregate.events:
                self._event_bus.publish(event)
            
            # Clear events after publishing
            aggregate.clear_events()
            
            return template
            
        except (ValueError, InvalidTemplateError) as e:
            logger.error(f"Error updating template: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            raise RepositoryError(f"Failed to update template: {e}")
    
    def delete_template(self, group_name: str, template_name: str) -> None:
        """
        Delete a template from a template group.
        
        Args:
            group_name: The name of the template group
            template_name: The name of the template to delete
            
        Raises:
            ValueError: If the template group or template doesn't exist
            RepositoryError: If there's an error saving the template group
        """
        try:
            # Get the template group
            aggregate = self._repository.get_template_group_by_name(group_name)
            if not aggregate:
                raise ValueError(f"Template group '{group_name}' not found")
            
            # Delete the template through the aggregate
            aggregate.delete_template(template_name)
            
            # Save the updated aggregate
            self._repository.save_template_group(aggregate)
            
            # Publish domain events
            for event in aggregate.events:
                self._event_bus.publish(event)
            
            # Clear events after publishing
            aggregate.clear_events()
            
        except ValueError as e:
            logger.error(f"Error deleting template: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            raise RepositoryError(f"Failed to delete template: {e}")
    
    def get_template(self, group_name: str, template_name: str) -> FolderTemplate:
        """
        Retrieve a template from a template group.
        
        Args:
            group_name: The name of the template group
            template_name: The name of the template
            
        Returns:
            The template
            
        Raises:
            ValueError: If the template group or template doesn't exist
        """
        template = self._repository.get_template(group_name, template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found in group '{group_name}'")
        
        return template
    
    # Studio Mapping Methods
    
    def create_studio_mapping(self, name: str, description: str = "") -> str:
        """
        Create a new studio mapping.
        
        Args:
            name: The name of the studio mapping
            description: Optional description of the studio mapping
            
        Returns:
            The name of the newly created studio mapping
            
        Raises:
            ValueError: If a studio mapping with the same name already exists
            RepositoryError: If there's an error saving the studio mapping
        """
        try:
            # Check if studio mapping already exists
            existing_mapping = self._repository.get_studio_mapping_by_name(name)
            if existing_mapping:
                raise ValueError(f"Studio mapping '{name}' already exists")
            
            # Create studio mapping entity
            studio_mapping = StudioMapping(
                name=name,
                description=description
            )
            
            # Create aggregate
            aggregate = StudioMappingAggregate(studio_mapping)
            
            # Save to repository
            self._repository.save_studio_mapping(aggregate)
            
            # Publish domain events
            from ..model.events import StudioMappingCreated
            self._event_bus.publish(StudioMappingCreated(
                studio_name=name,
                description=description
            ))
            
            return name
            
        except RepositoryError as e:
            logger.error(f"Error creating studio mapping: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating studio mapping: {e}")
            raise RepositoryError(f"Failed to create studio mapping: {e}")
    
    def get_studio_mapping(self, name: str) -> StudioMapping:
        """
        Retrieve a studio mapping by its name.
        
        Args:
            name: The name of the studio mapping
            
        Returns:
            The studio mapping
            
        Raises:
            ValueError: If the studio mapping doesn't exist
        """
        aggregate = self._repository.get_studio_mapping_by_name(name)
        if not aggregate:
            raise ValueError(f"Studio mapping '{name}' not found")
        
        return aggregate.studio_mapping
    
    def list_studio_mappings(self) -> List[str]:
        """
        List all studio mapping names.
        
        Returns:
            A list of studio mapping names
        """
        return self._repository.list_studio_mappings()
    
    def delete_studio_mapping(self, name: str) -> None:
        """
        Delete a studio mapping.
        
        Args:
            name: The name of the studio mapping to delete
            
        Raises:
            ValueError: If the studio mapping doesn't exist
            RepositoryError: If there's an error deleting the studio mapping
        """
        # Check if studio mapping exists
        aggregate = self._repository.get_studio_mapping_by_name(name)
        if not aggregate:
            raise ValueError(f"Studio mapping '{name}' not found")
        
        # Delete from repository
        success = self._repository.delete_studio_mapping(name)
        if not success:
            raise RepositoryError(f"Failed to delete studio mapping '{name}'")
        
        # Publish domain event
        from ..model.events import StudioMappingDeleted
        self._event_bus.publish(StudioMappingDeleted(
            studio_name=name
        ))
    
    def set_mapping_template(
        self,
        studio_name: str,
        entity_type: EntityType,
        data_type: DataType,
        template_string: str
    ) -> None:
        """
        Set a template for a specific entity and data type in a studio mapping.
        
        Args:
            studio_name: The name of the studio mapping
            entity_type: The type of entity
            data_type: The type of data
            template_string: The template string
            
        Raises:
            ValueError: If the studio mapping doesn't exist
            InvalidTemplateError: If the template is invalid
            RepositoryError: If there's an error saving the studio mapping
        """
        try:
            # Get the studio mapping
            aggregate = self._repository.get_studio_mapping_by_name(studio_name)
            if not aggregate:
                raise ValueError(f"Studio mapping '{studio_name}' not found")
            
            # Create template entity
            template = FolderTemplate(
                name=f"{entity_type.value}_{data_type.value}",
                template=template_string
            )
            
            # Set the template through the aggregate
            aggregate.set_template(entity_type, data_type, template)
            
            # Save the updated aggregate
            self._repository.save_studio_mapping(aggregate)
            
            # Publish domain events
            for event in aggregate.events:
                self._event_bus.publish(event)
            
            # Clear events after publishing
            aggregate.clear_events()
            
        except (ValueError, InvalidTemplateError) as e:
            logger.error(f"Error setting mapping template: {e}")
            raise
        except Exception as e:
            logger.error(f"Error setting mapping template: {e}")
            raise RepositoryError(f"Failed to set mapping template: {e}")
    
    # Path Resolution Methods
    
    def get_path(
        self, 
        entity_type: EntityType, 
        data_type: DataType, 
        entity_name: str, 
        studio_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get a path based on entity and data type.
        
        This method generates a file path according to the configured folder
        structure for the specified entity and data type.
        
        Args:
            entity_type: Type of entity (ASSET, SHOT, etc.)
            data_type: Type of data (WORK, PUBLISHED, etc.)
            entity_name: Name of the entity
            studio_name: Name of the studio mapping to use (default: from config)
            **kwargs: Additional path variables
            
        Returns:
            Formatted path string
            
        Raises:
            PathResolutionError: If the path cannot be resolved
        """
        try:
            # Use provided studio name or default from config
            studio = studio_name or self.studio_name
            
            # Get the template
            template = self._repository.get_template_for_entity(studio, entity_type, data_type)
            if not template:
                raise PathResolutionError(
                    entity_type.value,
                    data_type.value,
                    f"No template defined for {entity_type.value}/{data_type.value} in studio '{studio}'"
                )
            
            # Create format dictionary with common variables
            format_args = {
                'PROJECT': self.project_root,
                'ENTITY_NAME': entity_name,
                **kwargs
            }
            
            # Format the template
            path = template.format(**format_args)
            
            # Publish domain event
            from ..model.events import PathResolved
            self._event_bus.publish(PathResolved(
                studio_name=studio,
                entity_type=entity_type.value,
                data_type=data_type.value,
                entity_name=entity_name,
                resolved_path=path,
                context=format_args
            ))
            
            return path
            
        except VariableResolutionError as e:
            # Wrap in PathResolutionError for consistent error handling
            raise PathResolutionError(
                entity_type.value,
                data_type.value,
                f"Missing variable: {e}"
            )
        except Exception as e:
            logger.error(f"Error resolving path: {e}")
            raise PathResolutionError(
                entity_type.value,
                data_type.value,
                str(e)
            )
    
    def create_folder_structure(self, path: str) -> bool:
        """
        Create the folder structure for a given path.
        
        Args:
            path: Path to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created folder structure: {path}")
            
            # Publish domain event
            from ..model.events import FolderStructureCreated
            self._event_bus.publish(FolderStructureCreated(
                path=path
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error creating folder structure: {e}")
            return False
    
    def convert_path_between_studios(
        self, 
        path: str, 
        source_studio: str, 
        target_studio: str
    ) -> str:
        """
        Convert a path from one studio's format to another.
        
        Args:
            path: Path to convert
            source_studio: Source studio name
            target_studio: Target studio name
            
        Returns:
            Converted path
            
        Raises:
            ValueError: If either studio mapping doesn't exist
            PathResolutionError: If the path cannot be converted
        """
        try:
            # Get the studio mappings
            source_aggregate = self._repository.get_studio_mapping_by_name(source_studio)
            if not source_aggregate:
                raise ValueError(f"Source studio mapping '{source_studio}' not found")
            
            target_aggregate = self._repository.get_studio_mapping_by_name(target_studio)
            if not target_aggregate:
                raise ValueError(f"Target studio mapping '{target_studio}' not found")
            
            source_mapping = source_aggregate.studio_mapping
            target_mapping = target_aggregate.studio_mapping
            
            # Analyze the path to determine entity type, data type, and variables
            path_info = self._analyze_path(path, source_mapping)
            if not path_info:
                raise PathResolutionError(
                    "unknown",
                    "unknown",
                    f"Cannot analyze path '{path}' for conversion"
                )
            
            entity_type, data_type, variables = path_info
            
            # Get the target template
            target_template = target_mapping.get_template_for_entity(entity_type, data_type)
            if not target_template:
                raise PathResolutionError(
                    entity_type.value,
                    data_type.value,
                    f"No template defined for {entity_type.value}/{data_type.value} in studio '{target_studio}'"
                )
            
            # Format the target template with extracted variables
            converted_path = target_template.format(**variables)
            
            # Publish domain event
            from ..model.events import FolderStructureSynchronized
            self._event_bus.publish(FolderStructureSynchronized(
                source_path=path,
                target_path=converted_path
            ))
            
            return converted_path
            
        except (ValueError, PathResolutionError) as e:
            logger.error(f"Error converting path: {e}")
            raise
        except Exception as e:
            logger.error(f"Error converting path: {e}")
            raise PathResolutionError(
                "unknown",
                "unknown",
                f"Failed to convert path: {e}"
            )
    
    def _analyze_path(
        self, 
        path: str, 
        studio_mapping: StudioMapping
    ) -> Optional[Tuple[EntityType, DataType, Dict[str, str]]]:
        """
        Analyze a path to determine its entity type, data type, and variables.
        
        Args:
            path: Path to analyze
            studio_mapping: Studio mapping to use for analysis
            
        Returns:
            Tuple of (entity_type, data_type, variables) if successful, None otherwise
        """
        # Define the mappings to check
        mappings = [
            (EntityType.ASSET, DataType.PUBLISHED, studio_mapping.asset_published_path),
            (EntityType.ASSET, DataType.WORK, studio_mapping.asset_work_path),
            (EntityType.SHOT, DataType.PUBLISHED, studio_mapping.shot_published_path),
            (EntityType.SHOT, DataType.WORK, studio_mapping.shot_work_path)
        ]
        
        # Add optional mappings if defined
        if studio_mapping.render_path:
            # Check for both asset and shot
            mappings.append((EntityType.ASSET, DataType.RENDER, studio_mapping.render_path))
            mappings.append((EntityType.SHOT, DataType.RENDER, studio_mapping.render_path))
        
        if studio_mapping.cache_path:
            # Check for both asset and shot
            mappings.append((EntityType.ASSET, DataType.CACHE, studio_mapping.cache_path))
            mappings.append((EntityType.SHOT, DataType.CACHE, studio_mapping.cache_path))
        
        if studio_mapping.asset_published_cache_path:
            mappings.append((EntityType.ASSET, DataType.PUBLISHED_CACHE, studio_mapping.asset_published_cache_path))
        
        if studio_mapping.shot_published_cache_path:
            mappings.append((EntityType.SHOT, DataType.PUBLISHED_CACHE, studio_mapping.shot_published_cache_path))
        
        if studio_mapping.deliverable_path:
            # Check for both asset and shot
            mappings.append((EntityType.ASSET, DataType.DELIVERABLE, studio_mapping.deliverable_path))
            mappings.append((EntityType.SHOT, DataType.DELIVERABLE, studio_mapping.deliverable_path))
        
        # Check each mapping
        for entity_type, data_type, template in mappings:
            if not template:
                continue
            
            variables = self._match_template(path, template.raw_template)
            if variables:
                return entity_type, data_type, variables
        
        return None
    
    def _match_template(self, path: str, template: str) -> Optional[Dict[str, str]]:
        """
        Match a path against a template and extract variables.
        
        Args:
            path: Path to match
            template: Template string to match against
            
        Returns:
            Dictionary of extracted variables if match is successful, None otherwise
        """
        # Convert template to regex pattern
        pattern = self._template_to_regex(template)
        
        # Match against pattern
        match = re.fullmatch(pattern, path)
        if match:
            return match.groupdict()
        
        return None
    
    def _template_to_regex(self, template: str) -> str:
        """
        Convert a template string with {VARIABLE} format to a regex pattern.
        
        Args:
            template: Template string with variables
            
        Returns:
            Regex pattern string
        """
        # Escape regex special characters
        pattern = re.escape(template)
        
        # Replace escaped braces with regex capture groups
        # e.g., \{VARIABLE\} -> (?P<VARIABLE>[^/]+)
        pattern = re.sub(r'\\{([A-Z_][A-Z0-9_]*)\\}', r'(?P<\1>[^/]+)', pattern)
        
        return pattern
