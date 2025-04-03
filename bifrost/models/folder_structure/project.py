#!/usr/bin/env python
# project.py - Project structure models
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class ShotInfo:
    """
    Information about a shot in a sequence.
    
    Attributes:
        id: Shot identifier (e.g., "SH0010")
        name: Human-readable name
        frame_range: Tuple of (start, end) frames
        status: Current production status
        metadata: Additional shot metadata
    """
    id: str
    name: str = ""
    frame_range: tuple = (1, 1)  # (start, end)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SequenceInfo:
    """
    Information about a sequence in an episode.
    
    Attributes:
        id: Sequence identifier (e.g., "SQ001")
        name: Human-readable name
        shot_count: Number of shots in the sequence
        shots: Dictionary of shots, keyed by shot ID
        metadata: Additional sequence metadata
    """
    id: str
    name: str
    shot_count: int = 0
    shots: Dict[str, ShotInfo] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Episode:
    """
    Information about an episode in a series.
    
    Attributes:
        id: Episode identifier (e.g., "E01")
        name: Human-readable name
        code: Production code for the episode
        sequences: List of sequence information
        metadata: Additional episode metadata
    """
    id: str
    name: str
    code: str = ""
    sequences: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedElement:
    """
    An element shared across multiple episodes.
    
    Attributes:
        type: Type of element (character, prop, environment, etc.)
        name: Name of the element
        id: Unique identifier
        applies_to: List of episode IDs this element applies to
        metadata: Additional metadata
    """
    type: str
    name: str
    id: str
    applies_to: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Deliverable:
    """
    A deliverable format for the series.
    
    Attributes:
        name: Name of the deliverable
        format: Format specification
        resolution: Resolution specification
        frame_rate: Frame rate in frames per second
        metadata: Additional metadata
    """
    name: str
    format: str
    resolution: str
    frame_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Series:
    """
    Information about a series of episodes.
    
    Attributes:
        name: Series name
        code: Production code
        numbering: Dictionary of numbering patterns
        episodes: List of episodes
        shared_elements: List of elements shared across episodes
        deliverables: List of deliverable formats
        metadata: Additional series metadata
    """
    name: str
    code: str
    numbering: Dict[str, str] = field(default_factory=dict)
    episodes: List[Episode] = field(default_factory=list)
    shared_elements: List[SharedElement] = field(default_factory=list)
    deliverables: List[Deliverable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
