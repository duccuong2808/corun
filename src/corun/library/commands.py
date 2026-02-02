"""Library management commands."""

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..scanner import (
    ensure_addons_dir,
    get_addons_dir,
    get_library_by_id,
    load_metadata,
    scan_addons,
    scan_library,
)

app = typer.Typer(help="Manage script libraries")
console = Console()


@app.command("list")
def list_libraries():
    """List all installed libraries."""
    libraries, standalone = scan_addons()

    if not libraries and not standalone:
        console.print("[yellow]No libraries or scripts installed.[/yellow]")
        console.print(f"\nAddons directory: {get_addons_dir()}")
        return

    if libraries:
        console.print("\n[bold]Installed libraries:[/bold]\n")
        for lib in libraries:
            console.print(f"  • [cyan]{lib.name}[/cyan] (v{lib.version})")
            console.print(f"    {lib.description}")
            cmd_names = [c.name for c in lib.commands]
            console.print(f"    Commands: [green]{', '.join(cmd_names)}[/green]")
            console.print(f"    ID: [dim]{lib.library_id}[/dim]\n")

    if standalone:
        console.print("[bold]Standalone scripts:[/bold]\n")
        for cmd in standalone:
            console.print(f"  • [cyan]{cmd.name}[/cyan]")


@app.command("info")
def library_info(library_id: str = typer.Argument(..., help="Library ID")):
    """Show detailed information about a library."""
    library = get_library_by_id(library_id)

    if not library:
        console.print(f"[red]Error: Library '{library_id}' not found.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Library:[/bold] {library.name}")
    console.print(f"[bold]Version:[/bold] {library.version}")

    if library.metadata:
        if library.metadata.author:
            console.print(f"[bold]Author:[/bold] {library.metadata.author}")
        if library.metadata.shells:
            console.print(
                f"[bold]Supported shells:[/bold] {', '.join(library.metadata.shells)}"
            )

    console.print(f"[bold]Description:[/bold] {library.description}")

    cmd_names = [c.name for c in library.commands]
    console.print(f"[bold]Commands:[/bold] {', '.join(cmd_names)}")
    console.print(f"[bold]Path:[/bold] {library.path}")


@app.command("install")
def install_library(
    source_path: Path = typer.Argument(..., help="Path to library folder"),
    library_id: Optional[str] = typer.Option(
        None, "--id", "-i", help="Custom library ID"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if exists"),
):
    """Install a library from a local path."""
    if not source_path.exists():
        console.print(f"[red]Error: Path not found: {source_path}[/red]")
        raise typer.Exit(1)

    if not source_path.is_dir():
        console.print(f"[red]Error: Not a directory: {source_path}[/red]")
        raise typer.Exit(1)

    # Check for .sh files
    scripts = list(source_path.glob("*.sh"))
    if not scripts:
        console.print("[red]Error: No .sh files found in library.[/red]")
        raise typer.Exit(1)

    # Determine library ID
    metadata = load_metadata(source_path)
    if library_id is None:
        library_id = metadata.library_id if metadata else source_path.name

    # Target path
    addons_dir = ensure_addons_dir()
    target_path = addons_dir / library_id

    # Check if exists
    if target_path.exists() and not force:
        console.print(f"[yellow]Library '{library_id}' already exists.[/yellow]")
        if not typer.confirm("Overwrite?"):
            raise typer.Abort()
        shutil.rmtree(target_path)

    # Copy library
    shutil.copytree(source_path, target_path)

    # Make scripts executable
    for script in target_path.glob("*.sh"):
        script.chmod(0o755)

    console.print(f"[green]✓ Installed library: {library_id}[/green]")
    console.print(f"  Path: {target_path}")

    # Show available commands
    lib = scan_library(target_path)
    if lib:
        cmd_names = [c.name for c in lib.commands]
        console.print(f"  Commands: {', '.join(cmd_names)}")


@app.command("remove")
def remove_library(
    library_id: str = typer.Argument(..., help="Library ID to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove an installed library."""
    library = get_library_by_id(library_id)

    if not library:
        console.print(f"[red]Error: Library '{library_id}' not found.[/red]")
        raise typer.Exit(1)

    # Show what will be removed
    console.print(f"\n[yellow]Will remove library: {library.name}[/yellow]")
    cmd_names = [c.name for c in library.commands]
    console.print(f"Commands that will be lost: {', '.join(cmd_names)}")
    console.print(f"Path: {library.path}\n")

    if not force and not typer.confirm("Are you sure?"):
        raise typer.Abort()

    # Remove
    shutil.rmtree(library.path)
    console.print(f"[green]✓ Removed library: {library_id}[/green]")


@app.command("create")
def create_library(
    library_id: Optional[str] = typer.Argument(None, help="Library ID (folder name)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Library name"),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="Library description"
    ),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i/-I", help="Interactive mode"
    ),
):
    """Create a new library template."""
    import json
    import re

    # Interactive mode
    if interactive and library_id is None:
        console.print("\n[bold cyan]📦 Create New Library[/bold cyan]\n")
        
        # Prompt for library ID
        while True:
            library_id = typer.prompt("Library ID (folder name)")
            if re.match(r"^[a-zA-Z0-9_-]+$", library_id):
                break
            console.print(
                "[red]Error: Library ID can only contain letters, numbers, underscores, and hyphens.[/red]"
            )
        
        # Prompt for name (optional)
        default_name = library_id.replace("_", " ").replace("-", " ").title()
        name_input = typer.prompt(
            f"Library name", 
            default=default_name,
            show_default=True
        )
        name = name_input if name_input else default_name
        
        # Prompt for description (optional)
        description_input = typer.prompt(
            "Description",
            default=f"Custom library: {library_id}",
            show_default=True
        )
        description = description_input if description_input else f"Custom library: {library_id}"
        
        # Prompt for author (optional)
        author_input = typer.prompt(
            "Author name",
            default="Your Name",
            show_default=True
        )
        author = author_input if author_input else "Your Name"
        
        console.print()  # Empty line
    
    # Non-interactive mode validation
    if library_id is None:
        console.print("[red]Error: Library ID is required in non-interactive mode.[/red]")
        raise typer.Exit(1)
    
    # Validate library ID
    if not re.match(r"^[a-zA-Z0-9_-]+$", library_id):
        console.print(
            "[red]Error: Library ID can only contain letters, numbers, underscores, and hyphens.[/red]"
        )
        raise typer.Exit(1)

    # Target path
    addons_dir = ensure_addons_dir()
    target_path = addons_dir / library_id

    # Check if exists
    if target_path.exists():
        console.print(f"[red]Error: Library '{library_id}' already exists.[/red]")
        console.print(f"Path: {target_path}")
        raise typer.Exit(1)

    # Create directory
    target_path.mkdir(parents=True)

    # Generate metadata.json
    metadata = {
        "name": name or library_id.replace("_", " ").replace("-", " ").title(),
        "version": "0.1.0",
        "description": description or f"Custom library: {library_id}",
        "library_id": library_id,
        "author": author or "Your Name",
        "shells": ["bash", "zsh"],
        "commands": ["example"],
    }

    metadata_path = target_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Generate example.sh
    example_script = """#!/bin/bash
# Example command for {library_name}
# Usage: corun {library_id} example [args...]

echo "👋 Hello from {library_name}!"
echo "Arguments: $@"
""".format(
        library_name=metadata["name"], library_id=library_id
    )

    example_path = target_path / "example.sh"
    with open(example_path, "w") as f:
        f.write(example_script)

    # Make executable
    example_path.chmod(0o755)

    # Success message
    console.print(f"[green]✓ Created library: {library_id}[/green]")
    console.print(f"  Path: {target_path}")
    console.print(f"  Name: {metadata['name']}")
    console.print(f"  Author: {metadata['author']}")
    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"  1. Edit: {metadata_path}")
    console.print(f"  2. Add scripts: {target_path}/*.sh")
    console.print(f"  3. Test: [cyan]corun {library_id} example[/cyan]")
