"""
Domain-specific exceptions for the Asset domain.

This module defines custom exceptions that can be raised during domain operations.
"""


class AssetDomainError(Exception):
    """Base exception for all Asset domain errors."""
    pass


class AssetNotFoundError(AssetDomainError):
    """Raised when an asset cannot be found."""
    def __init__(self, asset_id):
        self.asset_id = asset_id
        message = f"Asset with ID {asset_id} not found."
        super().__init__(message)


class AssetVersionNotFoundError(AssetDomainError):
    """Raised when an asset version cannot be found."""
    def __init__(self, asset_id, version_id=None, version_number=None):
        self.asset_id = asset_id
        self.version_id = version_id
        self.version_number = version_number
        
        if version_id and version_number:
            message = f"Version with ID {version_id} (number {version_number}) not found for asset {asset_id}."
        elif version_id:
            message = f"Version with ID {version_id} not found for asset {asset_id}."
        elif version_number:
            message = f"Version number {version_number} not found for asset {asset_id}."
        else:
            message = f"Version not found for asset {asset_id}."
            
        super().__init__(message)


class AssetValidationError(AssetDomainError):
    """Raised when asset data fails validation."""
    pass


class AssetVersionValidationError(AssetDomainError):
    """Raised when asset version data fails validation."""
    pass


class AssetStateError(AssetDomainError):
    """Raised when an operation cannot be performed due to the asset's current state."""
    pass


class AssetVersionStateError(AssetDomainError):
    """Raised when an operation cannot be performed due to the version's current state."""
    pass


class DependencyError(AssetDomainError):
    """Raised when there are issues with asset dependencies."""
    pass


class DuplicateAssetError(AssetDomainError):
    """Raised when attempting to create an asset with a name that already exists."""
    def __init__(self, name):
        self.name = name
        message = f"Asset with name '{name}' already exists."
        super().__init__(message)
