"""
Folder structure service module initialization.

This module exposes the folder structure service and factory for use throughout the application.
"""

from .folder_structure_service import FolderStructureService
from .folder_structure_service_factory import create_folder_structure_service, folder_structure_service

__all__ = ['FolderStructureService', 'create_folder_structure_service', 'folder_structure_service']
