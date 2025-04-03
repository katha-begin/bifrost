#!/usr/bin/env python
# usd_asset.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from .asset import Asset, AssetVersion

# Check if USD is available
USD_AVAILABLE = False
try:
    from pxr import Usd, UsdGeom, Sdf, Ar
    USD_AVAILABLE = True
except ImportError:
    pass  # The integrations module will handle the warning

class UsdVersionStrategy(Enum):
    """Strategies for versioning USD files."""
    LAYER_STACK = "layer_stack"  # Use USD layer stacks for version control
    SEPARATE_FILES = "separate_files"  # Use separate files for each version


class UsdAssetType(Enum):
    """Types of USD assets."""
    MODEL = "model"  # 3D model
    SET = "set"  # Collection of models forming a set
    PROP = "prop"  # Prop model
    CHARACTER = "character"  # Character model
    SHADER = "shader"  # Shader network
    MATERIAL = "material"  # Material definition
    ANIMATION = "animation"  # Animation data
    LAYOUT = "layout"  # Scene layout
    LIGHT = "light"  # Lighting setup
    CAMERA = "camera"  # Camera setup
    RIG = "rig"  # Character rig
    SIMULATION = "simulation"  # Physics simulation
    POINTCLOUD = "pointcloud"  # Point cloud data
    OTHER = "other"  # Other USD asset type


@dataclass
class UsdPrimInfo:
    """Information about a specific USD prim."""
    path: str  # Prim path (e.g., "/Root/Model")
    type: str  # Prim type (e.g., "Xform", "Mesh")
    properties: Dict[str, str] = field(default_factory=dict)  # Property name -> type
    attributes: Dict[str, str] = field(default_factory=dict)  # Attribute name -> value
    metadata: Dict[str, str] = field(default_factory=dict)  # Metadata name -> value
    children: List[str] = field(default_factory=list)  # Child prim paths


@dataclass
class UsdStageInfo:
    """Information about a USD stage."""
    root_layer_path: Path
    referenced_layers: List[Path] = field(default_factory=list)
    prims: Dict[str, UsdPrimInfo] = field(default_factory=dict)  # Prim path -> PrimInfo
    default_prim: Optional[str] = None
    up_axis: str = "Y"  # Y, Z
    time_code_range: tuple = (0, 0)  # (start, end)
    frame_rate: float = 24.0
    metadata: Dict[str, str] = field(default_factory=dict)
    variants: Dict[str, List[str]] = field(default_factory=dict)  # variantSet -> variants


@dataclass
class UsdAssetVersion(AssetVersion):
    """USD-specific version information."""
    stage_info: Optional[UsdStageInfo] = None
    asset_references: List[str] = field(default_factory=list)  # Referenced asset IDs
    variant_selections: Dict[str, str] = field(default_factory=dict)  # variantSet -> selection
    stage_metadata: Dict[str, str] = field(default_factory=dict)  # Additional stage metadata
    layer_metadata: Dict[str, str] = field(default_factory=dict)  # Root layer metadata
    # For layer stack versioning:
    sublayer_path: Optional[Path] = None  # Path to the version's specific sublayer


@dataclass
class UsdAsset(Asset):
    """
    Represents a USD asset in the animation pipeline.
    
    This extends the base Asset class with USD-specific properties and methods.
    """
    usd_type: UsdAssetType = UsdAssetType.OTHER
    versions: List[UsdAssetVersion] = field(default_factory=list)  # Override type
    version_strategy: UsdVersionStrategy = UsdVersionStrategy.LAYER_STACK
    default_prim: Optional[str] = None
    compositions: Set[str] = field(default_factory=set)  # List of composed asset IDs
    payload_paths: List[str] = field(default_factory=list)  # Paths for deferred loading
    
    @property
    def latest_usd_version(self) -> Optional[UsdAssetVersion]:
        """Return the latest USD version of this asset if any versions exist."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)
    
    @property
    def latest_approved_usd_version(self) -> Optional[UsdAssetVersion]:
        """Return the latest approved or final USD version of this asset."""
        approved_versions = [v for v in self.versions 
                            if v.status in 
                            (self.AssetStatus.APPROVED, self.AssetStatus.FINAL)]
        if not approved_versions:
            return None
        return max(approved_versions, key=lambda v: v.version_number)
