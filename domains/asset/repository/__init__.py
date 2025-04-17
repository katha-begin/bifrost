"""
Asset repository module initialization.

This module exposes the asset repository interfaces and implementations.
"""

from .asset_repository import AssetRepository
from .sqlite_asset_repository import SQLiteAssetRepository

__all__ = ['AssetRepository', 'SQLiteAssetRepository']
