"""
Folder structure repository interface.

This module defines the interface for the folder structure repository, which is responsible
for persisting and retrieving folder structure entities.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..model.aggregates import TemplateGroupAggregate, StudioMappingAggregate
from ..model.entities import TemplateGroup, StudioMapping, FolderTemplate
from ..model.enums import EntityType, DataType


class FolderStructureRepository(ABC):
    """
    Repository interface for Folder Structure entities.
    
    This interface defines the contract for implementing repositories
    that can store and retrieve Folder Structure entities.
    """
    
    @abstractmethod
    def save_template_group(self, template_group_aggregate: TemplateGroupAggregate) -> None:
        """
        Save or update a template group aggregate.
        
        Args:
            template_group_aggregate: The template group aggregate to save.
            
        Raises:
            RepositoryError: If there's an error saving the aggregate.
        """
        pass
    
    @abstractmethod
    def get_template_group_by_name(self, group_name: str) -> Optional[TemplateGroupAggregate]:
        """
        Retrieve a template group aggregate by its name.
        
        Args:
            group_name: The name of the template group.
            
        Returns:
            The template group aggregate if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def list_template_groups(self) -> List[str]:
        """
        List all template group names.
        
        Returns:
            A list of template group names.
        """
        pass
    
    @abstractmethod
    def delete_template_group(self, group_name: str) -> bool:
        """
        Delete a template group.
        
        Args:
            group_name: The name of the template group to delete.
            
        Returns:
            True if the template group was deleted, False otherwise.
        """
        pass
    
    @abstractmethod
    def save_studio_mapping(self, studio_mapping_aggregate: StudioMappingAggregate) -> None:
        """
        Save or update a studio mapping aggregate.
        
        Args:
            studio_mapping_aggregate: The studio mapping aggregate to save.
            
        Raises:
            RepositoryError: If there's an error saving the aggregate.
        """
        pass
    
    @abstractmethod
    def get_studio_mapping_by_name(self, studio_name: str) -> Optional[StudioMappingAggregate]:
        """
        Retrieve a studio mapping aggregate by its name.
        
        Args:
            studio_name: The name of the studio mapping.
            
        Returns:
            The studio mapping aggregate if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def list_studio_mappings(self) -> List[str]:
        """
        List all studio mapping names.
        
        Returns:
            A list of studio mapping names.
        """
        pass
    
    @abstractmethod
    def delete_studio_mapping(self, studio_name: str) -> bool:
        """
        Delete a studio mapping.
        
        Args:
            studio_name: The name of the studio mapping to delete.
            
        Returns:
            True if the studio mapping was deleted, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_template(self, group_name: str, template_name: str) -> Optional[FolderTemplate]:
        """
        Retrieve a specific template.
        
        Args:
            group_name: The name of the template group.
            template_name: The name of the template.
            
        Returns:
            The template if found, None otherwise.
        """
        pass
    
    @abstractmethod
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
        pass
