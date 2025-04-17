from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ...services.shot_service import ShotService
from ..main import get_current_user

router = APIRouter()
shot_service = ShotService()

class ShotBase(BaseModel):
    code: str
    sequence_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"
    frame_start: int
    frame_end: int
    handle_pre: int = 0
    handle_post: int = 0
    metadata: Optional[dict] = None

class ShotCreate(ShotBase):
    pass

class Shot(ShotBase):
    id: str
    created_at: datetime
    created_by: str
    modified_at: datetime
    modified_by: Optional[str]
    thumbnail_path: Optional[str]

    class Config:
        from_attributes = True

@router.get("/shots/", response_model=List[Shot])
async def list_shots(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    sequence_id: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get a list of shots with optional filtering."""
    filters = {}
    if status:
        filters['status'] = status
    if sequence_id:
        filters['sequence_id'] = sequence_id
    
    shots = shot_service.list_shots(skip=skip, limit=limit, filters=filters)
    return shots

@router.post("/shots/", response_model=Shot, status_code=status.HTTP_201_CREATED)
async def create_shot(
    shot: ShotCreate,
    current_user = Depends(get_current_user)
):
    """Create a new shot."""
    return shot_service.create_shot(
        code=shot.code,
        sequence_id=shot.sequence_id,
        name=shot.name,
        description=shot.description,
        status=shot.status,
        frame_start=shot.frame_start,
        frame_end=shot.frame_end,
        handle_pre=shot.handle_pre,
        handle_post=shot.handle_post,
        created_by=current_user.username,
        metadata=shot.metadata
    )

@router.get("/shots/{shot_id}", response_model=Shot)
async def get_shot(
    shot_id: str,
    current_user = Depends(get_current_user)
):
    """Get a specific shot by ID."""
    shot = shot_service.get_shot(shot_id)
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    return shot

@router.put("/shots/{shot_id}", response_model=Shot)
async def update_shot(
    shot_id: str,
    shot_update: ShotBase,
    current_user = Depends(get_current_user)
):
    """Update a shot."""
    try:
        updated_shot = shot_service.update_shot(
            shot_id,
            code=shot_update.code,
            sequence_id=shot_update.sequence_id,
            name=shot_update.name,
            description=shot_update.description,
            status=shot_update.status,
            frame_start=shot_update.frame_start,
            frame_end=shot_update.frame_end,
            handle_pre=shot_update.handle_pre,
            handle_post=shot_update.handle_post,
            modified_by=current_user.username,
            metadata=shot_update.metadata
        )
        return updated_shot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/shots/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shot(
    shot_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a shot."""
    try:
        shot_service.delete_shot(shot_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )