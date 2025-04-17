"""
Factory for creating folder structure service instances.

This module provides a factory function for creating properly
configured folder structure service instances with the appropriate dependencies.
"""

from typing import Optional
from bifrost.core.event_bus import EventBus, InMemoryEventBus
from ..repository.folder_structure_repository import FolderStructureRepository 
from ..repository.yaml_folder_structure_repository import YAMLFolderStructureRepository
from .folder_structure_service import FolderStructureService


def create_folder_structure_service(
    repository: Optional[FolderStructureRepository] = None,
    event_bus: Optional[EventBus] = None
) -> FolderStructureService:
    """
    Create a folder structure service instance with the appropriate dependencies.
    
    Args:
        repository: Optional folder structure repository to use (defaults to YAMLFolderStructureRepository)
        event_bus: Optional event bus to use (defaults to InMemoryEventBus)
        
    Returns:
        Properly configured FolderStructureService instance
    """
    # Create default repository if not provided
    if repository is None:
        repository = YAMLFolderStructureRepository()
    
    # Create default event bus if not provided
    if event_bus is None:
        event_bus = InMemoryEventBus()
    
    # Create and return the service
    return FolderStructureService(repository, event_bus)


# Create a singleton instance for common use
folder_structure_service = create_folder_structure_service()
