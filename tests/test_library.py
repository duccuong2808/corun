"""Tests for library management functionality."""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from src.utils.library_manager import LibraryManager


class TestLibraryManager:
    """Test library management operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = LibraryManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_library(self, lib_name="test_lib"):
        """Create a test library structure."""
        lib_path = self.temp_dir / lib_name
        lib_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata.json
        metadata = {
            "name": f"Test Library {lib_name}",
            "version": "1.0.0",
            "author": "Test Author",
            "description": f"A test library named {lib_name}",
            "shells": ["bash"],
            "commands": ["hello", "world"]
        }
        (lib_path / "metadata.json").write_text(json.dumps(metadata, indent=2))
        
        # Create shell scripts
        hello_script = lib_path / "hello.sh"
        hello_script.write_text("#!/bin/bash\necho 'Hello from test'")
        hello_script.chmod(0o755)
        
        world_script = lib_path / "world.sh"
        world_script.write_text("#!/bin/bash\necho 'World from test'")
        world_script.chmod(0o755)
        
        return lib_path
    
    def test_validate_library_structure_valid(self):
        """Test validation of valid library structure."""
        lib_path = self.create_test_library()
        assert self.manager.validate_library_structure(lib_path)
    
    def test_validate_library_structure_missing_metadata(self):
        """Test validation fails when metadata.json is missing."""
        lib_path = self.temp_dir / "invalid_lib"
        lib_path.mkdir()
        (lib_path / "test.sh").write_text("#!/bin/bash\necho test")
        
        assert not self.manager.validate_library_structure(lib_path)
    
    def test_validate_library_structure_invalid_metadata(self):
        """Test validation fails when metadata.json is invalid."""
        lib_path = self.temp_dir / "invalid_lib"
        lib_path.mkdir()
        (lib_path / "metadata.json").write_text("{invalid json}")
        
        assert not self.manager.validate_library_structure(lib_path)
    
    def test_validate_library_structure_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        lib_path = self.temp_dir / "invalid_lib"
        lib_path.mkdir()
        
        # Metadata missing required fields
        metadata = {"name": "Test"}
        (lib_path / "metadata.json").write_text(json.dumps(metadata))
        
        assert not self.manager.validate_library_structure(lib_path)
    
    def test_list_installed_libraries_empty(self):
        """Test listing libraries when none are installed."""
        libraries = self.manager.list_installed_libraries()
        assert libraries == []
    
    def test_list_installed_libraries_with_libraries(self):
        """Test listing libraries when some are installed."""
        # Create test libraries directly in the library path
        old_lib_path = self.manager.library_path
        try:
            # Create libraries in the manager's library path
            lib1_path = self.manager.library_path / "lib1"
            lib1_path.mkdir(parents=True)
            metadata1 = {
                "name": "Library 1",
                "version": "1.0.0",
                "description": "First test library",
                "commands": ["cmd1"]
            }
            (lib1_path / "metadata.json").write_text(json.dumps(metadata1))
            
            lib2_path = self.manager.library_path / "lib2"
            lib2_path.mkdir()
            metadata2 = {
                "name": "Library 2",
                "version": "2.0.0",
                "description": "Second test library",
                "commands": ["cmd2"]
            }
            (lib2_path / "metadata.json").write_text(json.dumps(metadata2))
            
            # Test listing
            libraries = self.manager.list_installed_libraries()
            assert len(libraries) == 2
            
            library_names = [lib["name"] for lib in libraries]
            assert "Library 1" in library_names
            assert "Library 2" in library_names
            
        finally:
            self.manager.library_path = old_lib_path
    
    def test_get_library_metadata_exists(self):
        """Test getting metadata for existing library."""
        # Create library in manager's path
        lib_path = self.manager.library_path / "test_lib"
        lib_path.mkdir(parents=True)
        metadata = {
            "name": "Test Library",
            "version": "1.0.0",
            "description": "Test",
            "commands": ["test"]
        }
        (lib_path / "metadata.json").write_text(json.dumps(metadata))
        
        result = self.manager.get_library_metadata("test_lib")
        assert result is not None
        assert result["name"] == "Test Library"
        assert result["library_id"] == "test_lib"
    
    def test_get_library_metadata_not_exists(self):
        """Test getting metadata for non-existent library."""
        result = self.manager.get_library_metadata("nonexistent")
        assert result is None
    
    def test_install_library_from_path_success(self):
        """Test successful library installation from path."""
        # Create source library
        source_lib = self.create_test_library("source_lib")
        
        # Install it
        result = self.manager.install_library_from_path(source_lib, "installed_lib")
        assert result is True
        
        # Verify it was installed
        installed_path = self.manager.library_path / "installed_lib"
        assert installed_path.exists()
        assert (installed_path / "metadata.json").exists()
        assert (installed_path / "hello.sh").exists()
        assert (installed_path / "world.sh").exists()
    
    def test_install_library_from_path_invalid_source(self):
        """Test library installation fails with invalid source."""
        result = self.manager.install_library_from_path(Path("nonexistent"))
        assert result is False
    
    def test_create_library_template_success(self):
        """Test successful library template creation."""
        result = self.manager.create_library_template("new_lib", "New Library", "A new test library")
        assert result is True
        
        # Verify template was created
        lib_path = self.manager.library_path / "new_lib"
        assert lib_path.exists()
        assert (lib_path / "metadata.json").exists()
        assert (lib_path / "example.sh").exists()
        
        # Verify metadata content
        with open(lib_path / "metadata.json") as f:
            metadata = json.load(f)
        assert metadata["name"] == "New Library"
        assert metadata["description"] == "A new test library"
    
    def test_create_library_template_already_exists(self):
        """Test template creation fails when library already exists."""
        # Create a library first
        lib_path = self.manager.library_path / "existing_lib"
        lib_path.mkdir(parents=True)
        
        # Try to create template with same name
        result = self.manager.create_library_template("existing_lib", "Test", "Test")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])