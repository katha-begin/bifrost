"""
YAML implementation of the folder structure repository.

This module provides a YAML-based implementation of the folder structure repository interface.
"""

import os
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Set, Tuple

from ..model.aggregates import TemplateGroupAggregate, StudioMappingAggregate
from ..model.entities import TemplateGroup, StudioMapping, FolderTemplate
from ..model.value_objects import TemplateVariable
from ..model.enums import EntityType, DataType, VariableType, TemplateInheritance
from ..model.exceptions import RepositoryError
from .folder_structure_repository import FolderStructureRepository


# Setup logger
logger = logging.getLogger(__name__)


class YAMLFolderStructureRepository(FolderStructureRepository):
    """
    YAML implementation of the folder structure repository.
    
    This repository uses YAML files to store and retrieve folder structure entities.
    """
    
    def __init__(self, config_dir: str = "config/pipeline"):
        """
        Initialize the YAML folder structure repository.
        
        Args:
            config_dir: Directory where configuration files are stored
        """
        self.config_dir = Path(config_dir)
        self.template_groups_dir = self.config_dir / "templates"
        self.studio_mappings_dir = self.config_dir / "studios"
        
        # Create directories if they don't exist
        self.template_groups_dir.mkdir(parents=True, exist_ok=True)
        self.studio_mappings_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"YAML folder structure repository initialized at {self.config_dir}")
    
    def save_template_group(self, template_group_aggregate: TemplateGroupAggregate) -> None:
        """
        Save or update a template group aggregate in a YAML file.
        
        Args:
            template_group_aggregate: The template group aggregate to save.
            
        Raises:
            RepositoryError: If there's an error saving the aggregate.
        """
        try:
            template_group = template_group_aggregate.template_group
            file_path = self.template_groups_dir / f"{template_group.name}.yaml"
            
            # Create data structure for YAML file
            data = {
                "name": template_group.name,
                "description": template_group.description,
                "created_at": template_group.created_at.isoformat(),
                "updated_at": template_group.updated_at.isoformat(),
                "templates": {}
            }
            
            # Add templates
            for template_name, template in template_group.templates.items():
                template_data = {
                    "template": template.raw_template,
                    "description": template.description,
                    "created_at": template.created_at.isoformat(),
                    "updated_at": template.updated_at.isoformat(),
                    "variables": {},
                    "inheritance": {
                        "mode": template.inheritance_mode.value if template.inheritance_mode else "none",
                        "parent": template.parent.name if template.parent else None
                    }
                }
                
                # Add variables
                for var_name, var in template.variables.items():
                    var_data = {
                        "description": var.description,
                        "type": var.variable_type.value,
                        "required": var.required
                    }
                    
                    if var.default_value is not None:
                        var_data["default_value"] = var.default_value
                        
                    if var.allowed_values:
                        var_data["allowed_values"] = var.allowed_values
                        
                    if var.validation_pattern:
                        var_data["validation_pattern"] = var.validation_pattern
                        
                    template_data["variables"][var_name] = var_data
                
                data["templates"][template_name] = template_data
            
            # Write YAML file
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            logger.info(f"Template group {template_group.name} saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving template group: {e}")
            raise RepositoryError(f"Failed to save template group: {e}")
    
    def get_template_group_by_name(self, group_name: str) -> Optional[TemplateGroupAggregate]:
        """
        Retrieve a template group aggregate by its name from a YAML file.
        
        Args:
            group_name: The name of the template group.
            
        Returns:
            The template group aggregate if found, None otherwise.
        """
        try:
            file_path = self.template_groups_dir / f"{group_name}.yaml"
            if not file_path.exists():
                logger.warning(f"Template group file not found: {file_path}")
                return None
            
            # Read YAML file
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Create template group entity
            template_group = TemplateGroup(
                name=data.get("name", group_name),
                description=data.get("description", ""),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
            )
            
            # Load templates (without parent references first)
            templates = {}
            for template_name, template_data in data.get("templates", {}).items():
                # Create template without parent
                template = FolderTemplate(
                    name=template_name,
                    template=template_data.get("template", ""),
                    description=template_data.get("description", ""),
                    created_at=datetime.fromisoformat(template_data.get("created_at", datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(template_data.get("updated_at", datetime.now().isoformat()))
                )
                
                # Add variables
                for var_name, var_data in template_data.get("variables", {}).items():
                    variable = TemplateVariable(
                        name=var_name,
                        description=var_data.get("description", ""),
                        variable_type=VariableType(var_data.get("type", "string")),
                        required=var_data.get("required", True),
                        default_value=var_data.get("default_value"),
                        allowed_values=var_data.get("allowed_values", []),
                        validation_pattern=var_data.get("validation_pattern")
                    )
                    template.add_variable(variable)
                
                templates[template_name] = template
            
            # Set parent references
            for template_name, template_data in data.get("templates", {}).items():
                inheritance = template_data.get("inheritance", {})
                parent_name = inheritance.get("parent")
                
                if parent_name:
                    if parent_name in templates:
                        templates[template_name].parent = templates[parent_name]
                        templates[template_name].inheritance_mode = TemplateInheritance(
                            inheritance.get("mode", "none")
                        )
                    else:
                        logger.warning(f"Parent template '{parent_name}' not found for '{template_name}'")
            
            # Add templates to group
            for template_name, template in templates.items():
                template_group.templates[template_name] = template
            
            return TemplateGroupAggregate(template_group)
            
        except Exception as e:
            logger.error(f"Error loading template group {group_name}: {e}")
            return None
    
    def list_template_groups(self) -> List[str]:
        """
        List all template group names from YAML files.
        
        Returns:
            A list of template group names.
        """
        try:
            groups = []
            for file_path in self.template_groups_dir.glob("*.yaml"):
                group_name = file_path.stem
                groups.append(group_name)
            return groups
        except Exception as e:
            logger.error(f"Error listing template groups: {e}")
            return []
    
    def delete_template_group(self, group_name: str) -> bool:
        """
        Delete a template group YAML file.
        
        Args:
            group_name: The name of the template group to delete.
            
        Returns:
            True if the template group was deleted, False otherwise.
        """
        try:
            file_path = self.template_groups_dir / f"{group_name}.yaml"
            if not file_path.exists():
                logger.warning(f"Template group file not found: {file_path}")
                return False
            
            # Delete the file
            file_path.unlink()
            logger.info(f"Template group {group_name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting template group {group_name}: {e}")
            return False
    
    def save_studio_mapping(self, studio_mapping_aggregate: StudioMappingAggregate) -> None:
        """
        Save or update a studio mapping aggregate in a YAML file.
        
        Args:
            studio_mapping_aggregate: The studio mapping aggregate to save.
            
        Raises:
            RepositoryError: If there's an error saving the aggregate.
        """
        try:
            studio_mapping = studio_mapping_aggregate.studio_mapping
            file_path = self.studio_mappings_dir / f"{studio_mapping.name}.yaml"
            
            # Create data structure for YAML file
            data = {
                "name": studio_mapping.name,
                "description": studio_mapping.description,
                "created_at": studio_mapping.created_at.isoformat(),
                "updated_at": studio_mapping.updated_at.isoformat(),
                "mappings": {}
            }
            
            # Add mappings
            mapping_data = {}
            
            # Add required mappings
            if studio_mapping.asset_published_path:
                mapping_data["asset_published_path"] = studio_mapping.asset_published_path.raw_template
            
            if studio_mapping.asset_work_path:
                mapping_data["asset_work_path"] = studio_mapping.asset_work_path.raw_template
            
            if studio_mapping.shot_published_path:
                mapping_data["shot_published_path"] = studio_mapping.shot_published_path.raw_template
            
            if studio_mapping.shot_work_path:
                mapping_data["shot_work_path"] = studio_mapping.shot_work_path.raw_template
            
            # Add optional mappings
            if studio_mapping.render_path:
                mapping_data["render_path"] = studio_mapping.render_path.raw_template
            
            if studio_mapping.cache_path:
                mapping_data["cache_path"] = studio_mapping.cache_path.raw_template
            
            if studio_mapping.asset_published_cache_path:
                mapping_data["asset_published_cache_path"] = studio_mapping.asset_published_cache_path.raw_template
            
            if studio_mapping.shot_published_cache_path:
                mapping_data["shot_published_cache_path"] = studio_mapping.shot_published_cache_path.raw_template
            
            if studio_mapping.deliverable_path:
                mapping_data["deliverable_path"] = studio_mapping.deliverable_path.raw_template
            
            data["mappings"] = mapping_data
            
            # Write YAML file
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            logger.info(f"Studio mapping {studio_mapping.name} saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving studio mapping: {e}")
            raise RepositoryError(f"Failed to save studio mapping: {e}")
    
    def get_studio_mapping_by_name(self, studio_name: str) -> Optional[StudioMappingAggregate]:
        """
        Retrieve a studio mapping aggregate by its name from a YAML file.
        
        Args:
            studio_name: The name of the studio mapping.
            
        Returns:
            The studio mapping aggregate if found, None otherwise.
        """
        try:
            file_path = self.studio_mappings_dir / f"{studio_name}.yaml"
            if not file_path.exists():
                logger.warning(f"Studio mapping file not found: {file_path}")
                return None
            
            # Read YAML file
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Create studio mapping entity
            studio_mapping = StudioMapping(
                name=data.get("name", studio_name),
                description=data.get("description", ""),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
            )
            
            # Load mappings
            mappings = data.get("mappings", {})
            
            # Set templates
            if "asset_published_path" in mappings:
                studio_mapping.asset_published_path = FolderTemplate(
                    name="asset_published_path",
                    template=mappings["asset_published_path"]
                )
            
            if "asset_work_path" in mappings:
                studio_mapping.asset_work_path = FolderTemplate(
                    name="asset_work_path",
                    template=mappings["asset_work_path"]
                )
            
            if "shot_published_path" in mappings:
                studio_mapping.shot_published_path = FolderTemplate(
                    name="shot_published_path",
                    template=mappings["shot_published_path"]
                )
            
            if "shot_work_path" in mappings:
                studio_mapping.shot_work_path = FolderTemplate(
                    name="shot_work_path",
                    template=mappings["shot_work_path"]
                )
            
            # Set optional templates
            if "render_path" in mappings:
                studio_mapping.render_path = FolderTemplate(
                    name="render_path",
                    template=mappings["render_path"]
                )
            
            if "cache_path" in mappings:
                studio_mapping.cache_path = FolderTemplate(
                    name="cache_path",
                    template=mappings["cache_path"]
                )
            
            if "asset_published_cache_path" in mappings:
                studio_mapping.asset_published_cache_path = FolderTemplate(
                    name="asset_published_cache_path",
                    template=mappings["asset_published_cache_path"]
                )
            
            if "shot_published_cache_path" in mappings:
                studio_mapping.shot_published_cache_path = FolderTemplate(
                    name="shot_published_cache_path",
                    template=mappings["shot_published_cache_path"]
                )
            
            if "deliverable_path" in mappings:
                studio_mapping.deliverable_path = FolderTemplate(
                    name="deliverable_path",
                    template=mappings["deliverable_path"]
                )
            
            return StudioMappingAggregate(studio_mapping)
            
        except Exception as e:
            logger.error(f"Error loading studio mapping {studio_name}: {e}")
            return None
    
    def list_studio_mappings(self) -> List[str]:
        """
        List all studio mapping names from YAML files.
        
        Returns:
            A list of studio mapping names.
        """
        try:
            mappings = []
            for file_path in self.studio_mappings_dir.glob("*.yaml"):
                mapping_name = file_path.stem
                mappings.append(mapping_name)
            return mappings
        except Exception as e:
            logger.error(f"Error listing studio mappings: {e}")
            return []
    
    def delete_studio_mapping(self, studio_name: str) -> bool:
        """
        Delete a studio mapping YAML file.
        
        Args:
            studio_name: The name of the studio mapping to delete.
            
        Returns:
            True if the studio mapping was deleted, False otherwise.
        """
        try:
            file_path = self.studio_mappings_dir / f"{studio_name}.yaml"
            if not file_path.exists():
                logger.warning(f"Studio mapping file not found: {file_path}")
                return False
            
            # Delete the file
            file_path.unlink()
            logger.info(f"Studio mapping {studio_name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting studio mapping {studio_name}: {e}")
            return False
    
    def get_template(self, group_name: str, template_name: str) -> Optional[FolderTemplate]:
        """
        Retrieve a specific template from a template group.
        
        Args:
            group_name: The name of the template group.
            template_name: The name of the template.
            
        Returns:
            The template if found, None otherwise.
        """
        try:
            # Get the template group
            template_group_aggregate = self.get_template_group_by_name(group_name)
            if not template_group_aggregate:
                logger.warning(f"Template group {group_name} not found")
                return None
            
            # Get the template
            template_group = template_group_aggregate.template_group
            if template_name not in template_group.templates:
                logger.warning(f"Template {template_name} not found in group {group_name}")
                return None
            
            return template_group.templates[template_name]
            
        except Exception as e:
            logger.error(f"Error getting template {template_name} from group {group_name}: {e}")
            return None
    
    def get_template_for_entity(
        self,
        studio_name: str,
        entity_type: EntityType,
        data_type: DataType
    ) -> Optional[FolderTemplate]:
        """
        Get the template for a specific entity and data type in a studio mapping.
        
        Args:
            studio_name: The name of the studio mapping.
            entity_type: The type of entity.
            data_type: The type of data.
            
        Returns:
            The template if found, None otherwise.
        """
        try:
            # Get the studio mapping
            studio_mapping_aggregate = self.get_studio_mapping_by_name(studio_name)
            if not studio_mapping_aggregate:
                logger.warning(f"Studio mapping {studio_name} not found")
                return None
            
            # Get the template
            studio_mapping = studio_mapping_aggregate.studio_mapping
            return studio_mapping.get_template_for_entity(entity_type, data_type)
            
        except Exception as e:
            logger.error(f"Error getting template for {entity_type.value}/{data_type.value} in studio {studio_name}: {e}")
            return None
