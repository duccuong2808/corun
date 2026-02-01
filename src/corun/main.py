"""Corun CLI - Main entry point."""

import sys
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .executor import execute_script
from .library.commands import app as library_app
from .scanner import get_library_by_id, scan_addons

# Main app
app = typer.Typer(
    name="corun",
    help="Command Runner - CLI tool để quản lý và chạy shell scripts",
    add_completion=True,
    no_args_is_help=True,
)

# Add library subcommand
app.add_typer(library_app, name="library")

console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"corun version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
):
    """Corun - Command Runner CLI."""
    pass


@app.command(name="run", hidden=True)
def run_command(
    target: str = typer.Argument(..., help="Library ID or command name"),
    command: Optional[str] = typer.Argument(None, help="Command name (if library)"),
    args: Optional[list[str]] = typer.Argument(None, help="Arguments to pass"),
):
    """
    Run a library command or standalone script.

    This is a fallback command - normally dynamic commands are used.
    """
    libraries, standalone = scan_addons()

    # Check if target is a library
    library = None
    for lib in libraries:
        if lib.library_id == target:
            library = lib
            break

    if library:
        # Library command
        if not command:
            # Show available commands
            console.print(f"\n[bold]{library.name}[/bold] - {library.description}\n")
            console.print("[bold]Available commands:[/bold]")
            for cmd in library.commands:
                console.print(f"  • {cmd.name}")
            return

        # Find command in library
        cmd_obj = None
        for cmd in library.commands:
            if cmd.name == command:
                cmd_obj = cmd
                break

        if not cmd_obj:
            console.print(
                f"[red]Error: Command '{command}' not found in '{target}'[/red]"
            )
            console.print("\nAvailable commands:")
            for cmd in library.commands:
                console.print(f"  • {cmd.name}")
            raise typer.Exit(1)

        # Execute
        exit_code = execute_script(cmd_obj.script_path, args)
        raise typer.Exit(exit_code)

    # Check standalone
    for cmd in standalone:
        if cmd.name == target:
            # Standalone script - command becomes first arg
            all_args = []
            if command:
                all_args.append(command)
            if args:
                all_args.extend(args)

            exit_code = execute_script(cmd.script_path, all_args or None)
            raise typer.Exit(exit_code)

    # Not found
    console.print(f"[red]Error: '{target}' not found[/red]")
    console.print("\nRun [cyan]corun library list[/cyan] to see available commands.")
    raise typer.Exit(1)


def register_dynamic_commands():
    """Register dynamic commands from scanned libraries."""
    libraries, standalone = scan_addons()

    # Register library commands
    for library in libraries:
        # Create a sub-app for the library
        lib_app = typer.Typer(
            help=library.description,
            no_args_is_help=True,
        )

        # Add commands
        for cmd in library.commands:

            def make_command(script_path):
                """Create command function with closure."""

                def command_func(
                    args: Optional[list[str]] = typer.Argument(
                        None, help="Arguments to pass to the script"
                    ),
                ):
                    exit_code = execute_script(script_path, args)
                    raise typer.Exit(exit_code)

                return command_func

            lib_app.command(name=cmd.name)(make_command(cmd.script_path))

        app.add_typer(lib_app, name=library.library_id)

    # Register standalone commands
    for cmd in standalone:

        def make_standalone(script_path):
            """Create standalone command with closure."""

            def standalone_func(
                args: Optional[list[str]] = typer.Argument(
                    None, help="Arguments to pass to the script"
                ),
            ):
                exit_code = execute_script(script_path, args)
                raise typer.Exit(exit_code)

            return standalone_func

        app.command(name=cmd.name)(make_standalone(cmd.script_path))


# Register dynamic commands on import
register_dynamic_commands()


if __name__ == "__main__":
    app()
