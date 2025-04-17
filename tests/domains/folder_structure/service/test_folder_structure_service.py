"""Tests for the folder structure service."""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from bifrost.domains.folder_structure.model.enums import (
    EntityType, DataType, VariableType, TemplateInheritance
)
from bifrost.domains.folder_structure.model.value_objects import TemplateVariable
from bifrost.domains.folder_structure.model.entities import (
    FolderTemplate, TemplateGroup, StudioMapping
)
from bifrost.domains.folder_structure.model.aggregates import (
    TemplateGroupAggregate, StudioMappingAggregate
)
from bifrost.domains.folder_structure.model.exceptions import (
    PathResolutionError, VariableResolutionError
)
from bifrost.domains.folder_structure.service.folder_structure_service import (
    FolderStructureService
)
from bifrost.core.event_bus import EventBus


class MockRepository:
    """Mock repository for testing the folder structure service."""
    
    def __init__(self):
        self.template_groups = {}
        self.studio_mappings = {}
    
    def save_template_group(self, template_group_aggregate):
        self.template_groups[template_group_aggregate.template_group.name] = template_group_aggregate
    
    def get_template_group_by_name(self, group_name):
        return self.template_groups.get(group_name)
    
    def list_template_groups(self):
        return list(self.template_groups.keys())
    
    def delete_template_group(self, group_name):
        if group_name in self.template_groups:
            del self.template_groups[group_name]
            return True
        return False
    
    def save_studio_mapping(self, studio_mapping_aggregate):
        self.studio_mappings[studio_mapping_aggregate.studio_mapping.name] = studio_mapping_aggregate
    
    def get_studio_mapping_by_name(self, studio_name):
        return self.studio_mappings.get(studio_name)
    
    def list_studio_mappings(self):
        return list(self.studio_mappings.keys())
    
    def delete_studio_mapping(self, studio_name):
        if studio_name in self.studio_mappings:
            del self.studio_mappings[studio_name]
            return True
        return False
    
    def get_template(self, group_name, template_name):
        group_aggregate = self.get_template_group_by_name(group_name)
        if group_aggregate:
            group = group_aggregate.template_group
            return group.templates.get(template_name)
        return None
    
    def get_template_for_entity(self, studio_name, entity_type, data_type):
        aggregate = self.get_studio_mapping_by_name(studio_name)
        if aggregate:
            mapping = aggregate.studio_mapping
            return mapping.get_template_for_entity(entity_type, data_type)
        return None


@pytest.fixture
def mock_repository():
    """Create a mock repository for testing."""
    return MockRepository()


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus for testing."""
    return MagicMock(spec=EventBus)


@pytest.fixture
def service(mock_repository, mock_event_bus):
    """Create a folder structure service with mock dependencies."""
    return FolderStructureService(mock_repository, mock_event_bus)


@pytest.fixture
def setup_templates(mock_repository):
    """Setup templates and studio mappings for testing."""
    # Create template group
    group = TemplateGroup(name="test_templates")
    group_aggregate = TemplateGroupAggregate(group)
    
    # Create templates
    base = FolderTemplate(
        name="base",
        template="/projects/{PROJECT}"
    )
    group.add_template(base)
    
    asset_work = FolderTemplate(
        name="asset_work",
        template="assets/{ASSET_TYPE}/{ASSET_NAME}/work/{DEPARTMENT}/{VERSION}",
        parent=base,
        inheritance_mode=TemplateInheritance.EXTEND
    )
    group.add_template(asset_work)
    
    shot_work = FolderTemplate(
        name="shot_work",
        template="shots/{SEQUENCE}/{SHOT}/work/{DEPARTMENT}/{VERSION}",
        parent=base,
        inheritance_mode=TemplateInheritance.EXTEND
    )
    group.add_template(shot_work)
    
    # Save template group
    mock_repository.save_template_group(group_aggregate)
    
    # Create studio mapping
    mapping = StudioMapping(name="test_studio")
    mapping_aggregate = StudioMappingAggregate(mapping)
    
    # Add templates to mapping
    mapping.asset_work_path = FolderTemplate(
        name="asset_work",
        template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work/{DEPARTMENT}/{VERSION}"
    )
    
    mapping.asset_published_path = FolderTemplate(
        name="asset_published",
        template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/published/{DEPARTMENT}/{VERSION}"
    )
    
    mapping.shot_work_path = FolderTemplate(
        name="shot_work",
        template="/projects/{PROJECT}/shots/{SEQUENCE}/{SHOT}/work/{DEPARTMENT}/{VERSION}"
    )
    
    mapping.shot_published_path = FolderTemplate(
        name="shot_published",
        template="/projects/{PROJECT}/shots/{SEQUENCE}/{SHOT}/published/{DEPARTMENT}/{VERSION}"
    )
    
    # Save studio mapping
    mock_repository.save_studio_mapping(mapping_aggregate)


class TestFolderStructureService:
    """Tests for the FolderStructureService."""

    def test_create_template_group(self, service, mock_repository, mock_event_bus):
        """Test creating a template group."""
        # Create a template group
        group_name = service.create_template_group(
            name="test_group",
            description="Test Group"
        )
        
        # Verify group was created
        assert group_name == "test_group"
        assert "test_group" in mock_repository.template_groups
        group = mock_repository.template_groups["test_group"].template_group
        assert group.description == "Test Group"
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.group_name == "test_group"

    def test_create_duplicate_template_group(self, service, mock_repository):
        """Test creating a template group with a name that already exists."""
        # Create a template group
        service.create_template_group(name="test_group")
        
        # Try to create another group with the same name
        with pytest.raises(ValueError):
            service.create_template_group(name="test_group")

    def test_get_template_group(self, service, mock_repository):
        """Test retrieving a template group."""
        # Create a template group
        service.create_template_group(name="test_group", description="Test Group")
        
        # Retrieve the group
        group = service.get_template_group("test_group")
        
        # Verify group was retrieved correctly
        assert group.name == "test_group"
        assert group.description == "Test Group"

    def test_get_nonexistent_template_group(self, service):
        """Test retrieving a template group that doesn't exist."""
        with pytest.raises(ValueError):
            service.get_template_group("nonexistent")

    def test_list_template_groups(self, service):
        """Test listing all template groups."""
        # Create template groups
        service.create_template_group(name="group1")
        service.create_template_group(name="group2")
        service.create_template_group(name="group3")
        
        # List the groups
        groups = service.list_template_groups()
        
        # Verify all groups are listed
        assert len(groups) == 3
        assert "group1" in groups
        assert "group2" in groups
        assert "group3" in groups

    def test_delete_template_group(self, service, mock_repository, mock_event_bus):
        """Test deleting a template group."""
        # Create a template group
        service.create_template_group(name="test_group")
        
        # Reset the event bus mock
        mock_event_bus.reset_mock()
        
        # Delete the group
        service.delete_template_group("test_group")
        
        # Verify group was deleted
        assert "test_group" not in mock_repository.template_groups
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.group_name == "test_group"

    def test_delete_nonexistent_template_group(self, service):
        """Test deleting a template group that doesn't exist."""
        with pytest.raises(ValueError):
            service.delete_template_group("nonexistent")

    def test_create_template(self, service, mock_repository, mock_event_bus):
        """Test creating a template."""
        # Create a template group
        service.create_template_group(name="test_group")
        
        # Reset the event bus mock
        mock_event_bus.reset_mock()
        
        # Create a template
        variables = {
            "PROJECT": {
                "description": "Project name",
                "type": VariableType.STRING,
                "required": True,
                "default_value": "default_project"
            },
            "ASSET_NAME": {
                "description": "Asset name",
                "type": VariableType.STRING,
                "required": True
            }
        }
        
        template = service.create_template(
            group_name="test_group",
            template_name="asset_work",
            template_string="/projects/{PROJECT}/assets/{ASSET_NAME}/work",
            description="Asset work template",
            variables=variables
        )
        
        # Verify template was created
        assert template.name == "asset_work"
        assert template.raw_template == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        assert "PROJECT" in template.variables
        assert template.variables["PROJECT"].default_value == "default_project"
        
        # Verify template was added to group
        group = mock_repository.template_groups["test_group"].template_group
        assert "asset_work" in group.templates
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()

    def test_create_template_with_inheritance(self, service, mock_repository):
        """Test creating a template with inheritance."""
        # Create a template group
        service.create_template_group(name="test_group")
        
        # Create parent template
        service.create_template(
            group_name="test_group",
            template_name="base",
            template_string="/projects/{PROJECT}"
        )
        
        # Create child template with inheritance
        child = service.create_template(
            group_name="test_group",
            template_name="asset_work",
            template_string="assets/{ASSET_NAME}/work",
            parent_name="base",
            inheritance_mode="extend"
        )
        
        # Verify template was created with inheritance
        assert child.parent is not None
        assert child.parent.name == "base"
        assert child.inheritance_mode == TemplateInheritance.EXTEND
        assert child.get_effective_template() == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"

    def test_create_template_nonexistent_group(self, service):
        """Test creating a template in a group that doesn't exist."""
        with pytest.raises(ValueError):
            service.create_template(
                group_name="nonexistent",
                template_name="test",
                template_string="{PROJECT}"
            )

    def test_create_duplicate_template(self, service):
        """Test creating a template with a name that already exists."""
        # Create a template group and template
        service.create_template_group(name="test_group")
        service.create_template(
            group_name="test_group",
            template_name="test",
            template_string="{PROJECT}"
        )
        
        # Try to create another template with the same name
        with pytest.raises(ValueError):
            service.create_template(
                group_name="test_group",
                template_name="test",
                template_string="{PROJECT}"
            )

    def test_update_template(self, service, mock_repository, mock_event_bus):
        """Test updating a template."""
        # Create a template group and template
        service.create_template_group(name="test_group")
        service.create_template(
            group_name="test_group",
            template_name="asset_work",
            template_string="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        
        # Reset the event bus mock
        mock_event_bus.reset_mock()
        
        # Update the template
        updated = service.update_template(
            group_name="test_group",
            template_name="asset_work",
            template_string="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work",
            description="Updated description"
        )
        
        # Verify template was updated
        assert updated.raw_template == "/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work"
        assert updated.description == "Updated description"
        assert "ASSET_TYPE" in updated.variables
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()

    def test_update_nonexistent_template(self, service):
        """Test updating a template that doesn't exist."""
        # Create a template group
        service.create_template_group(name="test_group")
        
        # Try to update a nonexistent template
        with pytest.raises(ValueError):
            service.update_template(
                group_name="test_group",
                template_name="nonexistent",
                template_string="{PROJECT}"
            )

    def test_delete_template(self, service, mock_repository, mock_event_bus):
        """Test deleting a template."""
        # Create a template group and template
        service.create_template_group(name="test_group")
        service.create_template(
            group_name="test_group",
            template_name="test",
            template_string="{PROJECT}"
        )
        
        # Reset the event bus mock
        mock_event_bus.reset_mock()
        
        # Delete the template
        service.delete_template(
            group_name="test_group",
            template_name="test"
        )
        
        # Verify template was deleted
        group = mock_repository.template_groups["test_group"].template_group
        assert "test" not in group.templates
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()

    def test_delete_nonexistent_template(self, service):
        """Test deleting a template that doesn't exist."""
        # Create a template group
        service.create_template_group(name="test_group")
        
        # Try to delete a nonexistent template
        with pytest.raises(ValueError):
            service.delete_template(
                group_name="test_group",
                template_name="nonexistent"
            )

    def test_create_studio_mapping(self, service, mock_repository, mock_event_bus):
        """Test creating a studio mapping."""
        # Create a studio mapping
        studio_name = service.create_studio_mapping(
            name="test_studio",
            description="Test Studio"
        )
        
        # Verify mapping was created
        assert studio_name == "test_studio"
        assert "test_studio" in mock_repository.studio_mappings
        mapping = mock_repository.studio_mappings["test_studio"].studio_mapping
        assert mapping.description == "Test Studio"
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()

    def test_create_duplicate_studio_mapping(self, service):
        """Test creating a studio mapping with a name that already exists."""
        # Create a studio mapping
        service.create_studio_mapping(name="test_studio")
        
        # Try to create another mapping with the same name
        with pytest.raises(ValueError):
            service.create_studio_mapping(name="test_studio")

    def test_get_studio_mapping(self, service):
        """Test retrieving a studio mapping."""
        # Create a studio mapping
        service.create_studio_mapping(name="test_studio", description="Test Studio")
        
        # Retrieve the mapping
        mapping = service.get_studio_mapping("test_studio")
        
        # Verify mapping was retrieved correctly
        assert mapping.name == "test_studio"
        assert mapping.description == "Test Studio"

    def test_get_nonexistent_studio_mapping(self, service):
        """Test retrieving a studio mapping that doesn't exist."""
        with pytest.raises(ValueError):
            service.get_studio_mapping("nonexistent")

    def test_list_studio_mappings(self, service):
        """Test listing all studio mappings."""
        # Create studio mappings
        service.create_studio_mapping(name="studio1")
        service.create_studio_mapping(name="studio2")
        service.create_studio_mapping(name="studio3")
        
        # List the mappings
        mappings = service.list_studio_mappings()
        
        # Verify all mappings are listed
        assert len(mappings) == 3
        assert "studio1" in mappings
        assert "studio2" in mappings
        assert "studio3" in mappings

    def test_delete_studio_mapping(self, service, mock_repository, mock_event_bus):
        """Test deleting a studio mapping."""
        # Create a studio mapping
        service.create_studio_mapping(name="test_studio")
        
        # Reset the event bus mock
        mock_event_bus.reset_mock()
        
        # Delete the mapping
        service.delete_studio_mapping("test_studio")
        
        # Verify mapping was deleted
        assert "test_studio" not in mock_repository.studio_mappings
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()

    def test_delete_nonexistent_studio_mapping(self, service):
        """Test deleting a studio mapping that doesn't exist."""
        with pytest.raises(ValueError):
            service.delete_studio_mapping("nonexistent")

    def test_set_mapping_template(self, service, mock_repository, mock_event_bus):
        """Test setting a template for a studio mapping."""
        # Create a studio mapping
        service.create_studio_mapping(name="test_studio")
        
        # Reset the event bus mock
        mock_event_bus.reset_mock()
        
        # Set a template
        service.set_mapping_template(
            studio_name="test_studio",
            entity_type=EntityType.ASSET,
            data_type=DataType.WORK,
            template_string="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        
        # Verify template was set
        mapping = mock_repository.studio_mappings["test_studio"].studio_mapping
        assert mapping.asset_work_path is not None
        assert mapping.asset_work_path.raw_template == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        
        # Verify event was published
        mock_event_bus.publish.assert_called_once()

    def test_set_mapping_template_invalid(self, service):
        """Test setting an invalid template for a studio mapping."""
        # Create a studio mapping
        service.create_studio_mapping(name="test_studio")
        
        # Try to set an invalid template (missing variable)
        with pytest.raises(Exception):  # Could be InvalidTemplateError but needs proper exception propagation
            service.set_mapping_template(
                studio_name="test_studio",
                entity_type=EntityType.ASSET,
                data_type=DataType.WORK,
                template_string="/projects/{MISSING}/assets/{ASSET_NAME}/work"
            )

    def test_get_path(self, service, setup_templates):
        """Test resolving a path."""
        # Set the studio_name on the service
        service.studio_name = "test_studio"
        
        # Resolve a path
        path = service.get_path(
            entity_type=EntityType.ASSET,
            data_type=DataType.WORK,
            entity_name="hero",
            PROJECT="MyProject",
            ASSET_TYPE="character",
            DEPARTMENT="modeling",
            VERSION="v001"
        )
        
        # Verify path was resolved correctly
        assert path == "/projects/MyProject/assets/character/hero/work/modeling/v001"

    def test_get_path_missing_variable(self, service, setup_templates):
        """Test resolving a path with a missing variable."""
        # Set the studio_name on the service
        service.studio_name = "test_studio"
        
        # Try to resolve a path with missing variables
        with pytest.raises(PathResolutionError):
            service.get_path(
                entity_type=EntityType.ASSET,
                data_type=DataType.WORK,
                entity_name="hero",
                PROJECT="MyProject",
                # ASSET_TYPE is missing
                DEPARTMENT="modeling",
                VERSION="v001"
            )

    def test_get_path_nonexistent_template(self, service, setup_templates):
        """Test resolving a path for a nonexistent template."""
        # Set the studio_name on the service
        service.studio_name = "test_studio"
        
        # Try to resolve a path for a nonexistent data type
        with pytest.raises(PathResolutionError):
            service.get_path(
                entity_type=EntityType.ASSET,
                data_type=DataType.CACHE,  # No template defined for CACHE
                entity_name="hero"
            )

    def test_create_folder_structure(self, service, tmp_path):
        """Test creating a folder structure."""
        # Create a path to test with
        test_path = tmp_path / "test" / "structure"
        path_str = str(test_path)
        
        # Create the folder structure
        success = service.create_folder_structure(path_str)
        
        # Verify folder structure was created
        assert success
        assert test_path.exists()

    @patch("os.makedirs")
    def test_create_folder_structure_error(self, mock_makedirs, service, mock_event_bus):
        """Test creating a folder structure that fails."""
        # Make os.makedirs raise an exception
        mock_makedirs.side_effect = PermissionError("Access denied")
        
        # Try to create a folder structure
        success = service.create_folder_structure("/some/path")
        
        # Verify operation failed
        assert not success
        # No event should be published on failure
        mock_event_bus.publish.assert_not_called()

    def test_convert_path_between_studios(self, service, mock_repository):
        """Test converting a path between studio mappings."""
        # Create source studio
        source_mapping = StudioMapping(name="source_studio")
        source_mapping.asset_work_path = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work"
        )
        source_aggregate = StudioMappingAggregate(source_mapping)
        mock_repository.save_studio_mapping(source_aggregate)
        
        # Create target studio
        target_mapping = StudioMapping(name="target_studio")
        target_mapping.asset_work_path = FolderTemplate(
            name="asset_work",
            template="/shows/{PROJECT}/assets/{ASSET_NAME}/{ASSET_TYPE}/work"
        )
        target_aggregate = StudioMappingAggregate(target_mapping)
        mock_repository.save_studio_mapping(target_aggregate)
        
        # Convert a path
        source_path = "/projects/MyProject/assets/character/hero/work"
        converted_path = service.convert_path_between_studios(
            path=source_path,
            source_studio="source_studio",
            target_studio="target_studio"
        )
        
        # Verify path was converted correctly
        assert converted_path == "/shows/MyProject/assets/hero/character/work"

    def test_convert_path_nonexistent_studio(self, service):
        """Test converting a path with a nonexistent studio."""
        with pytest.raises(ValueError):
            service.convert_path_between_studios(
                path="/some/path",
                source_studio="nonexistent",
                target_studio="test_studio"
            )

    def test_analyze_path(self, service, mock_repository):
        """Test analyzing a path to extract entity type and variables."""
        # Create a studio mapping
        mapping = StudioMapping(name="test_studio")
        mapping.asset_work_path = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work/{DEPARTMENT}/{VERSION}"
        )
        mapping_aggregate = StudioMappingAggregate(mapping)
        mock_repository.save_studio_mapping(mapping_aggregate)
        
        # Get the mapping
        mapping = service.get_studio_mapping("test_studio")
        
        # Analyze a path
        path = "/projects/MyProject/assets/character/hero/work/modeling/v001"
        result = service._analyze_path(path, mapping)
        
        # Verify path was analyzed correctly
        assert result is not None
        entity_type, data_type, variables = result
        assert entity_type == EntityType.ASSET
        assert data_type == DataType.WORK
        assert variables["PROJECT"] == "MyProject"
        assert variables["ASSET_TYPE"] == "character"
        assert variables["ASSET_NAME"] == "hero"
        assert variables["DEPARTMENT"] == "modeling"
        assert variables["VERSION"] == "v001"

    def test_analyze_path_no_match(self, service, mock_repository):
        """Test analyzing a path that doesn't match any template."""
        # Create a studio mapping
        mapping = StudioMapping(name="test_studio")
        mapping.asset_work_path = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work"
        )
        mapping_aggregate = StudioMappingAggregate(mapping)
        mock_repository.save_studio_mapping(mapping_aggregate)
        
        # Get the mapping
        mapping = service.get_studio_mapping("test_studio")
        
        # Analyze a path that doesn't match any template
        path = "/some/unrelated/path"
        result = service._analyze_path(path, mapping)
        
        # Verify no match was found
        assert result is None

    def test_template_to_regex(self, service):
        """Test converting a template to a regex pattern."""
        # Convert a template to regex
        template = "/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work"
        pattern = service._template_to_regex(template)
        
        # Verify pattern works as expected
        import re
        match = re.fullmatch(pattern, "/projects/MyProject/assets/character/hero/work")
        assert match is not None
        assert match.group("PROJECT") == "MyProject"
        assert match.group("ASSET_TYPE") == "character"
        assert match.group("ASSET_NAME") == "hero"
        
        # Verify pattern doesn't match invalid paths
        assert re.fullmatch(pattern, "/projects/MyProject/shots/seq01/shot01") is None
