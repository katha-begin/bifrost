#!/usr/bin/env python
# usd_service.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import logging
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from ...core.config import get_config
from ...models.usd_asset import UsdAssetVersion, UsdStageInfo, UsdPrimInfo

logger = logging.getLogger(__name__)

# Check if USD is available
USD_AVAILABLE = False
try:
    from pxr import Usd, UsdGeom, Sdf, Ar, UsdUtils
    USD_AVAILABLE = True
except ImportError:
    logger.warning("OpenUSD modules could not be imported. USD functionality will be disabled.")

class UsdService:
    """
    Service for working with USD data.
    
    This service provides methods for creating, reading, and manipulating USD files,
    including support for USD's composition and layering capabilities.
    """
    
    def __init__(self):
        """Initialize the USD service."""
        if not USD_AVAILABLE:
            logger.warning("USD service initialized but USD libraries are not available.")
            return
        
        self.usd_enabled = get_config("usd.enabled", True)
        if not self.usd_enabled:
            logger.info("USD functionality is disabled in configuration.")
            return
        
        # Set up USD stage cache
        self.stage_cache_size_mb = get_config("usd.stage_cache_size_mb", 1024)
        # Set up USD supported formats
        self.supported_formats = get_config("usd.supported_formats", ["usd", "usda", "usdc", "usdz"])
        # Default up axis
        self.default_up_axis = get_config("usd.default_up_axis", "Y")
        # Version control strategy
        self.version_strategy = get_config("usd.version_strategy", "layer_stack")
        # Namespace prefix for creating prims
        self.namespace_prefix = get_config("usd.namespace_prefix", "bifrost")
        
        logger.info("USD service initialized.")
        
    def is_available(self) -> bool:
        """Check if USD functionality is available."""
        return USD_AVAILABLE and self.usd_enabled
        
    def open_stage(self, file_path: Union[str, Path]) -> Optional[Usd.Stage]:
        """
        Open a USD stage from a file path.
        
        Args:
            file_path: Path to the USD file
            
        Returns:
            The USD stage object or None if it couldn't be opened
        """
        if not self.is_available():
            return None
            
        try:
            file_path = str(file_path)
            stage = Usd.Stage.Open(file_path)
            return stage
        except Exception as e:
            logger.error(f"Error opening USD stage {file_path}: {e}")
            return None
    
    def create_new_stage(self, 
                       file_path: Union[str, Path], 
                       up_axis: str = None,
                       default_prim_name: Optional[str] = None) -> Optional[Usd.Stage]:
        """
        Create a new USD stage.
        
        Args:
            file_path: Path where the new USD file should be created
            up_axis: Up axis for the stage ("Y" or "Z")
            default_prim_name: Name for the default prim to create
            
        Returns:
            The new USD stage or None if creation failed
        """
        if not self.is_available():
            return None
            
        try:
            file_path = str(file_path)
            
            # Create the stage
            stage = Usd.Stage.CreateNew(file_path)
            if not stage:
                logger.error(f"Failed to create USD stage at {file_path}")
                return None
                
            # Set up axis
            if up_axis is None:
                up_axis = self.default_up_axis
                
            if up_axis.upper() in ["Y", "Z"]:
                UsdGeom.SetStageUpAxis(stage, up_axis.upper())
            
            # Create and set default prim if requested
            if default_prim_name:
                default_prim = stage.DefinePrim(f"/{default_prim_name}")
                stage.SetDefaultPrim(default_prim)
                
            # Save the stage
            stage.Save()
            
            return stage
            
        except Exception as e:
            logger.error(f"Error creating USD stage {file_path}: {e}")
            return None
    
    def save_stage(self, stage: Usd.Stage) -> bool:
        """
        Save changes to a USD stage.
        
        Args:
            stage: The USD stage to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
            
        try:
            stage.Save()
            return True
        except Exception as e:
            logger.error(f"Error saving USD stage: {e}")
            return False
            
    def extract_stage_info(self, stage: Usd.Stage) -> UsdStageInfo:
        """
        Extract key information from a USD stage.
        
        Args:
            stage: The USD stage to analyze
            
        Returns:
            UsdStageInfo object containing stage metadata and structure
        """
        if not self.is_available():
            return None
            
        try:
            root_layer = stage.GetRootLayer()
            
            # Get referenced layers
            referenced_layers = []
            for layer in stage.GetUsedLayers():
                if layer != root_layer:
                    referenced_layers.append(Path(layer.realPath))
            
            # Get default prim
            default_prim_name = None
            if stage.GetDefaultPrim():
                default_prim_name = stage.GetDefaultPrim().GetName()
                
            # Get time code range
            start_timeframe = stage.GetStartTimeCode()
            end_timeframe = stage.GetEndTimeCode()
            
            # Get frame rate and up axis
            timeCodesPerSecond = root_layer.timeCodesPerSecond
            upAxis = UsdGeom.GetStageUpAxis(stage)
            
            # Extract variant information
            variants = {}
            for prim in stage.Traverse():
                for variantSet in prim.GetVariantSets().GetNames():
                    variantSet_obj = prim.GetVariantSet(variantSet)
                    if variantSet not in variants:
                        variants[variantSet] = []
                    for variant in variantSet_obj.GetVariantNames():
                        if variant not in variants[variantSet]:
                            variants[variantSet].append(variant)
            
            # Extract prim information
            prims = {}
            for prim in stage.Traverse():
                prim_path = str(prim.GetPath())
                prim_type = prim.GetTypeName()
                
                # Get properties and attributes
                properties = {}
                attributes = {}
                for prop in prim.GetProperties():
                    properties[prop.GetName()] = str(prop.GetTypeName())
                    if prop.IsAttribute():
                        attr = prop.As(Usd.Attribute)
                        if attr.HasValue():
                            attributes[prop.GetName()] = str(attr.Get())
                
                # Get metadata
                metadata = {}
                for key in prim.GetAllMetadata().keys():
                    metadata[key] = str(prim.GetMetadata(key))
                
                # Get children
                children = []
                for child in prim.GetChildren():
                    children.append(str(child.GetPath()))
                
                prims[prim_path] = UsdPrimInfo(
                    path=prim_path,
                    type=prim_type,
                    properties=properties,
                    attributes=attributes,
                    metadata=metadata,
                    children=children
                )
            
            # Create stage info
            stage_info = UsdStageInfo(
                root_layer_path=Path(root_layer.realPath),
                referenced_layers=referenced_layers,
                prims=prims,
                default_prim=default_prim_name,
                up_axis=upAxis,
                time_code_range=(start_timeframe, end_timeframe),
                frame_rate=timeCodesPerSecond,
                metadata={},  # Additional metadata could be added here
                variants=variants
            )
            
            return stage_info
            
        except Exception as e:
            logger.error(f"Error extracting stage info: {e}")
            return None
    
    def create_reference(self, 
                        stage: Usd.Stage, 
                        target_prim_path: str, 
                        reference_file_path: Union[str, Path], 
                        reference_prim_path: Optional[str] = None) -> bool:
        """
        Add a reference to a prim in a USD stage.
        
        Args:
            stage: The USD stage to modify
            target_prim_path: Path to the prim that will reference another asset
            reference_file_path: Path to the USD file to reference
            reference_prim_path: Path to the specific prim within the referenced file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
            
        try:
            # Get or create the target prim
            target_prim = stage.GetPrimAtPath(target_prim_path)
            if not target_prim:
                # Create the prim hierarchy if it doesn't exist
                target_prim = stage.DefinePrim(target_prim_path)
                if not target_prim:
                    logger.error(f"Failed to create prim at {target_prim_path}")
                    return False
            
            # Add the reference
            references = target_prim.GetReferences()
            if reference_prim_path:
                references.AddReference(str(reference_file_path), reference_prim_path)
            else:
                references.AddReference(str(reference_file_path))
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding reference: {e}")
            return False
    
    def create_sublayer(self, 
                       stage: Usd.Stage, 
                       sublayer_path: Union[str, Path], 
                       position: int = -1) -> bool:
        """
        Add a sublayer to a USD stage.
        
        Args:
            stage: The USD stage to modify
            sublayer_path: Path to the USD file to add as a sublayer
            position: Position in the layer stack (-1 means strongest/top)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
            
        try:
            root_layer = stage.GetRootLayer()
            sublayer_paths = root_layer.subLayerPaths
            
            # Check if the sublayer already exists
            sublayer_path_str = str(sublayer_path)
            if sublayer_path_str in sublayer_paths:
                logger.warning(f"Sublayer {sublayer_path_str} already exists in stage")
                return True
            
            # Add the sublayer at the specified position
            if position < 0:
                sublayer_paths.insert(0, sublayer_path_str)
            elif position >= len(sublayer_paths):
                sublayer_paths.append(sublayer_path_str)
            else:
                sublayer_paths.insert(position, sublayer_path_str)
            
            root_layer.subLayerPaths = sublayer_paths
            
            # Save the stage to reflect changes
            stage.Save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding sublayer: {e}")
            return False
    
    def create_variant(self, 
                      stage: Usd.Stage, 
                      prim_path: str, 
                      variant_set_name: str, 
                      variant_name: str) -> bool:
        """
        Create a variant for a prim.
        
        Args:
            stage: The USD stage to modify
            prim_path: Path to the prim to add the variant to
            variant_set_name: Name of the variant set
            variant_name: Name of the variant
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
            
        try:
            # Get or create the prim
            prim = stage.GetPrimAtPath(prim_path)
            if not prim:
                logger.error(f"Prim {prim_path} does not exist")
                return False
            
            # Get or create the variant set
            variant_sets = prim.GetVariantSets()
            variant_set = variant_sets.GetVariantSet(variant_set_name)
            if not variant_set:
                variant_set = variant_sets.AddVariantSet(variant_set_name)
            
            # Check if the variant already exists
            variant_names = variant_set.GetVariantNames()
            if variant_name not in variant_names:
                # Add the variant
                variant_set.AddVariant(variant_name)
            
            # Set the current variant selection
            variant_set.SetVariantSelection(variant_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating variant: {e}")
            return False
    
    def select_variant(self, 
                     stage: Usd.Stage, 
                     prim_path: str, 
                     variant_set_name: str, 
                     variant_name: str) -> bool:
        """
        Select a variant for a prim.
        
        Args:
            stage: The USD stage to modify
            prim_path: Path to the prim
            variant_set_name: Name of the variant set
            variant_name: Name of the variant to select
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
            
        try:
            # Get the prim
            prim = stage.GetPrimAtPath(prim_path)
            if not prim:
                logger.error(f"Prim {prim_path} does not exist")
                return False
            
            # Get the variant set
            variant_sets = prim.GetVariantSets()
            variant_set = variant_sets.GetVariantSet(variant_set_name)
            if not variant_set:
                logger.error(f"Variant set {variant_set_name} does not exist")
                return False
            
            # Check if the variant exists
            variant_names = variant_set.GetVariantNames()
            if variant_name not in variant_names:
                logger.error(f"Variant {variant_name} does not exist in set {variant_set_name}")
                return False
            
            # Set the variant selection
            variant_set.SetVariantSelection(variant_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error selecting variant: {e}")
            return False
    
    def flatten_stage(self, 
                    source_stage: Usd.Stage, 
                    output_path: Union[str, Path] = None) -> Optional[Usd.Stage]:
        """
        Flatten a USD stage to a single layer.
        
        Args:
            source_stage: The USD stage to flatten
            output_path: Path where the flattened USD file should be saved
            
        Returns:
            The flattened USD stage or None if flattening failed
        """
        if not self.is_available():
            return None
            
        try:
            # Flatten the stage
            flattened_layer = UsdUtils.FlattenLayerStack(source_stage)
            
            if output_path:
                # Save the flattened layer to the specified path
                flattened_layer.Export(str(output_path))
                
                # Open and return the new stage
                return self.open_stage(output_path)
            else:
                # Create an anonymous in-memory stage
                in_memory_stage = Usd.Stage.Open(flattened_layer)
                return in_memory_stage
                
        except Exception as e:
            logger.error(f"Error flattening stage: {e}")
            return None
    
    def convert_to_usd(self, 
                     source_file: Union[str, Path], 
                     output_path: Union[str, Path] = None) -> Optional[Path]:
        """
        Convert a file to USD format.
        
        Args:
            source_file: Path to the source file
            output_path: Path where the converted USD file should be saved
            
        Returns:
            Path to the converted USD file or None if conversion failed
        """
        if not self.is_available():
            return None
            
        # Handle output path
        source_path = Path(source_file)
        if output_path is None:
            output_path = source_path.with_suffix('.usd')
        else:
            output_path = Path(output_path)
        
        source_ext = source_path.suffix.lower()
        
        # Check if conversion is enabled
        conversion_enabled = get_config("usd.conversion.enabled", True)
        if not conversion_enabled:
            logger.error("USD conversion is disabled in configuration")
            return None
        
        # Get conversion temp directory
        temp_dir = get_config("usd.conversion.temp_dir", "temp/usd_conversion")
        temp_dir_path = Path(temp_dir)
        temp_dir_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Handle different file formats
            if source_ext == '.abc':  # Alembic
                import subprocess
                cmd = ['usdcat', '--in', str(source_path), '--out', str(output_path)]
                subprocess.run(cmd, check=True)
                return output_path
                
            elif source_ext == '.obj':  # OBJ
                import subprocess
                cmd = ['usdcat', '--in', str(source_path), '--out', str(output_path)]
                subprocess.run(cmd, check=True)
                return output_path
                
            elif source_ext == '.fbx':  # FBX
                # This requires the FBX2USD tool
                import subprocess
                cmd = ['FBX2USD', str(source_path), str(output_path)]
                subprocess.run(cmd, check=True)
                return output_path
                
            else:
                logger.error(f"Unsupported format for conversion: {source_ext}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting {source_path} to USD: {e}")
            return None
    
    def create_version_layer(self, 
                          base_layer_path: Union[str, Path], 
                          version_number: int) -> Optional[Path]:
        """
        Create a new version layer for layer stack versioning.
        
        Args:
            base_layer_path: Path to the base USD file
            version_number: Version number for the new layer
            
        Returns:
            Path to the new version layer or None if creation failed
        """
        if not self.is_available():
            return None
            
        try:
            base_path = Path(base_layer_path)
            
            # Create the version layer file path
            version_dir = base_path.parent / f"v{version_number:03d}"
            version_dir.mkdir(parents=True, exist_ok=True)
            
            version_file = version_dir / f"{base_path.stem}_v{version_number:03d}{base_path.suffix}"
            
            # Create a new layer that references the base layer
            layer = Sdf.Layer.CreateNew(str(version_file))
            
            # If this is the first version, don't add any sublayers
            if version_number > 1:
                # Add previous version as sublayer
                prev_version = version_number - 1
                prev_file = base_path.parent / f"v{prev_version:03d}" / f"{base_path.stem}_v{prev_version:03d}{base_path.suffix}"
                
                if prev_file.exists():
                    layer.subLayerPaths = [str(prev_file)]
                else:
                    # If previous version file doesn't exist, reference the base layer
                    layer.subLayerPaths = [str(base_layer_path)]
            
            # Add timestamp metadata
            layer.SetStartTimeCode(1)
            layer.SetEndTimeCode(1)
            
            # Add version metadata
            layer.customLayerData = {
                "version": version_number,
                "bifrost_asset_version": version_number
            }
            
            # Save the layer
            layer.Save()
            
            return version_file
            
        except Exception as e:
            logger.error(f"Error creating version layer: {e}")
            return None
