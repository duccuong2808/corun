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
