"""Shell script execution utilities."""

import subprocess
import click
import os
import stat
from pathlib import Path


def run_shell_script(script_path):
    """
    Execute a shell script and handle output.
    
    Args:
        script_path (Path): Path to the shell script to execute
    """
    script_path = Path(script_path)
    
    if not script_path.exists():
        click.echo(f"Error: Script {script_path} not found.", err=True)
        return False
    
    # Check if script is executable
    if not is_executable(script_path):
        click.echo(f"Error: Script {script_path} is not executable.", err=True)
        click.echo("Run: chmod +x {script_path} to make it executable.", err=True)
        return False
    
    try:
        # Use the script's shebang to determine interpreter
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=script_path.parent  # Run in script's directory for relative paths
        )
        
        # Output stdout
        if result.stdout:
            click.echo(result.stdout.rstrip())
        
        # Output stderr as warning (not error)
        if result.stderr:
            click.echo(f"Warning: {result.stderr.rstrip()}", err=True)
            
        return True
        
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running script {script_path}:", err=True)
        click.echo(f"Exit code: {e.returncode}", err=True)
        if e.stdout:
            click.echo(f"Output: {e.stdout.rstrip()}", err=True)
        if e.stderr:
            click.echo(f"Error: {e.stderr.rstrip()}", err=True)
        return False
    
    except FileNotFoundError:
        click.echo(f"Error: Cannot execute {script_path}. Check shebang or permissions.", err=True)
        return False
    
    except Exception as e:
        click.echo(f"Unexpected error running {script_path}: {str(e)}", err=True)
        return False


def is_executable(file_path):
    """
    Check if a file is executable.
    
    Args:
        file_path (Path): Path to the file to check
        
    Returns:
        bool: True if file is executable, False otherwise
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        return False
    
    # On Unix-like systems, check execute permission
    if os.name != 'nt':  # Not Windows
        st = file_path.stat()
        return bool(st.st_mode & stat.S_IEXEC)
    
    # On Windows, check if it has a script extension or .exe
    if os.name == 'nt':
        return file_path.suffix.lower() in ['.bat', '.cmd', '.exe', '.sh']
    
    return True


def make_executable(file_path):
    """
    Make a file executable.
    
    Args:
        file_path (Path): Path to the file to make executable
        
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = Path(file_path)
    
    try:
        if os.name != 'nt':  # Unix-like systems
            current_mode = file_path.stat().st_mode
            file_path.chmod(current_mode | stat.S_IEXEC)
        return True
    except Exception as e:
        click.echo(f"Error making {file_path} executable: {str(e)}", err=True)
        return False