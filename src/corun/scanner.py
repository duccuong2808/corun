"""Scanner for ~/.corun/addons/ directory."""

import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from .models import Command, Library, Metadata

# Default addons directory
ADDONS_DIR = Path.home() / ".corun" / "addons"


def get_addons_dir() -> Path:
    """Get the addons directory path."""
    return ADDONS_DIR


def ensure_addons_dir() -> Path:
    """Ensure addons directory exists."""
    addons_dir = get_addons_dir()
    addons_dir.mkdir(parents=True, exist_ok=True)
    return addons_dir


def load_metadata(library_path: Path) -> Optional[Metadata]:
    """Load metadata.json from a library directory."""
    metadata_file = library_path / "metadata.json"

    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Metadata(**data)
    except (json.JSONDecodeError, ValidationError):
        return None


def scan_library(library_path: Path) -> Optional[Library]:
    """Scan a single library directory."""
    if not library_path.is_dir():
        return None

    # Find all .sh files
    scripts = list(library_path.glob("*.sh"))
    if not scripts:
        return None

    # Load metadata
    metadata = load_metadata(library_path)

    # Create library
    library_id = metadata.library_id if metadata else library_path.name
    library = Library(
        library_id=library_id,
        path=library_path,
        metadata=metadata,
    )

    # Add commands
    for script in scripts:
        cmd = Command(
            name=script.stem,
            script_path=script,
            library_id=library_id,
        )
        library.commands.append(cmd)

    return library


def scan_standalone_scripts(addons_dir: Path) -> list[Command]:
    """Scan for standalone .sh scripts in addons directory."""
    scripts = []

    for item in addons_dir.iterdir():
        if item.is_file() and item.suffix == ".sh":
            scripts.append(
                Command(
                    name=item.stem,
                    script_path=item,
                    library_id=None,
                )
            )

    return scripts


def scan_addons() -> tuple[list[Library], list[Command]]:
    """
    Scan the addons directory for libraries and standalone scripts.

    Returns:
        Tuple of (libraries, standalone_commands)
    """
    addons_dir = ensure_addons_dir()

    libraries: list[Library] = []
    standalone: list[Command] = []

    # Scan directories as libraries
    for item in addons_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            library = scan_library(item)
            if library:
                libraries.append(library)

    # Scan standalone scripts
    standalone = scan_standalone_scripts(addons_dir)

    return libraries, standalone


def get_library_by_id(library_id: str) -> Optional[Library]:
    """Get a library by its ID."""
    libraries, _ = scan_addons()
    for lib in libraries:
        if lib.library_id == library_id:
            return lib
    return None
