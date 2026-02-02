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


@app.command(name="completion")
def completion_command(
    shell: Optional[str] = typer.Argument(
        None, help="Shell type (bash/zsh/fish). Auto-detect if not specified."
    ),
):
    """
    Show shell completion setup instructions.
    
    This command helps you set up tab completion for your shell.
    """
    from .completion import show_completion_help
    
    show_completion_help(shell)


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


def show_conflict_warning(conflicts: dict):
    """Display startup warning about conflicts."""
    if not conflicts:
        return
    
    console.print("\n[yellow bold]⚠️  Naming conflicts detected![/yellow bold]")
    for name, (lib, cmd) in conflicts.items():
        console.print(f"   • [cyan]{name}[/cyan]: library [green]{lib.library_id}/[/green] vs standalone [dim]{cmd.script_path.name}[/dim]")
    console.print("[dim]   Run 'corun library list' for details.[/dim]\n")


def make_conflict_command(name: str, library, standalone_cmd):
    """Create interactive command for conflicting names."""
    
    def conflict_func(
        args: Optional[list[str]] = typer.Argument(
            None, help="Arguments to pass to the script"
        ),
    ):
        console.print(f"\n[yellow bold]⚠️  Conflict: '{name}' exists as both library and standalone[/yellow bold]\n")
        console.print(f"  [cyan]1.[/cyan] Library [green]{library.library_id}/[/green] - {library.description}")
        console.print(f"  [cyan]2.[/cyan] Standalone [dim]{standalone_cmd.script_path}[/dim]")
        console.print()
        
        choice = typer.prompt(
            "Which one do you want to run?",
            type=str,
            default="1",
            show_default=True,
        )
        
        if choice == "1":
            # Show library commands
            console.print(f"\n[bold]{library.name}[/bold] - {library.description}\n")
            console.print("[bold]Available commands:[/bold]")
            for cmd in library.commands:
                console.print(f"  • [cyan]corun {library.library_id} {cmd.name}[/cyan]")
            console.print()
        elif choice == "2":
            # Run standalone
            exit_code = execute_script(standalone_cmd.script_path, args)
            raise typer.Exit(exit_code)
        else:
            console.print("[red]Invalid choice. Exiting.[/red]")
            raise typer.Exit(1)
        
        # Show fix suggestion
        console.print("[dim]──────────────────────────────────────────[/dim]")
        console.print("[bold]💡 To fix this conflict:[/bold]")
        console.print(f"   Rename: [cyan]mv {standalone_cmd.script_path} {standalone_cmd.script_path.parent}/{name}_script.sh[/cyan]")
        console.print(f"   Or remove: [cyan]rm {standalone_cmd.script_path}[/cyan]")
        console.print()
    
    return conflict_func


def register_dynamic_commands():
    """Register dynamic commands from scanned libraries."""
    libraries, standalone, conflicts = scan_addons()
    
    # Show conflict warnings at startup
    show_conflict_warning(conflicts)

    # Register library commands (skip those with conflicts - they get interactive handler)
    for library in libraries:
        if library.library_id in conflicts:
            # Skip - will be handled by interactive conflict handler below
            continue
            
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

    # Register standalone commands (those with conflicts get interactive handler)
    for cmd in standalone:
        if cmd.name in conflicts:
            # Register interactive conflict handler
            lib, standalone_cmd = conflicts[cmd.name]
            app.command(name=cmd.name)(make_conflict_command(cmd.name, lib, standalone_cmd))
            continue

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
