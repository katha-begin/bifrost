#!/usr/bin/env python
# folder_service.py - Folder structure management
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import re
import string

from ...core.config import get_config
from ...models.folder_structure import (
    EntityType, DataType, FolderTemplate, StudioMapping,
    Department, DepartmentDependency, DepartmentOutput, Workflow,
    Series, Episode, SequenceInfo, ShotInfo, SharedElement, Deliverable
)

logger = logging.getLogger(__name__)

class FolderService:
    """
    Service for managing production folder structures.
    
    This service provides methods for generating file paths according to
    the configured folder structure, creating folders, and managing
    cross-studio synchronization of folder structures.
    """
    
    def __init__(self):
        """Initialize the folder service."""
        # Load configurations
        self.project_root = get_config("project.root_path", "")
        self.studio_name = get_config("project.studio_name", "main_studio")
        
        # Load root paths
        self.work_root = get_config("folder_structure.work_root", "work")
        self.published_root = get_config("folder_structure.published_root", "published")
        self.output_root = get_config("folder_structure.output_root", "output")
        
        # Load mappings
        mappings_file = get_config("folder_structure.mappings_file", 
                                 "config/pipeline/folder_mapping.yaml")
        self.studio_mappings = self._load_studio_mappings(mappings_file)
        
        # Load department dependencies
        deps_file = get_config("folder_structure.dependencies_file",
                             "config/pipeline/dependencies.yaml")
        self.departments, self.workflows = self._load_dependencies(deps_file)
        
        # Load series data for episodic
        series_file = get_config("folder_structure.series_file",
                               "config/show/series_metadata.yaml")
        self.series_info = self._load_series_info(series_file)
        
        logger.info(f"Folder service initialized with project root: {self.project_root}")
    
    def _load_studio_mappings(self, file_path: str) -> Dict[str, StudioMapping]:
        """
        Load studio mappings from YAML file.
        
        Args:
            file_path: Path to the mapping YAML file
            
        Returns:
            Dictionary of studio mappings
        """
        try:
            if not Path(file_path).exists():
                logger.warning(f"Studio mappings file not found: {file_path}")
                return {}
                
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                
            mappings = {}
            for studio_name, paths in data.get('studio_mappings', {}).items():
                # Process template variables before creating FolderTemplate
                # This allows for substitution of config values
                processed_paths = {}
                for key, template in paths.items():
                    # Replace ${...} variables with config values
                    template = self._process_template_variables(template)
                    processed_paths[key] = template
                
                # Create mapping with processed templates
                mappings[studio_name] = StudioMapping(
                    name=studio_name,
                    asset_published_path=FolderTemplate(processed_paths['asset_published_path']),
                    asset_work_path=FolderTemplate(processed_paths['asset_work_path']),
                    shot_published_path=FolderTemplate(processed_paths['shot_published_path']),
                    shot_work_path=FolderTemplate(processed_paths['shot_work_path']),
                    render_path=FolderTemplate(processed_paths['render_path']) if 'render_path' in processed_paths else None,
                    cache_path=FolderTemplate(processed_paths['cache_path']) if 'cache_path' in processed_paths else None,
                    deliverable_path=FolderTemplate(processed_paths['deliverable_path']) if 'deliverable_path' in processed_paths else None
                )
            return mappings
            
        except Exception as e:
            logger.error(f"Error loading studio mappings: {e}")
            return {}
    
    def _process_template_variables(self, template: str) -> str:
        """
        Process template variables in the form ${variable.name}.
        
        Args:
            template: Template string with variables
            
        Returns:
            Processed template with variables substituted
        """
        # Find all ${...} occurrences
        pattern = r'\${([^}]*)}'
        matches = re.findall(pattern, template)
        
        # Replace each occurrence with config value
        for match in matches:
            value = get_config(match, "")
            template = template.replace(f"${{{match}}}", str(value))
            
        return template
    
    def _load_dependencies(self, file_path: str) -> Tuple[List[Department], Dict[str, Workflow]]:
        """
        Load department dependencies from YAML file.
        
        Args:
            file_path: Path to the dependencies YAML file
            
        Returns:
            Tuple of (departments, workflows)
        """
        try:
            if not Path(file_path).exists():
                logger.warning(f"Dependencies file not found: {file_path}")
                return [], {}
                
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                
            departments = []
            for dept_data in data.get('departments', []):
                # Create department dependencies
                requires = []
                for req in dept_data.get('requires', []):
                    requires.append(DepartmentDependency(
                        department=req['department'],
                        status=req.get('status', 'approved'),
                        version=req.get('version')
                    ))
                
                # Create department outputs
                produces = []
                for output in dept_data.get('produces', []):
                    produces.append(DepartmentOutput(
                        type=output['type'],
                        format=output.get('format', []),
                        location=output.get('location', '')
                    ))
                
                # Create department
                departments.append(Department(
                    id=dept_data['id'],
                    name=dept_data['name'],
                    requires=requires,
                    produces=produces
                ))
            
            # Create workflows
            workflows = {}
            for wf_name, wf_data in data.get('workflows', {}).items():
                workflows[wf_name] = Workflow(
                    name=wf_name,
                    asset_types=wf_data.get('asset_types', {}),
                    shot_types=wf_data.get('shot_types', {})
                )
                
            return departments, workflows
            
        except Exception as e:
            logger.error(f"Error loading dependencies: {e}")
            return [], {}
    
    def _load_series_info(self, file_path: str) -> Optional[Series]:
        """
        Load series metadata from YAML file.
        
        Args:
            file_path: Path to the series metadata YAML file
            
        Returns:
            Series object or None if loading failed
        """
        try:
            if not Path(file_path).exists():
                logger.warning(f"Series metadata file not found: {file_path}")
                return None
                
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f).get('series', {})
            
            # Create episodes list
            episodes = []
            for ep_data in data.get('episodes', []):
                episodes.append(Episode(
                    id=ep_data['id'],
                    name=ep_data['name'],
                    code=ep_data.get('code', ''),
                    sequences=ep_data.get('sequences', [])
                ))
            
            # Create shared elements
            shared_elements = []
            for elem_data in data.get('shared_elements', []):
                shared_elements.append(SharedElement(
                    type=elem_data['type'],
                    name=elem_data['name'],
                    id=elem_data['id'],
                    applies_to=elem_data.get('applies_to', [])
                ))
            
            # Create deliverables
            deliverables = []
            for deliv_data in data.get('deliverables', []):
                deliverables.append(Deliverable(
                    name=deliv_data['name'],
                    format=deliv_data['format'],
                    resolution=deliv_data['resolution'],
                    frame_rate=deliv_data['frame_rate']
                ))
            
            return Series(
                name=data.get('name', ''),
                code=data.get('code', ''),
                numbering=data.get('numbering', {}),
                episodes=episodes,
                shared_elements=shared_elements,
                deliverables=deliverables
            )
        except Exception as e:
            logger.error(f"Error loading series info: {e}")
            return None
    
    def get_path(self, 
                entity_type: EntityType, 
                data_type: DataType, 
                entity_name: str, 
                department: str = None,
                version: str = None, 
                user: str = None,
                asset_type: str = None,
                series: str = None,
                episode: str = None,
                sequence: str = None,
                cache_type: str = None,
                deliverable_type: str = None,
                layer: str = None,
                **kwargs) -> str:
        """
        Get a path based on entity and data type.
        
        This method generates a file path according to the configured folder
        structure for the specified entity and data type.
        
        Args:
            entity_type: Type of entity (ASSET, SHOT, etc.)
            data_type: Type of data (WORK, PUBLISHED, etc.)
            entity_name: Name of the entity
            department: Department name
            version: Version identifier
            user: Username (for work files)
            asset_type: Type of asset (for assets only)
            series: Series identifier (for episodic)
            episode: Episode identifier (for episodic)
            sequence: Sequence name (for shots only)
            cache_type: Type of cache (for cache data)
            deliverable_type: Type of deliverable
            layer: Render layer name
            **kwargs: Additional path variables
            
        Returns:
            Formatted path string
        """
        # Get the correct studio mapping
        studio = self.studio_mappings.get(self.studio_name)
        if not studio:
            logger.error(f"Studio mapping not found: {self.studio_name}")
            raise ValueError(f"Studio mapping not found: {self.studio_name}")
        
        # Create format dictionary
        format_args = {
            'PROJECT': self.project_root,
            'USER': user or os.environ.get('USERNAME', 'anonymous'),
            'DEPARTMENT': department or 'shared',
            'VERSION': version or 'v001',
            'SERIES': series or '',
            'EPISODE': episode or '',
            'CACHE_TYPE': cache_type or 'general',
            'DELIVERABLE_TYPE': deliverable_type or 'master',
            'LAYER': layer or 'beauty',
            **kwargs
        }
        
        # Add entity-specific arguments
        if entity_type == EntityType.ASSET:
            if not asset_type:
                raise ValueError("Asset type is required for asset paths")
                
            format_args['ASSET_NAME'] = entity_name
            format_args['ASSET_TYPE'] = asset_type
            
            if data_type == DataType.PUBLISHED:
                template = studio.asset_published_path
            elif data_type == DataType.WORK:
                template = studio.asset_work_path
            elif data_type == DataType.RENDER:
                if studio.render_path:
                    template = studio.render_path
                else:
                    raise ValueError(f"Render path not defined for studio: {self.studio_name}")
            elif data_type == DataType.CACHE:
                if studio.cache_path:
                    template = studio.cache_path
                else:
                    raise ValueError(f"Cache path not defined for studio: {self.studio_name}")
            elif data_type == DataType.DELIVERABLE:
                if studio.deliverable_path:
                    template = studio.deliverable_path
                else:
                    raise ValueError(f"Deliverable path not defined for studio: {self.studio_name}")
            else:
                raise ValueError(f"Unsupported data type for assets: {data_type}")
                
        elif entity_type == EntityType.SHOT:
            if not sequence:
                raise ValueError("Sequence is required for shot paths")
                
            format_args['SHOT'] = entity_name
            format_args['SEQUENCE'] = sequence
            
            if data_type == DataType.PUBLISHED:
                template = studio.shot_published_path
            elif data_type == DataType.WORK:
                template = studio.shot_work_path
            elif data_type == DataType.RENDER:
                if studio.render_path:
                    template = studio.render_path
                else:
                    raise ValueError(f"Render path not defined for studio: {self.studio_name}")
            elif data_type == DataType.CACHE:
                if studio.cache_path:
                    template = studio.cache_path
                else:
                    raise ValueError(f"Cache path not defined for studio: {self.studio_name}")
            elif data_type == DataType.DELIVERABLE:
                if studio.deliverable_path:
                    template = studio.deliverable_path
                else:
                    raise ValueError(f"Deliverable path not defined for studio: {self.studio_name}")
            else:
                raise ValueError(f"Unsupported data type for shots: {data_type}")
                
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        
        # Format the template using the arguments
        try:
            # Use string.Formatter to identify missing keys first
            required_keys = set()
            for _, arg_name, _, _ in string.Formatter().parse(template.template):
                if arg_name is not None:
                    required_keys.add(arg_name)
            
            # Check for missing keys
            missing_keys = required_keys - set(format_args.keys())
            if missing_keys:
                raise ValueError(f"Missing required path arguments: {', '.join(missing_keys)}")
                
            path = template.format(**format_args)
            return path
        except KeyError as e:
            logger.error(f"Missing format argument: {e}")
            raise ValueError(f"Missing format argument: {e}")
        except Exception as e:
            logger.error(f"Error formatting path: {e}")
            raise ValueError(f"Error formatting path: {e}")
    
    def create_folder_structure(self, path: str) -> bool:
        """
        Create the folder structure for a given path.
        
        Args:
            path: Path to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created folder structure: {path}")
            return True
        except Exception as e:
            logger.error(f"Error creating folder structure: {e}")
            return False
    
    def get_department_dependencies(self, department_id: str) -> List[DepartmentDependency]:
        """
        Get dependencies for a department.
        
        Args:
            department_id: Department identifier
            
        Returns:
            List of department dependencies
        """
        for dept in self.departments:
            if dept.id == department_id:
                return dept.requires
        return []
    
    def get_episode_info(self, episode_id: str) -> Optional[Episode]:
        """
        Get information about a specific episode.
        
        Args:
            episode_id: Episode identifier
            
        Returns:
            Episode object or None if not found
        """
        if not self.series_info:
            return None
            
        for episode in self.series_info.episodes:
            if episode.id == episode_id:
                return episode
        return None
    
    def get_sequence_info(self, episode_id: str, sequence_id: str) -> Optional[Dict]:
        """
        Get information about a specific sequence in an episode.
        
        Args:
            episode_id: Episode identifier
            sequence_id: Sequence identifier
            
        Returns:
            Dictionary with sequence information or None if not found
        """
        episode = self.get_episode_info(episode_id)
        if not episode:
            return None
            
        for sequence in episode.sequences:
            if sequence['id'] == sequence_id:
                return sequence
        return None
    
    def generate_shot_id(self, episode_id: str, sequence_id: str, shot_number: int) -> str:
        """
        Generate a shot ID based on series naming conventions.
        
        Args:
            episode_id: Episode identifier
            sequence_id: Sequence identifier
            shot_number: Shot number
            
        Returns:
            Generated shot ID
        """
        if not self.series_info:
            # Default pattern if no series info
            return f"SH{shot_number:04d}"
            
        pattern = self.series_info.numbering.get('shot_pattern', 'SH{number:04d}')
        return pattern.format(number=shot_number)
    
    def get_shared_elements(self, episode_id: str = None) -> List[SharedElement]:
        """
        Get shared elements for an episode or all shared elements.
        
        Args:
            episode_id: Episode identifier (optional)
            
        Returns:
            List of shared elements
        """
        if not self.series_info:
            return []
            
        if not episode_id:
            return self.series_info.shared_elements
            
        return [elem for elem in self.series_info.shared_elements 
                if episode_id in elem.applies_to]
    
    def convert_path_between_studios(self, 
                                   path: str, 
                                   source_studio: str, 
                                   target_studio: str) -> str:
        """
        Convert a path from one studio's format to another.
        
        Args:
            path: Path to convert
            source_studio: Source studio name
            target_studio: Target studio name
            
        Returns:
            Converted path
        """
        # Get studio mappings
        source = self.studio_mappings.get(source_studio)
        target = self.studio_mappings.get(target_studio)
        
        if not source or not target:
            raise ValueError(f"Studio mapping not found: {source_studio} or {target_studio}")
        
        # Determine the path type and extract variables
        path_type, variables = self._analyze_path(path, source)
        
        if not path_type or not variables:
            raise ValueError(f"Could not analyze path: {path}")
        
        # Get target template based on path type
        if path_type == "asset_published":
            template = target.asset_published_path
        elif path_type == "asset_work":
            template = target.asset_work_path
        elif path_type == "shot_published":
            template = target.shot_published_path
        elif path_type == "shot_work":
            template = target.shot_work_path
        elif path_type == "render":
            template = target.render_path
        elif path_type == "cache":
            template = target.cache_path
        elif path_type == "deliverable":
            template = target.deliverable_path
        else:
            raise ValueError(f"Unsupported path type: {path_type}")
        
        # Format the target template with extracted variables
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable in target template: {e}")
    
    def _analyze_path(self, path: str, studio_mapping: StudioMapping) -> Tuple[Optional[str], Dict[str, str]]:
        """
        Analyze a path to determine its type and extract variables.
        
        Args:
            path: Path to analyze
            studio_mapping: Studio mapping to use for analysis
            
        Returns:
            Tuple of (path_type, variables)
        """
        # Try to match against all template types
        template_types = [
            ("asset_published", studio_mapping.asset_published_path),
            ("asset_work", studio_mapping.asset_work_path),
            ("shot_published", studio_mapping.shot_published_path),
            ("shot_work", studio_mapping.shot_work_path)
        ]
        
        # Add optional templates if they exist
        if studio_mapping.render_path:
            template_types.append(("render", studio_mapping.render_path))
        if studio_mapping.cache_path:
            template_types.append(("cache", studio_mapping.cache_path))
        if studio_mapping.deliverable_path:
            template_types.append(("deliverable", studio_mapping.deliverable_path))
        
        # Try to match each template type
        for type_name, template in template_types:
            path_pattern = self._template_to_regex(template.template)
            match = re.match(path_pattern, path)
            if match:
                return type_name, match.groupdict()
        
        return None, {}
    
    def _template_to_regex(self, template: str) -> str:
        """
        Convert a template string with {VARIABLE} format to a regex pattern.
        
        Args:
            template: Template string with variables
            
        Returns:
            Regex pattern string
        """
        # Escape regex special characters
        pattern = re.escape(template)
        
        # Replace escaped braces with regex capture groups
        # e.g., \{VARIABLE\} -> (?P<VARIABLE>[^/]+)
        pattern = re.sub(r'\\{([A-Z_]+)\\}', r'(?P<\1>[^/]+)', pattern)
        
        # Add start and end markers
        pattern = f'^{pattern}$'
        
        return pattern
