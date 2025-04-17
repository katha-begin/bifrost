"""Tests for the folder structure domain aggregates."""

import pytest
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
from bifrost.domains.folder_structure.model.exceptions import (
    InvalidTemplateError, StudioMappingError
)


class TestTemplateGroupAggregate:
    """Tests for the TemplateGroupAggregate."""

    def test_creation(self):
        """Test basic creation of a template group aggregate."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )
        aggregate = TemplateGroupAggregate(group)

        assert aggregate.template_group is group
        assert len(aggregate.events) == 0

    def test_create_template(self):
        """Test creating a template through the aggregate."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )
        aggregate = TemplateGroupAggregate(group)

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
        
        template = aggregate.create_template(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work",
            description="Asset work template",
            variables=variables
        )

        # Verify template was created
        assert template.name == "asset_work"
        assert template.raw_template == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        assert "PROJECT" in template.variables
        assert "ASSET_NAME" in template.variables
        assert template.variables["PROJECT"].default_value == "default_project"

        # Verify template was added to group
        assert "asset_work" in aggregate.template_group.templates
        assert aggregate.template_group.templates["asset_work"] is template

        # Verify event was generated
        assert len(aggregate.events) == 1
        event = aggregate.events[0]
        assert event.group_name == "studio_templates"
        assert event.template_name == "asset_work"

    def test_create_template_with_inheritance(self):
        """Test creating a template with inheritance."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )
        aggregate = TemplateGroupAggregate(group)

        # Create parent template
        parent = aggregate.create_template(
            name="base",
            template="/projects/{PROJECT}"
        )

        # Clear events
        aggregate.clear_events()

        # Create child template with inheritance
        child = aggregate.create_template(
            name="asset_work",
            template="assets/{ASSET_NAME}/work",
            parent_name="base",
            inheritance_mode="extend"
        )

        # Verify template was created with inheritance
        assert child.parent is parent
        assert child.inheritance_mode == TemplateInheritance.EXTEND
        assert child.get_effective_template() == "/projects/{PROJECT}/assets/{ASSET_NAME}/work"

        # Verify event was generated
        assert len(aggregate.events) == 1

    def test_update_template(self):
        """Test updating a template through the aggregate."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )
        aggregate = TemplateGroupAggregate(group)

        # Create a template
        template = aggregate.create_template(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        
        # Clear events
        aggregate.clear_events()

        # Update the template
        updated_template = aggregate.update_template(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work",
            description="Updated description"
        )

        # Verify template was updated
        assert updated_template.raw_template == "/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work"
        assert updated_template.description == "Updated description"
        assert "ASSET_TYPE" in updated_template.variables  # New variable added

        # Verify event was generated
        assert len(aggregate.events) == 1
        event = aggregate.events[0]
        assert event.group_name == "studio_templates"
        assert event.template_name == "asset_work"

    def test_delete_template(self):
        """Test deleting a template through the aggregate."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )
        aggregate = TemplateGroupAggregate(group)

        # Create templates
        aggregate.create_template(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        
        # Clear events
        aggregate.clear_events()

        # Delete the template
        aggregate.delete_template("asset_work")

        # Verify template was deleted
        assert "asset_work" not in aggregate.template_group.templates

        # Verify event was generated
        assert len(aggregate.events) == 1
        event = aggregate.events[0]
        assert event.group_name == "studio_templates"
        assert event.template_name == "asset_work"

    def test_delete_parent_template(self):
        """Test that deleting a parent template raises an error."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )
        aggregate = TemplateGroupAggregate(group)

        # Create parent template
        aggregate.create_template(
            name="base",
            template="/projects/{PROJECT}"
        )

        # Create child template
        aggregate.create_template(
            name="asset_work",
            template="assets/{ASSET_NAME}/work",
            parent_name="base",
            inheritance_mode="extend"
        )

        # Try to delete the parent template
        with pytest.raises(ValueError):
            aggregate.delete_template("base")


class TestStudioMappingAggregate:
    """Tests for the StudioMappingAggregate."""

    def test_creation(self):
        """Test basic creation of a studio mapping aggregate."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )
        aggregate = StudioMappingAggregate(mapping)

        assert aggregate.studio_mapping is mapping
        assert len(aggregate.events) == 0

    def test_set_template(self):
        """Test setting a template through the aggregate."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )
        aggregate = StudioMappingAggregate(mapping)

        # Create a template
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        
        # Set the template
        aggregate.set_template(EntityType.ASSET, DataType.WORK, template)

        # Verify template was set
        assert aggregate.studio_mapping.asset_work_path is template

        # Verify event was generated
        assert len(aggregate.events) == 1
        event = aggregate.events[0]
        assert event.studio_name == "studio_a"
        assert event.entity_type == "asset"
        assert event.data_type == "work"

    def test_set_template_invalid(self):
        """Test setting an invalid template raises an error."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )
        aggregate = StudioMappingAggregate(mapping)

        # Create an invalid template
        template = FolderTemplate(
            name="invalid",
            template="/projects/{MISSING}/work"
        )
        # Remove the automatically created MISSING variable
        template.variables.pop("MISSING")

        # Try to set the invalid template
        with pytest.raises(InvalidTemplateError):
            aggregate.set_template(EntityType.ASSET, DataType.WORK, template)

    def test_validate(self):
        """Test validating a studio mapping aggregate."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )
        aggregate = StudioMappingAggregate(mapping)

        # Validation should fail because required templates are missing
        with pytest.raises(StudioMappingError):
            aggregate.validate()

        # Add required templates
        asset_published_template = FolderTemplate(
            name="asset_published",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/published"
        )
        asset_work_template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        shot_published_template = FolderTemplate(
            name="shot_published",
            template="/projects/{PROJECT}/shots/{SHOT}/published"
        )
        shot_work_template = FolderTemplate(
            name="shot_work",
            template="/projects/{PROJECT}/shots/{SHOT}/work"
        )

        aggregate.set_template(EntityType.ASSET, DataType.PUBLISHED, asset_published_template)
        aggregate.set_template(EntityType.ASSET, DataType.WORK, asset_work_template)
        aggregate.set_template(EntityType.SHOT, DataType.PUBLISHED, shot_published_template)
        aggregate.set_template(EntityType.SHOT, DataType.WORK, shot_work_template)

        # Clear events
        aggregate.clear_events()

        # Validation should now pass
        aggregate.validate()  # Should not raise an exception

        # Add an invalid template
        invalid_template = FolderTemplate(
            name="invalid",
            template="/projects/{MISSING}/work"
        )
        # Remove the automatically created MISSING variable
        invalid_template.variables.pop("MISSING")
        
        # Bypass the validation in set_template by directly setting the property
        aggregate.studio_mapping.render_path = invalid_template

        # Validation should now fail
        with pytest.raises(StudioMappingError):
            aggregate.validate()
