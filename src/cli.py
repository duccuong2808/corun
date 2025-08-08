"""Main CLI module with dynamic command generation using metaprogramming."""

import click
import json
import os
from pathlib import Path
from .utils.shell import run_shell_script
from .utils.library_manager import LibraryManager


# Path to the addons directory
LIBRARY_PATH = Path(__file__).parent.parent / "addons"


def get_library_ids():
    """Get list of available library IDs for autocomplete."""
    manager = LibraryManager(LIBRARY_PATH)
    libraries = manager.list_installed_libraries()
    return [lib['library_id'] for lib in libraries]


def get_library_commands(library_id):
    """Get list of commands for a specific library."""
    manager = LibraryManager(LIBRARY_PATH)
    metadata = manager.get_library_metadata(library_id)
    if metadata:
        return metadata.get('commands', [])
    return []


def complete_library_id(ctx, param, incomplete):
    """Autocomplete function for library IDs."""
    library_ids = get_library_ids()
    return [lib_id for lib_id in library_ids if lib_id.startswith(incomplete)]


def complete_library_command(ctx, param, incomplete):
    """Autocomplete function for library commands based on library_id in context."""
    # Get library_id from previous parameter
    library_id = ctx.params.get('library_id')
    if not library_id:
        return []
    
    commands = get_library_commands(library_id)
    return [cmd for cmd in commands if cmd.startswith(incomplete)]


def create_dynamic_command(script_path, library_commands=None):
    """
    Create a dynamic Click command from a shell script.
    
    Args:
        script_path (Path): Path to the shell script
        library_commands (list): List of available commands in this library for autocomplete
        
    Returns:
        click.Command: Dynamic Click command
    """
    def complete_script_args(ctx, param, incomplete):
        """Autocomplete function for script arguments."""
        # For now, we'll provide basic autocomplete with available commands from the library
        if library_commands:
            return [cmd for cmd in library_commands if cmd.startswith(incomplete)]
        return []
    
    def dynamic_command(args):
        """Execute the shell script."""
        if script_path.exists():
            # Pass arguments from the command line to the script
            run_shell_script(script_path, list(args) if args else None)
        else:
            click.echo(f"Error: Script {script_path} not found.", err=True)
    
    # Set function metadata for Click
    dynamic_command.__name__ = script_path.stem
    dynamic_command.__doc__ = f"Run {script_path.stem} command from {script_path.parent.name} library."
    
    # Apply Click decorators after setting metadata
    return click.command(
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
    )(
        click.argument('args', nargs=-1, shell_complete=complete_script_args if library_commands else None)(
            dynamic_command
        )
    )


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
    
    # Load metadata for group description and commands if available
    library_commands = []
    metadata_path = library_path / "metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            dynamic_group.__doc__ = f"{metadata.get('name', group_name)}: {metadata.get('description', '')}"
            library_commands = metadata.get('commands', [])
        except (json.JSONDecodeError, IOError):
            pass
    
    # Add sub-commands from shell scripts
    for script in library_path.glob("*.sh"):
        if script.is_file():
            command = create_dynamic_command(script, library_commands)
            dynamic_group.add_command(command, name=script.stem)
    
    return dynamic_group


# Create main CLI group
@click.group()
@click.version_option(version="1.0.0", prog_name="corun")
def cli():
    """Corun CLI: Run commands from community-contributed library collections."""
    pass


@cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']), required=False)
def completion(shell):
    """
    Show shell completion setup instructions or generate completion script.
    
    Supported shells: bash, zsh, fish
    
    Examples:
        corun completion bash     # Show bash completion setup
        corun completion zsh      # Show zsh completion setup  
        corun completion fish     # Show fish completion setup
        corun completion          # Auto-detect shell from environment
    """
    import shutil
    
    # Auto-detect shell if not provided
    if not shell:
        shell_path = os.environ.get('SHELL', '')
        if 'bash' in shell_path:
            shell = 'bash'
        elif 'zsh' in shell_path:
            shell = 'zsh'
        elif 'fish' in shell_path:
            shell = 'fish'
        else:
            click.echo("Could not auto-detect shell. Please specify one: bash, zsh, fish")
            return
    
    click.echo(f"Setting up autocomplete for {shell}:")
    click.echo()
    
    if shell == 'bash':
        click.echo("Add this line to your ~/.bashrc or ~/.bash_profile:")
        click.echo('eval "$(_CORUN_COMPLETE=bash_source corun)"')
        click.echo()
        click.echo("Or run this command to add it automatically:")
        click.echo('echo \'eval "$(_CORUN_COMPLETE=bash_source corun)"\' >> ~/.bashrc')
        
    elif shell == 'zsh':
        click.echo("Add this line to your ~/.zshrc:")
        click.echo('eval "$(_CORUN_COMPLETE=zsh_source corun)"')
        click.echo()
        click.echo("Or run this command to add it automatically:")
        click.echo('echo \'eval "$(_CORUN_COMPLETE=zsh_source corun)"\' >> ~/.zshrc')
        
    elif shell == 'fish':
        click.echo("Add this line to your ~/.config/fish/config.fish:")
        click.echo('eval (env _CORUN_COMPLETE=fish_source corun)')
        click.echo()
        click.echo("Or run this command to add it automatically:")
        click.echo('echo \'eval (env _CORUN_COMPLETE=fish_source corun)\' >> ~/.config/fish/config.fish')
    
    click.echo()
    click.echo("After adding the line, restart your shell or run:")
    click.echo(f"source ~/.{shell}rc" if shell in ['bash', 'zsh'] else "source ~/.config/fish/config.fish")
    click.echo()
    click.echo("Then you can use TAB completion with corun commands:")
    click.echo("  corun <TAB>              # Show available commands")
    click.echo("  corun library <TAB>      # Show library management commands")
    click.echo("  corun library info <TAB> # Autocomplete library IDs")
    
    # Show actual library examples if any exist
    library_ids = get_library_ids()
    if library_ids:
        click.echo("  # Library-specific commands:")
        for lib_id in library_ids[:3]:  # Show up to 3 examples
            click.echo(f"  corun {lib_id} <TAB>        # Show commands in {lib_id} library")
    
    click.echo()


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
@click.argument('library_id', shell_complete=complete_library_id)
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
@click.argument('library_id', shell_complete=complete_library_id)
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
            # Load metadata to get library_id
            metadata_path = library_dir / "metadata.json"
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                # Use library_id from metadata, fallback to directory name conversion
                group_name = metadata.get('library_id', library_dir.name.replace("_", "-"))
                group = create_dynamic_group(group_name, library_dir)
                cli.add_command(group)
            except (json.JSONDecodeError, IOError) as e:
                click.echo(f"Warning: Could not load library {library_dir.name}: {e}", err=True)


# Load library commands when module is imported
load_library_commands()


if __name__ == "__main__":
    cli()