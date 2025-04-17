"""
Asset service module initialization.

This module exposes the asset service and factory for use throughout the application.
"""

from .asset_service import AssetService
from .asset_service_factory import create_asset_service, asset_service

__all__ = ['AssetService', 'create_asset_service', 'asset_service']
