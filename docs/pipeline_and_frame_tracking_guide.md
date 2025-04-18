# Pipeline Configuration Guide

This document explains how to configure pipeline dependencies and workflows in the Bifrost system, as well as how to use the global frame tracking features.

## Pipeline Step Configuration

The Bifrost system provides a flexible way to configure pipeline steps and their dependencies based on project needs. There are two levels of configuration:

1. **Global Configuration**: Defined in `config/pipeline/dependencies.yaml`
2. **Project-Specific Configuration**: Defined in `config/project/<project_code>_pipeline.yaml`

### Global Pipeline Configuration

The global configuration defines the standard departments, their dependencies, and workflows that apply to all projects by default. This is defined in `dependencies.yaml`:

```yaml
# Example from dependencies.yaml
departments:
  - id: concept
    name: "Concept Art"
    requires: []
    produces:
      - type: "image"
        format: ["jpg", "png", "psd"]
        location: "published/{VERSION}/concept/"
    
  - id: modeling
    name: "3D Modeling"
    requires:
      - department: "concept"
        status: "approved"
    produces:
      - type: "model"
        format: ["usd", "usdc", "obj", "fbx"]
        location: "published/{VERSION}/modeling/"
  
  # ... other departments
  
workflows:
  default:
    asset_types:
      character:
        sequence: ["concept", "modeling", "texture", "shading", "rigging"]
      # ... other asset types
    
    shot_types:
      standard:
        sequence: ["layout", "animation", "lighting", "rendering", "comp"]
      # ... other shot types
```

### Project-Specific Configuration

For project-specific pipeline workflows and dependencies, create a configuration file in the `config/project/` directory with the naming convention `<project_code>_pipeline.yaml`:

```yaml
# Example project-specific pipeline configuration
project_id: "my_project"
name: "My Project"
description: "Project description"

# Pipeline configuration
pipeline:
  # Override global workflow with project-specific settings
  workflow_type: "default"  # Use 'default' or 'lightweight' from dependencies.yaml, or 'custom'
  
  # Custom department dependencies (overrides global settings)
  custom_department_dependencies:
    # Example: Lighting doesn't need animation approval for this project
    lighting:
      requires:
        - department: "shading"
          status: "approved"
        # Note: animation dependency removed
  
  # Custom asset workflows
  asset_workflows:
    character:
      # Override character workflow sequence
      sequence: ["concept", "modeling", "texture", "shading", "rigging"]
    
    # Project-specific asset type
    set_piece:
      sequence: ["concept", "modeling", "texture", "shading"]
  
  # Custom shot workflows  
  shot_workflows:
    # Project-specific shot type
    dialogue:
      sequence: ["layout", "animation", "comp"]

# Task template overrides
task_templates:
  modeling:
    name_template: "{asset_name} Modeling"
    description_template: "Create 3D model for {asset_name}"
    estimated_hours: 16
    priority: "medium"
```

### How to Customize Pipeline Steps for a Project

1. **Create a Project Configuration File**:
   - Create a file in `config/project/` named `<project_code>_pipeline.yaml`
   - Define the basic project information

2. **Override Department Dependencies**:
   - Use `custom_department_dependencies` to modify what each department requires
   - This allows you to remove or add dependencies for specific projects

3. **Define Custom Workflows**:
   - Customize asset workflows with `asset_workflows`
   - Customize shot workflows with `shot_workflows`
   - Add project-specific asset types or shot types

4. **Override Task Templates**:
   - Define custom task templates for specific departments
   - Customize naming, descriptions, and default values

### Accessing Pipeline Configuration in Code

The system provides utility functions in `bifrost.utils.pipeline_config` to work with these configurations:

```python
from bifrost.utils.pipeline_config import get_project_pipeline_steps

# Get pipeline steps with project overrides applied
steps = get_project_pipeline_steps("my_project")

# Use the steps in your application
for step in steps:
    print(f"{step.name} requires: {[r.department for r in step.requires]}")
```

## Global Frame Tracking

Bifrost supports tracking both local frame numbers and global frame numbers throughout the project hierarchy (series > episode > sequence > shot).

### Understanding Frame Tracking

- **Local Frame Numbers**: Each element (shot, sequence, etc.) has its own local frame range (e.g., 1001-1100)
- **Global Frame Numbers**: Each element also tracks its position in the global timeline (e.g., shot020 starts at global frame 1101)

### Example Frame Numbering

For a sequence with a total of 500 frames (1001-1500) divided into 5 shots of 100 frames each:

```
Sequence 01 (seq01):
- Local frames: 1001-1500
- Global frames: 1001-1500

Shot 010 (shot010):
- Local frames: 1001-1100
- Global frames: 1001-1100

Shot 020 (shot020):
- Local frames: 1001-1100
- Global frames: 1101-1200

Shot 030 (shot030):
- Local frames: 1001-1100
- Global frames: 1201-1300

... and so on
```

### Configuring Frame Ranges

When creating or updating shots, sequences, or episodes, you can specify both local and global frame ranges:

```python
from bifrost.models.shot import Shot

# Create a new shot with local and global frame ranges
shot = Shot(
    id="shot020",
    code="sq001_sh020",
    sequence_id="seq001",
    name="Shot 020",
    description="Second shot in sequence",
    frame_range=(1001, 1100),  # Local frame range
    global_frame_start=1101,    # Global start frame
    global_frame_end=1200       # Global end frame
)

# The shot provides methods for calculating duration
print(f"Local duration: {shot.duration} frames")
print(f"Global duration: {shot.global_duration} frames")
```

### Best Practices for Frame Tracking

1. **Consistent Numbering**: Use consistent frame numbering conventions (e.g., always start shots at 1001)
2. **Calculate Global Frames Automatically**: When possible, calculate global frames based on the shot's position in the sequence
3. **Update Related Elements**: When changing a shot's duration, update the global frames of subsequent shots
4. **Validate Frame Ranges**: Ensure shots don't overlap in the global timeline and that they fit within their parent sequence

By using these configuration capabilities, you can customize the pipeline to match the specific needs of each project while maintaining consistent frame tracking throughout the production.