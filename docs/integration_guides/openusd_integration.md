# OpenUSD Integration with Bifrost

This guide explains how to work with the OpenUSD integration in Bifrost. The integration allows you to use USD (Universal Scene Description) files with Bifrost's asset management system.

## Overview

Bifrost's OpenUSD integration provides:

1. **USD Asset Management** - Track, version, and organize USD assets
2. **USD File Operations** - Create, read, modify, and save USD files
3. **USD Composition Support** - Work with USD layers, references, and variants
4. **USD Version Control** - Version USD assets using USD's layer stack mechanism

## Requirements

Before using OpenUSD with Bifrost, ensure you have:

- OpenUSD installed (via pip package `usd-core>=23.11.0`)
- Additional system packages if required:
  - Linux: `libgl1-mesa-dev libglu1-mesa-dev libxi-dev libxrandr-dev`
  - macOS: Homebrew with `boost python`

You can run the dependency setup script to install these requirements:

```bash
python scripts/setup_dependencies.py
```

## Configuration

The OpenUSD integration is configured in Bifrost's configuration file (`config/default_config.yaml`). Key settings include:

```yaml
# OpenUSD configuration
usd:
  enabled: true                    # Enable/disable USD support
  stage_cache_size_mb: 1024        # Memory allocated for USD stage cache
  supported_formats:               # Supported file formats
    - usd
    - usda
    - usdc
    - usdz
  default_up_axis: "Y"             # Default up axis for new stages
  conversion:
    enabled: true                  # Enable format conversion
    temp_dir: temp/usd_conversion  # Directory for temporary files
  version_strategy: "layer_stack"  # Version control strategy
  namespace_prefix: "bifrost"      # Namespace prefix for prims
```

## Working with USD Assets

### Creating a USD Asset

```python
from bifrost.services.asset_service import asset_service
from bifrost.models.asset import AssetType
from bifrost.models.usd_asset import UsdAssetType

# Create a basic USD asset
asset = asset_service.create_asset(
    name="Character_Hero",
    asset_type=AssetType.CHARACTER,
    description="Main character model",
    created_by="artist1",
    usd_type=UsdAssetType.MODEL,
    version_strategy="layer_stack"
)
```

### Working with USD Stages

```python
from bifrost.integrations.usd.usd_service import UsdService

# Initialize USD service
usd_service = UsdService()

# Create a new USD stage
stage = usd_service.create_new_stage(
    file_path="/path/to/new_stage.usd",
    up_axis="Y",
    default_prim_name="Root"
)

# Open an existing USD stage
stage = usd_service.open_stage("/path/to/existing.usd")

# Extract stage information
stage_info = usd_service.extract_stage_info(stage)
print(f"Default prim: {stage_info.default_prim}")
print(f"Up axis: {stage_info.up_axis}")
print(f"Time code range: {stage_info.time_code_range}")
```

### USD Version Control

Bifrost supports two versioning strategies for USD assets:

1. **Layer Stack Strategy** (default) - Uses USD's layer composition to create version history
2. **Separate Files Strategy** - Each version is stored as a separate file

```python
# Create a new version using layer stack strategy
version_layer = usd_service.create_version_layer(
    base_layer_path="/path/to/asset/main.usd",
    version_number=2
)

# Open the version layer
stage = usd_service.open_stage(version_layer)

# Make changes
# ...

# Save the stage
usd_service.save_stage(stage)
```

### USD Composition

```python
# Add a reference to another USD asset
usd_service.create_reference(
    stage=stage,
    target_prim_path="/Root/Props",
    reference_file_path="/path/to/other_asset.usd",
    reference_prim_path="/Prop"
)

# Add a sublayer
usd_service.create_sublayer(
    stage=stage,
    sublayer_path="/path/to/layer.usd",
    position=0  # 0 means strongest (top of stack)
)

# Create and select variants
usd_service.create_variant(
    stage=stage,
    prim_path="/Root/Character",
    variant_set_name="costume",
    variant_name="default"
)

usd_service.select_variant(
    stage=stage,
    prim_path="/Root/Character",
    variant_set_name="costume",
    variant_name="alternate"
)
```

### File Conversion

```python
# Convert an OBJ file to USD
usd_path = usd_service.convert_to_usd(
    source_file="/path/to/model.obj",
    output_path="/path/to/converted.usd"
)

# Flatten a USD stage with references to a single layer
flattened_stage = usd_service.flatten_stage(
    source_stage=stage,
    output_path="/path/to/flattened.usd"
)
```

## Command Line Interface

Bifrost provides USD-related commands in its CLI:

```bash
# Display information about a USD file
bifrost usd info /path/to/file.usd

# Convert a file to USD format
bifrost usd convert /path/to/file.obj /path/to/output.usd

# Flatten a USD file
bifrost usd flatten /path/to/file.usd /path/to/flattened.usd
```

## Best Practices

1. **Use Layer Stack Versioning** - This provides efficient storage and allows easy comparison between versions

2. **Set Default Prims** - Always set a default prim in your USD stages to make referencing easier

3. **Consistent Up Axis** - Stick to a consistent up axis across your project (usually Y)

4. **Standardize Naming** - Use consistent naming conventions for variants and layers

5. **Asset References** - Use asset references instead of file paths when possible

6. **Add Metadata** - Include descriptive metadata in your USD files

## Troubleshooting

Common issues and their solutions:

1. **USD Import Errors** - Make sure OpenUSD is properly installed with `pip install usd-core`

2. **Missing Libraries** - On Linux, ensure you've installed the required system packages

3. **Path Resolution** - Check that file paths are absolute or properly resolved

4. **Layer Stack Issues** - If layers aren't composing correctly, ensure paths are correct and the layer exists

5. **Performance Problems** - Adjust the stage cache size in the configuration if you're working with large USD files
