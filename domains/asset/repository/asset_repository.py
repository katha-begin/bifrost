"""
Asset repository interface.

This module defines the interface for the asset repository, which is responsible
for persisting and retrieving asset aggregates.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union

from ..model.entities import Asset, AssetVersion
from ..model.aggregates import AssetAggregate
from ..model.value_objects import AssetId, VersionId
from ..model.enums import AssetStatus, AssetType


class AssetRepository(ABC):
    """
    Repository interface for Asset aggregates.
    
    This interface defines the contract for implementing repositories
    that can store and retrieve Asset aggregates.
    """
    
    @abstractmethod
    def save(self, asset_aggregate: AssetAggregate) -> None:
        """
        Save or update an asset aggregate.
        
        Args:
            asset_aggregate: The asset aggregate to save.
            
        Raises:
            RepositoryError: If there's an error saving the aggregate.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, asset_id: AssetId) -> Optional[AssetAggregate]:
        """
        Retrieve an asset aggregate by its ID.
        
        Args:
            asset_id: The unique identifier of the asset.
            
        Returns:
            The asset aggregate if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> List[AssetAggregate]:
        """
        Retrieve asset aggregates by name.
        
        Args:
            name: The name to search for.
            
        Returns:
            A list of matching asset aggregates.
        """
        pass
    
    @abstractmethod
    def search(self, 
              query: str = "", 
              asset_type: Optional[AssetType] = None,
              status: Optional[AssetStatus] = None,
              tags: List[str] = None,
              created_by: str = None,
              limit: int = 100,
              offset: int = 0) -> List[AssetAggregate]:
        """
        Search for assets based on various criteria.
        
        Args:
            query: Text search term for name and description
            asset_type: Filter by asset type
            status: Filter by status
            tags: Filter by tags (list of tag names)
            created_by: Filter by creator
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of matching Asset aggregates
        """
        pass
    
    @abstractmethod
    def delete(self, asset_id: AssetId) -> bool:
        """
        Delete an asset aggregate.
        
        Args:
            asset_id: The unique identifier of the asset to delete.
            
        Returns:
            True if the asset was deleted, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_version(self, version_id: VersionId) -> Optional[AssetVersion]:
        """
        Retrieve a specific asset version.
        
        Args:
            version_id: The unique identifier of the version.
            
        Returns:
            The asset version if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def get_dependencies(self, version_id: VersionId) -> List[VersionId]:
        """
        Get all dependencies for a specific version.
        
        Args:
            version_id: The version to get dependencies for.
            
        Returns:
            List of version IDs that the specified version depends on.
        """
        pass
    
    @abstractmethod
    def get_dependents(self, version_id: VersionId) -> List[VersionId]:
        """
        Get all dependents for a specific version.
        
        Args:
            version_id: The version to get dependents for.
            
        Returns:
            List of version IDs that depend on the specified version.
        """
        pass
    
    @abstractmethod
    def exists(self, asset_id: AssetId) -> bool:
        """
        Check if an asset exists.
        
        Args:
            asset_id: The unique identifier of the asset.
            
        Returns:
            True if the asset exists, False otherwise.
        """
        pass
