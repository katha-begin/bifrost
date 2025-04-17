#!/usr/bin/env python
# cli_app.py
# Part of the Bifrost Animation Asset Management System
#
# Created: 2025-04-02

import click
import logging
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Dict, List, Optional

# Add the parent directory to the path so we can import from the package
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from bifrost.core.config import config
from bifrost.models.asset import AssetStatus, AssetType
from bifrost.services.asset_service import asset_service
from bifrost.services.review_service import review_service
from bifrost.models.review import ReviewStatus, NoteStatus

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a rich console for pretty output
console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Bifrost: Animation Asset Management System CLI.
    
    This command-line interface allows you to interact with the Bifrost
    system for managing animation assets and shots.
    """
    pass


@cli.group()
def asset():
    """Commands for managing assets."""
    pass


@asset.command("create")
@click.option("--name", "-n", required=True, help="Name of the asset")
@click.option("--type", "-t", required=True, 
              type=click.Choice([t.value for t in AssetType]),
              help="Type of the asset")
@click.option("--description", "-d", default="", help="Description of the asset")
@click.option("--status", "-s", default="concept",
              type=click.Choice([s.value for s in AssetStatus]),
              help="Status of the asset")
@click.option("--user", "-u", default=os.getenv("USER", "anonymous"),
              help="Username of the creator")
@click.option("--thumbnail", help="Path to a thumbnail image")
@click.option("--preview", help="Path to a preview file")
def create_asset(name, type, description, status, user, thumbnail, preview):
    """Create a new asset in the system."""
    try:
        # Create the asset
        asset = asset_service.create_asset(
            name=name,
            asset_type=type,
            description=description,
            status=status,
            created_by=user,
            thumbnail_path=thumbnail,
            preview_path=preview
        )
        
        console.print(f"[green]Asset created successfully![/green]")
        console.print(f"Asset ID: [blue]{asset.id}[/blue]")
        console.print(f"Name: {asset.name}")
        console.print(f"Type: {asset.asset_type.value}")
        console.print(f"Status: {asset.status.value}")
        
    except Exception as e:
        console.print(f"[red]Error creating asset: {str(e)}[/red]")
        logger.exception("Error creating asset")


@asset.command("list")
@click.option("--query", "-q", help="Text search term for name and description")
@click.option("--type", "-t", help="Filter by asset type",
              type=click.Choice([t.value for t in AssetType] + ['']))
@click.option("--status", "-s", help="Filter by status",
              type=click.Choice([s.value for s in AssetStatus] + ['']))
@click.option("--creator", "-c", help="Filter by creator")
@click.option("--limit", "-l", default=50, help="Maximum number of results to return")
@click.option("--offset", "-o", default=0, help="Offset for pagination")
def list_assets(query, type, status, creator, limit, offset):
    """List assets based on various filters."""
    try:
        # Handle empty string filters
        asset_type = None if not type else type
        asset_status = None if not status else status
        
        # Search for assets
        assets = asset_service.search_assets(
            query=query or "",
            asset_type=asset_type,
            status=asset_status,
            created_by=creator,
            limit=limit,
            offset=offset
        )
        
        if not assets:
            console.print("[yellow]No assets found matching the criteria.[/yellow]")
            return
        
        # Create a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=36)
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Created By")
        table.add_column("Versions")
        
        # Add rows to the table
        for asset in assets:
            table.add_row(
                asset.id,
                asset.name,
                asset.asset_type.value,
                asset.status.value,
                asset.created_by,
                str(len(asset.versions))
            )
        
        console.print(table)
        console.print(f"Showing {len(assets)} assets (offset: {offset}, limit: {limit})")
        
    except Exception as e:
        console.print(f"[red]Error listing assets: {str(e)}[/red]")
        logger.exception("Error listing assets")


@asset.command("info")
@click.argument("asset_id")
def asset_info(asset_id):
    """Get detailed information about an asset."""
    try:
        # Get the asset
        asset = asset_service.get_asset(asset_id)
        
        if not asset:
            console.print(f"[red]Asset with ID {asset_id} not found.[/red]")
            return
        
        # Print asset information
        console.print(f"[bold]Asset Information[/bold]")
        console.print(f"ID: [blue]{asset.id}[/blue]")
        console.print(f"Name: {asset.name}")
        console.print(f"Type: {asset.asset_type.value}")
        console.print(f"Status: {asset.status.value}")
        console.print(f"Description: {asset.description}")
        console.print(f"Created by: {asset.created_by} at {asset.created_at}")
        console.print(f"Last modified by: {asset.modified_by} at {asset.modified_at}")
        
        if asset.thumbnail_path:
            console.print(f"Thumbnail: {asset.thumbnail_path}")
        if asset.preview_path:
            console.print(f"Preview: {asset.preview_path}")
        
        # Print tags
        if asset.tags:
            console.print("\n[bold]Tags:[/bold]")
            for tag in asset.tags:
                console.print(f"- {tag.name} [#{tag.color}]")
        
        # Print versions
        if asset.versions:
            console.print("\n[bold]Versions:[/bold]")
            version_table = Table(show_header=True)
            version_table.add_column("Number")
            version_table.add_column("Created")
            version_table.add_column("By")
            version_table.add_column("Status")
            version_table.add_column("Comment")
            
            for version in sorted(asset.versions, key=lambda v: v.version_number):
                version_table.add_row(
                    str(version.version_number),
                    str(version.created_at),
                    version.created_by,
                    version.status.value,
                    version.comment[:50] + ("..." if len(version.comment) > 50 else "")
                )
            
            console.print(version_table)
        
        # Print dependencies
        if asset.dependencies:
            console.print("\n[bold]Dependencies:[/bold]")
            for dep in asset.dependencies:
                optional_text = " (optional)" if dep.optional else ""
                console.print(f"- {dep.dependent_asset_id} ({dep.dependency_type}){optional_text}")
        
        # Print dependents
        if asset.dependents:
            console.print("\n[bold]Used by:[/bold]")
            for dep in asset.dependents:
                optional_text = " (optional)" if dep.optional else ""
                console.print(f"- {dep.dependent_asset_id} ({dep.dependency_type}){optional_text}")
        
    except Exception as e:
        console.print(f"[red]Error getting asset info: {str(e)}[/red]")
        logger.exception("Error getting asset info")


@asset.command("update")
@click.argument("asset_id")
@click.option("--name", "-n", help="New name for the asset")
@click.option("--description", "-d", help="New description for the asset")
@click.option("--status", "-s", 
              type=click.Choice([s.value for s in AssetStatus]),
              help="New status for the asset")
@click.option("--user", "-u", default=os.getenv("USER", "anonymous"),
              help="Username making the update")
def update_asset(asset_id, name, description, status, user):
    """Update an existing asset."""
    try:
        # Get the asset
        asset = asset_service.get_asset(asset_id)
        
        if not asset:
            console.print(f"[red]Asset with ID {asset_id} not found.[/red]")
            return
        
        # Update fields if provided
        if name:
            asset.name = name
        if description:
            asset.description = description
        if status:
            asset.status = AssetStatus(status)
        
        asset.modified_by = user
        
        # Save the changes
        success = asset_service.update_asset(asset)
        
        if success:
            console.print(f"[green]Asset updated successfully![/green]")
        else:
            console.print(f"[red]Failed to update asset.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error updating asset: {str(e)}[/red]")
        logger.exception("Error updating asset")


@asset.command("delete")
@click.argument("asset_id")
@click.option("--confirm", is_flag=True, help="Confirm deletion without prompting")
def delete_asset(asset_id, confirm):
    """Delete an asset."""
    try:
        # Get the asset
        asset = asset_service.get_asset(asset_id)
        
        if not asset:
            console.print(f"[red]Asset with ID {asset_id} not found.[/red]")
            return
        
        # Confirm deletion
        if not confirm:
            if not click.confirm(f"Are you sure you want to delete asset '{asset.name}' ({asset_id})?"):
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        # Delete the asset
        success = asset_service.delete_asset(asset_id)
        
        if success:
            console.print(f"[green]Asset deleted successfully![/green]")
        else:
            console.print(f"[red]Failed to delete asset.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error deleting asset: {str(e)}[/red]")
        logger.exception("Error deleting asset")


@asset.command("add-version")
@click.argument("asset_id")
@click.option("--file", "-f", required=True, help="Path to the version file")
@click.option("--version", "-v", type=int, help="Version number (auto-incremented if not provided)")
@click.option("--comment", "-c", default="", help="Comment describing the version changes")
@click.option("--status", "-s", default="in_progress",
              type=click.Choice([s.value for s in AssetStatus]),
              help="Status of the version")
@click.option("--user", "-u", default=os.getenv("USER", "anonymous"),
              help="Username of the creator")
def add_asset_version(asset_id, file, version, comment, status, user):
    """Add a new version to an existing asset."""
    try:
        # Check if file exists
        file_path = Path(file)
        if not file_path.exists():
            console.print(f"[red]File '{file}' not found.[/red]")
            return
        
        # Add the version
        asset_version = asset_service.add_version(
            asset_id=asset_id,
            version_number=version,
            file_path=file_path,
            comment=comment,
            status=status,
            created_by=user
        )
        
        if asset_version:
            console.print(f"[green]Version {asset_version.version_number} added successfully![/green]")
        else:
            console.print(f"[red]Failed to add version. Asset may not exist.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error adding version: {str(e)}[/red]")
        logger.exception("Error adding version")


@asset.command("add-tag")
@click.argument("asset_id")
@click.option("--name", "-n", required=True, help="Name of the tag")
@click.option("--color", "-c", default="808080", help="Color of the tag (hex code without #)")
@click.option("--description", "-d", default="", help="Description of the tag")
def add_asset_tag(asset_id, name, color, description):
    """Add a tag to an asset."""
    try:
        # Get the asset
        asset = asset_service.get_asset(asset_id)
        
        if not asset:
            console.print(f"[red]Asset with ID {asset_id} not found.[/red]")
            return
        
        # Check if tag already exists
        for tag in asset.tags:
            if tag.name == name:
                console.print(f"[yellow]Tag '{name}' already exists on this asset.[/yellow]")
                return
        
        # Add the tag
        asset.add_tag(name, f"#{color}" if not color.startswith("#") else color, description)
        
        # Save the changes
        success = asset_service.update_asset(asset)
        
        if success:
            console.print(f"[green]Tag '{name}' added successfully![/green]")
        else:
            console.print(f"[red]Failed to add tag.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error adding tag: {str(e)}[/red]")
        logger.exception("Error adding tag")


@asset.command("add-dependency")
@click.argument("asset_id")
@click.argument("dependent_asset_id")
@click.option("--type", "-t", default="reference", help="Type of dependency")
@click.option("--optional", is_flag=True, help="Mark dependency as optional")
def add_asset_dependency(asset_id, dependent_asset_id, type, optional):
    """Add a dependency between two assets."""
    try:
        # Add the dependency
        success = asset_service.add_dependency(
            asset_id=asset_id,
            dependent_asset_id=dependent_asset_id,
            dependency_type=type,
            optional=optional
        )
        
        if success:
            console.print(f"[green]Dependency added successfully![/green]")
        else:
            console.print(f"[red]Failed to add dependency. One or both assets may not exist.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error adding dependency: {str(e)}[/red]")
        logger.exception("Error adding dependency")


@cli.group()
def review():
    """Commands for managing reviews."""
    pass

@review.command("create")
@click.option("--name", "-n", required=True, help="Name of the review session")
@click.option("--description", "-d", default="", help="Description of the review")
@click.option("--items", "-i", multiple=True, help="List of item IDs to review")
def create_review(name: str, description: str, items: List[str]):
    """Create a new review session."""
    try:
        review = review_service.create_review(
            name=name,
            description=description,
            items=items
        )
        console.print(f"[green]Created review session: {review.id}[/green]")
        console.print(f"Name: {review.name}")
        console.print(f"Status: {review.status.value}")
    except Exception as e:
        console.print(f"[red]Error creating review: {str(e)}[/red]")
        logger.exception("Error creating review")

@review.command("show")
@click.argument("review_id")
def show_review(review_id: str):
    """Show details of a specific review."""
    try:
        review = review_service.get_review(review_id)
        if not review:
            console.print(f"[yellow]Review not found: {review_id}[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field")
        table.add_column("Value")
        
        table.add_row("ID", review.id)
        table.add_row("Name", review.name)
        table.add_row("Description", review.description)
        table.add_row("Status", review.status.value)
        table.add_row("Created", str(review.created_at))
        table.add_row("Created by", review.created_by)
        
        console.print(table)
        
        if review.items:
            console.print("\n[bold]Review Items:[/bold]")
            items_table = Table(show_header=True, header_style="bold blue")
            items_table.add_column("Type")
            items_table.add_column("ID")
            items_table.add_column("Version")
            items_table.add_column("Status")
            
            for item in review.items:
                items_table.add_row(
                    item.item_type,
                    item.item_id,
                    item.version_id,
                    item.status.value
                )
            console.print(items_table)
            
    except Exception as e:
        console.print(f"[red]Error showing review: {str(e)}[/red]")
        logger.exception("Error showing review")

@review.command("update-status")
@click.argument("review_id")
@click.option("--status", "-s", required=True,
              type=click.Choice([s.value for s in ReviewStatus]),
              help="New status for the review")
def update_review_status(review_id: str, status: str):
    """Update the status of a review."""
    try:
        review = review_service.update_review_status(review_id, ReviewStatus(status))
        console.print(f"[green]Updated review {review_id} status to: {status}[/green]")
    except Exception as e:
        console.print(f"[red]Error updating review status: {str(e)}[/red]")
        logger.exception("Error updating review status")

@review.command("add-item")
@click.argument("review_id")
@click.option("--item-id", "-i", required=True, help="ID of the item to add")
@click.option("--type", "-t", required=True,
              type=click.Choice(["shot", "asset"]),
              help="Type of item")
@click.option("--version", "-v", required=True, help="Version ID of the item")
def add_review_item(review_id: str, item_id: str, type: str, version: str):
    """Add an item to a review session."""
    try:
        item = review_service.add_review_item(
            review_id=review_id,
            item_id=item_id,
            item_type=type,
            version_id=version
        )
        console.print(f"[green]Added {type} {item_id} to review {review_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error adding review item: {str(e)}[/red]")
        logger.exception("Error adding review item")

@review.command("remove-item")
@click.argument("review_id")
@click.argument("item_id")
def remove_review_item(review_id: str, item_id: str):
    """Remove an item from a review session."""
    try:
        review_service.remove_review_item(review_id, item_id)
        console.print(f"[green]Removed item {item_id} from review {review_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error removing review item: {str(e)}[/red]")
        logger.exception("Error removing review item")


@cli.group()
def config():
    """Commands for managing configuration."""
    pass


@config.command("get")
@click.argument("key", required=False)
def get_config_value(key):
    """Get a configuration value or all configuration."""
    try:
        if key:
            value = config.get(key)
            if value is None:
                console.print(f"[yellow]Config key '{key}' not found.[/yellow]")
            else:
                console.print(f"{key} = {value}")
        else:
            # Print all config
            all_config = config.get_all()
            console.print("[bold]Current Configuration:[/bold]")
            _print_config_dict(all_config)
        
    except Exception as e:
        console.print(f"[red]Error getting configuration: {str(e)}[/red]")
        logger.exception("Error getting configuration")


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config_value(key, value):
    """Set a configuration value."""
    try:
        # Try to parse the value as JSON
        try:
            import json
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            # If not valid JSON, use the raw string
            parsed_value = value
        
        # Set the config value
        config.set(key, parsed_value)
        
        # Save the changes
        success = config.save()
        
        if success:
            console.print(f"[green]Config value '{key}' set successfully![/green]")
        else:
            console.print(f"[red]Failed to save configuration.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error setting configuration: {str(e)}[/red]")
        logger.exception("Error setting configuration")


def _print_config_dict(config_dict, indent=0):
    """Recursively print a configuration dictionary."""
    for key, value in config_dict.items():
        if isinstance(value, dict):
            console.print("  " * indent + f"{key}:")
            _print_config_dict(value, indent + 1)
        else:
            console.print("  " * indent + f"{key} = {value}")


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == "__main__":
    main()





