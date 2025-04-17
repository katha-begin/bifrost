"""Tests for the YAML implementation of the folder structure repository."""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

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
from bifrost.domains.folder_structure.repository.yaml_folder_structure_repository import (
    YAMLFolderStructureRepository
)
from bifrost.domains.folder_structure.model.exceptions import RepositoryError


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def yaml_repository(temp_config_dir):
    """Create a YAML repository with a temporary configuration directory."""
    return YAMLFolderStructureRepository(str(temp_config_dir))


class TestYAMLFolderStructureRepository:
    """Tests for the YAMLFolderStructureRepository."""

    def test_initialization(self, temp_config_dir):
        """Test repository initialization creates the required directories."""
        repo = YAMLFolderStructureRepository(str(temp_config_dir))
        
        assert (temp_config_dir / "templates").exists()
        assert (temp_config_dir / "studios").exists()

    def test_save_template_group(self, yaml_repository):
        """Test saving a template group."""
        # Create a template group
        group = TemplateGroup(
            name="test_group",
            description="Test Group"
        )
        
        # Add a template
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work",
            description="Asset work template"
        )
        group.add_template(template)
        
        # Create aggregate
        aggregate = TemplateGroupAggregate(group)
        
        # Save to repository
        yaml_repository.save_template_group(aggregate)
        
        # Verify file was created
        template_file = yaml_repository.template_groups_dir / "test_group.yaml"
        assert template_file.exists()

    def test_get_template_group_by_name(self, yaml_repository):
        """Test retrieving a template group by name."""
        # Create and save a template group
        group = TemplateGroup(
            name="test_group",
            description="Test Group"
        )
        
        # Add templates with inheritance
        base_template = FolderTemplate(
            name="base",
            template="/projects/{PROJECT}",
            description="Base template"
        )
        group.add_template(base_template)
        
        child_template = FolderTemplate(
            name="asset_work",
            template="assets/{ASSET_NAME}/work",
            description="Asset work template",
            parent=base_template,
            inheritance_mode=TemplateInheritance.EXTEND
        )
        group.add_template(child_template)
        
        # Create aggregate and save
        aggregate = TemplateGroupAggregate(group)
        yaml_repository.save_template_group(aggregate)
        
        # Retrieve the group
        retrieved_aggregate = yaml_repository.get_template_group_by_name("test_group")
        
        # Verify group was retrieved correctly
        assert retrieved_aggregate is not None
        retrieved_group = retrieved_aggregate.template_group
        assert retrieved_group.name == "test_group"
        assert retrieved_group.description == "Test Group"
        assert "base" in retrieved_group.templates
        assert "asset_work" in retrieved_group.templates
        
        # Verify inheritance was preserved
        asset_work = retrieved_group.templates["asset_work"]
        assert asset_work.parent is not None
        assert asset_work.parent.name == "base"
        assert asset_work.inheritance_mode == TemplateInheritance.EXTEND
        assert asset_work.get_effective_template() == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"

    def test_get_nonexistent_template_group(self, yaml_repository):
        """Test retrieving a template group that doesn't exist."""
        aggregate = yaml_repository.get_template_group_by_name("nonexistent")
        assert aggregate is None

    def test_list_template_groups(self, yaml_repository):
        """Test listing all template groups."""
        # Create and save multiple template groups
        for name in ["group1", "group2", "group3"]:
            group = TemplateGroup(name=name)
            aggregate = TemplateGroupAggregate(group)
            yaml_repository.save_template_group(aggregate)
        
        # List the groups
        groups = yaml_repository.list_template_groups()
        
        # Verify all groups are listed
        assert len(groups) == 3
        assert "group1" in groups
        assert "group2" in groups
        assert "group3" in groups

    def test_delete_template_group(self, yaml_repository):
        """Test deleting a template group."""
        # Create and save a template group
        group = TemplateGroup(name="test_group")
        aggregate = TemplateGroupAggregate(group)
        yaml_repository.save_template_group(aggregate)
        
        # Verify file was created
        template_file = yaml_repository.template_groups_dir / "test_group.yaml"
        assert template_file.exists()
        
        # Delete the group
        success = yaml_repository.delete_template_group("test_group")
        
        # Verify deletion was successful
        assert success
        assert not template_file.exists()

    def test_delete_nonexistent_template_group(self, yaml_repository):
        """Test deleting a template group that doesn't exist."""
        success = yaml_repository.delete_template_group("nonexistent")
        assert not success

    def test_save_studio_mapping(self, yaml_repository):
        """Test saving a studio mapping."""
        # Create a studio mapping
        mapping = StudioMapping(
            name="test_studio",
            description="Test Studio"
        )
        
        # Add templates
        asset_published = FolderTemplate(
            name="asset_published",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/published"
        )
        asset_work = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        shot_published = FolderTemplate(
            name="shot_published",
            template="/projects/{PROJECT}/shots/{SHOT}/published"
        )
        shot_work = FolderTemplate(
            name="shot_work",
            template="/projects/{PROJECT}/shots/{SHOT}/work"
        )
        
        mapping.asset_published_path = asset_published
        mapping.asset_work_path = asset_work
        mapping.shot_published_path = shot_published
        mapping.shot_work_path = shot_work
        
        # Create aggregate
        aggregate = StudioMappingAggregate(mapping)
        
        # Save to repository
        yaml_repository.save_studio_mapping(aggregate)
        
        # Verify file was created
        mapping_file = yaml_repository.studio_mappings_dir / "test_studio.yaml"
        assert mapping_file.exists()

    def test_get_studio_mapping_by_name(self, yaml_repository):
        """Test retrieving a studio mapping by name."""
        # Create and save a studio mapping
        mapping = StudioMapping(
            name="test_studio",
            description="Test Studio"
        )
        
        # Add templates
        asset_published = FolderTemplate(
            name="asset_published",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/published"
        )
        asset_work = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        shot_published = FolderTemplate(
            name="shot_published",
            template="/projects/{PROJECT}/shots/{SHOT}/published"
        )
        shot_work = FolderTemplate(
            name="shot_work",
            template="/projects/{PROJECT}/shots/{SHOT}/work"
        )
        
        mapping.asset_published_path = asset_published
        mapping.asset_work_path = asset_work
        mapping.shot_published_path = shot_published
        mapping.shot_work_path = shot_work
        
        # Create aggregate and save
        aggregate = StudioMappingAggregate(mapping)
        yaml_repository.save_studio_mapping(aggregate)
        
        # Retrieve the mapping
        retrieved_aggregate = yaml_repository.get_studio_mapping_by_name("test_studio")
        
        # Verify mapping was retrieved correctly
        assert retrieved_aggregate is not None
        retrieved_mapping = retrieved_aggregate.studio_mapping
        assert retrieved_mapping.name == "test_studio"
        assert retrieved_mapping.description == "Test Studio"
        
        # Verify templates were loaded
        assert retrieved_mapping.asset_published_path is not None
        assert retrieved_mapping.asset_published_path.raw_template == "/projects/{PROJECT}/assets/{ASSET_NAME}/published"
        assert retrieved_mapping.asset_work_path is not None
        assert retrieved_mapping.shot_published_path is not None
        assert retrieved_mapping.shot_work_path is not None

    def test_get_nonexistent_studio_mapping(self, yaml_repository):
        """Test retrieving a studio mapping that doesn't exist."""
        aggregate = yaml_repository.get_studio_mapping_by_name("nonexistent")
        assert aggregate is None

    def test_list_studio_mappings(self, yaml_repository):
        """Test listing all studio mappings."""
        # Create and save multiple studio mappings
        for name in ["studio1", "studio2", "studio3"]:
            mapping = StudioMapping(name=name)
            aggregate = StudioMappingAggregate(mapping)
            yaml_repository.save_studio_mapping(aggregate)
        
        # List the mappings
        mappings = yaml_repository.list_studio_mappings()
        
        # Verify all mappings are listed
        assert len(mappings) == 3
        assert "studio1" in mappings
        assert "studio2" in mappings
        assert "studio3" in mappings

    def test_delete_studio_mapping(self, yaml_repository):
        """Test deleting a studio mapping."""
        # Create and save a studio mapping
        mapping = StudioMapping(name="test_studio")
        aggregate = StudioMappingAggregate(mapping)
        yaml_repository.save_studio_mapping(aggregate)
        
        # Verify file was created
        mapping_file = yaml_repository.studio_mappings_dir / "test_studio.yaml"
        assert mapping_file.exists()
        
        # Delete the mapping
        success = yaml_repository.delete_studio_mapping("test_studio")
        
        # Verify deletion was successful
        assert success
        assert not mapping_file.exists()

    def test_delete_nonexistent_studio_mapping(self, yaml_repository):
        """Test deleting a studio mapping that doesn't exist."""
        success = yaml_repository.delete_studio_mapping("nonexistent")
        assert not success

    def test_get_template(self, yaml_repository):
        """Test retrieving a specific template."""
        # Create and save a template group with templates
        group = TemplateGroup(name="test_group")
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        group.add_template(template)
        aggregate = TemplateGroupAggregate(group)
        yaml_repository.save_template_group(aggregate)
        
        # Retrieve the template
        retrieved_template = yaml_repository.get_template("test_group", "asset_work")
        
        # Verify template was retrieved correctly
        assert retrieved_template is not None
        assert retrieved_template.name == "asset_work"
        assert retrieved_template.raw_template == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"

    def test_get_nonexistent_template(self, yaml_repository):
        """Test retrieving a template that doesn't exist."""
        # Create and save a template group
        group = TemplateGroup(name="test_group")
        aggregate = TemplateGroupAggregate(group)
        yaml_repository.save_template_group(aggregate)
        
        # Try to retrieve a nonexistent template
        template = yaml_repository.get_template("test_group", "nonexistent")
        assert template is None

    def test_get_template_for_entity(self, yaml_repository):
        """Test retrieving a template for a specific entity and data type."""
        # Create and save a studio mapping with templates
        mapping = StudioMapping(name="test_studio")
        
        asset_work = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        mapping.asset_work_path = asset_work
        
        aggregate = StudioMappingAggregate(mapping)
        yaml_repository.save_studio_mapping(aggregate)
        
        # Retrieve the template
        template = yaml_repository.get_template_for_entity(
            "test_studio", EntityType.ASSET, DataType.WORK
        )
        
        # Verify template was retrieved correctly
        assert template is not None
        assert template.name == "asset_work"
        assert template.raw_template == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"

    def test_get_nonexistent_template_for_entity(self, yaml_repository):
        """Test retrieving a template for an entity and data type that doesn't exist."""
        # Create and save a studio mapping
        mapping = StudioMapping(name="test_studio")
        aggregate = StudioMappingAggregate(mapping)
        yaml_repository.save_studio_mapping(aggregate)
        
        # Try to retrieve a nonexistent template
        template = yaml_repository.get_template_for_entity(
            "test_studio", EntityType.ASSET, DataType.WORK
        )
        assert template is None
