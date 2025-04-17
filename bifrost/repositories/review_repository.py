#!/usr/bin/env python
# review_repository.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-14

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from ..core.database import db
from ..models.review import Review, ReviewItem, ReviewNote, ReviewStatus, NoteStatus

# Setup logger
logger = logging.getLogger(__name__)


class ReviewRepository:
    """
    Repository for managing reviews in the database.
    
    This class handles persistence operations for reviews, review items, and notes.
    """
    
    def create_review(self, review: Review) -> Review:
        """
        Create a new review in the database.
        
        Args:
            review: The Review object to persist
            
        Returns:
            The created Review with populated ID
        """
        # Generate ID if not provided
        if not review.id:
            review.id = str(uuid.uuid4())
            
        # Prepare review data
        review_data = {
            'id': review.id,
            'name': review.name,
            'description': review.description,
            'created_at': review.created_at,
            'created_by': review.created_by,
            'completed_at': review.completed_at,
            'status': review.status.value,
            'metadata': db.serialize_json(review.metadata)
        }
        
        # Insert into database
        db.insert('reviews', review_data)
        
        # Insert items if any
        for item in review.items:
            self.add_item(review.id, item)
            
        return review
        
    def get_review(self, review_id: str) -> Optional[Review]:
        """
        Get a review by ID.
        
        Args:
            review_id: ID of the review to retrieve
            
        Returns:
            Review object or None if not found
        """
        # Get review data
        review_data = db.get_by_id('reviews', review_id)
        if not review_data:
            return None
            
        # Get review items
        items_query = "SELECT * FROM review_items WHERE review_id = ?"
        items_data = db.execute(items_query, (review_id,))
        
        # Create ReviewItem objects
        items = []
        for item_data in items_data:
            # Get notes for this item
            notes_query = "SELECT * FROM review_notes WHERE review_id = ? AND item_id = ?"
            notes_data = db.execute(notes_query, (review_id, item_data['item_id']))
            
            # Create ReviewNote objects
            notes = []
            for note_data in notes_data:
                # Parse attachments
                attachments = []
                if note_data.get('attachments'):
                    try:
                        attachments = json.loads(note_data['attachments'])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse attachments for note {note_data['id']}")
                
                note = ReviewNote(
                    id=note_data['id'],
                    review_id=note_data['review_id'],
                    item_id=note_data['item_id'],
                    author=note_data['author'],
                    content=note_data['content'],
                    timestamp=note_data.get('timestamp'),
                    frame=note_data.get('frame'),
                    timecode=note_data.get('timecode'),
                    status=note_data.get('status', 'open'),
                    metadata=db.deserialize_json(note_data.get('metadata')),
                    attachments=attachments
                )
                notes.append(note)
            
            item = ReviewItem(
                id=item_data['id'],
                review_id=item_data['review_id'],
                item_id=item_data['item_id'],
                item_type=item_data['item_type'],
                version_id=item_data['version_id'],
                status=item_data.get('status', 'pending'),
                notes=notes,
                preview_path=item_data.get('preview_path'),
                metadata=db.deserialize_json(item_data.get('metadata'))
            )
            items.append(item)
            
        # Convert status string to enum
        try:
            status = ReviewStatus(review_data['status'])
        except ValueError:
            status = ReviewStatus.PENDING
            
        # Create Review object
        review = Review(
            id=review_data['id'],
            name=review_data['name'],
            description=review_data.get('description', ''),
            created_at=review_data['created_at'],
            created_by=review_data.get('created_by', ''),
            completed_at=review_data.get('completed_at'),
            status=status,
            items=items,
            metadata=db.deserialize_json(review_data.get('metadata'))
        )
        
        return review
        
    def update_review(self, review: Review) -> bool:
        """
        Update a review.
        
        Args:
            review: Review object with updated values
            
        Returns:
            True if successful, False otherwise
        """
        # Check if review exists
        existing_review = db.get_by_id('reviews', review.id)
        if not existing_review:
            logger.warning(f"Cannot update review with ID {review.id} - not found")
            return False
            
        # Prepare update data
        review_data = {
            'name': review.name,
            'description': review.description,
            'created_by': review.created_by,
            'completed_at': review.completed_at,
            'status': review.status.value,
            'metadata': db.serialize_json(review.metadata)
        }
        
        # Update in database
        db.update('reviews', review.id, review_data)
        
        # Note: This doesn't update items/notes - use specific methods for that
        return True
        
    def delete_review(self, review_id: str) -> bool:
        """
        Delete a review.
        
        Args:
            review_id: ID of the review to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Check if review exists
        existing_review = db.get_by_id('reviews', review_id)
        if not existing_review:
            logger.warning(f"Cannot delete review with ID {review_id} - not found")
            return False
            
        # Delete the review (cascade will handle items and notes)
        db.delete('reviews', review_id)
        return True
        
    def add_item(self, review_id: str, item: ReviewItem) -> ReviewItem:
        """
        Add an item to a review.
        
        Args:
            review_id: Review ID
            item: ReviewItem to add
            
        Returns:
            The added ReviewItem with populated ID
        """
        # Check if review exists
        existing_review = db.get_by_id('reviews', review_id)
        if not existing_review:
            logger.warning(f"Cannot add item to review with ID {review_id} - not found")
            raise ValueError(f"Review {review_id} not found")
            
        # Generate ID if not provided
        if not item.id:
            item.id = str(uuid.uuid4())
            
        # Set review ID
        item.review_id = review_id
        
        # Prepare item data
        item_data = {
            'id': item.id,
            'review_id': review_id,
            'item_id': item.item_id,
            'item_type': item.item_type,
            'version_id': item.version_id,
            'status': item.status,
            'preview_path': str(item.preview_path) if item.preview_path else None,
            'metadata': db.serialize_json(item.metadata)
        }
        
        # Insert into database
        db.insert('review_items', item_data)
        
        # Insert notes if any
        for note in item.notes:
            self.add_note(review_id, item.item_id, note)
            
        return item
        
    def add_note(self, review_id: str, item_id: str, note: ReviewNote) -> ReviewNote:
        """
        Add a note to a review item.
        
        Args:
            review_id: Review ID
            item_id: Item ID (shot or asset ID)
            note: ReviewNote to add
            
        Returns:
            The added ReviewNote with populated ID
        """
        # Generate ID if not provided
        if not note.id:
            note.id = str(uuid.uuid4())
            
        # Set review and item IDs
        note.review_id = review_id
        note.item_id = item_id
        
        # Convert attachments to JSON
        attachments_json = None
        if note.attachments:
            attachments_json = json.dumps([str(path) for path in note.attachments])
            
        # Prepare note data
        note_data = {
            'id': note.id,
            'review_id': review_id,
            'item_id': item_id,
            'author': note.author,
            'content': note.content,
            'timestamp': note.timestamp,
            'frame': note.frame,
            'timecode': note.timecode,
            'status': note.status,
            'metadata': db.serialize_json(note.metadata),
            'attachments': attachments_json
        }
        
        # Insert into database
        db.insert('review_notes', note_data)
        
        return note
        
    def get_item_reviews(self, item_id: str, item_type: str = None) -> List[Review]:
        """
        Get all reviews for a specific item.
        
        Args:
            item_id: Item ID (shot or asset ID)
            item_type: Optional item type filter
            
        Returns:
            List of Review objects
        """
        # Build query
        query = "SELECT review_id FROM review_items WHERE item_id = ?"
        params = [item_id]
        
        if item_type:
            query += " AND item_type = ?"
            params.append(item_type)
            
        # Execute query
        results = db.execute(query, tuple(params))
        
        # Get full reviews
        reviews = []
        for result in results:
            review = self.get_review(result['review_id'])
            if review:
                reviews.append(review)
                
        return reviews
        
    def list_reviews(self, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Review]:
        """
        List reviews, optionally filtered by status.
        
        Args:
            status: Optional status filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of Review objects
        """
        # Build query
        query = "SELECT id FROM reviews"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        results = db.execute(query, tuple(params))
        
        # Get full reviews
        reviews = []
        for result in results:
            review = self.get_review(result['id'])
            if review:
                reviews.append(review)
                
        return reviews

    def update_note_status(self, note_id: str, status: Union[str, NoteStatus]) -> bool:
        """
        Update the status of a note.
        
        Args:
            note_id: Note ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        # Convert enum to string if needed
        if isinstance(status, NoteStatus):
            status = status.value
            
        # Update note
        return db.update('review_notes', note_id, {'status': status})
