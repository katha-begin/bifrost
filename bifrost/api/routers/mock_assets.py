"""
Mock API endpoints for assets.
"""

from typing import Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Path, Query, status
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

# In-memory storage for mock data
assets_db = {}
assembly_components_db = {}

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_asset(asset: Dict) -> Dict:
    """Create a new asset."""
    asset_id = str(uuid.uuid4())
    asset["id"] = asset_id
    asset["created_at"] = datetime.now().isoformat()
    asset["modified_at"] = datetime.now().isoformat()
    
    # Default values
    asset.setdefault("status", "pending")
    asset.setdefault("is_assembly", False)
    asset.setdefault("tags", [])
    asset.setdefault("metadata", {})
    
    # Store the asset
    assets_db[asset_id] = asset
    
    # Process contained assets if this is an assembly
    if asset.get("is_assembly") and "contained_assets" in asset:
        for contained_asset_id in asset.get("contained_assets", []):
            component_id = str(uuid.uuid4())
            component = {
                "id": component_id,
                "assembly_id": asset_id,
                "component_asset_id": contained_asset_id,
                "transform": {},
                "override_parameters": {}
            }
            assembly_components_db[component_id] = component
    
    return asset


@router.get("/")
async def list_assets(
    type_id: Optional[str] = None,
    is_assembly: Optional[bool] = None,
    status: Optional[str] = None
) -> List[Dict]:
    """List all assets with optional filtering."""
    filtered_assets = list(assets_db.values())
    
    if type_id:
        filtered_assets = [a for a in filtered_assets if a.get("asset_type_id") == type_id]
    
    if is_assembly is not None:
        filtered_assets = [a for a in filtered_assets if a.get("is_assembly") == is_assembly]
    
    if status:
        filtered_assets = [a for a in filtered_assets if a.get("status") == status]
    
    return filtered_assets


@router.get("/{asset_id}")
async def get_asset(asset_id: str = Path(..., description="The ID of the asset to retrieve")) -> Dict:
    """Get a specific asset by ID."""
    if asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = assets_db[asset_id].copy()
    
    # If this is an assembly, include component details
    if asset.get("is_assembly", False):
        components = [c for c in assembly_components_db.values() if c["assembly_id"] == asset_id]
        asset["components"] = components
    
    return asset


@router.put("/{asset_id}")
async def update_asset(
    asset_update: Dict,
    asset_id: str = Path(..., description="The ID of the asset to update")
) -> Dict:
    """Update an existing asset."""
    if asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update the asset
    asset = assets_db[asset_id]
    
    # Don't allow changing certain fields
    protected_fields = ["id", "created_at", "created_by"]
    for field, value in asset_update.items():
        if field not in protected_fields:
            asset[field] = value
    
    asset["modified_at"] = datetime.now().isoformat()
    
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: str = Path(..., description="The ID of the asset to delete")) -> None:
    """Delete an asset."""
    if asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check if this asset is used in any assemblies
    for component in assembly_components_db.values():
        if component["component_asset_id"] == asset_id:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete asset that is used in assemblies"
            )
    
    # Delete all assembly components if this is an assembly
    components_to_delete = [
        comp_id for comp_id, comp in assembly_components_db.items() 
        if comp["assembly_id"] == asset_id
    ]
    
    for comp_id in components_to_delete:
        del assembly_components_db[comp_id]
    
    # Delete the asset
    del assets_db[asset_id]


@router.post("/{asset_id}/components")
async def add_component_to_assembly(
    component: Dict,
    asset_id: str = Path(..., description="The ID of the assembly asset")
) -> Dict:
    """Add a component to an assembly asset."""
    if asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Assembly asset not found")
    
    assembly = assets_db[asset_id]
    if not assembly.get("is_assembly", False):
        raise HTTPException(status_code=400, detail="Asset is not an assembly")
    
    component_asset_id = component.get("component_asset_id")
    if not component_asset_id or component_asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Component asset not found")
    
    # Create the assembly component
    component_id = str(uuid.uuid4())
    new_component = {
        "id": component_id,
        "assembly_id": asset_id,
        "component_asset_id": component_asset_id,
        "transform": component.get("transform", {}),
        "override_parameters": component.get("override_parameters", {})
    }
    
    assembly_components_db[component_id] = new_component
    assembly["modified_at"] = datetime.now().isoformat()
    
    return new_component


@router.get("/{asset_id}/components")
async def get_assembly_components(
    asset_id: str = Path(..., description="The ID of the assembly asset")
) -> List[Dict]:
    """Get all components of an assembly asset."""
    if asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Assembly asset not found")
    
    assembly = assets_db[asset_id]
    if not assembly.get("is_assembly", False):
        raise HTTPException(status_code=400, detail="Asset is not an assembly")
    
    components = [c for c in assembly_components_db.values() if c["assembly_id"] == asset_id]
    
    # Enhance with component asset details
    for component in components:
        component_asset_id = component["component_asset_id"]
        if component_asset_id in assets_db:
            component["asset_details"] = {
                "name": assets_db[component_asset_id]["name"],
                "type": assets_db[component_asset_id].get("asset_type_id"),
                "status": assets_db[component_asset_id].get("status")
            }
    
    return components


@router.delete("/{asset_id}/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_component_from_assembly(
    asset_id: str = Path(..., description="The ID of the assembly asset"),
    component_id: str = Path(..., description="The ID of the component to remove")
) -> None:
    """Remove a component from an assembly asset."""
    if asset_id not in assets_db:
        raise HTTPException(status_code=404, detail="Assembly asset not found")
    
    if component_id not in assembly_components_db:
        raise HTTPException(status_code=404, detail="Component not found")
    
    component = assembly_components_db[component_id]
    if component["assembly_id"] != asset_id:
        raise HTTPException(status_code=400, detail="Component does not belong to this assembly")
    
    # Remove the component
    del assembly_components_db[component_id]
    
    # Update the assembly
    assets_db[asset_id]["modified_at"] = datetime.now().isoformat()