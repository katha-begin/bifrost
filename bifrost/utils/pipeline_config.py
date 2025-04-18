"""
Pipeline configuration utilities.
"""

import os
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from bifrost.models.pipeline_step import (
    FileFormat, DepartmentDependency, PipelineStep,
    AssetWorkflow, ShotWorkflow, PipelineWorkflow, WorkflowType
)
from bifrost.models.project import (
    Project, ProjectPipelineConfig, DepartmentOverride, TaskTemplateOverride
)


DEFAULT_CONFIG_PATH = os.path.join('config', 'pipeline', 'dependencies.yaml')


def load_pipeline_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load pipeline configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file, defaults to DEFAULT_CONFIG_PATH
        
    Returns:
        Parsed YAML configuration as dictionary
    """
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def load_project_config(project_code: str) -> Dict[str, Any]:
    """
    Load project-specific pipeline configuration.
    
    Args:
        project_code: Project code to load configuration for
        
    Returns:
        Project configuration as dictionary
    """
    config_path = os.path.join('config', 'project', f"{project_code}_pipeline.yaml")
    
    if not os.path.exists(config_path):
        return {}
        
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_departments(config_path: Optional[str] = None) -> List[PipelineStep]:
    """
    Get all departments from the pipeline configuration.
    
    Args:
        config_path: Path to the configuration file, defaults to DEFAULT_CONFIG_PATH
        
    Returns:
        List of PipelineStep objects representing departments
    """
    config = load_pipeline_config(config_path)
    departments = []
    
    for i, dept in enumerate(config.get('departments', [])):
        # Convert the YAML structure to our model structure
        requires = [
            DepartmentDependency(
                department=req['department'],
                status=req.get('status', 'approved')
            ) for req in dept.get('requires', [])
        ]
        
        produces = [
            FileFormat(
                type=prod['type'],
                formats=prod['format'],
                location=prod['location']
            ) for prod in dept.get('produces', [])
        ]
        
        departments.append(
            PipelineStep(
                department_id=dept['id'],
                name=dept['name'],
                description=f"Pipeline step for {dept['name']}",
                step_order=i,
                requires=requires,
                produces=produces,
                enabled=True,
                created_by="system"
            )
        )
    
    return departments


def get_workflows(config_path: Optional[str] = None) -> List[PipelineWorkflow]:
    """
    Get all workflows from the pipeline configuration.
    
    Args:
        config_path: Path to the configuration file, defaults to DEFAULT_CONFIG_PATH
        
    Returns:
        List of PipelineWorkflow objects
    """
    config = load_pipeline_config(config_path)
    workflows = []
    
    for workflow_id, workflow_data in config.get('workflows', {}).items():
        # Process asset workflows
        asset_workflows = []
        for asset_type, asset_data in workflow_data.get('asset_types', {}).items():
            asset_workflows.append(
                AssetWorkflow(
                    asset_type=asset_type,
                    sequence=asset_data['sequence']
                )
            )
        
        # Process shot workflows
        shot_workflows = []
        for shot_type, shot_data in workflow_data.get('shot_types', {}).items():
            shot_workflows.append(
                ShotWorkflow(
                    shot_type=shot_type,
                    sequence=shot_data['sequence']
                )
            )
        
        # Create workflow object
        try:
            workflow_type = WorkflowType(workflow_id)
        except ValueError:
            workflow_type = WorkflowType.CUSTOM
            
        workflows.append(
            PipelineWorkflow(
                name=workflow_id.capitalize(),
                type=workflow_type,
                description=f"{workflow_id.capitalize()} pipeline workflow",
                asset_workflows=asset_workflows,
                shot_workflows=shot_workflows,
                created_by="system"
            )
        )
    
    return workflows


def get_department_by_id(department_id: str, config_path: Optional[str] = None) -> Optional[PipelineStep]:
    """
    Get a specific department by ID.
    
    Args:
        department_id: ID of the department to retrieve
        config_path: Path to the configuration file, defaults to DEFAULT_CONFIG_PATH
        
    Returns:
        PipelineStep object if found, None otherwise
    """
    departments = get_departments(config_path)
    for dept in departments:
        if dept.department_id == department_id:
            return dept
    return None


def get_project_pipeline_config(project_code: str) -> ProjectPipelineConfig:
    """
    Load project pipeline configuration from project config file.
    
    Args:
        project_code: Project code to load configuration for
        
    Returns:
        ProjectPipelineConfig object with the project's pipeline configuration
    """
    project_config = load_project_config(project_code)
    
    if not project_config or 'pipeline' not in project_config:
        return ProjectPipelineConfig()
    
    pipeline_config = project_config['pipeline']
    
    # Parse workflow type
    workflow_type = WorkflowType.DEFAULT
    if 'workflow_type' in pipeline_config:
        try:
            workflow_type = WorkflowType(pipeline_config['workflow_type'])
        except ValueError:
            workflow_type = WorkflowType.CUSTOM
    
    # Parse department dependency overrides
    custom_deps = {}
    if 'custom_department_dependencies' in pipeline_config:
        for dept_id, dept_data in pipeline_config['custom_department_dependencies'].items():
            custom_deps[dept_id] = DepartmentOverride(
                requires=dept_data.get('requires', [])
            )
    
    # Parse asset workflows
    asset_workflows = {}
    if 'asset_workflows' in pipeline_config:
        for asset_type, asset_data in pipeline_config['asset_workflows'].items():
            asset_workflows[asset_type] = AssetWorkflow(
                asset_type=asset_type,
                sequence=asset_data.get('sequence', [])
            )
    
    # Parse shot workflows
    shot_workflows = {}
    if 'shot_workflows' in pipeline_config:
        for shot_type, shot_data in pipeline_config['shot_workflows'].items():
            shot_workflows[shot_type] = ShotWorkflow(
                shot_type=shot_type,
                sequence=shot_data.get('sequence', [])
            )
    
    return ProjectPipelineConfig(
        workflow_type=workflow_type,
        custom_department_dependencies=custom_deps,
        asset_workflows=asset_workflows,
        shot_workflows=shot_workflows
    )


def get_task_template_overrides(project_code: str) -> Dict[str, TaskTemplateOverride]:
    """
    Load task template overrides from project config file.
    
    Args:
        project_code: Project code to load configuration for
        
    Returns:
        Dictionary of department IDs to TaskTemplateOverride objects
    """
    project_config = load_project_config(project_code)
    
    if not project_config or 'task_templates' not in project_config:
        return {}
    
    templates = {}
    for dept_id, template_data in project_config['task_templates'].items():
        templates[dept_id] = TaskTemplateOverride(
            name_template=template_data.get('name_template'),
            description_template=template_data.get('description_template'),
            estimated_hours=template_data.get('estimated_hours'),
            priority=template_data.get('priority'),
            status=template_data.get('status')
        )
    
    return templates


def get_project_pipeline_steps(project_code: str) -> List[PipelineStep]:
    """
    Get pipeline steps with project-specific overrides applied.
    
    Args:
        project_code: Project code to get pipeline steps for
        
    Returns:
        List of PipelineStep objects with project overrides applied
    """
    # Get global pipeline steps
    steps = get_departments()
    
    # Get project pipeline configuration
    project_pipeline = get_project_pipeline_config(project_code)
    
    # Apply department dependency overrides
    for step in steps:
        if step.department_id in project_pipeline.custom_department_dependencies:
            override = project_pipeline.custom_department_dependencies[step.department_id]
            
            # Convert the override format to DepartmentDependency objects
            requires = []
            for req in override.requires:
                requires.append(
                    DepartmentDependency(
                        department=req['department'],
                        status=req.get('status', 'approved')
                    )
                )
            
            # Update the step dependencies with the overrides
            step.requires = requires
    
    return steps