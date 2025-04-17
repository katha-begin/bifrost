# Example Project Structure

This document illustrates the default project structure created by Bifrost for a new animation project.

## Default Project Structure

```
ProjectName/                           # Project root directory
│
├── .bifrost/                          # Bifrost project metadata (hidden)
│   ├── project_config.yaml            # Project-specific configuration
│   ├── database.db                    # SQLite database (if using SQLite)
│   └── logs/                          # Project-specific logs
│
├── published/                         # Published content
│   ├── asset/                         # Published assets
│   │   ├── characters/                # Asset type: characters
│   │   │   ├── hero/                  # Asset: hero character
│   │   │   │   ├── model/             # Department: modeling
│   │   │   │   │   ├── version/       # Versioning directory
│   │   │   │   │   │   ├── v001/      # Version 001
│   │   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   │   └── metadata.json    # Metadata
│   │   │   │   │   │   ├── v002/      # Version 002
│   │   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   │   └── metadata.json    # Metadata
│   │   │   │   │   │   │
│   │   │   │   │   │   └── v003/      # Version 003
│   │   │   │   │
│   │   │   │   ├── asset/             # General asset directory
│   │   │   │   │   ├── version/       # Versioning directory
│   │   │   │   │   │   ├── v001/      # Version 001
│   │   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   │   └── metadata.json    # Metadata
│   │   │   │   │   │   ├── v002/      # Version 002
│   │   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   │   └── metadata.json    # Metadata
│   │   │   │   │   │   │
│   │   │   │   │   │   └── v003/      # Version 003
│   │   │   │   │
│   │   │   │   ├── rig/               # Department: rigging
│   │   │   │   │   ├── version/       # Versioning directory
│   │   │   │   │   │   ├── v001/      # Version 001
│   │   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   │   └── metadata.json    # Metadata
│   │   │   │   │   │   │
│   │   │   │   │   │   └── v002/      # Version 002
│   │   │   │   │
│   │   │   │   └── texture/           # Department: texturing
│   │   │   │       ├── version/       # Versioning directory
│   │   │   │       │   ├── v001/      # Version 001
│   │   │   │       │   │   ├── asset.usd    # Main asset file
│   │   │   │       │   │   ├── payload.usd  # Payload data
│   │   │   │       │   │   └── metadata.json    # Metadata
│   │   │   │       │   │
│   │   │   │       │   └── v002/      # Version 002
│   │   │   │
│   │   │   └── villain/               # Asset: villain character
│   │   │       ├── model/             # Department: modeling
│   │   │       │   ├── version/       # Versioning directory
│   │   │       │   │   ├── v001/      # Version 001
│   │   │       │   │   │   ├── asset.usd    # Main asset file
│   │   │       │   │   │   ├── payload.usd  # Payload data
│   │   │       │   │   │   └── metadata.json    # Metadata
│   │   │       │   │   │
│   │   │       │   │   └── v002/      # Version 002
│   │   │       │
│   │   │       └── asset/             # General asset directory
│   │   │           ├── version/       # Versioning directory
│   │   │           │   ├── v001/      # Version 001
│   │   │           │   │   ├── asset.usd    # Main asset file
│   │   │           │   │   ├── payload.usd  # Payload data
│   │   │           │   │   └── metadata.json    # Metadata
│   │   │           │   │
│   │   │           │   └── v002/      # Version 002
│   │   │
│   │   ├── environments/              # Asset type: environments
│   │   │   ├── forest/                # Asset: forest environment
│   │   │   │   ├── model/             # Department: modeling
│   │   │   │   │   ├── version/       # Versioning directory
│   │   │   │   │   │   ├── v001/      # Version 001
│   │   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   │   └── metadata.json    # Metadata
│   │   │   │   │   │   │
│   │   │   │   │   │   └── v002/      # Version 002
│   │   │   │   │
│   │   │   │   └── asset/             # General asset directory
│   │   │   │       ├── version/       # Versioning directory
│   │   │   │       │   ├── v001/      # Version 001
│   │   │   │       │   │   ├── asset.usd    # Main asset file
│   │   │   │       │   │   ├── payload.usd  # Payload data
│   │   │   │       │   │   └── metadata.json    # Metadata
│   │   │   │       │   │
│   │   │   │       │   └── v002/      # Version 002
│   │   │   │
│   │   │   └── city/                  # Asset: city environment
│   │   │       ├── model/             # Department: modeling
│   │   │       │   └── version/       # Versioning directory
│   │   │       │       └── v001/      # Version 001
│   │   │       │
│   │   │       └── asset/             # General asset directory
│   │   │           └── version/       # Versioning directory
│   │   │               └── v001/      # Version 001
│   │   │
│   │   └── props/                     # Asset type: props
│   │       ├── sword/                 # Asset: sword prop
│   │       │   ├── model/             # Department: modeling
│   │       │   │   └── version/       # Versioning directory
│   │       │   │       └── v001/      # Version 001
│   │       │   │
│   │       │   └── asset/             # General asset directory
│   │       │       └── version/       # Versioning directory
│   │       │           └── v001/      # Version 001
│   │       │
│   │       └── ...
│   │
│   └── shot/                          # Published shots
│       ├── s01/                       # Series (or show) 01
│       │   ├── ep01/                  # Episode 01
│       │   │   ├── seq001/            # Sequence 001
│       │   │   │   ├── master/                         # seq master data
│       │   │   │   │   ├── version/                    # Versioning directory
│       │   │   │   │   │   ├── v001/                   # Version 001
│       │   │   │   │   │   │   ├── seq.usd             # Main seq config usd fle
│       │   │   │   │   │   │   └── metadata.json       # Metadata
│       │   │   │   │   │   │
│       │   │   │   │   │   └── v002/     # Version 002
│       │   │   │   │   │       ├── seq.usd    # Main animation file
│       │   │   │   │   │       ├── payload.usd  # Payload data
│       │   │   │   │   │       └── metadata.json    # Metadata
│       │   │   │   ├── shot010/       # Shot 010
│       │   │   │   │   ├── anim/       # Department: animation
│       │   │   │   │   │   ├── version/  # Versioning directory
│       │   │   │   │   │   │   ├── v001/     # Version 001
│       │   │   │   │   │   │   │   ├── anim.usd     # Main animation file
│       │   │   │   │   │   │   │   ├── payload.usd  # Payload data
│       │   │   │   │   │   │   │   └── metadata.json    # Metadata
│       │   │   │   │   │   │   │
│       │   │   │   │   │   │   └── v002/     # Version 002
│       │   │   │   │   │   │       ├── anim.usd    # Main animation file
│       │   │   │   │   │   │       ├── payload.usd  # Payload data
│       │   │   │   │   │   │       └── metadata.json    # Metadata
│       │   │   │   │   │   │
│       │   │   │   │   │   └── cache/     # Cache directory
│       │   │   │   │   │       ├── fx.abc      # FX simulation cache
│       │   │   │   │   │       ├── hair.vdb    # Hair volume cache
│       │   │   │   │   │       └── metadata.json   # Cache metadata
│       │   │   │   │   │
│       │   │   │   │   ├── comp/       # Department: compositing
│       │   │   │   │   │   ├── version/  # Versioning directory
│       │   │   │   │   │   │   ├── v001/     # Version 001
│       │   │   │   │   │   │   │   ├── comp.nk      # Main composite file
│       │   │   │   │   │   │   │   └── metadata.json    # Metadata
│       │   │   │   │   │   │   │
│       │   │   │   │   │   │   └── v002/     # Version 002
│       │   │   │   │   │
│       │   │   │   │   ├── fx/         # Department: effects
│       │   │   │   │   │   ├── version/  # Versioning directory
│       │   │   │   │   │   │   ├── v001/     # Version 001
│       │   │   │   │   │   │   │   ├── fx.usd    # Main fx file
│       │   │   │   │   │   │   │   └── metadata.json    # Metadata
│       │   │   │   │   │   │   │
│       │   │   │   │   │   │   └── v002/     # Version 002
│       │   │   │   │   |   └── cache/     # Cache directory
│       │   │   │   │   |       ├── fx.abc      # FX simulation cache
│       │   │   │   │   |       ├── hair.vdb    # Hair volume cache
│       │   │   │   │   |       └── metadata.json   # Cache metadata
│       │   │   │   │   └── master/              # General shot directory
│       │   │   │   │       ├── version/  # Versioning directory
│       │   │   │   │       │   ├── v001/     # Version 001
│       │   │   │   │       │   │   ├──shot.usd   # Main shot config usd
│       │   │   │   │       │   │   └── metadata.json    # Metadata
│       │   │   │   │       │   └── v002/     # Version 002
│       │   │   │   │       │
│       │   │   │   │       └── cache/     # Cache directory
│       │   │   │   │           ├── fx.abc      # FX simulation cache
│       │   │   │   │           ├── hair.vdb    # Hair volume cache
│       │   │   │   │           └── meta.json   # Cache metadata
│       │   │   │   │
│       │   │   │   ├── shot020/       # Shot 020
│       │   │   │   │   ├── anim/       # Department: animation
│       │   │   │   │   │   └── version/  # Versioning directory
│       │   │   │   │   │       └── v001/     # Version 001
│       │   │   │   │   │
│       │   │   │   │   └── shot/       # General shot directory
│       │   │   │   │       └── version/  # Versioning directory
│       │   │   │   │           └── v001/     # Version 001
│       │   │   │   │
│       │   │   │   └── shot030/       # Shot 030
│       │   │   │       ├── anim/       # Department: animation
│       │   │   │       │   └── version/  # Versioning directory
│       │   │   │       │       └── v001/     # Version 001
│       │   │   │       │
│       │   │   │       └── shot/       # General shot directory
│       │   │   │           └── version/  # Versioning directory
│       │   │   │               └── v001/     # Version 001
│       │   │   │
│       │   │   └── seq002/            # Sequence 002
│       │   │       ├── shot010/       # Shot 010
│       │   │       │   ├── anim/       # Department: animation
│       │   │       │   │   └── version/  # Versioning directory
│       │   │       │   │       └── v001/     # Version 001
│       │   │       │   │
│       │   │       │   └── shot/       # General shot directory
│       │   │       │       └── version/  # Versioning directory
│       │   │       │           └── v001/     # Version 001
│       │   │       │
│       │   │       └── ...
│       │   │
│       │   └── ep02/                  # Episode 02
│       │       └── ...
│       │
│       └── s02/                       # Series (or show) 02
│           └── ...
│
├── work/                              # Work in progress
│   ├── assets/                        # WIP assets
│   │   ├── characters/                # Asset type: characters
│   │   │   ├── hero/                  # Asset: hero character
│   │   │   │   ├── model/             # Department: modeling
│   │   │   │   │   ├── artist1/       # Artist workspace
│   │   │   │   │   │   ├── hero.blend # Work files
│   │   │   │   │   │   └── ...
│   │   │   │   │   │
│   │   │   │   │   └── artist2/       # Artist workspace
│   │   │   │   │       └── ...
│   │   │   │   │
│   │   │   │   ├── rig/               # Department: rigging
│   │   │   │   │   └── ...
│   │   │   │   │
│   │   │   │   ├── texture/           # Department: texturing
│   │   │   │   │   └── ...
│   │   │   │   │
│   │   │   │   └── cache/             # Department: simulation/caches
│   │   │   │       ├── artist1/       # Artist workspace
│   │   │   │       │   ├── cloth/     # Cloth simulation
│   │   │   │       │   └── fur/       # Fur simulation
│   │   │   │       │
│   │   │   │       └── artist2/       # Artist workspace
│   │   │   │           └── ...
│   │   │   │
│   │   │   └── villain/               # Asset: villain character
│   │   │       └── ...
│   │   │
│   │   ├── environments/              # Asset type: environments
│   │   └── props/                     # Asset type: props
│   │
│   └── shots/                         # WIP shots
│       ├── s01/                       # Series (or show) 01
│       │   ├── ep01/                  # Episode 01
│       │   │   ├── seq001/            # Sequence 001
│       │   │   │   ├── shot010/       # Shot 010
│       │   │   │   │   ├── anim/      # Department: animation
│       │   │   │   │   │   ├── artist1/ # Artist workspace
│       │   │   │   │   │   └── artist2/ # Artist workspace
│       │   │   │   │   │
│       │   │   │   │   ├── comp/      # Department: compositing
│       │   │   │   │   │   └── ...
│       │   │   │   │   │
│       │   │   │   │   └── fx/        # Department: effects
│       │   │   │   │       ├── artist1/ # Artist workspace
│       │   │   │   │       │   ├── sim/ # Simulation files
│       │   │   │   │       │   └── cache/ # Cache files
│       │   │   │   │       │
│       │   │   │   │       └── artist2/ # Artist workspace
│       │   │   │   │
│       │   │   │   └── ...
│       │   │   │
│       │   │   └── ...
│       │   │
│       │   └── ...
│       │
│       └── ...
│
├── output/                            # Output files
│   ├── renders/                       # Rendered frames
│   │   ├── s01/                       # Series 01
│   │   │   ├── ep01/                  # Episode 01
│   │   │   │   ├── seq001/            # Sequence 001
│   │   │   │   │   ├── shot010/       # Shot 010
│   │   │   │   │   │   ├── comp/       # Department: compositing
│   │   │   │   │   │   │   ├── version/  # Versioning directory
│   │   │   │   │   │   │   │   ├── v001/     # Version 001
│   │   │   │   │   │   │   │   │   ├── beauty/    # Beauty layer
│   │   │   │   │   │   │   │   │   ├── depth/     # Depth layer
│   │   │   │   │   │   │   │   │   └── ...        # Other render layers
│   │   │   │   │   │   │   │   │
│   │   │   │   │   │   │   │   └── v002/     # Version 002
│   │   │   │   │   │   │   │       ├── beauty/    # Beauty layer
│   │   │   │   │   │   │   │       └── depth/     # Depth layer
│   │   │   │   │   │   │   │
│   │   │   │   │   │   │   └── cache/     # Cache directory
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── lighting/   # Department: lighting
│   │   │   │   │   │   │   ├── version/  # Versioning directory
│   │   │   │   │   │   │   │   ├── v001/     # Version 001
│   │   │   │   │   │   │   │   │   ├── beauty/    # Beauty layer
│   │   │   │   │   │   │   │   │   └── specular/  # Specular layer
│   │   │   │   │   │   │   │   │
│   │   │   │   │   │   │   │   └── v002/     # Version 002
│   │   │   │   │   │   │
│   │   │   │   │   │   └── render/     # Department: rendering
│   │   │   │   │   │       ├── version/  # Versioning directory
│   │   │   │   │   │       │   ├── v001/     # Version 001
│   │   │   │   │   │       │   │   ├── beauty/    # Beauty layer
│   │   │   │   │   │       │   │   ├── depth/     # Depth layer
│   │   │   │   │   │       │   │   └── normal/    # Normal layer
│   │   │   │   │   │       │   │
│   │   │   │   │   │       │   └── v002/     # Version 002
│   │   │   │   │   │       │
│   │   │   │   │   │       └── cache/     # Cache directory
│   │   │   │   │   │
│   │   │   │   │   └── shot020/       # Shot 020
│   │   │   │   │       ├── comp/       # Department: compositing
│   │   │   │   │       │   ├── version/  # Versioning directory
│   │   │   │   │       │   │   └── v001/     # Version 001
│   │   │   │   │       │
│   │   │   │   │       └── render/     # Department: rendering
│   │   │   │   │           └── version/  # Versioning directory
│   │   │   │   │               └── v001/     # Version 001
│   │   │   │   │
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── ...
│   │   │
│   │   └── ...
│   │
│   ├── cache/                         # Working/Intermediate caches
│   │   ├── alembic/                   # Alembic caches
│   │   │   ├── s01/                   # Series 01
│   │   │   │   ├── ep01/              # Episode 01
│   │   │   │   │   ├── seq001/        # Sequence 001
│   │   │   │   │   │   ├── shot010/   # Shot 010
│   │   │   │   │   │   │   ├── cloth/ # Cloth simulation
│   │   │   │   │   │   │   └── fx/    # FX simulation
│   │   │   │   │   │   │
│   │   │   │   │   │   └── ...
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │   │
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── ...
│   │   │
│   │   └── vdb/                       # VDB caches
│   │       └── ...
│   │
│   └── deliverables/                  # Final deliverables
│       ├── s01/                       # Series 01
│       │   ├── ep01/                  # Episode 01
│       │   │   ├── video/             # Final video files
│       │   │   │   ├── ep01_final.mp4 # Final episode
│       │   │   │   └── ...
│       │   │   │
│       │   │   ├── audio/             # Final audio files
│       │   │   └── subtitles/         # Subtitle files
│       │   │
│       │   └── ...
│       │
│       └── ...
│
├── shared/                            # Shared resources
│   ├── reference/                     # Reference materials
│   ├── luts/                          # LUTs for color correction
│   ├── hdri/                          # HDRI maps
│   └── scripts/                       # Shared scripts and tools
│
└── temp/                              # Temporary files
    └── ...
```

## Note on Cache Data

In the Bifrost system, cache data is handled in multiple locations:

1. **Published Caches**
   - Location: `published/assets/{ASSET_TYPE}/{ASSET_NAME}/{VERSION}/cache/` and
     `published/shots/{SERIES}/{EPISODE}/{SEQUENCE}/{SHOT}/{VERSION}/cache/`
   - Purpose: Final, approved cache files that are part of the published asset/shot
   - Includes: Simulation caches (alembic, vdb), hair, cloth, fx, etc.
   - These are versioned and tracked like other published content

2. **Working Caches**
   - Location: `work/assets/{ASSET_TYPE}/{ASSET_NAME}/cache/{USER}/` and
     `work/shots/{SERIES}/{EPISODE}/{SEQUENCE}/{SHOT}/fx/{USER}/cache/`
   - Purpose: Work-in-progress simulation caches by individual artists
   - These are typically not versioned in the same way as published content

3. **Output/Intermediate Caches**
   - Location: `output/cache/{CACHE_TYPE}/{SERIES}/{EPISODE}/{SEQUENCE}/{SHOT}/`
   - Purpose: Intermediate caches used across departments or for rendering
   - Organized by cache type (alembic, vdb, etc.)
   - These may be regenerated or modified during production

## Customizing the Project Structure

The project structure is customizable via configuration files. You can modify the following in the project configuration:

1. Change the main directories (work, published, output)
2. Adjust the asset type categories
3. Modify the department names and organization
4. Change the versioning scheme
5. Add custom directories for specific project needs

## Project Structure Configuration

The project structure is determined by templates in the configuration files:

1. **Main Configuration**: `config/default_config.yaml`
   - Defines the main directory names and paths

2. **Folder Mapping**: `config/pipeline/folder_mapping.yaml`
   - Defines the detailed folder structure templates
   - Can be customized per studio

For example, to ensure caches are properly published, you would modify the folder mapping to include:

```yaml
# In folder_mapping.yaml
studio_mappings:
  main_studio:
    # Add a specific path for published caches
    asset_published_cache_path: "${project.root_path}/${folder_structure.published_root}/assets/{ASSET_TYPE}/{ASSET_NAME}/{VERSION}/cache/{CACHE_TYPE}/"
    shot_published_cache_path: "${project.root_path}/${folder_structure.published_root}/shots/{SERIES}/{EPISODE}/{SEQUENCE}/{SHOT}/{VERSION}/cache/{CACHE_TYPE}/"

    # Keep the working/intermediate cache path
    cache_path: "${project.root_path}/${folder_structure.output_root}/cache/{CACHE_TYPE}/{SERIES}/{EPISODE}/{SEQUENCE}/{SHOT}/"
```

## Structure Variables

The folder structure templates support the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{PROJECT}` | Project name | "MyProject" |
| `{ASSET_TYPE}` | Type of asset | "characters" |
| `{ASSET_NAME}` | Name of the asset | "hero" |
| `{VERSION}` | Version number | "v001" |
| `{DEPARTMENT}` | Department name | "model" |
| `{USER}` | Artist username | "artist1" |
| `{SERIES}` | Series identifier | "s01" |
| `{EPISODE}` | Episode identifier | "ep01" |
| `{SEQUENCE}` | Sequence identifier | "seq001" |
| `{SHOT}` | Shot identifier | "shot010" |
| `{LAYER}` | Render layer | "beauty" |
| `{CACHE_TYPE}` | Cache format | "alembic" |
| `{DELIVERABLE_TYPE}` | Deliverable type | "video" |
| `{TASK}` | Task name | "modeling" |
| `{DATE}` | Current date | "2025-04-03" |

## Creating a New Project

When you run `bifrost project create --name "ProjectName" --type animation`, the system will:

1. Create the directory structure based on the templates
2. Initialize the project database
3. Create the project configuration file
4. Set up basic asset types and departments

You can also use a custom template:

```bash
bifrost project create --name "ProjectName" --template "feature_film"
```

This would use a different set of folder templates specifically configured for feature film production.
