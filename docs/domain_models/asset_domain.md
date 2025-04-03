# Asset Domain Model

This document outlines the domain model for the Asset domain in the Bifrost system.

## Domain Overview

The Asset domain represents production assets that are created, modified, and used in the animation production process. Assets have versions, dependencies, and metadata. They are organized by types and can be part of larger asset hierarchies.

## Domain Entities

### Asset

The central entity in the Asset domain representing a production asset.

#### Attributes

| Attribute      | Type              | Description                                     |
|----------------|-------------------|-------------------------------------------------|
| id             | UUID              | Unique identifier                               |
| name           | String            | Human-readable name                             |
| asset_type     | AssetType         | Type of asset (character, prop, etc.)           |
| description    | String            | Text description                                |
| status         | String            | Current workflow status                         |
| created_at     | DateTime          | Creation timestamp                              |
| created_by     | String            | Creator identifier                              |
| modified_at    | DateTime          | Last modification timestamp                     |
| modified_by    | String            | Last modifier identifier                        |
| tags           | List[String]      | Searchable tags                                 |
| metadata       | Dict[String, Any] | Additional metadata key-value pairs             |

#### Methods

```python
class Asset:
    def __init__(self, name, asset_type, description=None, created_by=None):
        self.id = uuid.uuid4()
        self.name = name
        self.asset_type = asset_type
        self.description = description
        self.status = "draft"
        self.created_at = datetime.datetime.now()
        self.created_by = created_by
        self.modified_at = self.created_at
        self.modified_by = created_by
        self.tags = []
        self.metadata = {}
        self._versions = []
        self._latest_version = None
        self._dependencies = []
        
    def add_version(self, file_path, comment=None, created_by=None) -> AssetVersion:
        """Add a new version to this asset."""
        version_number = len(self._versions) + 1
        version = AssetVersion(
            asset_id=self.id,
            version_number=version_number,
            file_path=file_path,
            comment=comment,
            created_by=created_by or self.created_by
        )
        self._versions.append(version)
        self._latest_version = version
        self.modified_at = datetime.datetime.now()
        self.modified_by = created_by or self.created_by
        return version
        
    def get_version(self, version_number=None) -> Optional[AssetVersion]:
        """Get a specific version or the latest version if none specified."""
        if version_number is None:
            return self._latest_version
            
        for version in self._versions:
            if version.version_number == version_number:
                return version
                
        return None
        
    def get_all_versions(self) -> List[AssetVersion]:
        """Get all versions of this asset."""
        return sorted(self._versions, key=lambda v: v.version_number)
        
    def add_dependency(self, dependent_asset_id, dependency_type=None, optional=False) -> AssetDependency:
        """Add a dependency to another asset."""
        dependency = AssetDependency(
            source_asset_id=self.id,
            dependent_asset_id=dependent_asset_id,
            dependency_type=dependency_type,
            optional=optional
        )
        self._dependencies.append(dependency)
        return dependency
        
    def get_dependencies(self) -> List[AssetDependency]:
        """Get all dependencies of this asset."""
        return self._dependencies
        
    def add_tag(self, tag):
        """Add a tag to this asset."""
        if tag not in self.tags:
            self.tags.append(tag)
            
    def remove_tag(self, tag):
        """Remove a tag from this asset."""
        if tag in self.tags:
            self.tags.remove(tag)
            
    def set_metadata(self, key, value):
        """Set a metadata key-value pair."""
        self.metadata[key] = value
        
    def get_metadata(self, key, default=None):
        """Get a metadata value by key."""
        return self.metadata.get(key, default)
        
    def update_status(self, new_status, modified_by=None):
        """Update the workflow status."""
        self.status = new_status
        self.modified_at = datetime.datetime.now()
        self.modified_by = modified_by or self.modified_by
```

### AssetVersion

Represents a specific version of an asset.

#### Attributes

| Attribute      | Type              | Description                                     |
|----------------|-------------------|-------------------------------------------------|
| id             | UUID              | Unique identifier                               |
| asset_id       | UUID              | Reference to parent asset                        |
| version_number | Integer           | Sequential version number                       |
| file_path      | Path              | Path to asset file                              |
| comment        | String            | Version comment                                 |
| created_at     | DateTime          | Creation timestamp                              |
| created_by     | String            | Creator identifier                              |
| metadata       | Dict[String, Any] | Additional metadata key-value pairs             |

#### Methods

```python
class AssetVersion:
    def __init__(self, asset_id, version_number, file_path, comment=None, created_by=None):
        self.id = uuid.uuid4()
        self.asset_id = asset_id
        self.version_number = version_number
        self.file_path = file_path
        self.comment = comment
        self.created_at = datetime.datetime.now()
        self.created_by = created_by
        self.metadata = {}
        
    def set_metadata(self, key, value):
        """Set a metadata key-value pair."""
        self.metadata[key] = value
        
    def get_metadata(self, key, default=None):
        """Get a metadata value by key."""
        return self.metadata.get(key, default)
        
    def get_file_size(self):
        """Get the file size of this version."""
        try:
            return os.path.getsize(self.file_path)
        except (OSError, FileNotFoundError):
            return 0
            
    def exists(self):
        """Check if the file exists."""
        return os.path.exists(self.file_path)
```

### AssetDependency

Represents a dependency relationship between assets.

#### Attributes

| Attribute         | Type              | Description                                     |
|-------------------|-------------------|-------------------------------------------------|
| id                | UUID              | Unique identifier                               |
| source_asset_id   | UUID              | Asset that depends on another                   |
| dependent_asset_id| UUID              | Asset being depended on                         |
| dependency_type   | String            | Type of dependency (reference, use, etc.)       |
| optional          | Boolean           | Whether the dependency is optional              |
| metadata          | Dict[String, Any] | Additional metadata key-value pairs             |

#### Methods

```python
class AssetDependency:
    def __init__(self, source_asset_id, dependent_asset_id, dependency_type=None, optional=False):
        self.id = uuid.uuid4()
        self.source_asset_id = source_asset_id
        self.dependent_asset_id = dependent_asset_id
        self.dependency_type = dependency_type or "default"
        self.optional = optional
        self.metadata = {}
        
    def set_metadata(self, key, value):
        """Set a metadata key-value pair."""
        self.metadata[key] = value
        
    def get_metadata(self, key, default=None):
        """Get a metadata value by key."""
        return self.metadata.get(key, default)
```

### AssetType

Represents a classification of assets.

#### Attributes

| Attribute      | Type              | Description                                     |
|----------------|-------------------|-------------------------------------------------|
| id             | UUID              | Unique identifier                               |
| name           | String            | Type name                                       |
| display_name   | String            | Human-readable display name                     |
| description    | String            | Text description                                |
| icon           | String            | Icon identifier                                 |
| metadata       | Dict[String, Any] | Additional metadata key-value pairs             |

#### Methods

```python
class AssetType:
    def __init__(self, name, display_name=None, description=None, icon=None):
        self.id = uuid.uuid4()
        self.name = name
        self.display_name = display_name or name.title()
        self.description = description
        self.icon = icon
        self.metadata = {}
        
    def set_metadata(self, key, value):
        """Set a metadata key-value pair."""
        self.metadata[key] = value
        
    def get_metadata(self, key, default=None):
        """Get a metadata value by key."""
        return self.metadata.get(key, default)
```

## Repository Interface

The repository interface for the Asset domain:

```python
class AssetRepository:
    def create(self, asset: Asset) -> Asset:
        """Create a new asset."""
        pass
        
    def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """Get an asset by ID."""
        pass
        
    def get_by_name(self, name: str) -> Optional[Asset]:
        """Get an asset by name."""
        pass
        
    def update(self, asset: Asset) -> Asset:
        """Update an asset."""
        pass
        
    def delete(self, asset_id: UUID) -> bool:
        """Delete an asset."""
        pass
        
    def list_all(self) -> List[Asset]:
        """List all assets."""
        pass
        
    def list_by_type(self, asset_type: AssetType) -> List[Asset]:
        """List assets by type."""
        pass
        
    def list_by_tag(self, tag: str) -> List[Asset]:
        """List assets by tag."""
        pass
        
    def search(self, query: str) -> List[Asset]:
        """Search assets by query string."""
        pass
        
    def add_version(self, asset_id: UUID, version: AssetVersion) -> AssetVersion:
        """Add a version to an asset."""
        pass
        
    def get_version(self, asset_id: UUID, version_number: int) -> Optional[AssetVersion]:
        """Get a specific version of an asset."""
        pass
        
    def get_latest_version(self, asset_id: UUID) -> Optional[AssetVersion]:
        """Get the latest version of an asset."""
        pass
        
    def add_dependency(self, dependency: AssetDependency) -> AssetDependency:
        """Add a dependency between assets."""
        pass
        
    def get_dependencies(self, asset_id: UUID) -> List[AssetDependency]:
        """Get all dependencies of an asset."""
        pass
        
    def get_dependents(self, asset_id: UUID) -> List[AssetDependency]:
        """Get all assets that depend on the given asset."""
        pass
```

## Service Interface

The service interface for the Asset domain:

```python
class AssetService:
    def __init__(self, repository: AssetRepository):
        self.repository = repository
        
    def create_asset(self, name: str, asset_type: AssetType, description: str = None, 
                    created_by: str = None) -> Asset:
        """Create a new asset."""
        asset = Asset(name, asset_type, description, created_by)
        return self.repository.create(asset)
        
    def get_asset(self, asset_id: UUID) -> Optional[Asset]:
        """Get an asset by ID."""
        return self.repository.get_by_id(asset_id)
        
    def update_asset(self, asset: Asset) -> Asset:
        """Update an asset."""
        return self.repository.update(asset)
        
    def delete_asset(self, asset_id: UUID) -> bool:
        """Delete an asset."""
        return self.repository.delete(asset_id)
        
    def add_version(self, asset_id: UUID, file_path: str, comment: str = None,
                   created_by: str = None) -> AssetVersion:
        """Add a new version to an asset."""
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")
            
        version = asset.add_version(file_path, comment, created_by)
        self.repository.update(asset)
        return version
        
    def get_version(self, asset_id: UUID, version_number: int = None) -> Optional[AssetVersion]:
        """Get a specific version or the latest version of an asset."""
        if version_number is None:
            return self.repository.get_latest_version(asset_id)
        return self.repository.get_version(asset_id, version_number)
        
    def add_dependency(self, source_id: UUID, target_id: UUID, 
                      dependency_type: str = None, optional: bool = False) -> AssetDependency:
        """Add a dependency between assets."""
        dependency = AssetDependency(source_id, target_id, dependency_type, optional)
        return self.repository.add_dependency(dependency)
        
    def get_dependencies(self, asset_id: UUID) -> List[AssetDependency]:
        """Get all dependencies of an asset."""
        return self.repository.get_dependencies(asset_id)
        
    def get_dependents(self, asset_id: UUID) -> List[AssetDependency]:
        """Get all assets that depend on the given asset."""
        return self.repository.get_dependents(asset_id)
        
    def add_tag(self, asset_id: UUID, tag: str) -> Asset:
        """Add a tag to an asset."""
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")
            
        asset.add_tag(tag)
        return self.repository.update(asset)
        
    def remove_tag(self, asset_id: UUID, tag: str) -> Asset:
        """Remove a tag from an asset."""
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")
            
        asset.remove_tag(tag)
        return self.repository.update(asset)
        
    def update_status(self, asset_id: UUID, new_status: str, modified_by: str = None) -> Asset:
        """Update the status of an asset."""
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")
            
        asset.update_status(new_status, modified_by)
        return self.repository.update(asset)
        
    def search_assets(self, query: str) -> List[Asset]:
        """Search for assets."""
        return self.repository.search(query)
        
    def list_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """List assets by type."""
        return self.repository.list_by_type(asset_type)
        
    def list_assets_by_tag(self, tag: str) -> List[Asset]:
        """List assets by tag."""
        return self.repository.list_by_tag(tag)
```

## Value Objects

### AssetIdentifier

A value object for uniquely identifying assets across systems.

```python
class AssetIdentifier:
    def __init__(self, id: UUID, namespace: str = "bifrost"):
        self.id = id
        self.namespace = namespace
        
    def to_uri(self):
        """Convert to an OpenAssetIO URI."""
        return f"{self.namespace}:///assets/{self.id}"
        
    @classmethod
    def from_uri(cls, uri: str):
        """Create from an OpenAssetIO URI."""
        if not uri.startswith("bifrost:///assets/"):
            raise ValueError(f"Invalid URI format: {uri}")
            
        id_str = uri.split("/")[-1]
        return cls(uuid.UUID(id_str))
        
    def __str__(self):
        return str(self.id)
        
    def __eq__(self, other):
        if isinstance(other, AssetIdentifier):
            return self.id == other.id and self.namespace == other.namespace
        return False
```

## Domain Events

Events that occur within the Asset domain:

```python
class AssetCreated:
    def __init__(self, asset_id: UUID, asset_name: str, asset_type: str, created_by: str):
        self.asset_id = asset_id
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.created_by = created_by
        self.timestamp = datetime.datetime.now()

class AssetUpdated:
    def __init__(self, asset_id: UUID, modified_by: str):
        self.asset_id = asset_id
        self.modified_by = modified_by
        self.timestamp = datetime.datetime.now()

class AssetDeleted:
    def __init__(self, asset_id: UUID, deleted_by: str):
        self.asset_id = asset_id
        self.deleted_by = deleted_by
        self.timestamp = datetime.datetime.now()

class VersionAdded:
    def __init__(self, asset_id: UUID, version_number: int, file_path: str, created_by: str):
        self.asset_id = asset_id
        self.version_number = version_number
        self.file_path = file_path
        self.created_by = created_by
        self.timestamp = datetime.datetime.now()

class DependencyAdded:
    def __init__(self, source_id: UUID, target_id: UUID, dependency_type: str):
        self.source_id = source_id
        self.target_id = target_id
        self.dependency_type = dependency_type
        self.timestamp = datetime.datetime.now()

class StatusChanged:
    def __init__(self, asset_id: UUID, old_status: str, new_status: str, modified_by: str):
        self.asset_id = asset_id
        self.old_status = old_status
        self.new_status = new_status
        self.modified_by = modified_by
        self.timestamp = datetime.datetime.now()
```

## Domain Rules

1. Asset names must be unique within the same asset type
2. Version numbers must be sequential and start from 1
3. An asset cannot depend on itself
4. Circular dependencies should be detected and prevented
5. Only the latest version of an asset can be modified
6. Asset status changes must follow the workflow state machine
7. Asset dependencies must respect type constraints (e.g., a shot can reference a character, but not vice versa)

## Use Cases

1. Create a new asset
2. Update asset metadata
3. Add a new version to an asset
4. Query asset dependencies
5. Search for assets by criteria
6. Change asset status
7. Track asset usage across shots
8. Generate asset reports

## Implementation Considerations

1. **Persistence**: Repository implementations will handle the persistence details (SQLite, PostgreSQL)
2. **Caching**: Consider caching frequently accessed assets and their latest versions
3. **Transactions**: Use transactions for operations that modify multiple entities
4. **Validation**: Implement comprehensive validation at the service layer
5. **Events**: Publish domain events to enable cross-domain communication
