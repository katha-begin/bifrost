# bifrost/models/folder_structure.py
# Add these new classes

class EpisodeInfo:
    """Information about an episode in a series."""
    id: str
    name: str
    sequences: List[Dict]
    
class SeriesInfo:
    """Information about a series of episodes."""
    name: str
    code: str
    numbering: Dict[str, str]
    episodes: List[EpisodeInfo]
    shared_elements: List[Dict]

# bifrost/services/folder_service.py
# Update the service

class FolderService:
    """Service for managing production folder structures."""
    
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
    
    def _load_series_info(self, file_path: str) -> SeriesInfo:
        """Load series metadata from YAML file."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f).get('series', {})
            
            # Create episodes list
            episodes = []
            for ep_data in data.get('episodes', []):
                episodes.append(EpisodeInfo(
                    id=ep_data['id'],
                    name=ep_data['name'],
                    sequences=ep_data.get('sequences', [])
                ))
            
            return SeriesInfo(
                name=data.get('name', ''),
                code=data.get('code', ''),
                numbering=data.get('numbering', {}),
                episodes=episodes,
                shared_elements=data.get('shared_elements', [])
            )
        except Exception as e:
            print(f"Error loading series info: {e}")
            return SeriesInfo(name="", code="", numbering={}, episodes=[], shared_elements=[])
    
    # Updated path generation for separated roots
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
                **kwargs) -> str:
        """
        Get a path based on entity and data type.
        
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
            **kwargs: Additional path variables
            
        Returns:
            Formatted path string
        """
        # Determine base root directory based on data type
        if data_type == DataType.WORK:
            root_dir = os.path.join(self.project_root, self.work_root)
        elif data_type == DataType.PUBLISHED:
            root_dir = os.path.join(self.project_root, self.published_root)
        elif data_type in [DataType.CACHE, DataType.DELIVERABLE]:
            root_dir = os.path.join(self.project_root, self.output_root)
            # Further refinement for output subtypes
            if data_type == DataType.CACHE:
                root_dir = os.path.join(root_dir, "cache")
            else:  # DELIVERABLE
                root_dir = os.path.join(root_dir, "deliverables")
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Generate path based on entity type
        if entity_type == EntityType.ASSET:
            if not asset_type:
                raise ValueError("Asset type is required for asset paths")
                
            # Create asset path
            path_parts = [root_dir, "assets", asset_type, entity_name]
            
            # Add version/department/user based on data type
            if data_type == DataType.WORK:
                if department:
                    path_parts.append(department)
                if user:
                    path_parts.append(user)
            elif data_type == DataType.PUBLISHED:
                if version:
                    path_parts.append(version)
                if department:
                    path_parts.append(department)
            
        elif entity_type == EntityType.SHOT:
            # Basic validation
            if not sequence:
                raise ValueError("Sequence is required for shot paths")
            
            # Start building the shot path
            path_parts = [root_dir, "shots"]
            
            # Add series and episode for episodic content
            if series:
                path_parts.append(series)
                if episode:
                    path_parts.append(episode)
            
            # Add sequence and shot
            path_parts.append(sequence)
            path_parts.append(entity_name)
            
            # Add version/department/user based on data type
            if data_type == DataType.WORK:
                if department:
                    path_parts.append(department)
                if user:
                    path_parts.append(user)
            elif data_type == DataType.PUBLISHED:
                if version:
                    path_parts.append(version)
                if department:
                    path_parts.append(department)
            elif data_type == DataType.CACHE:
                if kwargs.get('cache_type'):
                    path_parts.append(kwargs['cache_type'])
            
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        
        # Join path parts and return
        return os.path.join(*path_parts)
    
    # Add methods for episodic management
    def get_episode_info(self, episode_id: str) -> Optional[EpisodeInfo]:
        """Get information about a specific episode."""
        for episode in self.series_info.episodes:
            if episode.id == episode_id:
                return episode
        return None
    
    def get_sequence_info(self, episode_id: str, sequence_id: str) -> Optional[Dict]:
        """Get information about a specific sequence in an episode."""
        episode = self.get_episode_info(episode_id)
        if not episode:
            return None
            
        for sequence in episode.sequences:
            if sequence['id'] == sequence_id:
                return sequence
        return None
    
    def generate_shot_id(self, episode_id: str, sequence_id: str, shot_number: int) -> str:
        """Generate a shot ID based on series naming conventions."""
        pattern = self.series_info.numbering.get('shot_pattern', 'SH{number:04d}')
        return pattern.format(number=shot_number)
    
    def get_shared_elements(self, episode_id: str = None) -> List[Dict]:
        """Get shared elements for an episode or all shared elements."""
        if not episode_id:
            return self.series_info.shared_elements
            
        return [elem for elem in self.series_info.shared_elements 
                if episode_id in elem.get('applies_to', [])]