#!/usr/bin/env python
# review_service.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-14

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from ..core.config import get_config
from ..models.review import Review, ReviewItem, ReviewNote, ReviewStatus, NoteStatus
from ..repositories.review_repository import ReviewRepository
from ..integrations.rv.rv_service import rv_service

# Setup logger
logger = logging.getLogger(__name__)


class ReviewService:
    """
    Service for managing review sessions in the Bifrost system.
    
    This service provides methods for creating, retrieving, and updating
    review sessions, as well as integrating with review tools like OpenRV.
    """
    
    def __init__(self):
        """Initialize the review service."""
        self.repository = ReviewRepository()
        self.enable_rv = get_config("review.rv_enabled", True)
        
    def create_review(self,
                    name: str,
                    created_by: str,
                    description: str = "",
                    items: List[Dict] = None,
                    metadata: Dict = None) -> Review:
        """
        Create a new review session.
        
        Args:
            name: Name of the review session
            created_by: User who created the review
            description: Optional description
            items: Optional list of items to include in the review
                  Each item should have: item_id, item_type, version_id
            metadata: Optional additional metadata
            
        Returns:
            The created Review object
        """
        # Generate ID
        review_id = str(uuid.uuid4())
        
        # Create Review object
        review = Review(
            id=review_id,
            name=name,
            description=description,
            created_by=created_by,
            created_at=datetime.now(),
            status=ReviewStatus.PENDING,
            items=[],
            metadata=metadata or {}
        )
        
        # Add items if provided
        if items:
            for item_data in items:
                item_id = item_data.get('item_id')
                item_type = item_data.get('item_type')
                version_id = item_data.get('version_id')
                
                if not item_id or not item_type or not version_id:
                    logger.warning(f"Skipping invalid item: {item_data}")
                    continue
                
                # Create the item
                item = ReviewItem(
                    id=str(uuid.uuid4()),
                    review_id=review_id,
                    item_id=item_id,
                    item_type=item_type,
                    version_id=version_id,
                    status='pending',
                    preview_path=item_data.get('preview_path'),
                    metadata=item_data.get('metadata', {})
                )
                
                # Add to review
                review.add_item(item)
        
        # Save to database
        return self.repository.create_review(review)
        
    def get_review(self, review_id: str) -> Optional[Review]:
        """
        Get a review by ID.
        
        Args:
            review_id: ID of the review
            
        Returns:
            Review object or None if not found
        """
        return self.repository.get_review(review_id)
        
    def add_item_to_review(self,
                         review_id: str,
                         item_id: str,
                         item_type: str,
                         version_id: str,
                         preview_path: Optional[Union[str, Path]] = None,
                         metadata: Optional[Dict] = None) -> Optional[ReviewItem]:
        """
        Add an item to a review.
        
        Args:
            review_id: ID of the review
            item_id: ID of the item (shot or asset)
            item_type: Type of item ("shot" or "asset")
            version_id: Version ID
            preview_path: Optional path to preview media
            metadata: Optional metadata
            
        Returns:
            Added ReviewItem or None if failed
        """
        # Create ReviewItem
        item = ReviewItem(
            id=str(uuid.uuid4()),
            review_id=review_id,
            item_id=item_id,
            item_type=item_type,
            version_id=version_id,
            status='pending',
            preview_path=preview_path,
            metadata=metadata or {}
        )
        
        try:
            # Add to database
            return self.repository.add_item(review_id, item)
        except ValueError:
            logger.error(f"Failed to add item to review {review_id}")
            return None
            
    def add_note_to_item(self,
                       review_id: str,
                       item_id: str,
                       content: str,
                       author: str,
                       frame: Optional[int] = None,
                       timecode: Optional[str] = None,
                       status: str = 'open',
                       attachments: List[Union[str, Path]] = None,
                       metadata: Dict = None) -> Optional[ReviewNote]:
        """
        Add a note to a review item.
        
        Args:
            review_id: ID of the review
            item_id: ID of the item (shot or asset)
            content: Note content
            author: Note author
            frame: Optional frame number
            timecode: Optional timecode
            status: Note status
            attachments: Optional attachments
            metadata: Optional metadata
            
        Returns:
            Added ReviewNote or None if failed
        """
        # Create ReviewNote
        note = ReviewNote(
            id=str(uuid.uuid4()),
            review_id=review_id,
            item_id=item_id,
            author=author,
            content=content,
            timestamp=datetime.now(),
            frame=frame,
            timecode=timecode,
            status=status,
            attachments=attachments or [],
            metadata=metadata or {}
        )
        
        try:
            # Add to database
            return self.repository.add_note(review_id, item_id, note)
        except Exception as e:
            logger.error(f"Failed to add note to item {item_id}: {e}")
            return None
            
    def update_review_status(self, 
                          review_id: str, 
                          status: Union[ReviewStatus, str],
                          modified_by: str) -> bool:
        """
        Update the status of a review.
        
        Args:
            review_id: ID of the review
            status: New status
            modified_by: User making the change
            
        Returns:
            True if successful, False otherwise
        """
        # Get the review
        review = self.get_review(review_id)
        if not review:
            logger.error(f"Review not found: {review_id}")
            return False
            
        # Convert string to enum if needed
        if isinstance(status, str):
            try:
                status = ReviewStatus(status)
            except ValueError:
                logger.error(f"Invalid review status: {status}")
                return False
        
        # Update the review
        prev_status = review.status
        review.status = status
        
        # Set completed_at if completing
        if status == ReviewStatus.COMPLETED:
            review.completed_at = datetime.now()
            review.metadata["completed_by"] = modified_by
        elif status == ReviewStatus.REOPENED:
            review.completed_at = None
            review.metadata["reopened_by"] = modified_by
            review.metadata["reopened_at"] = datetime.now().isoformat()
            
        # Update metadata
        if "status_history" not in review.metadata:
            review.metadata["status_history"] = []
            
        review.metadata["status_history"].append({
            "from": prev_status.value,
            "to": status.value,
            "by": modified_by,
            "at": datetime.now().isoformat()
        })
        
        # Save to database
        return self.repository.update_review(review)
        
    def update_note_status(self, 
                         note_id: str, 
                         status: Union[NoteStatus, str]) -> bool:
        """
        Update the status of a note.
        
        Args:
            note_id: ID of the note
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        # Convert string to enum if needed
        if isinstance(status, str):
            try:
                status = NoteStatus(status)
            except ValueError:
                logger.error(f"Invalid note status: {status}")
                return False
                
        # Convert enum to string if needed
        status_str = status.value if isinstance(status, NoteStatus) else status
        
        # Update in database
        return self.repository.update_note_status(note_id, status_str)
        
    def list_reviews(self, 
                   status: Optional[Union[ReviewStatus, str]] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Review]:
        """
        List reviews, optionally filtered by status.
        
        Args:
            status: Optional status filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of Review objects
        """
        # Convert enum to string if needed
        status_str = None
        if status:
            if isinstance(status, ReviewStatus):
                status_str = status.value
            else:
                status_str = status
                
        return self.repository.list_reviews(status_str, limit, offset)
        
    def get_item_reviews(self, 
                       item_id: str, 
                       item_type: Optional[str] = None) -> List[Review]:
        """
        Get all reviews for a specific item.
        
        Args:
            item_id: Item ID (shot or asset ID)
            item_type: Optional item type filter
            
        Returns:
            List of Review objects
        """
        return self.repository.get_item_reviews(item_id, item_type)
        
    def delete_review(self, review_id: str) -> bool:
        """
        Delete a review.
        
        Args:
            review_id: ID of the review
            
        Returns:
            True if successful, False otherwise
        """
        return self.repository.delete_review(review_id)
        
    def play_review_in_rv(self, 
                        review_id: str, 
                        shot_service=None, 
                        asset_service=None) -> bool:
        """
        Play a review in OpenRV.
        
        Args:
            review_id: ID of the review
            shot_service: Optional ShotService for accessing shots
            asset_service: Optional AssetService for accessing assets
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_rv:
            logger.warning("RV integration is disabled")
            return False
            
        return rv_service.play_review(review_id, shot_service, asset_service)
        
    def export_review_to_rv(self, review_id: str) -> Optional[Path]:
        """
        Export a review to an RV session file.
        
        Args:
            review_id: ID of the review
            
        Returns:
            Path to the created session file, or None if failed
        """
        if not self.enable_rv:
            logger.warning("RV integration is disabled")
            return None
            
        return rv_service.export_notes_to_rv(review_id)
        
    def import_notes_from_rv(self, 
                           review_id: str, 
                           session_file: Union[str, Path],
                           author: str) -> int:
        """
        Import notes from an RV session file into a review.
        
        Args:
            review_id: ID of the review
            session_file: Path to the RV session file
            author: Author to attribute the notes to
            
        Returns:
            Number of notes imported
        """
        if not self.enable_rv:
            logger.warning("RV integration is disabled")
            return 0
            
        # Get the review
        review = self.get_review(review_id)
        if not review:
            logger.error(f"Review not found: {review_id}")
            return 0
            
        # Import notes from RV
        notes_data = rv_service.import_notes_from_rv(session_file)
        if not notes_data:
            logger.warning(f"No notes found in RV session file: {session_file}")
            return 0
            
        # Find the first item in the review to attach notes to
        # This is simplified - in reality, we would need to match media files
        # from the RV session to items in the review
        if not review.items:
            logger.error(f"Review has no items to attach notes to: {review_id}")
            return 0
            
        # Assume first item for simplicity
        item = review.items[0]
        
        # Add each note to the review
        count = 0
        for note_data in notes_data:
            # Create note
            note = self.add_note_to_item(
                review_id=review_id,
                item_id=item.item_id,
                content=note_data.get('content', ''),
                author=author,
                frame=note_data.get('frame'),
                timecode=note_data.get('timestamp'),
                status='open',
                metadata=note_data.get('metadata', {})
            )
            
            if note:
                count += 1
                
        return count


# Create singleton instance
review_service = ReviewService()
