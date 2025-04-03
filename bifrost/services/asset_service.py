#!/usr/bin/env python
# asset_service.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.database import db
from ..models.asset import Asset, AssetDependency, AssetStatus, AssetTag, AssetType, AssetVersion

# Setup logger
logger = logging.getLogger(__name__)


class AssetService:
    """
    Service for managing assets in the Bifrost system.
    
    This service provides methods for creating, retrieving, updating, and
    deleting assets, as well as managing asset versions and dependencies.
    """
    
    def create_asset(self, 
                    name: str,
                    asset_type: Union[AssetType, str],
                    description: str = "",
                    status: Union[AssetStatus, str] = AssetStatus.CONCEPT,
                    created_by: str = "",
                    thumbnail_path: Optional[Union[str, Path]] = None,
                    preview_path: Optional[Union[str, Path]] = None,
                    metadata: Optional[Dict] = None) -> Asset:
        """
        Create a new asset in the system.
        
        Args:
            name: The name of the asset
            asset_type: The type of asset (can be AssetType enum or string)
            description: Optional description of the asset
            status: Status of the asset (default: CONCEPT)
            created_by: Username of the creator
            thumbnail_path: Optional path to a thumbnail image
            preview_path: Optional path to a preview file
            metadata: Optional additional metadata
            
        Returns:
            The newly created Asset object
        """
        # Convert string type to enum if needed
        if isinstance(asset_type, str):
            try:
                asset_type = AssetType(asset_type)
            except ValueError:
                asset_type = AssetType.OTHER
                logger.warning(f"Invalid asset type '{asset_type}', using OTHER instead")
                
        # Convert string status to enum if needed
        if isinstance(status, str):
            try:
                status = AssetStatus(status)
            except ValueError:
                status = AssetStatus.CONCEPT
                logger.warning(f"Invalid asset status '{status}', using CONCEPT instead")
        
        # Generate a unique ID
        asset_id = str(uuid.uuid4())
        
        # Create the timestamp
        now = datetime.now()
        
        # Convert paths to strings for storage if they're Path objects
        thumbnail_path_str = str(thumbnail_path) if thumbnail_path else None
        preview_path_str = str(preview_path) if preview_path else None
        
        # Prepare asset data for database
        asset_data = {
            'id': asset_id,
            'name': name,
            'asset_type': asset_type.value,
            'description': description,
            'status': status.value,
            'created_at': now,
            'created_by': created_by,
            'modified_at': now,
            'modified_by': created_by,
            'thumbnail_path': thumbnail_path_str,
            'preview_path': preview_path_str,
            'metadata': db.serialize_json(metadata or {})
        }
        
        # Insert into database
        db.insert('assets', asset_data)
        
        # Create and return Asset object
        return Asset(
            id=asset_id,
            name=name,
            asset_type=asset_type,
            description=description,
            status=status,
            created_at=now,
            created_by=created_by,
            modified_at=now,
            modified_by=created_by,
            thumbnail_path=thumbnail_path,
            preview_path=preview_path,
            metadata=metadata or {},
            tags=[],
            versions=[],
            dependencies=[],
            dependents=[]
        )
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """
        Retrieve an asset by its ID.
        
        Args:
            asset_id: The unique ID of the asset
            
        Returns:
            The Asset object or None if not found
        """
        # Get asset data from database
        asset_data = db.get_by_id('assets', asset_id)
        if not asset_data:
            logger.warning(f"Asset with ID {asset_id} not found")
            return None
            
        # Get associated tags
        tags_query = "SELECT * FROM asset_tags WHERE asset_id = ?"
        tags_data = db.execute(tags_query, (asset_id,))
        
        # Get associated versions
        versions_query = "SELECT * FROM asset_versions WHERE asset_id = ? ORDER BY version_number"
        versions_data = db.execute(versions_query, (asset_id,))
        
        # Get dependencies
        dependencies_query = """
            SELECT * FROM asset_dependencies 
            WHERE asset_id = ?
        """
        dependencies_data = db.execute(dependencies_query, (asset_id,))
        
        # Get dependents
        dependents_query = """
            SELECT * FROM asset_dependencies 
            WHERE dependent_asset_id = ?
        """
        dependents_data = db.execute(dependents_query, (asset_id,))
        
        # Convert data to model objects
        tags = [
            AssetTag(
                name=tag['name'],
                color=tag['color'],
                description=tag['description'] or ""
            )
            for tag in tags_data
        ]
        
        versions = [
            AssetVersion(
                version_number=version['version_number'],
                created_at=version['created_at'],
                created_by=version['created_by'] or "",
                comment=version['comment'] or "",
                file_path=version['file_path'],
                status=AssetStatus(version['status']),
                metadata=db.deserialize_json(version['metadata']) or {}
            )
            for version in versions_data
        ]
        
        dependencies = [
            AssetDependency(
                dependent_asset_id=dep['dependent_asset_id'],
                dependency_type=dep['dependency_type'],
                optional=bool(dep['optional'])
            )
            for dep in dependencies_data
        ]
        
        dependents = [
            AssetDependency(
                dependent_asset_id=dep['asset_id'],
                dependency_type=dep['dependency_type'],
                optional=bool(dep['optional'])
            )
            for dep in dependents_data
        ]
        
        # Create asset object
        try:
            asset_type = AssetType(asset_data['asset_type'])
        except ValueError:
            asset_type = AssetType.OTHER
            
        try:
            asset_status = AssetStatus(asset_data['status'])
        except ValueError:
            asset_status = AssetStatus.CONCEPT
        
        asset = Asset(
            id=asset_data['id'],
            name=asset_data['name'],
            asset_type=asset_type,
            description=asset_data['description'] or "",
            status=asset_status,
            created_at=asset_data['created_at'],
            created_by=asset_data['created_by'] or "",
            modified_at=asset_data['modified_at'],
            modified_by=asset_data['modified_by'] or "",
            thumbnail_path=asset_data['thumbnail_path'],
            preview_path=asset_data['preview_path'],
            metadata=db.deserialize_json(asset_data['metadata']) or {},
            tags=tags,
            versions=versions,
            dependencies=dependencies,
            dependents=dependents
        )
        
        return asset
    
    def update_asset(self, asset: Asset) -> bool:
        """
        Update an existing asset in the database.
        
        Args:
            asset: The Asset object with updated values
            
        Returns:
            True if the update was successful, False otherwise
        """
        # Check if asset exists
        existing_asset = db.get_by_id('assets', asset.id)
        if not existing_asset:
            logger.warning(f"Cannot update asset with ID {asset.id} - not found")
            return False
        
        # Update the modified timestamp
        asset.modified_at = datetime.now()
        
        # Prepare asset data for update
        asset_data = {
            'name': asset.name,
            'asset_type': asset.asset_type.value,
            'description': asset.description,
            'status': asset.status.value,
            'modified_at': asset.modified_at,
            'modified_by': asset.modified_by,
            'thumbnail_path': str(asset.thumbnail_path) if asset.thumbnail_path else None,
            'preview_path': str(asset.preview_path) if asset.preview_path else None,
            'metadata': db.serialize_json(asset.metadata)
        }
        
        # Update in database
        db.update('assets', asset.id, asset_data)
        
        # Process tags (delete all and recreate)
        db.execute("DELETE FROM asset_tags WHERE asset_id = ?", (asset.id,))
        for tag in asset.tags:
            tag_data = {
                'id': str(uuid.uuid4()),
                'asset_id': asset.id,
                'name': tag.name,
                'color': tag.color,
                'description': tag.description
            }
            db.insert('asset_tags', tag_data)
        
        return True
    
    def delete_asset(self, asset_id: str) -> bool:
        """
        Delete an asset from the database.
        
        Args:
            asset_id: The ID of the asset to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        # Check if asset exists
        existing_asset = db.get_by_id('assets', asset_id)
        if not existing_asset:
            logger.warning(f"Cannot delete asset with ID {asset_id} - not found")
            return False
        
        # Delete the asset
        db.delete('assets', asset_id)
        return True
    
    def add_version(self, 
                    asset_id: str, 
                    version_number: Optional[int] = None,
                    file_path: Optional[Union[str, Path]] = None,
                    comment: str = "",
                    status: Union[AssetStatus, str] = AssetStatus.IN_PROGRESS,
                    created_by: str = "",
                    metadata: Dict = None) -> Optional[AssetVersion]:
        """
        Add a new version to an existing asset.
        
        Args:
            asset_id: The ID of the asset to add a version to
            version_number: Optional version number (auto-incremented if not provided)
            file_path: Path to the version file
            comment: Comment describing the version changes
            status: Status of the version
            created_by: Username of the creator
            metadata: Additional metadata for this version
            
        Returns:
            The created AssetVersion object or None if the asset doesn't exist
        """
        # Check if asset exists
        asset = self.get_asset(asset_id)
        if not asset:
            logger.warning(f"Cannot add version to asset with ID {asset_id} - not found")
            return None
        
        # Convert string status to enum if needed
        if isinstance(status, str):
            try:
                status = AssetStatus(status)
            except ValueError:
                status = AssetStatus.IN_PROGRESS
                logger.warning(f"Invalid asset status '{status}', using IN_PROGRESS instead")
        
        # Determine version number if not provided
        if version_number is None:
            if asset.versions:
                version_number = max(v.version_number for v in asset.versions) + 1
            else:
                version_number = 1
                
        # Create timestamp
        now = datetime.now()
        
        # Convert file path to string for storage if it's a Path object
        file_path_str = str(file_path) if file_path else None
        
        # Create version record
        version_id = str(uuid.uuid4())
        version_data = {
            'id': version_id,
            'asset_id': asset_id,
            'version_number': version_number,
            'created_at': now,
            'created_by': created_by,
            'comment': comment,
            'file_path': file_path_str,
            'status': status.value,
            'metadata': db.serialize_json(metadata or {})
        }
        
        # Insert into database
        db.insert('asset_versions', version_data)
        
        # Update asset's modified timestamp
        db.update('assets', asset_id, {
            'modified_at': now,
            'modified_by': created_by
        })
        
        # Create and return version object
        version = AssetVersion(
            version_number=version_number,
            created_at=now,
            created_by=created_by,
            comment=comment,
            file_path=file_path,
            status=status,
            metadata=metadata or {}
        )
        
        return version
    
    def add_dependency(self, 
                      asset_id: str, 
                      dependent_asset_id: str,
                      dependency_type: str = "reference",
                      optional: bool = False) -> bool:
        """
        Add a dependency between two assets.
        
        Args:
            asset_id: ID of the asset that will have a dependency
            dependent_asset_id: ID of the asset being depended on
            dependency_type: Type of dependency (reference, import, etc.)
            optional: Whether this dependency is optional
            
        Returns:
            True if successful, False otherwise
        """
        # Check if both assets exist
        if not db.get_by_id('assets', asset_id):
            logger.warning(f"Cannot add dependency - asset with ID {asset_id} not found")
            return False
            
        if not db.get_by_id('assets', dependent_asset_id):
            logger.warning(f"Cannot add dependency - dependent asset with ID {dependent_asset_id} not found")
            return False
        
        # Check if dependency already exists
        check_query = """
            SELECT * FROM asset_dependencies 
            WHERE asset_id = ? AND dependent_asset_id = ?
        """
        existing = db.execute(check_query, (asset_id, dependent_asset_id))
        if existing:
            logger.info(f"Dependency already exists between {asset_id} and {dependent_asset_id}")
            return True
        
        # Create dependency record
        dependency_id = str(uuid.uuid4())
        dependency_data = {
            'id': dependency_id,
            'asset_id': asset_id,
            'dependent_asset_id': dependent_asset_id,
            'dependency_type': dependency_type,
            'optional': optional
        }
        
        # Insert into database
        db.insert('asset_dependencies', dependency_data)
        
        # Update asset's modified timestamp
        now = datetime.now()
        db.update('assets', asset_id, {
            'modified_at': now
        })
        
        return True
    
    def remove_dependency(self, asset_id: str, dependent_asset_id: str) -> bool:
        """
        Remove a dependency between two assets.
        
        Args:
            asset_id: ID of the asset that has the dependency
            dependent_asset_id: ID of the asset being depended on
            
        Returns:
            True if successful, False otherwise
        """
        # Delete the dependency
        delete_query = """
            DELETE FROM asset_dependencies 
            WHERE asset_id = ? AND dependent_asset_id = ?
        """
        db.execute(delete_query, (asset_id, dependent_asset_id))
        
        # Update asset's modified timestamp
        now = datetime.now()
        db.update('assets', asset_id, {
            'modified_at': now
        })
        
        return True
    
    def search_assets(self, 
                     query: str = "", 
                     asset_type: Optional[Union[AssetType, str]] = None,
                     status: Optional[Union[AssetStatus, str]] = None,
                     tags: List[str] = None,
                     created_by: str = None,
                     limit: int = 100,
                     offset: int = 0) -> List[Asset]:
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
            List of matching Asset objects
        """
        # Build query conditions
        conditions = []
        params = []
        
        if query:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if asset_type:
            if isinstance(asset_type, AssetType):
                asset_type = asset_type.value
            conditions.append("asset_type = ?")
            params.append(asset_type)
        
        if status:
            if isinstance(status, AssetStatus):
                status = status.value
            conditions.append("status = ?")
            params.append(status)
        
        if created_by:
            conditions.append("created_by = ?")
            params.append(created_by)
        
        # Build the SQL query
        sql = "SELECT * FROM assets"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        if limit:
            sql += f" LIMIT {limit}"
            
        if offset:
            sql += f" OFFSET {offset}"
        
        # Execute the query
        asset_data_list = db.execute(sql, tuple(params))
        
        # Handle tag filtering as a post-process step
        results = []
        for asset_data in asset_data_list:
            asset_id = asset_data['id']
            
            # If tag filtering is enabled, check tags
            if tags:
                tags_query = """
                    SELECT name FROM asset_tags 
                    WHERE asset_id = ?
                """
                asset_tags = db.execute(tags_query, (asset_id,))
                asset_tag_names = {tag['name'] for tag in asset_tags}
                
                # Skip if the asset doesn't have all required tags
                if not all(tag in asset_tag_names for tag in tags):
                    continue
            
            # Get full asset with all associations
            asset = self.get_asset(asset_id)
            if asset:
                results.append(asset)
        
        return results


# Create a singleton instance
asset_service = AssetService()
