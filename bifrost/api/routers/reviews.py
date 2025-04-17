from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ...services.review_service import ReviewService
from ..main import get_current_user

router = APIRouter()
review_service = ReviewService()

class ReviewBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "open"
    metadata: Optional[dict] = None

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: str
    created_at: datetime
    created_by: str
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReviewItemBase(BaseModel):
    item_id: str
    item_type: str
    version_id: str
    status: str = "pending"
    metadata: Optional[dict] = None

class ReviewItem(ReviewItemBase):
    id: str
    review_id: str
    preview_path: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/reviews/", response_model=List[Review])
async def list_reviews(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get a list of reviews with optional filtering."""
    filters = {}
    if status:
        filters['status'] = status
    
    reviews = review_service.list_reviews(skip=skip, limit=limit, filters=filters)
    return reviews

@router.post("/reviews/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    current_user = Depends(get_current_user)
):
    """Create a new review."""
    return review_service.create_review(
        name=review.name,
        description=review.description,
        status=review.status,
        created_by=current_user.username,
        metadata=review.metadata
    )

@router.get("/reviews/{review_id}", response_model=Review)
async def get_review(
    review_id: str,
    current_user = Depends(get_current_user)
):
    """Get a specific review by ID."""
    review = review_service.get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return review

@router.put("/reviews/{review_id}", response_model=Review)
async def update_review(
    review_id: str,
    review_update: ReviewBase,
    current_user = Depends(get_current_user)
):
    """Update a review."""
    try:
        updated_review = review_service.update_review(
            review_id,
            name=review_update.name,
            description=review_update.description,
            status=review_update.status,
            metadata=review_update.metadata
        )
        return updated_review
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a review."""
    try:
        review_service.delete_review(review_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Review items endpoints
@router.get("/reviews/{review_id}/items", response_model=List[ReviewItem])
async def list_review_items(
    review_id: str,
    current_user = Depends(get_current_user)
):
    """Get all items in a review."""
    items = review_service.list_review_items(review_id)
    return items

@router.post("/reviews/{review_id}/items", response_model=ReviewItem)
async def add_review_item(
    review_id: str,
    item: ReviewItemBase,
    current_user = Depends(get_current_user)
):
    """Add an item to a review."""
    return review_service.add_review_item(
        review_id=review_id,
        item_id=item.item_id,
        item_type=item.item_type,
        version_id=item.version_id,
        status=item.status,
        metadata=item.metadata
    )

@router.delete("/reviews/{review_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_review_item(
    review_id: str,
    item_id: str,
    current_user = Depends(get_current_user)
):
    """Remove an item from a review."""
    try:
        review_service.remove_review_item(review_id, item_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )