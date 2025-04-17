"""
Exceptions for the Folder Structure domain.

This module defines the various exceptions that can be raised within the Folder Structure domain.
"""


class FolderStructureDomainError(Exception):
    """Base exception for all errors in the Folder Structure domain."""
    pass


class TemplateError(FolderStructureDomainError):
    """Base exception for template-related errors."""
    pass


class InvalidTemplateError(TemplateError):
    """Exception raised when a template is invalid."""
    
    def __init__(self, template: str, reason: str):
        self.template = template
        self.reason = reason
        super().__init__(f"Invalid template '{template}': {reason}")


class TemplateParsingError(TemplateError):
    """Exception raised when a template cannot be parsed."""
    
    def __init__(self, template: str, position: int, reason: str):
        self.template = template
        self.position = position
        self.reason = reason
        super().__init__(f"Error parsing template '{template}' at position {position}: {reason}")


class VariableResolutionError(TemplateError):
    """Exception raised when a variable cannot be resolved."""
    
    def __init__(self, variable_name: str, template: str = None):
        self.variable_name = variable_name
        self.template = template
        message = f"Cannot resolve variable '{variable_name}'"
        if template:
            message += f" in template '{template}'"
        super().__init__(message)


class PathResolutionError(FolderStructureDomainError):
    """Exception raised when a path cannot be resolved."""
    
    def __init__(self, entity_type: str, data_type: str, reason: str):
        self.entity_type = entity_type
        self.data_type = data_type
        self.reason = reason
        super().__init__(f"Cannot resolve path for {entity_type}/{data_type}: {reason}")


class ContextError(FolderStructureDomainError):
    """Exception raised when there's an issue with the context."""
    
    def __init__(self, message: str):
        super().__init__(message)


class StudioMappingError(FolderStructureDomainError):
    """Exception raised when there's an issue with studio mappings."""
    
    def __init__(self, studio_name: str, message: str):
        self.studio_name = studio_name
        super().__init__(f"Error with studio mapping '{studio_name}': {message}")


class TemplateValidationError(TemplateError):
    """Exception raised when template validation fails."""
    
    def __init__(self, template_name: str, reason: str):
        self.template_name = template_name
        self.reason = reason
        super().__init__(f"Validation failed for template '{template_name}': {reason}")
