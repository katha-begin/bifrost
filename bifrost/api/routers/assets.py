from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ...services.asset_service import AssetService
from ..main import get_current_user

router = APIRouter()
asset_service = AssetService()

class AssetBase(BaseModel):
    name: str
    asset_type: str
    description: Optional[str] = None
    status: str = "concept"
    metadata: Optional[dict] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: str
    created_at: datetime
    created_by: str
    modified_at: datetime
    modified_by: Optional[str]
    thumbnail_path: Optional[str]
    preview_path: Optional[str]

    class Config:
        from_attributes = True

@router.get("/assets/", response_model=List[Asset])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get a list of assets with optional filtering."""
    filters = {}
    if status:
        filters['status'] = status
    if asset_type:
        filters['asset_type'] = asset_type
    
    assets = asset_service.list_assets(skip=skip, limit=limit, filters=filters)
    return assets

@router.post("/assets/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: AssetCreate,
    current_user = Depends(get_current_user)
):
    """Create a new asset."""
    return asset_service.create_asset(
        name=asset.name,
        asset_type=asset.asset_type,
        description=asset.description,
        status=asset.status,
        created_by=current_user.username,
        metadata=asset.metadata
    )

@router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: str,
    current_user = Depends(get_current_user)
):
    """Get a specific asset by ID."""
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset

@router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: str,
    asset_update: AssetBase,
    current_user = Depends(get_current_user)
):
    """Update an asset."""
    try:
        updated_asset = asset_service.update_asset(
            asset_id,
            name=asset_update.name,
            asset_type=asset_update.asset_type,
            description=asset_update.description,
            status=asset_update.status,
            modified_by=current_user.username,
            metadata=asset_update.metadata
        )
        return updated_asset
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    current_user = Depends(get_current_user)
):
    """Delete an asset."""
    try:
        asset_service.delete_asset(asset_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )