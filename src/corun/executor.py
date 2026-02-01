"""Execute shell scripts."""

import os
import subprocess
import sys
from pathlib import Path


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

    # Build command
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
