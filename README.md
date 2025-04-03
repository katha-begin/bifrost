# Bifrost Animation Asset Management System

Bifrost is a cross-platform Python-based animation asset and shot management system designed for professional animation production pipelines. It provides efficient data management between departments with minimal dependencies and is built for future cloud integration.

## Features

- **Asset Management**: Create, track, and version all production assets
- **Shot Management**: Organize and track shots with frame ranges and associated assets
- **Version Control**: Maintain version history of assets and shots
- **Dependency Tracking**: Track relationships between assets and shots
- **Folder Structure Management**: Template-based project organization
- **OpenAssetIO Integration**: Standardized asset management interoperability
- **USD Pipeline Support**: First-class support for Universal Scene Description
- **Extensible Architecture**: Built to adapt to different production needs
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Multi-DCC Integration**: Planned integration with Maya, Blender, and Houdini
- **Cloud-Ready**: Designed with future cloud storage integration in mind

## System Architecture

Bifrost follows a domain-driven design approach with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Service Layer**: Use cases that orchestrate domain objects
- **Core Layer**: Infrastructure services (database, config, auth, logging)
- **Integration Layer**: Connects to external systems (storage, DCC tools)
- **User Interfaces**: Multiple interfaces (CLI, GUI, API, webhooks)

For more details, see the [Architecture Documentation](docs/architecture/updated_overview.md).

## Prerequisites

- Python 3.10 or higher
- SQLite3 (PostgreSQL support for production environments)
- Git (for development workflow)

## Installation

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://your-repo-url/bifrost.git
   cd bifrost
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Initialize the workspace:
   ```bash
   python scripts/init_workspace.py
   ```

### Production Installation

For production environments, we recommend:

1. Install from PyPI (once available):
   ```bash
   pip install bifrost-pipeline
   ```

2. Configure the system:
   ```bash
   bifrost config set database.path /path/to/your/database.db
   bifrost config set storage.local.root_path /path/to/your/assets
   ```

## Usage

### Command Line Interface

Bifrost comes with a powerful command-line interface:

```bash
# Get help
bifrost --help

# List all assets
bifrost asset list

# Create a new asset
bifrost asset create --name "Character_Hero" --type character --description "Main character" 

# Get asset information
bifrost asset info [ASSET_ID]

# Add a new version to an asset
bifrost asset add-version [ASSET_ID] --file /path/to/file.blend --comment "Fixed rig issues"
```

### Python API

You can also use Bifrost as a Python library:

```python
from bifrost.services.asset_service import asset_service
from bifrost.models.asset import AssetType

# Create a new asset
asset = asset_service.create_asset(
    name="Environment_Forest", 
    asset_type=AssetType.ENVIRONMENT,
    description="Forest environment for Act 1",
    created_by="artist1"
)

# Get asset information
asset = asset_service.get_asset(asset_id)

# Add a new version
asset_service.add_version(
    asset_id=asset.id,
    file_path="/path/to/forest_v2.blend",
    comment="Updated lighting"
)
```

### OpenAssetIO Integration

Bifrost includes an OpenAssetIO integration for standardized asset management:

```python
from bifrost.integrations.assetio.bifrost_host import bifrost_host

# Initialize the host interface
bifrost_host.initialize()

# Resolve an asset URI to a file path
file_path = bifrost_host.resolve_asset_path("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")

# Get the version number for an asset
version = bifrost_host.get_version("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")
```

For more details, see the [OpenAssetIO Integration Guide](docs/integration_guides/openassetio_integration.md).

## Project Structure

```
bifrost/
├── bifrost/                    # Main package directory
│   ├── core/                   # Core functionality
│   ├── models/                 # Data models
│   │   ├── asset.py           # Asset domain models
│   │   ├── shot.py            # Shot domain models
│   │   └── folder_structure/   # Folder structure models
│   ├── services/               # Business logic services
│   │   ├── asset_service.py   # Asset management service
│   │   └── folder_service/    # Folder structure services
│   ├── storage/                # Storage interfaces
│   ├── api/                    # API endpoints
│   ├── ui/                     # User interfaces
│   │   ├── cli/               # Command-line interface
│   │   └── gui/               # Graphical user interface
│   ├── integrations/           # External software integrations
│   │   ├── assetio/           # OpenAssetIO integration
│   │   └── usd/               # USD pipeline integration
│   └── utils/                  # Utility functions
├── scripts/                    # Deployment and utility scripts
├── docs/                       # Documentation
│   ├── architecture/          # System architecture docs
│   └── integration_guides/    # Integration guides
├── config/                     # Configuration files
│   ├── default_config.yaml    # Default configuration
│   ├── pipeline/              # Pipeline configuration
│   └── show/                  # Show-specific configuration
├── tests/                      # Test suite
└── examples/                   # Example scripts and workflows
```

## Development Status

Bifrost is currently in active development. See the [Development Milestones](docs/architecture/updated_development_milestones.md) for current status and roadmap.

### Current Focus Areas

- Domain-driven design implementation
- Enhanced OpenAssetIO integration
- Folder structure management system
- Workflow engine development

## Contributing

Bifrost is under active development and contributions are welcome. Please see the [Contributing Guide](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
