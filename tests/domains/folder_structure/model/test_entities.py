"""Tests for the folder structure domain entities."""

import pytest
from datetime import datetime

from bifrost.domains.folder_structure.model.enums import (
    EntityType, DataType, VariableType, TemplateInheritance, TokenType
)
from bifrost.domains.folder_structure.model.value_objects import TemplateVariable
from bifrost.domains.folder_structure.model.entities import (
    FolderTemplate, TemplateGroup, StudioMapping
)
from bifrost.domains.folder_structure.model.exceptions import (
    InvalidTemplateError, VariableResolutionError
)


class TestFolderTemplate:
    """Tests for the FolderTemplate entity."""

    def test_creation(self):
        """Test basic creation of a folder template."""
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work/{DEPARTMENT}/{VERSION}"
        )

        assert template.name == "asset_work"
        assert template.raw_template == "/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work/{DEPARTMENT}/{VERSION}"
        assert len(template.parsed_template.tokens) > 0
        assert len(template.variables) == 5  # All variables extracted from template
        assert "PROJECT" in template.variables
        assert "ASSET_TYPE" in template.variables
        assert "ASSET_NAME" in template.variables
        assert "DEPARTMENT" in template.variables
        assert "VERSION" in template.variables

    def test_add_variable(self):
        """Test adding a variable to a template."""
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}"
        )

        # Add a new variable
        var = TemplateVariable(
            name="VERSION",
            description="Version number",
            variable_type=VariableType.STRING,
            default_value="v001"
        )
        template.add_variable(var)

        assert "VERSION" in template.variables
        assert template.variables["VERSION"].default_value == "v001"

        # Cannot add a variable with the same name
        with pytest.raises(ValueError):
            template.add_variable(var)

    def test_remove_variable(self):
        """Test removing a variable from a template."""
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/work"
        )

        # Create and add a variable not used in the template
        var = TemplateVariable(
            name="EXTRA",
            description="Extra variable"
        )
        template.add_variable(var)

        # Remove the variable
        template.remove_variable("EXTRA")
        assert "EXTRA" not in template.variables

        # Cannot remove a variable that doesn't exist
        with pytest.raises(KeyError):
            template.remove_variable("NONEXISTENT")

        # Cannot remove a variable used in the template
        with pytest.raises(ValueError):
            template.remove_variable("PROJECT")

    def test_update_variable(self):
        """Test updating a variable in a template."""
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/work"
        )

        # Update an existing variable
        new_var = TemplateVariable(
            name="PROJECT",
            description="Updated description",
            default_value="default_project"
        )
        template.update_variable(new_var)

        assert template.variables["PROJECT"].description == "Updated description"
        assert template.variables["PROJECT"].default_value == "default_project"

        # Cannot update a variable that doesn't exist
        with pytest.raises(KeyError):
            template.update_variable(TemplateVariable(name="NONEXISTENT"))

    def test_validate(self):
        """Test template validation."""
        # Valid template
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/work"
        )
        assert template.validate() is True

        # Invalid template (variable not defined)
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/work"
        )
        # Remove the automatically created PROJECT variable
        template.variables.pop("PROJECT")
        
        with pytest.raises(InvalidTemplateError):
            template.validate()

    def test_format(self):
        """Test formatting a template with variables."""
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_TYPE}/{ASSET_NAME}/work/{DEPARTMENT}/{VERSION}"
        )

        # Format with all variables provided
        path = template.format(
            PROJECT="MyProject",
            ASSET_TYPE="character",
            ASSET_NAME="hero",
            DEPARTMENT="modeling",
            VERSION="v001"
        )
        assert path == "/projects/MyProject/assets/character/hero/work/modeling/v001"

        # Format with missing required variable
        with pytest.raises(VariableResolutionError):
            template.format(
                PROJECT="MyProject",
                ASSET_TYPE="character",
                # ASSET_NAME missing
                DEPARTMENT="modeling",
                VERSION="v001"
            )

        # Format with default values
        for var_name in template.variables:
            template.variables[var_name].default_value = f"default_{var_name.lower()}"
        
        path = template.format()  # No variables provided, using defaults
        assert path == "/projects/default_project/assets/default_asset_type/default_asset_name/work/default_department/default_version"

    def test_inheritance(self):
        """Test template inheritance."""
        # Parent template
        parent = FolderTemplate(
            name="base",
            template="/projects/{PROJECT}"
        )

        # Child template with EXTEND inheritance
        child_extend = FolderTemplate(
            name="child_extend",
            template="assets/{ASSET_TYPE}",
            parent=parent,
            inheritance_mode=TemplateInheritance.EXTEND
        )

        # Get effective template
        effective_template = child_extend.get_effective_template()
        assert effective_template == "/projects/{PROJECT}/assets/{ASSET_TYPE}"

        # Child template with OVERRIDE inheritance
        child_override = FolderTemplate(
            name="child_override",
            template="/custom/{PROJECT}/assets",
            parent=parent,
            inheritance_mode=TemplateInheritance.OVERRIDE
        )

        # Get effective template
        effective_template = child_override.get_effective_template()
        assert effective_template == "/custom/{PROJECT}/assets"

        # Child template with NONE inheritance
        child_none = FolderTemplate(
            name="child_none",
            template="/standalone/{PROJECT}",
            parent=parent,
            inheritance_mode=TemplateInheritance.NONE
        )

        # Get effective template
        effective_template = child_none.get_effective_template()
        assert effective_template == "/standalone/{PROJECT}"


class TestTemplateGroup:
    """Tests for the TemplateGroup entity."""

    def test_creation(self):
        """Test basic creation of a template group."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )

        assert group.name == "studio_templates"
        assert group.description == "Templates for a studio"
        assert len(group.templates) == 0

    def test_add_template(self):
        """Test adding a template to a group."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )

        # Create and add a template
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        group.add_template(template)

        assert "asset_work" in group.templates
        assert group.templates["asset_work"] is template

        # Cannot add a template with the same name
        with pytest.raises(ValueError):
            group.add_template(template)

    def test_remove_template(self):
        """Test removing a template from a group."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )

        # Create and add a template
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        group.add_template(template)

        # Remove the template
        group.remove_template("asset_work")
        assert "asset_work" not in group.templates

        # Cannot remove a template that doesn't exist
        with pytest.raises(KeyError):
            group.remove_template("nonexistent")

    def test_get_template(self):
        """Test getting a template from a group."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )

        # Create and add a template
        template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        group.add_template(template)

        # Get the template
        retrieved = group.get_template("asset_work")
        assert retrieved is template

        # Cannot get a template that doesn't exist
        with pytest.raises(KeyError):
            group.get_template("nonexistent")

    def test_validate_all(self):
        """Test validating all templates in a group."""
        group = TemplateGroup(
            name="studio_templates",
            description="Templates for a studio"
        )

        # Create and add a valid template
        valid_template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        group.add_template(valid_template)

        # Create and add an invalid template
        invalid_template = FolderTemplate(
            name="invalid",
            template="/projects/{MISSING}/work"
        )
        # Remove the automatically created MISSING variable
        invalid_template.variables.pop("MISSING")
        group.templates["invalid"] = invalid_template  # Add directly to bypass validation

        # Validate all templates
        errors = group.validate_all()
        assert len(errors) == 1
        assert errors[0][0] == "invalid"  # Name of invalid template


class TestStudioMapping:
    """Tests for the StudioMapping entity."""

    def test_creation(self):
        """Test basic creation of a studio mapping."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )

        assert mapping.name == "studio_a"
        assert mapping.description == "Mapping for Studio A"
        assert mapping.asset_published_path is None
        assert mapping.asset_work_path is None
        assert mapping.shot_published_path is None
        assert mapping.shot_work_path is None

    def test_get_set_template(self):
        """Test getting and setting templates for entity types."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )

        # Create templates
        asset_work_template = FolderTemplate(
            name="asset_work",
            template="/projects/{PROJECT}/assets/{ASSET_NAME}/work"
        )
        shot_published_template = FolderTemplate(
            name="shot_published",
            template="/projects/{PROJECT}/shots/{SHOT}/published"
        )

        # Set templates
        mapping.set_template_for_entity(EntityType.ASSET, DataType.WORK, asset_work_template)
        mapping.set_template_for_entity(EntityType.SHOT, DataType.PUBLISHED, shot_published_template)

        # Get templates
        retrieved_asset_work = mapping.get_template_for_entity(EntityType.ASSET, DataType.WORK)
        retrieved_shot_published = mapping.get_template_for_entity(EntityType.SHOT, DataType.PUBLISHED)

        assert retrieved_asset_work is asset_work_template
        assert retrieved_shot_published is shot_published_template

        # Get nonexistent template
        assert mapping.get_template_for_entity(EntityType.ASSET, DataType.RENDER) is None

    def test_validate(self):
        """Test validating a studio mapping."""
        mapping = StudioMapping(
            name="studio_a",
            description="Mapping for Studio A"
        )

        # No templates defined yet - validation should fail
        errors = mapping.validate()
        assert len(errors) == 4  # Missing all required templates

        # Add valid templates
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

        mapping.asset_published_path = asset_published_template
        mapping.asset_work_path = asset_work_template
        mapping.shot_published_path = shot_published_template
        mapping.shot_work_path = shot_work_template

        # Validation should pass
        errors = mapping.validate()
        assert len(errors) == 0

        # Add an invalid template
        invalid_template = FolderTemplate(
            name="invalid",
            template="/projects/{MISSING}/work"
        )
        # Remove the automatically created MISSING variable
        invalid_template.variables.pop("MISSING")
        mapping.render_path = invalid_template

        # Validation should fail
        errors = mapping.validate()
        assert len(errors) == 1
