# Revised Asset Directory Structure

```
published/
│
├── asset/                           # Root asset directory
│   │
│   ├── characters/                  # Asset category: characters
│   │   │
│   │   ├── hero/                    # Asset name: hero
│   │   │   │
│   │   │   ├── model/               # Department: model
│   │   │   │   │
│   │   │   │   ├── version/         # Versioning directory
│   │   │   │   │   │
│   │   │   │   │   ├── v001/        # Version number
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   └── meta.json    # Metadata
│   │   │   │   │   │
│   │   │   │   │   ├── v002/        # Next version
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── asset.usd
│   │   │   │   │   │   ├── payload.usd
│   │   │   │   │   │   └── meta.json
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   ├── asset/               # General asset directory
│   │   │   │   │
│   │   │   │   ├── version/         # Versioning directory
│   │   │   │   │   │
│   │   │   │   │   ├── v001/        # Version number
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── asset.usd    # Main asset file
│   │   │   │   │   │   ├── payload.usd  # Payload data
│   │   │   │   │   │   └── meta.json    # Metadata
│   │   │   │   │   │
│   │   │   │   │   ├── v002/        # Next version
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── asset.usd
│   │   │   │   │   │   ├── payload.usd
│   │   │   │   │   │   └── meta.json
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   ├── rig/                 # Department: rig
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   ├── v001/
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── asset.usd
│   │   │   │   │   │   ├── payload.usd
│   │   │   │   │   │   └── meta.json
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   └── texture/             # Department: texture
│   │   │       │
│   │   │       ├── version/
│   │   │       │   │
│   │   │       │   ├── v001/
│   │   │       │   │   │
│   │   │       │   │   ├── asset.usd
│   │   │       │   │   ├── payload.usd
│   │   │       │   │   └── meta.json
│   │   │       │   │
│   │   │       │   └── ...
│   │   │
│   │   ├── villain/                 # Another character asset
│   │   │   │
│   │   │   ├── model/
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   ├── asset/
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   └── ...
│   │   │
│   │   └── ...
│   │
│   ├── environments/                # Asset category: environments
│   │   │
│   │   ├── forest/                  # Asset name: forest
│   │   │   │
│   │   │   ├── model/
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   ├── asset/
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   └── ...
│   │   │
│   │   └── ...
│   │
│   ├── props/                       # Asset category: props
│   │   │
│   │   ├── sword/                   # Asset name: sword
│   │   │   │
│   │   │   ├── model/
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   ├── asset/
│   │   │   │   │
│   │   │   │   ├── version/
│   │   │   │   │   │
│   │   │   │   │   └── ...
│   │   │   │
│   │   │   └── ...
│   │   │
│   │   └── ...
│   │
│   └── ...
│
└── ...
```

## Key Changes:

1. Each asset (e.g., hero, villain, forest, sword) now has:
   - Department-specific directories (model, rig, texture, etc.)
   - A general "asset" directory for the complete asset

2. Both department directories and the asset directory follow the same versioning structure:
   ```
   version/
   ├── v001/
   │   ├── asset.usd    # Main asset file
   │   ├── payload.usd  # Payload data
   │   └── meta.json    # Metadata
   ├── v002/
   │   └── ...
   └── ...
   ```

3. The full path to a specific asset version would be:
   - For department-specific files:
     `published/asset/characters/hero/model/version/v001/asset.usd`
   
   - For the complete asset:
     `published/asset/characters/hero/asset/version/v001/asset.usd`

This structure allows you to:
- Maintain department-specific versions (model, rig, texture)
- Keep complete asset versions in the "asset" directory
- Have consistent versioning across all assets and departments
- Store the required files (asset.usd, payload.usd, meta.json) in each version directory
