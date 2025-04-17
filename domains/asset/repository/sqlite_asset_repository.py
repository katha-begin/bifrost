"""
SQLite implementation of the asset repository.

This module provides a SQLite-based implementation of the asset repository interface.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Set, Tuple

from bifrost.core.database import db
from .asset_repository import AssetRepository
from ..model.aggregates import AssetAggregate
from ..model.entities import Asset, AssetVersion, AssetDependency
from ..model.value_objects import (
    AssetId, VersionId, DependencyId, AssetMetadata, FilePath,
    generate_asset_id, generate_version_id, generate_dependency_id
)
from ..model.enums import AssetStatus, VersionStatus, AssetType, DependencyType
from ..model.exceptions import (
    AssetNotFoundError, VersionNotFoundError, RepositoryError
)

# Setup logger
logger = logging.getLogger(__name__)


class SQLiteAssetRepository(AssetRepository):
    """
    SQLite implementation of the asset repository.
    
    This repository uses an SQLite database to store and retrieve asset aggregates.
    """
    
    def save(self, asset_aggregate: AssetAggregate) -> None:
        """
        Save or update an asset aggregate in the SQLite database.
        
        Args:
            asset_aggregate: The asset aggregate to save.
            
        Raises:
            RepositoryError: If there's an error saving the aggregate.
        """
        asset = asset_aggregate.asset
        
        try:
            # Start a transaction
            db.begin_transaction()
            
            # Check if this is a new asset or an update
            existing_asset = db.get_by_id('assets', str(asset.id))
            is_new = existing_asset is None
            
            # Prepare asset data for database
            asset_data = {
                'name': asset.name,
                'asset_type': asset.asset_type.value,
                'description': asset.metadata.description,
                'status': asset.status.value,
                'modified_at': datetime.now(),
                'metadata': json.dumps(asset.metadata.properties or {})
            }
            
            if is_new:
                # Add creation data for new assets
                asset_data.update({
                    'id': str(asset.id),
                    'created_at': asset.created_at,
                    'created_by': '',  # This should be populated from context
                    'modified_by': ''  # This should be populated from context
                })
                db.insert('assets', asset_data)
            else:
                # Update existing asset
                db.update('assets', str(asset.id), asset_data)
            
            # Handle versions
            self._save_versions(asset)
            
            # Commit the transaction
            db.commit_transaction()
            
            # Clear events after successful save
            asset_aggregate.clear_events()
            
        except Exception as e:
            # Rollback the transaction on error
            db.rollback_transaction()
            logger.error(f"Error saving asset aggregate: {e}")
            raise RepositoryError(f"Failed to save asset: {e}")
    
    def _save_versions(self, asset: Asset) -> None:
        """
        Save all versions of an asset.
        
        Args:
            asset: The asset whose versions should be saved.
        """
        # Get existing versions
        versions_query = "SELECT id, version_number FROM asset_versions WHERE asset_id = ?"
        existing_versions = db.execute(versions_query, (str(asset.id),))
        existing_version_map = {v['version_number']: v['id'] for v in existing_versions}
        
        # Process each version
        for version in asset.versions:
            version_id = str(version.id)
            
            # Prepare version data
            version_data = {
                'asset_id': str(asset.id),
                'version_number': version.version_number,
                'status': version.status.value,
                'comment': version.comment,
                'created_at': version.created_at,
                'updated_at': version.updated_at,
                'file_path': str(version.file_path) if version.file_path else None,
                'metadata': json.dumps(version.metadata)
            }
            
            # Check if this version already exists
            if version.version_number in existing_version_map:
                # Update existing version
                existing_id = existing_version_map[version.version_number]
                db.update('asset_versions', existing_id, version_data)
            else:
                # Insert new version
                version_data['id'] = version_id
                db.insert('asset_versions', version_data)
            
            # Process dependencies for this version
            self._save_dependencies(version)
    
    def _save_dependencies(self, version: AssetVersion) -> None:
        """
        Save all dependencies of a version.
        
        Args:
            version: The version whose dependencies should be saved.
        """
        # Delete existing dependencies for this version
        delete_query = "DELETE FROM asset_dependencies WHERE source_id = ?"
        db.execute(delete_query, (str(version.id),))
        
        # Insert all dependencies
        for dependency in version.dependencies:
            dependency_data = {
                'id': str(dependency.id),
                'source_id': str(dependency.source_id),
                'target_id': str(dependency.target_id),
                'dependency_type': dependency.dependency_type.value,
                'is_required': dependency.is_required,
                'created_at': dependency.created_at
            }
            db.insert('asset_dependencies', dependency_data)
    
    def get_by_id(self, asset_id: AssetId) -> Optional[AssetAggregate]:
        """
        Retrieve an asset aggregate by its ID from the SQLite database.
        
        Args:
            asset_id: The unique identifier of the asset.
            
        Returns:
            The asset aggregate if found, None otherwise.
        """
        try:
            # Get asset data from database
            asset_data = db.get_by_id('assets', str(asset_id))
            if not asset_data:
                return None
            
            # Get versions
            versions_query = """
                SELECT * FROM asset_versions 
                WHERE asset_id = ? 
                ORDER BY version_number
            """
            versions_data = db.execute(versions_query, (str(asset_id),))
            
            # Create Asset entity
            try:
                asset_type = AssetType(asset_data['asset_type'])
            except (ValueError, KeyError):
                asset_type = AssetType.OTHER
                
            try:
                status = AssetStatus(asset_data['status'])
            except (ValueError, KeyError):
                status = AssetStatus.DRAFT
            
            # Parse metadata
            try:
                metadata_dict = json.loads(asset_data.get('metadata', '{}'))
            except json.JSONDecodeError:
                metadata_dict = {}
            
            # Extract description from metadata or separate field
            description = asset_data.get('description', "")
            
            # Create asset metadata value object
            metadata = AssetMetadata(
                description=description,
                properties=metadata_dict,
                tags=()  # We'll populate tags later if needed
            )
            
            # Create base Asset entity
            asset = Asset(
                name=asset_data['name'],
                asset_type=asset_type,
                status=status,
                created_at=asset_data.get('created_at'),
                asset_id=asset_id,
                metadata=metadata
            )
            
            # Process versions
            for version_data in versions_data:
                version_id = VersionId(version_data['id'])
                
                try:
                    version_status = VersionStatus(version_data['status'])
                except (ValueError, KeyError):
                    version_status = VersionStatus.WORK_IN_PROGRESS
                
                # Parse file path
                file_path = None
                if version_data.get('file_path'):
                    file_path = FilePath(version_data['file_path'])
                
                # Parse metadata
                try:
                    version_metadata = json.loads(version_data.get('metadata', '{}'))
                except json.JSONDecodeError:
                    version_metadata = {}
                
                # Create version entity
                version = AssetVersion(
                    asset_id=asset_id,
                    version_number=version_data['version_number'],
                    comment=version_data.get('comment', ""),
                    status=version_status,
                    created_at=version_data.get('created_at'),
                    version_id=version_id,
                    metadata=version_metadata,
                    file_path=file_path
                )
                
                # Add dependencies to version
                self._load_dependencies(version)
                
                # Add version to asset
                asset.add_version(version)
            
            # Create and return aggregate
            return AssetAggregate(asset)
            
        except Exception as e:
            logger.error(f"Error retrieving asset {asset_id}: {e}")
            return None
    
    def _load_dependencies(self, version: AssetVersion) -> None:
        """
        Load all dependencies for a version from the database.
        
        Args:
            version: The version to load dependencies for.
        """
        try:
            # Query dependencies
            query = """
                SELECT * FROM asset_dependencies 
                WHERE source_id = ?
            """
            dependencies_data = db.execute(query, (str(version.id),))
            
            # Process each dependency
            for dep_data in dependencies_data:
                try:
                    dependency_type = DependencyType(dep_data['dependency_type'])
                except (ValueError, KeyError):
                    dependency_type = DependencyType.REFERENCES
                
                # Create dependency object
                dependency = AssetDependency(
                    source_id=version.id,
                    target_id=VersionId(dep_data['target_id']),
                    dependency_type=dependency_type,
                    is_required=bool(dep_data.get('is_required', True)),
                    dependency_id=DependencyId(dep_data['id'])
                )
                
                # Add to version (directly accessing protected attribute)
                version._dependencies.append(dependency)
                
        except Exception as e:
            logger.error(f"Error loading dependencies for version {version.id}: {e}")
    
    def get_by_name(self, name: str) -> List[AssetAggregate]:
        """
        Retrieve asset aggregates by name from the SQLite database.
        
        Args:
            name: The name to search for.
            
        Returns:
            A list of matching asset aggregates.
        """
        try:
            # Query assets with matching name
            query = "SELECT id FROM assets WHERE name LIKE ?"
            results = db.execute(query, (f"%{name}%",))
            
            # Load each asset
            assets = []
            for result in results:
                asset_id = AssetId(result['id'])
                asset = self.get_by_id(asset_id)
                if asset:
                    assets.append(asset)
            
            return assets
            
        except Exception as e:
            logger.error(f"Error retrieving assets by name '{name}': {e}")
            return []
    
    def search(self, 
              query: str = "", 
              asset_type: Optional[AssetType] = None,
              status: Optional[AssetStatus] = None,
              tags: List[str] = None,
              created_by: str = None,
              limit: int = 100,
              offset: int = 0) -> List[AssetAggregate]:
        """
        Search for assets based on various criteria in the SQLite database.
        
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
        try:
            # Build query conditions
            conditions = []
            params = []
            
            if query:
                conditions.append("(name LIKE ? OR description LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%"])
            
            if asset_type:
                conditions.append("asset_type = ?")
                params.append(asset_type.value)
            
            if status:
                conditions.append("status = ?")
                params.append(status.value)
            
            if created_by:
                conditions.append("created_by = ?")
                params.append(created_by)
            
            # Build the SQL query
            sql = "SELECT id FROM assets"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += f" LIMIT {limit} OFFSET {offset}"
            
            # Execute the query
            results = db.execute(sql, tuple(params))
            
            # Load each asset
            assets = []
            for result in results:
                asset_id = AssetId(result['id'])
                asset = self.get_by_id(asset_id)
                if asset:
                    # If tag filtering is enabled, check tags
                    if tags:
                        # This is simplified - in a real implementation, 
                        # we would need to check tags properly
                        asset_tags = set(asset.asset.metadata.tags)
                        if not all(tag in asset_tags for tag in tags):
                            continue
                    
                    assets.append(asset)
            
            return assets
            
        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            return []
    
    def delete(self, asset_id: AssetId) -> bool:
        """
        Delete an asset aggregate from the SQLite database.
        
        Args:
            asset_id: The unique identifier of the asset to delete.
            
        Returns:
            True if the asset was deleted, False otherwise.
        """
        try:
            # Start a transaction
            db.begin_transaction()
            
            # Delete dependencies for all versions of this asset
            deps_query = """
                DELETE FROM asset_dependencies 
                WHERE source_id IN (SELECT id FROM asset_versions WHERE asset_id = ?)
            """
            db.execute(deps_query, (str(asset_id),))
            
            # Delete versions
            versions_query = "DELETE FROM asset_versions WHERE asset_id = ?"
            db.execute(versions_query, (str(asset_id),))
            
            # Delete the asset
            asset_query = "DELETE FROM assets WHERE id = ?"
            db.execute(asset_query, (str(asset_id),))
            
            # Commit the transaction
            db.commit_transaction()
            
            return True
            
        except Exception as e:
            # Rollback the transaction on error
            db.rollback_transaction()
            logger.error(f"Error deleting asset {asset_id}: {e}")
            return False
    
    def get_version(self, version_id: VersionId) -> Optional[AssetVersion]:
        """
        Retrieve a specific asset version from the SQLite database.
        
        Args:
            version_id: The unique identifier of the version.
            
        Returns:
            The asset version if found, None otherwise.
        """
        try:
            # Get version data
            version_data = db.get_by_id('asset_versions', str(version_id))
            if not version_data:
                return None
            
            # Get asset ID
            asset_id = AssetId(version_data['asset_id'])
            
            # Create version entity
            try:
                version_status = VersionStatus(version_data['status'])
            except (ValueError, KeyError):
                version_status = VersionStatus.WORK_IN_PROGRESS
            
            # Parse file path
            file_path = None
            if version_data.get('file_path'):
                file_path = FilePath(version_data['file_path'])
            
            # Parse metadata
            try:
                version_metadata = json.loads(version_data.get('metadata', '{}'))
            except json.JSONDecodeError:
                version_metadata = {}
            
            # Create version entity
            version = AssetVersion(
                asset_id=asset_id,
                version_number=version_data['version_number'],
                comment=version_data.get('comment', ""),
                status=version_status,
                created_at=version_data.get('created_at'),
                version_id=version_id,
                metadata=version_metadata,
                file_path=file_path
            )
            
            # Load dependencies
            self._load_dependencies(version)
            
            return version
            
        except Exception as e:
            logger.error(f"Error retrieving version {version_id}: {e}")
            return None
    
    def get_dependencies(self, version_id: VersionId) -> List[VersionId]:
        """
        Get all dependencies for a specific version from the SQLite database.
        
        Args:
            version_id: The version to get dependencies for.
            
        Returns:
            List of version IDs that the specified version depends on.
        """
        try:
            # Query dependencies
            query = "SELECT target_id FROM asset_dependencies WHERE source_id = ?"
            results = db.execute(query, (str(version_id),))
            
            # Extract target IDs
            return [VersionId(result['target_id']) for result in results]
            
        except Exception as e:
            logger.error(f"Error retrieving dependencies for version {version_id}: {e}")
            return []
    
    def get_dependents(self, version_id: VersionId) -> List[VersionId]:
        """
        Get all dependents for a specific version from the SQLite database.
        
        Args:
            version_id: The version to get dependents for.
            
        Returns:
            List of version IDs that depend on the specified version.
        """
        try:
            # Query dependents
            query = "SELECT source_id FROM asset_dependencies WHERE target_id = ?"
            results = db.execute(query, (str(version_id),))
            
            # Extract source IDs
            return [VersionId(result['source_id']) for result in results]
            
        except Exception as e:
            logger.error(f"Error retrieving dependents for version {version_id}: {e}")
            return []
    
    def exists(self, asset_id: AssetId) -> bool:
        """
        Check if an asset exists in the SQLite database.
        
        Args:
            asset_id: The unique identifier of the asset.
            
        Returns:
            True if the asset exists, False otherwise.
        """
        try:
            query = "SELECT COUNT(*) as count FROM assets WHERE id = ?"
            result = db.execute(query, (str(asset_id),))
            return result[0]['count'] > 0
            
        except Exception as e:
            logger.error(f"Error checking if asset {asset_id} exists: {e}")
            return False
