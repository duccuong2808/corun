"""Library management utilities for installing and managing command libraries."""

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import click
import requests
from .shell import make_executable


class LibraryManager:
    """Manages installation and removal of command libraries."""
    
    def __init__(self, library_path: Path):
        """
        Initialize library manager.
        
        Args:
            library_path (Path): Path to the library directory
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
    
    def list_installed_libraries(self) -> List[Dict]:
        """
        List all installed libraries with their metadata.
        
        Returns:
            List[Dict]: List of library metadata dictionaries
        """
        libraries = []
        
        for lib_dir in self.library_path.iterdir():
            if lib_dir.is_dir():
                metadata_path = lib_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        metadata['path'] = str(lib_dir)
                        metadata['library_id'] = lib_dir.name
                        libraries.append(metadata)
                    except (json.JSONDecodeError, IOError) as e:
                        click.echo(f"Warning: Could not read metadata for {lib_dir.name}: {e}")
        
        return libraries
    
    def get_library_metadata(self, library_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific library.
        
        Args:
            library_id (str): Library identifier
            
        Returns:
            Optional[Dict]: Library metadata or None if not found
        """
        lib_path = self.library_path / library_id
        metadata_path = lib_path / "metadata.json"
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            metadata['path'] = str(lib_path)
            metadata['library_id'] = library_id
            return metadata
        except (json.JSONDecodeError, IOError):
            return None
    
    def validate_library_structure(self, lib_path: Path) -> bool:
        """
        Validate that a library has the correct structure.
        
        Args:
            lib_path (Path): Path to the library directory
            
        Returns:
            bool: True if library structure is valid
        """
        # Check for metadata.json
        metadata_path = lib_path / "metadata.json"
        if not metadata_path.exists():
            click.echo(f"Error: Missing metadata.json in {lib_path}")
            return False
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            click.echo(f"Error: Invalid metadata.json in {lib_path}: {e}")
            return False
        
        # Validate required metadata fields
        required_fields = ['name', 'version', 'description', 'commands']
        for field in required_fields:
            if field not in metadata:
                click.echo(f"Error: Missing required field '{field}' in metadata.json")
                return False
        
        # Check that declared commands exist as shell scripts
        declared_commands = metadata.get('commands', [])
        for command in declared_commands:
            script_path = lib_path / f"{command}.sh"
            if not script_path.exists():
                click.echo(f"Warning: Declared command '{command}' has no corresponding {command}.sh file")
        
        return True
    
    def install_library_from_path(self, source_path: Path, library_id: Optional[str] = None) -> bool:
        """
        Install a library from a local path.
        
        Args:
            source_path (Path): Path to the library source
            library_id (str, optional): Custom library ID, defaults to source directory name
            
        Returns:
            bool: True if installation successful
        """
        source_path = Path(source_path)
        
        if not source_path.exists() or not source_path.is_dir():
            click.echo(f"Error: Source path {source_path} does not exist or is not a directory")
            return False
        
        # Validate library structure
        if not self.validate_library_structure(source_path):
            return False
        
        # Determine target library ID
        if library_id is None:
            library_id = source_path.name
        
        target_path = self.library_path / library_id
        
        # Check if library already exists
        if target_path.exists():
            if not click.confirm(f"Library '{library_id}' already exists. Overwrite?"):
                return False
            shutil.rmtree(target_path)
        
        try:
            # Copy library files
            shutil.copytree(source_path, target_path)
            
            # Make shell scripts executable
            for script in target_path.glob("*.sh"):
                make_executable(script)
            
            click.echo(f"Successfully installed library '{library_id}'")
            return True
            
        except Exception as e:
            click.echo(f"Error installing library: {e}")
            if target_path.exists():
                shutil.rmtree(target_path)
            return False
    
    def remove_library(self, library_id: str) -> bool:
        """
        Remove an installed library.
        
        Args:
            library_id (str): Library identifier to remove
            
        Returns:
            bool: True if removal successful
        """
        lib_path = self.library_path / library_id
        
        if not lib_path.exists():
            click.echo(f"Error: Library '{library_id}' is not installed")
            return False
        
        if not click.confirm(f"Remove library '{library_id}'?"):
            return False
        
        try:
            shutil.rmtree(lib_path)
            click.echo(f"Successfully removed library '{library_id}'")
            return True
        except Exception as e:
            click.echo(f"Error removing library: {e}")
            return False
    
    def create_library_template(self, library_id: str, name: str, description: str) -> bool:
        """
        Create a new library template.
        
        Args:
            library_id (str): Library directory name
            name (str): Human-readable library name
            description (str): Library description
            
        Returns:
            bool: True if template created successfully
        """
        lib_path = self.library_path / library_id
        
        if lib_path.exists():
            click.echo(f"Error: Library '{library_id}' already exists")
            return False
        
        try:
            lib_path.mkdir(parents=True)
            
            # Create metadata.json
            metadata = {
                "name": name,
                "version": "1.0.0",
                "author": "Local Developer",
                "description": description,
                "shells": ["bash", "zsh"],
                "commands": ["example"]
            }
            
            with open(lib_path / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Create example shell script
            example_script = lib_path / "example.sh"
            with open(example_script, 'w', encoding='utf-8') as f:
                f.write(f"""#!/bin/bash
# Example command for {name} library
echo "This is an example command from the {name} library"
echo "Edit this file to implement your command logic"
""")
            
            make_executable(example_script)
            
            click.echo(f"Successfully created library template '{library_id}' at {lib_path}")
            click.echo("Edit the metadata.json and shell scripts to customize your library")
            return True
            
        except Exception as e:
            click.echo(f"Error creating library template: {e}")
            if lib_path.exists():
                shutil.rmtree(lib_path)
            return False