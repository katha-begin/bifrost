# OpenAssetIO Integration with Bifrost

This guide explains how to work with the OpenAssetIO integration in Bifrost. The integration allows you to interact with various asset management systems through a standardized interface.

## Overview

Bifrost's OpenAssetIO integration provides:

1. **Asset Management Abstraction** - A consistent interface for accessing assets regardless of the underlying storage system
2. **URI-Based Asset References** - Reference assets using standardized URI strings
3. **Asset Resolution** - Translate asset references to concrete file paths
4. **Asset Relationship Management** - Track dependencies between assets
5. **DCC Tool Integration** - Standardized asset access across different digital content creation tools

## Requirements

Before using OpenAssetIO with Bifrost, ensure you have:

- OpenAssetIO installed (via pip package `openassetio>=1.0.0b1`)
- A compatible asset management system or the OpenAssetIO test manager

You can run the dependency setup script to install these requirements:

```bash
python scripts/setup_dependencies.py
```

## Configuration

The OpenAssetIO integration is configured in Bifrost's configuration file (`config/default_config.yaml`). Key settings include:

```yaml
# OpenAssetIO configuration
assetio:
  enabled: true                        # Enable/disable OpenAssetIO support
  manager: "org.bifrost.assetmanager"  # Primary asset manager to use
  fallback_manager: "org.openassetio.test.manager"  # Fallback manager
  host_name: "Bifrost Asset Manager"   # Host name for identification
  host_version: "0.1.0"                # Host version
  uri_scheme: "bifrost"                # URI scheme for Bifrost assets
  environment:
    OPENASSETIO_PLUGIN_PATH: ""        # Additional plugin paths
```

## Working with Asset References

### Creating Asset URIs

Asset references in OpenAssetIO are expressed as URI strings. In Bifrost, these typically follow the pattern `bifrost:///assets/{asset_id}`.

```python
from bifrost.integrations.assetio.uri_mapper import AssetUriMapper
from bifrost.services.asset_service import asset_service

# Get an asset
asset = asset_service.get_asset("12345678-1234-5678-9abc-123456789abc")

# Create a URI for the asset
uri = AssetUriMapper.asset_to_uri(asset)
# Result: "bifrost:///assets/12345678-1234-5678-9abc-123456789abc"

# Extract asset ID from a URI
asset_id = AssetUriMapper.uri_to_asset_id("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")
# Result: "12345678-1234-5678-9abc-123456789abc"
```

### Resolving Asset References

Once you have an asset URI, you can resolve it to get concrete file paths or other information:

```python
from bifrost.integrations.assetio.bifrost_host import bifrost_host

# Initialize the host interface
bifrost_host.initialize()

# Resolve an asset URI to a file path
file_path = bifrost_host.resolve_asset_path("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")

# Get the version number for an asset
version = bifrost_host.get_version("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")

# Get complete entity information
entity_info = bifrost_host.get_entity_info("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")
```

## Implementing a Manager

Bifrost provides a built-in OpenAssetIO manager implementation that interfaces with Bifrost's asset system. If you need to extend or modify this implementation:

```python
from bifrost.integrations.assetio.bifrost_manager import BifrostManagerInterface

# Create a customized manager that extends the default one
class CustomBifrostManager(BifrostManagerInterface):
    def __init__(self):
        super().__init__()
        
    def capabilities(self):
        # Add custom capabilities
        capabilities = super().capabilities()
        capabilities["customFeature"] = True
        return capabilities
        
    def resolve(self, entityRefs, traitSet, context, hostSession):
        # Add custom resolution logic
        results = super().resolve(entityRefs, traitSet, context, hostSession)
        
        # Enhance results with additional information
        for i, result in enumerate(results):
            if "location" in result:
                result["customInfo"] = "Additional data about " + entityRefs[i].toString()
                
        return results
```

## Asset Path to URI Conversion

You can convert file paths to URIs when they match your asset structure:

```python
# Convert a file path to a URI if it matches Bifrost's patterns
uri = AssetUriMapper.path_to_uri("/data/assets/12345678-1234-5678-9abc-123456789abc/v001/model.usd")
# Result: "bifrost:///assets/12345678-1234-5678-9abc-123456789abc"

# Convert a URI to a path
path = AssetUriMapper.uri_to_path("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")
```

## Integration with DCC Tools

OpenAssetIO is designed to allow different DCC tools to access assets in a standard way. Here's how you might use Bifrost's OpenAssetIO implementation in a DCC plugin:

```python
import openassetio
from openassetio.hostApi import ManagerFactory

# In your DCC plugin
def initialize_openassetio():
    # Create an OpenAssetIO context
    context = openassetio.Context()
    
    # Create a manager factory
    factory = ManagerFactory()
    
    # Find and create the Bifrost manager
    managers = factory.identifiers()
    if "org.bifrost.assetmanager" in managers:
        manager = factory.createManager("org.bifrost.assetmanager")
        
        # Initialize the manager
        host_session = {
            "hostIdentifier": "com.example.dcc",
            "hostName": "Example DCC",
            "hostVersion": "1.0.0"
        }
        
        manager.initialize({}, host_session)
        return manager
    
    return None

# Use the manager to resolve an asset
def get_asset_path(asset_uri):
    manager = initialize_openassetio()
    if not manager:
        return None
        
    # Create context
    context = openassetio.Context()
    
    # Resolve the URI
    entity_reference = manager.createEntityReference(asset_uri)
    results = manager.resolve([entity_reference], ["locatableContent"], context)
    
    if results and results[0] and "location" in results[0]:
        return results[0]["location"]
    
    return None
```

## Working with Asset Relationships

You can track relationships between assets:

```python
# Get relationships for an asset
relationships = bifrost_host.get_relationships("bifrost:///assets/12345678-1234-5678-9abc-123456789abc")

# Analyze the relationships
for relationship in relationships:
    from_entity = relationship["fromEntity"]
    to_entity = relationship["toEntity"]
    relationship_type = relationship["traits"]["dependency"]["type"]
    
    print(f"Asset {from_entity} depends on {to_entity} (type: {relationship_type})")
```

## Command Line Interface

Bifrost provides OpenAssetIO-related commands in its CLI:

```bash
# Resolve an asset URI to a path
bifrost asset resolve bifrost:///assets/12345678-1234-5678-9abc-123456789abc

# Get information about an asset URI
bifrost asset info-uri bifrost:///assets/12345678-1234-5678-9abc-123456789abc

# List available asset managers
bifrost asset managers
```

## Best Practices

1. **Use URIs Instead of Paths** - Where possible, store and pass around asset URIs rather than direct file paths

2. **Handle Resolution Failures** - Always check if resolution was successful before using results

3. **Consistent URI Scheme** - Stick to a consistent URI scheme throughout your project

4. **Cache Resolutions** - Cache resolution results when appropriate to improve performance

5. **Track Relationships** - Use the relationship tracking features to maintain dependency information

6. **Version Selection** - Be explicit about which version of an asset you want to resolve

## Troubleshooting

Common issues and their solutions:

1. **Import Errors** - Make sure OpenAssetIO is properly installed with `pip install openassetio`

2. **Manager Not Found** - Ensure your manager is registered with OpenAssetIO by checking the manager factory identifiers

3. **Resolution Failures** - Check that your asset URIs follow the correct format and that the assets exist

4. **Missing File Paths** - Verify that your resolver is correctly mapping from URIs to file paths

5. **Integration Issues** - When integrating with DCC tools, make sure the host session information is properly set
