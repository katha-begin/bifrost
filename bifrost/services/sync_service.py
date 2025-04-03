# bifrost/services/sync_service.py
from pathlib import Path
import shutil
import json
import os
from typing import Dict, List, Optional, Union, Any

from ..core.config import get_config
from ..models.folder_structure import EntityType, DataType
from .folder_service import FolderService

class SyncService:
    """
    Service for synchronizing assets and shots between studios with different folder structures.
    """
    
    def __init__(self):
        """Initialize the sync service."""
        self.folder_service = FolderService()
        
    def sync_published_asset(self,
                           asset_name: str,
                           asset_type: str,
                           version: str,
                           source_studio: str,
                           target_studio: str,
                           department: Optional[str] = None) -> bool:
        """
        Synchronize a published asset between studios.
        
        Args:
            asset_name: Name of the asset
            asset_type: Type of asset
            version: Version to sync
            source_studio: Source studio name
            target_studio: Target studio name
            department: Optional department filter
            
        Returns:
            True if successful, False otherwise
        """
        # Get source and target studio mappings
        source_mapping = self.folder_service.studio_mappings.get(source_studio)
        target_mapping = self.folder_service.studio_mappings.get(target_studio)
        
        if not source_mapping or not target_mapping:
            print(f"Studio mapping not found: {source_studio} or {target_studio}")
            return False
        
        # Configure folder service for source studio
        self.folder_service.studio_name = source_studio
        
        # Get source path
        source_path = self.folder_service.get_path(
            entity_type=EntityType.ASSET,
            data_type=DataType.PUBLISHED,
            entity_name=asset_name,
            asset_type=asset_type,
            version=version,
            department=department
        )
        
        # Configure folder service for target studio
        self.folder_service.studio_name = target_studio
        
        # Get target path
        target_path = self.folder_service.get_path(
            entity_type=EntityType.ASSET,
            data_type=DataType.PUBLISHED,
            entity_name=asset_name,
            asset_type=asset_type,
            version=version,
            department=department
        )
        
        # Ensure target directory exists
        Path(target_path).mkdir(parents=True, exist_ok=True)
        
        # Copy files
        return self._sync_files(source_path, target_path)
    
    def sync_published_shot(self,
                          shot_id: str,
                          sequence_id: str,
                          version: str,
                          source_studio: str,
                          target_studio: str,
                          department: Optional[str] = None,
                          series: Optional[str] = None,
                          episode: Optional[str] = None) -> bool:
        """
        Synchronize a published shot between studios.
        
        Args:
            shot_id: Shot identifier
            sequence_id: Sequence identifier
            version: Version to sync
            source_studio: Source studio name
            target_studio: Target studio name
            department: Optional department filter
            series: Series identifier (for episodic)
            episode: Episode identifier (for episodic)
            
        Returns:
            True if successful, False otherwise
        """
        # Get source and target studio mappings
        source_mapping = self.folder_service.studio_mappings.get(source_studio)
        target_mapping = self.folder_service.studio_mappings.get(target_studio)
        
        if not source_mapping or not target_mapping:
            print(f"Studio mapping not found: {source_studio} or {target_studio}")
            return False
        
        # Configure folder service for source studio
        self.folder_service.studio_name = source_studio
        
        # Get source path
        source_path = self.folder_service.get_path(
            entity_type=EntityType.SHOT,
            data_type=DataType.PUBLISHED,
            entity_name=shot_id,
            sequence=sequence_id,
            version=version,
            department=department,
            series=series,
            episode=episode
        )
        
        # Configure folder service for target studio
        self.folder_service.studio_name = target_studio
        
        # Get target path
        target_path = self.folder_service.get_path(
            entity_type=EntityType.SHOT,
            data_type=DataType.PUBLISHED,
            entity_name=shot_id,
            sequence=sequence_id,
            version=version,
            department=department,
            series=series,
            episode=episode
        )
        
        # Ensure target directory exists
        Path(target_path).mkdir(parents=True, exist_ok=True)
        
        # Copy files
        return self._sync_files(source_path, target_path)

    def _sync_files(self, source_path: str, target_path: str) -> bool:
        """
        Synchronize files from the source path to the target path.

        Args:
            source_path: Path to the source directory or file.
            target_path: Path to the target directory or file.

        Returns:
            True if synchronization is successful, False otherwise.
        """
        try:
            if not Path(source_path).exists():
                print(f"Source path does not exist: {source_path}")
                return False

            if Path(source_path).is_dir():
                # Copy directory
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                # Copy single file
                shutil.copy2(source_path, target_path)

            print(f"Files synchronized from {source_path} to {target_path}")
            return True
        except Exception as e:
            print(f"Error synchronizing files: {e}")
            return False