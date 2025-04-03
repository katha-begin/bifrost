#!/usr/bin/env python
# uri_mapper.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from pathlib import Path
from typing import Optional, Union
import re
import logging

from ...core.config import get_config
from ...models.asset import Asset

logger = logging.getLogger(__name__)

class AssetUriMapper:
    """
    Maps between Bifrost assets and OpenAssetIO URIs.
    
    This class provides utilities for converting between Bifrost asset IDs
    and OpenAssetIO URI strings, as well as detecting URIs in file paths.
    """
    
    @staticmethod
    def asset_to_uri(asset: Asset) -> str:
        """
        Convert an asset to a URI.
        
        Args:
            asset: A Bifrost asset
            
        Returns:
            URI string in the form "bifrost:///assets/{asset_id}"
        """
        uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        return f"{uri_scheme}:///assets/{asset.id}"
        
    @staticmethod
    def uri_to_asset_id(uri: str) -> Optional[str]:
        """
        Extract asset ID from a URI.
        
        Args:
            uri: An OpenAssetIO URI string
            
        Returns:
            Asset ID extracted from the URI, or None if invalid
        """
        uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        prefix = f"{uri_scheme}:///assets/"
        
        if not uri.startswith(prefix):
            return None
            
        asset_id = uri[len(prefix):]
        
        # Handle any additional path components or query params by taking just the first part
        if '/' in asset_id:
            asset_id = asset_id.split('/')[0]
        if '?' in asset_id:
            asset_id = asset_id.split('?')[0]
            
        return asset_id
        
    @staticmethod
    def path_to_uri(path: Union[str, Path]) -> Optional[str]:
        """
        Convert a file path to a URI if it matches Bifrost's patterns.
        
        Args:
            path: A file path that might belong to a Bifrost asset
            
        Returns:
            URI string if the path matches patterns, or None
        """
        path = Path(path)
        
        # Convert the path to string parts for analysis
        parts = path.parts
        
        # Get the URI scheme
        uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        
        # Try to find 'assets' in the path
        if 'assets' not in parts:
            return None
            
        assets_idx = parts.index('assets')
        
        # Check if there are enough parts after 'assets'
        if len(parts) <= assets_idx + 1:
            return None
            
        # The part after 'assets' should be the asset ID
        asset_id = parts[assets_idx + 1]
        
        # Basic validation for asset ID format (this will depend on your ID format)
        # For example, if using UUIDs:
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        if len(asset_id) == 36 and uuid_pattern.match(asset_id):
            return f"{uri_scheme}:///assets/{asset_id}"
            
        # Alternative formats - if your asset IDs follow different patterns
        # For example, if using custom identifiers:
        if asset_id.startswith('asset_'):
            return f"{uri_scheme}:///assets/{asset_id}"
            
        return None
        
    @staticmethod
    def uri_to_path(uri: str, version: Optional[int] = None) -> Optional[Path]:
        """
        Convert a URI to a file path.
        
        Args:
            uri: An OpenAssetIO URI string
            version: Optional specific version to target
            
        Returns:
            Path to the asset's file, or None if not found
        """
        # Extract the asset ID from the URI
        asset_id = AssetUriMapper.uri_to_asset_id(uri)
        if not asset_id:
            return None
            
        # Get the storage root from configuration
        storage_root = get_config("storage.local.root_path", "data/assets")
        
        # Construct path to the asset directory
        asset_dir = Path(storage_root) / asset_id
        
        # If version is specified, find that specific version
        if version is not None:
            version_dir = asset_dir / f"v{version:03d}"
            
            # Find a file in this directory (could be any file type)
            if version_dir.exists():
                for file in version_dir.iterdir():
                    if file.is_file():
                        return file
        
        # Otherwise, find the latest version by directory name pattern
        version_dirs = []
        if asset_dir.exists():
            for dir_path in asset_dir.iterdir():
                if dir_path.is_dir() and dir_path.name.startswith('v'):
                    try:
                        # Extract version number from directory name
                        version_num = int(dir_path.name[1:])
                        version_dirs.append((version_num, dir_path))
                    except ValueError:
                        # Not a version directory
                        pass
        
        # Find the highest version
        if version_dirs:
            latest_version, latest_dir = max(version_dirs, key=lambda x: x[0])
            
            # Find a file in this directory (could be any file type)
            for file in latest_dir.iterdir():
                if file.is_file():
                    return file
        
        return None
    
    @staticmethod
    def detect_uri_in_string(text: str) -> Optional[str]:
        """
        Detect if a string contains a Bifrost URI.
        
        Args:
            text: Text that might contain a URI
            
        Returns:
            The detected URI or None
        """
        uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        pattern = re.compile(f"{uri_scheme}:///assets/[^\\s/]+")
        
        match = pattern.search(text)
        if match:
            return match.group(0)
            
        return None
    
    @staticmethod
    def is_valid_uri(uri: str) -> bool:
        """
        Check if a string is a valid Bifrost URI.
        
        Args:
            uri: The URI string to check
            
        Returns:
            True if valid, False otherwise
        """
        uri_scheme = get_config("assetio.uri_scheme", "bifrost")
        pattern = re.compile(f"^{uri_scheme}:///assets/[^\\s/]+$")
        
        return bool(pattern.match(uri))
