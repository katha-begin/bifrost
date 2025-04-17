"""Tests for the folder structure domain value objects."""

import pytest
from datetime import datetime

from bifrost.domains.folder_structure.model.enums import VariableType, TokenType
from bifrost.domains.folder_structure.model.value_objects import (
    TemplateVariable, PathToken, TemplatePath
)


class TestTemplateVariable:
    """Tests for the TemplateVariable value object."""

    def test_creation(self):
        """Test basic creation of a template variable."""
        var = TemplateVariable(
            name="PROJECT",
            description="Project name",
            variable_type=VariableType.STRING,
            required=True,
            default_value="default_project",
            allowed_values=["project1", "project2", "default_project"],
            validation_pattern=r"^[a-zA-Z0-9_]+$"
        )

        assert var.name == "PROJECT"
        assert var.description == "Project name"
        assert var.variable_type == VariableType.STRING
        assert var.required is True
        assert var.default_value == "default_project"
        assert "project1" in var.allowed_values
        assert var.validation_pattern == r"^[a-zA-Z0-9_]+$"

    def test_name_validation(self):
        """Test that variable names must be valid."""
        # Valid names
        TemplateVariable(name="PROJECT")
        TemplateVariable(name="ASSET_NAME")
        TemplateVariable(name="VERSION_123")
        
        # Invalid names
        with pytest.raises(ValueError):
            TemplateVariable(name="project")  # Lowercase
        
        with pytest.raises(ValueError):
            TemplateVariable(name="Project")  # Mixed case
        
        with pytest.raises(ValueError):
            TemplateVariable(name="123_PROJECT")  # Starts with number
        
        with pytest.raises(ValueError):
            TemplateVariable(name="PROJECT-NAME")  # Invalid character

    def test_value_validation(self):
        """Test that values are validated against constraints."""
        # Create a variable with constraints
        var = TemplateVariable(
            name="PROJECT",
            variable_type=VariableType.STRING,
            allowed_values=["project1", "project2"],
            validation_pattern=r"^project\d$"
        )

        # Valid values
        assert var.validate_value("project1") is True
        assert var.validate_value("project2") is True

        # Invalid values
        with pytest.raises(ValueError):
            var.validate_value("project3")  # Not in allowed values

        with pytest.raises(ValueError):
            var.validate_value("proj1")  # Doesn't match pattern

    def test_variable_types(self):
        """Test different variable types."""
        # String variable
        string_var = TemplateVariable(
            name="NAME",
            variable_type=VariableType.STRING
        )
        assert string_var.validate_value("test") is True

        # Integer variable
        int_var = TemplateVariable(
            name="COUNT",
            variable_type=VariableType.INTEGER
        )
        assert int_var.validate_value(10) is True
        with pytest.raises(ValueError):
            int_var.validate_value("10")  # String, not int

        # Enum variable
        enum_var = TemplateVariable(
            name="STATUS",
            variable_type=VariableType.ENUM,
            allowed_values=["draft", "final"]
        )
        assert enum_var.validate_value("draft") is True
        with pytest.raises(ValueError):
            enum_var.validate_value("in_progress")  # Not in allowed values

        # Boolean variable
        bool_var = TemplateVariable(
            name="APPROVED",
            variable_type=VariableType.BOOLEAN
        )
        assert bool_var.validate_value(True) is True
        with pytest.raises(ValueError):
            bool_var.validate_value("true")  # String, not bool

        # Date variable
        date_var = TemplateVariable(
            name="CREATED_AT",
            variable_type=VariableType.DATE
        )
        assert date_var.validate_value(datetime.now()) is True
        assert date_var.validate_value("2023-01-01") is True  # String date also valid


class TestPathToken:
    """Tests for the PathToken value object."""

    def test_creation(self):
        """Test basic creation of a path token."""
        # Literal token
        literal_token = PathToken(
            token_type=TokenType.LITERAL,
            content="/path/to/",
            position=(0, 9)
        )

        assert literal_token.token_type == TokenType.LITERAL
        assert literal_token.content == "/path/to/"
        assert literal_token.position == (0, 9)

        # Variable token
        var_token = PathToken(
            token_type=TokenType.VARIABLE,
            content="PROJECT",
            position=(9, 18)
        )

        assert var_token.token_type == TokenType.VARIABLE
        assert var_token.content == "PROJECT"
        assert var_token.position == (9, 18)

    def test_position_validation(self):
        """Test that position is always a tuple of two integers."""
        # Position should be a tuple of two integers
        token = PathToken(
            token_type=TokenType.LITERAL,
            content="test",
            position=(1, 5)
        )
        assert token.position == (1, 5)

        # Invalid position converted to (0, 0)
        token = PathToken(
            token_type=TokenType.LITERAL,
            content="test",
            position="invalid"
        )
        assert token.position == (0, 0)

        token = PathToken(
            token_type=TokenType.LITERAL,
            content="test",
            position=(1, 2, 3)  # Too many values
        )
        assert token.position == (0, 0)


class TestTemplatePath:
    """Tests for the TemplatePath value object."""

    def test_creation(self):
        """Test basic creation of a template path."""
        # Create with tokens
        tokens = [
            PathToken(TokenType.LITERAL, "/path/to/", (0, 9)),
            PathToken(TokenType.VARIABLE, "PROJECT", (9, 18)),
            PathToken(TokenType.LITERAL, "/assets/", (18, 26)),
            PathToken(TokenType.VARIABLE, "ASSET_NAME", (26, 38))
        ]

        template_path = TemplatePath(
            raw_template="/path/to/{PROJECT}/assets/{ASSET_NAME}",
            tokens=tokens
        )

        assert template_path.raw_template == "/path/to/{PROJECT}/assets/{ASSET_NAME}"
        assert len(template_path.tokens) == 4
        assert template_path.variables == frozenset(["PROJECT", "ASSET_NAME"])

    def test_contains_variable(self):
        """Test checking if a template contains a variable."""
        tokens = [
            PathToken(TokenType.LITERAL, "/path/to/", (0, 9)),
            PathToken(TokenType.VARIABLE, "PROJECT", (9, 18)),
            PathToken(TokenType.LITERAL, "/assets/", (18, 26)),
            PathToken(TokenType.VARIABLE, "ASSET_NAME", (26, 38))
        ]

        template_path = TemplatePath(
            raw_template="/path/to/{PROJECT}/assets/{ASSET_NAME}",
            tokens=tokens
        )

        assert template_path.contains_variable("PROJECT") is True
        assert template_path.contains_variable("ASSET_NAME") is True
        assert template_path.contains_variable("VERSION") is False
