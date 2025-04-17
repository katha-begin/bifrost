"""
Exceptions for the Asset domain.

This module defines exceptions that can be raised by the Asset domain.
"""

from typing import Optional
from ..model.value_objects import AssetId, VersionId


class AssetDomainError(Exception):
    """Base exception for all errors in the Asset domain."""
    pass


class AssetNotFoundError(AssetDomainError):
    """Exception raised when an asset is not found."""
    
    def __init__(self, asset_id: AssetId):
        self.asset_id = asset_id
        super().__init__(f"Asset with ID {asset_id} not found.")


class AssetVersionNotFoundError(AssetDomainError):
    """Exception raised when an asset version is not found."""
    
    def __init__(self, asset_id: AssetId, version_id: Optional[VersionId] = None, version_number: Optional[int] = None):
        self.asset_id = asset_id
        self.version_id = version_id
        self.version_number = version_number
        
        if version_id:
            message = f"Version with ID {version_id} not found for asset {asset_id}."
        elif version_number:
            message = f"Version number {version_number} not found for asset {asset_id}."
        else:
            message = f"Version not found for asset {asset_id}."
        
        super().__init__(message)


class AssetStateError(AssetDomainError):
    """Exception raised when an asset is in an invalid state for an operation."""
    pass


class DependencyError(AssetDomainError):
    """Exception raised when there's an issue with asset dependencies."""
    pass


class RepositoryError(AssetDomainError):
    """Exception raised when there's an error with the repository operations."""
    pass
