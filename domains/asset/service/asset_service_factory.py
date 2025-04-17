"""
Factory for creating asset service instances.

This module provides a factory function for creating properly
configured asset service instances with the appropriate dependencies.
"""

from typing import Optional
from bifrost.core.event_bus import EventBus, InMemoryEventBus
from ..repository.asset_repository import AssetRepository 
from ..repository.sqlite_asset_repository import SQLiteAssetRepository
from .asset_service import AssetService


def create_asset_service(
    repository: Optional[AssetRepository] = None,
    event_bus: Optional[EventBus] = None
) -> AssetService:
    """
    Create an asset service instance with the appropriate dependencies.
    
    Args:
        repository: Optional asset repository to use (defaults to SQLiteAssetRepository)
        event_bus: Optional event bus to use (defaults to InMemoryEventBus)
        
    Returns:
        Properly configured AssetService instance
    """
    # Create default repository if not provided
    if repository is None:
        repository = SQLiteAssetRepository()
    
    # Create default event bus if not provided
    if event_bus is None:
        event_bus = InMemoryEventBus()
    
    # Create and return the service
    return AssetService(repository, event_bus)


# Create a singleton instance for common use
asset_service = create_asset_service()
