"""Main CLI module with dynamic command generation using metaprogramming."""

import click
import json
import os
from pathlib import Path
from .utils.shell import run_shell_script
from .utils.library_manager import LibraryManager


# Path to the addons directory
LIBRARY_PATH = Path(__file__).parent.parent / "addons"


def create_dynamic_command(script_path):
    """
    Create a dynamic Click command from a shell script.
    
    Args:
        script_path (Path): Path to the shell script
        
    Returns:
        click.Command: Dynamic Click command
    """
    @click.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
    @click.pass_context
    def dynamic_command(ctx):
        """Execute the shell script."""
        if script_path.exists():
            # Pass any extra arguments from the command line to the script
            args = ctx.args if ctx.args else None
            run_shell_script(script_path, args)
        else:
            click.echo(f"Error: Script {script_path} not found.", err=True)
    
    # Set function metadata for Click
    dynamic_command.__name__ = script_path.stem
    dynamic_command.__doc__ = f"Run {script_path.stem} command from {script_path.parent.name} library."
    
    return dynamic_command


def create_dynamic_group(group_name, library_path):
    """
    Create a dynamic Click group from a library directory.
    
    Args:
        group_name (str): Name of the command group
        library_path (Path): Path to the library directory
        
    Returns:
        click.Group: Dynamic Click group with sub-commands
    """
    @click.group(name=group_name)
    def dynamic_group():
        f"""Command group for {group_name} library, auto-generated from {library_path}."""
        pass
    
    # Load metadata for group description if available
    metadata_path = library_path / "metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            dynamic_group.__doc__ = f"{metadata.get('name', group_name)}: {metadata.get('description', '')}"
        except (json.JSONDecodeError, IOError):
            pass
    
    # Add sub-commands from shell scripts
    for script in library_path.glob("*.sh"):
        if script.is_file():
            command = create_dynamic_command(script)
            dynamic_group.add_command(command, name=script.stem)
    
    return dynamic_group


# Create main CLI group
@click.group()
@click.version_option(version="1.0.0", prog_name="corun")
def cli():
    """Corun CLI: Run commands from community-contributed library collections."""
    pass


# Library management commands
@cli.group()
def library():
    """Manage command libraries."""
    pass


@library.command()
def list():
    """List installed libraries."""
    manager = LibraryManager(LIBRARY_PATH)
    libraries = manager.list_installed_libraries()
    
    if not libraries:
        click.echo("No libraries installed.")
        return
    
    click.echo("Installed libraries:")
    for lib in libraries:
        commands = ", ".join(lib.get('commands', []))
        click.echo(f"  • {lib['name']} (v{lib.get('version', 'unknown')}) - {lib.get('description', 'No description')}")
        click.echo(f"    Commands: {commands}")
        click.echo(f"    ID: {lib['library_id']}")
        click.echo()


@library.command()
@click.argument('library_id')
def info(library_id):
    """Show detailed information about a library."""
    manager = LibraryManager(LIBRARY_PATH)
    metadata = manager.get_library_metadata(library_id)
    
    if not metadata:
        click.echo(f"Library '{library_id}' not found.")
        return
    
    click.echo(f"Library: {metadata['name']}")
    click.echo(f"Version: {metadata.get('version', 'unknown')}")
    click.echo(f"Author: {metadata.get('author', 'unknown')}")
    click.echo(f"Description: {metadata.get('description', 'No description')}")
    click.echo(f"Supported shells: {', '.join(metadata.get('shells', []))}")
    click.echo(f"Commands: {', '.join(metadata.get('commands', []))}")
    click.echo(f"Path: {metadata['path']}")


@library.command()
@click.argument('source_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--id', 'library_id', help='Custom library ID (defaults to directory name)')
def install(source_path, library_id):
    """Install a library from a local path."""
    manager = LibraryManager(LIBRARY_PATH)
    if manager.install_library_from_path(Path(source_path), library_id):
        click.echo("Library installed successfully. Restart corun to use new commands.")


@library.command()
@click.argument('library_id')
def remove(library_id):
    """Remove an installed library."""
    manager = LibraryManager(LIBRARY_PATH)
    if manager.remove_library(library_id):
        click.echo("Library removed successfully.")


@library.command()
@click.argument('library_id')
@click.argument('name')
@click.argument('description')
def create(library_id, name, description):
    """Create a new library template."""
    manager = LibraryManager(LIBRARY_PATH)
    manager.create_library_template(library_id, name, description)


# Dynamically add command groups from library directories
def load_library_commands():
    """Load and register command groups from library directories."""
    if not LIBRARY_PATH.exists():
        return
    
    for library_dir in LIBRARY_PATH.iterdir():
        if library_dir.is_dir() and (library_dir / "metadata.json").exists():
            # Convert directory name to command group name (app_list -> app-list)
            group_name = library_dir.name.replace("_", "-")
            group = create_dynamic_group(group_name, library_dir)
            cli.add_command(group)


# Load library commands when module is imported
load_library_commands()


if __name__ == "__main__":
    cli()