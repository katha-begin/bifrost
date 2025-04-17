#!/usr/bin/env python
# rv_service.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-14

import os
import subprocess
import tempfile
import json
import logging
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from ...core.config import get_config
from . import RV_AVAILABLE

logger = logging.getLogger(__name__)


class RVService:
    """
    Service for integrating with OpenRV for media review.
    
    This service provides methods for launching RV with media files and
    for creating RV session files for more complex review sessions.
    """
    
    def __init__(self):
        """Initialize the RV service."""
        self.rv_binary = get_config("review.rv_binary_path", "rv")
        self.rv_enabled = get_config("review.rv_enabled", True) and RV_AVAILABLE
        self.rv_session_dir = get_config("review.rv_session_dir", "temp/rv_sessions")
        
        # Ensure session directory exists
        os.makedirs(self.rv_session_dir, exist_ok=True)
        
        # Log initialization status
        if self.rv_enabled:
            logger.info(f"RV service initialized with binary: {self.rv_binary}")
        else:
            logger.warning("RV service initialized but RV is not available or disabled")
        
    def launch_viewer(self, file_paths: List[Union[str, Path]], 
                     session_name: Optional[str] = None,
                     comparison_mode: bool = False,
                     start_frame: Optional[int] = None,
                     end_frame: Optional[int] = None) -> bool:
        """
        Launch OpenRV with the given files.
        
        Args:
            file_paths: List of paths to media files to open
            session_name: Optional name for the RV session
            comparison_mode: Enable comparison mode
            start_frame: Optional start frame
            end_frame: Optional end frame
            
        Returns:
            True if RV was launched successfully, False otherwise
        """
        if not self.rv_enabled:
            logger.warning("OpenRV integration is disabled or unavailable")
            return False
            
        if not file_paths:
            logger.warning("No files provided to open in RV")
            return False
            
        # Convert Path objects to strings
        str_paths = [str(p) for p in file_paths]
            
        # Build command
        cmd = [self.rv_binary]
        
        # Add session name if provided
        if session_name:
            cmd.extend(["-sessname", session_name])
            
        # Add comparison mode if enabled
        if comparison_mode and len(str_paths) > 1:
            cmd.append("-c")
            
        # Add frame range if specified
        if start_frame is not None:
            cmd.extend(["-s", str(start_frame)])
        if end_frame is not None:
            cmd.extend(["-e", str(end_frame)])
            
        # Add files to open
        cmd.extend(str_paths)
        
        try:
            # Launch RV
            logger.info(f"Launching RV with command: {' '.join(cmd)}")
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"Error launching RV: {e}")
            return False
    
    def create_session_file(self, 
                          file_paths: List[Union[str, Path]], 
                          session_name: str,
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """
        Create an RV session file (.rv) for the given files.
        
        Args:
            file_paths: List of paths to media files to include
            session_name: Name for the RV session
            metadata: Optional metadata to include in the session
            
        Returns:
            Path to the created session file, or None if creation failed
        """
        if not file_paths:
            logger.warning("No files provided for RV session")
            return None
            
        # Create a sanitized filename from the session name
        safe_name = "".join(c if c.isalnum() else "_" for c in session_name)
        session_file = Path(self.rv_session_dir) / f"{safe_name}.rv"
        
        try:
            # Convert Path objects to strings
            str_paths = [str(p) for p in file_paths]
            
            # Create RV session file using RV command
            cmd = [self.rv_binary]
            
            # Add session name
            cmd.extend(["-sessname", session_name])
            
            # Add files
            cmd.extend(str_paths)
            
            # Save session
            cmd.extend(["-save", str(session_file)])
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create RV session: {result.stderr}")
                return None
                
            logger.info(f"Created RV session file: {session_file}")
            return session_file
            
        except Exception as e:
            logger.error(f"Error creating RV session file: {e}")
            return None
            
    def play_review(self, review_id: str, shot_service=None, asset_service=None) -> bool:
        """
        Play a review session in RV.
        
        This method requires either the shot_service or asset_service to be passed,
        depending on what types of items are in the review.
        
        Args:
            review_id: ID of the review to play
            shot_service: Optional ShotService for accessing shots
            asset_service: Optional AssetService for accessing assets
            
        Returns:
            True if the review was played successfully, False otherwise
        """
        # This requires the review_service to be imported at runtime to avoid
        # circular dependencies
        from ...services.review_service import review_service
        
        # Get the review
        review = review_service.get_review(review_id)
        if not review:
            logger.error(f"Review not found: {review_id}")
            return False
            
        # Collect file paths for all items in the review
        file_paths = []
        
        for item in review.items:
            # If item has a preview path, use it directly
            if item.preview_path and os.path.exists(item.preview_path):
                file_paths.append(item.preview_path)
                continue
                
            # Otherwise look up the item
            if item.item_type == "shot" and shot_service:
                shot = shot_service.get_shot(item.item_id)
                if shot:
                    version = None
                    for v in shot.versions:
                        if str(v.version_number) == item.version_id:
                            version = v
                            break
                    
                    if version and version.preview_path and os.path.exists(version.preview_path):
                        file_paths.append(version.preview_path)
                        
            elif item.item_type == "asset" and asset_service:
                asset = asset_service.get_asset(item.item_id)
                if asset:
                    version = None
                    for v in asset.versions:
                        if str(v.version_number) == item.version_id:
                            version = v
                            break
                    
                    if version and version.preview_path and os.path.exists(version.preview_path):
                        file_paths.append(version.preview_path)
        
        if not file_paths:
            logger.warning(f"No valid media files found for review: {review_id}")
            return False
            
        # Launch RV with the files
        return self.launch_viewer(file_paths, session_name=review.name)
        
    def import_notes_from_rv(self, session_file: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Import review notes from an RV session file.
        
        Args:
            session_file: Path to the RV session file
            
        Returns:
            List of note dictionaries
        """
        if not self.rv_enabled:
            logger.warning("OpenRV integration is disabled or unavailable")
            return []
            
        session_file = Path(session_file)
        if not session_file.exists():
            logger.error(f"RV session file not found: {session_file}")
            return []
            
        try:
            # Use RV to extract notes - RV has JSON export options for annotations
            temp_json = tempfile.mktemp(suffix=".json")
            cmd = [
                self.rv_binary,
                str(session_file),
                "-evaluate",
                f"require('annotations').export('{temp_json}')",
                "-quit"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0 or not os.path.exists(temp_json):
                logger.error(f"Failed to extract notes from RV session: {result.stderr}")
                return []
                
            # Read and parse the JSON file
            with open(temp_json, 'r') as f:
                notes_data = json.load(f)
                
            # Clean up the temp file
            os.remove(temp_json)
            
            # Convert RV annotations to Bifrost note format
            notes = []
            for annotation in notes_data.get('annotations', []):
                note = {
                    'content': annotation.get('text', ''),
                    'frame': annotation.get('frame'),
                    'author': annotation.get('author', 'Unknown'),
                    'timestamp': annotation.get('timestamp'),
                    'status': 'open',
                    'metadata': {
                        'rv_id': annotation.get('id'),
                        'rv_type': annotation.get('type'),
                        'rv_color': annotation.get('color'),
                        'rv_properties': annotation.get('properties', {})
                    }
                }
                notes.append(note)
                
            return notes
            
        except Exception as e:
            logger.error(f"Error importing notes from RV: {e}")
            return []
    
    def export_notes_to_rv(self, 
                         review_id: str, 
                         session_file: Union[str, Path] = None) -> Optional[Path]:
        """
        Export review notes to an RV session file.
        
        Args:
            review_id: ID of the review to export notes from
            session_file: Optional session file to augment (creates new if None)
            
        Returns:
            Path to the created/modified session file, or None if failed
        """
        # Import review_service at runtime to avoid circular dependencies
        from ...services.review_service import review_service
        
        # Get the review
        review = review_service.get_review(review_id)
        if not review:
            logger.error(f"Review not found: {review_id}")
            return None
            
        # If no session file is provided, create one
        if not session_file:
            # Create a temp file path for the notes
            temp_notes = tempfile.mktemp(suffix=".json")
            
            # Collect all notes from the review
            all_notes = []
            for item in review.items:
                # Extract the media path if available
                media_path = str(item.preview_path) if item.preview_path else ""
                
                # Add each note
                for note in item.notes:
                    rv_note = {
                        'id': note.id,
                        'type': 'text',
                        'text': note.content,
                        'frame': note.frame or 1,
                        'media': media_path,
                        'author': note.author,
                        'timestamp': note.timestamp.isoformat() if hasattr(note.timestamp, 'isoformat') else str(note.timestamp),
                        'color': note.metadata.get('color', '#FFFF00'),
                        'properties': note.metadata
                    }
                    all_notes.append(rv_note)
            
            # Write notes to temp file
            with open(temp_notes, 'w') as f:
                json.dump({'annotations': all_notes}, f)
            
            # Create RV session with the notes
            session_name = f"{review.name}_notes"
            safe_name = "".join(c if c.isalnum() else "_" for c in session_name)
            session_file = Path(self.rv_session_dir) / f"{safe_name}.rv"
            
            # Build file paths list from review items
            file_paths = []
            for item in review.items:
                if item.preview_path:
                    file_paths.append(item.preview_path)
            
            # Create session file
            if file_paths:
                cmd = [
                    self.rv_binary,
                    *[str(p) for p in file_paths],
                    "-evaluate",
                    f"require('annotations').import('{temp_notes}')",
                    "-save",
                    str(session_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Failed to create RV session with notes: {result.stderr}")
                    os.remove(temp_notes)
                    return None
            else:
                logger.warning("No media files found for review items")
                os.remove(temp_notes)
                return None
            
            # Clean up temp file
            os.remove(temp_notes)
            
            return session_file
        else:
            # Add notes to existing session
            session_file = Path(session_file)
            if not session_file.exists():
                logger.error(f"RV session file not found: {session_file}")
                return None
                
            # Similar implementation to above, but modifying existing session
            # This requires RV APIs that may be more complex
            # For simplicity, we'll create a new file with the review name
            new_session = Path(session_file.parent) / f"{review.name}_notes{session_file.suffix}"
            
            # This is simplified - would need actual RV API integration
            # to properly modify an existing session
            logger.warning("Modifying existing RV sessions not fully implemented")
            return None


# Create singleton instance
rv_service = RVService()
