"""Execute shell scripts."""

import os
import subprocess
import sys
from pathlib import Path

# ANSI codes
ITALIC = '\033[3m'
RESET = '\033[0m'


def has_shebang(script_path: Path) -> bool:
    """
    Check if a script has a shebang line.

    Args:
        script_path: Path to the shell script

    Returns:
        True if script starts with #!, False otherwise
    """
    try:
        with open(script_path, 'rb') as f:
            first_bytes = f.read(2)
            return first_bytes == b'#!'
    except Exception:
        return False


def get_default_shell() -> str:
    """
    Get the default shell to use for scripts without shebang.

    Returns:
        Path to user's shell (from $SHELL) or /bin/bash as fallback
    """
    shell = os.environ.get('SHELL', '/bin/bash')
    return shell


def execute_script(script_path: Path, args: list[str] | None = None) -> int:
    """
    Execute a shell script with the given arguments.

    Args:
        script_path: Path to the shell script
        args: Optional list of arguments to pass

    Returns:
        Exit code from the script
    """
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}", file=sys.stderr)
        return 1

    if not os.access(script_path, os.X_OK):
        print(f"Error: Script not executable: {script_path}", file=sys.stderr)
        print(f"\nTo fix, run:\n  chmod +x {script_path}", file=sys.stderr)
        return 1

    # Check for shebang
    if not has_shebang(script_path):
        shell = get_default_shell()
        print(f"{ITALIC}Warning: '{script_path.name}' missing shebang, using {shell}{RESET}\n", file=sys.stderr)
        # Build command with explicit shell
        cmd = [shell, str(script_path)]
    else:
        # Build command normally
        cmd = [str(script_path)]

    if args:
        cmd.extend(args)

    try:
        # Run script, passing through stdin/stdout/stderr
        result = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return result.returncode
    except Exception as e:
        print(f"Error executing script: {e}", file=sys.stderr)
        return 1
