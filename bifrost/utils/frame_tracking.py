"""
Frame tracking utilities for the Bifrost system.

These utilities help manage global frame tracking across the production hierarchy
(series > episodes > sequences > shots).
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from bifrost.core.database import db
from bifrost.models.episode import Episode
from bifrost.models.sequence import Sequence
from bifrost.models.shot import Shot

logger = logging.getLogger(__name__)

def get_episode_frame_range(episode_id: UUID) -> Tuple[int, int]:
    """
    Get the total frame range for an episode.
    
    Args:
        episode_id: UUID of the episode
        
    Returns:
        Tuple of (frame_start, frame_end)
    """
    query = "SELECT frame_start, frame_end FROM episodes WHERE id = ?"
    results = db.execute(query, (str(episode_id),))
    
    if not results:
        raise ValueError(f"Episode with ID {episode_id} not found")
    
    return (results[0]['frame_start'], results[0]['frame_end'])


def get_sequence_frame_range(sequence_id: UUID) -> Tuple[int, int]:
    """
    Get the total frame range for a sequence.
    
    Args:
        sequence_id: UUID of the sequence
        
    Returns:
        Tuple of (frame_start, frame_end)
    """
    query = "SELECT frame_start, frame_end FROM sequences WHERE id = ?"
    results = db.execute(query, (str(sequence_id),))
    
    if not results:
        raise ValueError(f"Sequence with ID {sequence_id} not found")
    
    return (results[0]['frame_start'], results[0]['frame_end'])


def get_shots_in_sequence(sequence_id: UUID) -> List[Dict[str, Any]]:
    """
    Get all shots in a sequence ordered by their global frame start.
    
    Args:
        sequence_id: UUID of the sequence
        
    Returns:
        List of shot records
    """
    query = """
    SELECT id, code, frame_start, frame_end, global_frame_start, global_frame_end 
    FROM shots 
    WHERE sequence_id = ? 
    ORDER BY global_frame_start NULLS LAST, frame_start
    """
    return db.execute(query, (str(sequence_id),))


def update_shot_global_frames(shot_id: UUID, global_start: int, global_end: int) -> bool:
    """
    Update the global frame range for a shot.
    
    Args:
        shot_id: UUID of the shot
        global_start: Global timeline start frame
        global_end: Global timeline end frame
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db.update('shots', str(shot_id), {
            'global_frame_start': global_start,
            'global_frame_end': global_end
        })
        return True
    except Exception as e:
        logger.error(f"Error updating shot global frames: {e}")
        return False


def update_sequence_global_frames(sequence_id: UUID, global_start: Optional[int] = None) -> bool:
    """
    Update the global frame range for a sequence based on its shots.
    If global_start is provided, it will reposition all shots to start from that point.
    
    Args:
        sequence_id: UUID of the sequence
        global_start: Optional global timeline start frame
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get all shots in the sequence
        shots = get_shots_in_sequence(sequence_id)
        
        if not shots:
            logger.warning(f"No shots found in sequence {sequence_id}")
            if global_start is not None:
                # Just update the sequence global start if no shots
                db.update('sequences', str(sequence_id), {
                    'global_frame_start': global_start,
                    'global_frame_end': global_start  # Same as start if no shots
                })
            return True
        
        # Handle repositioning if global_start is provided
        if global_start is not None:
            current_position = global_start
            for shot in shots:
                # Calculate shot duration
                duration = shot['frame_end'] - shot['frame_start']
                
                # Update shot global frames
                new_global_end = current_position + duration
                update_shot_global_frames(
                    UUID(shot['id']), 
                    current_position, 
                    new_global_end
                )
                
                # Move position for next shot
                current_position = new_global_end + 1
                
            # Update sequence global frames based on shots
            seq_global_start = global_start
            seq_global_end = current_position - 1
        else:
            # Find min and max global frames from shots
            shots_with_global = [s for s in shots if s.get('global_frame_start') is not None]
            if not shots_with_global:
                return True  # No shots with global frames
                
            seq_global_start = min(s['global_frame_start'] for s in shots_with_global)
            seq_global_end = max(s['global_frame_end'] for s in shots_with_global)
        
        # Update sequence
        db.update('sequences', str(sequence_id), {
            'global_frame_start': seq_global_start,
            'global_frame_end': seq_global_end
        })
        
        return True
    except Exception as e:
        logger.error(f"Error updating sequence global frames: {e}")
        return False


def update_episode_global_frames(episode_id: UUID, global_start: Optional[int] = None) -> bool:
    """
    Update the global frame range for an episode based on its sequences.
    If global_start is provided, it will reposition all sequences to start from that point.
    
    Args:
        episode_id: UUID of the episode
        global_start: Optional global timeline start frame
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get all sequences in the episode
        query = """
        SELECT id, frame_start, frame_end, global_frame_start, global_frame_end 
        FROM sequences 
        WHERE episode_id = ? 
        ORDER BY global_frame_start NULLS LAST, frame_start
        """
        sequences = db.execute(query, (str(episode_id),))
        
        if not sequences:
            logger.warning(f"No sequences found in episode {episode_id}")
            if global_start is not None:
                # Just update the episode global start if no sequences
                db.update('episodes', str(episode_id), {
                    'global_frame_start': global_start,
                    'global_frame_end': global_start  # Same as start if no sequences
                })
            return True
        
        # Handle repositioning if global_start is provided
        if global_start is not None:
            current_position = global_start
            for sequence in sequences:
                # Update sequence and its shots
                update_sequence_global_frames(UUID(sequence['id']), current_position)
                
                # Get updated sequence data
                updated_seq = db.get_by_id('sequences', sequence['id'])
                
                # Move position for next sequence
                current_position = updated_seq['global_frame_end'] + 1
                
            # Update episode global frames based on sequences
            ep_global_start = global_start
            ep_global_end = current_position - 1
        else:
            # Find min and max global frames from sequences
            sequences_with_global = [s for s in sequences if s.get('global_frame_start') is not None]
            if not sequences_with_global:
                return True  # No sequences with global frames
                
            ep_global_start = min(s['global_frame_start'] for s in sequences_with_global)
            ep_global_end = max(s['global_frame_end'] for s in sequences_with_global)
        
        # Update episode
        db.update('episodes', str(episode_id), {
            'global_frame_start': ep_global_start,
            'global_frame_end': ep_global_end
        })
        
        return True
    except Exception as e:
        logger.error(f"Error updating episode global frames: {e}")
        return False


def validate_frame_consistency(sequence_id: UUID) -> List[Dict[str, Any]]:
    """
    Validate the consistency of frame ranges in a sequence.
    
    Args:
        sequence_id: UUID of the sequence
        
    Returns:
        List of validation issues
    """
    issues = []
    shots = get_shots_in_sequence(sequence_id)
    
    # Sort shots by global frame start
    shots_with_global = [s for s in shots if s.get('global_frame_start') is not None]
    shots_with_global.sort(key=lambda s: s['global_frame_start'])
    
    # Check for overlaps or gaps
    for i in range(len(shots_with_global) - 1):
        current = shots_with_global[i]
        next_shot = shots_with_global[i + 1]
        
        # Check for overlap
        if current['global_frame_end'] >= next_shot['global_frame_start']:
            issues.append({
                'type': 'overlap',
                'shot1_id': current['id'],
                'shot1_code': current['code'],
                'shot2_id': next_shot['id'],
                'shot2_code': next_shot['code'],
                'message': f"Shot {current['code']} (ends at {current['global_frame_end']}) overlaps with {next_shot['code']} (starts at {next_shot['global_frame_start']})"
            })
        
        # Check for gap
        elif (current['global_frame_end'] + 1) < next_shot['global_frame_start']:
            gap_size = next_shot['global_frame_start'] - (current['global_frame_end'] + 1)
            issues.append({
                'type': 'gap',
                'shot1_id': current['id'],
                'shot1_code': current['code'],
                'shot2_id': next_shot['id'],
                'shot2_code': next_shot['code'],
                'gap_size': gap_size,
                'message': f"Gap of {gap_size} frames between {current['code']} and {next_shot['code']}"
            })
    
    return issues


def reposition_shots(sequence_id: UUID, shot_order: List[str], start_frame: int) -> bool:
    """
    Reposition shots in a sequence based on a specified order and start frame.
    
    Args:
        sequence_id: UUID of the sequence
        shot_order: List of shot IDs in the desired order
        start_frame: Global start frame for the first shot
        
    Returns:
        True if successful, False otherwise
    """
    try:
        current_position = start_frame
        
        # Process shots in the specified order
        for shot_id in shot_order:
            # Get shot details
            shot = db.get_by_id('shots', shot_id)
            if not shot:
                logger.warning(f"Shot with ID {shot_id} not found")
                continue
                
            # Calculate shot duration
            duration = shot['frame_end'] - shot['frame_start']
            
            # Update shot global frames
            new_global_end = current_position + duration
            update_shot_global_frames(
                UUID(shot_id), 
                current_position, 
                new_global_end
            )
            
            # Move position for next shot
            current_position = new_global_end + 1
        
        # Update sequence global frames
        update_sequence_global_frames(sequence_id)
        
        return True
    except Exception as e:
        logger.error(f"Error repositioning shots: {e}")
        return False