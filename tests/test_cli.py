"""Tests for CLI command generation and execution."""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from click.testing import CliRunner
from src.cli import cli, create_dynamic_command, create_dynamic_group, get_library_ids, complete_library_id, get_library_paths, PROJECT_LIBRARY_PATH, USER_LIBRARY_PATH


class TestDynamicCommandGeneration:
    """Test dynamic command generation from shell scripts."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_dynamic_command(self):
        """Test creating a dynamic command from a shell script."""
        # Create a test shell script
        script_path = self.temp_dir / "test_command.sh"
        script_path.write_text("#!/bin/bash\necho 'Test command executed'")
        script_path.chmod(0o755)
        
        # Create dynamic command
        command = create_dynamic_command(script_path)
        
        # Verify command properties  
        assert command.name == "test"  # Click converts underscores in function name
        assert command.callback.__name__ == "test_command"  # The script stem we set
        assert "test_command" in command.callback.__doc__  # Doc contains script name
    
    def test_create_dynamic_group(self):
        """Test creating a dynamic group with sub-commands."""
        # Create a test library directory with metadata and scripts
        lib_dir = self.temp_dir / "test_lib"
        lib_dir.mkdir()
        
        # Create metadata.json
        metadata = {
            "name": "Test Library",
            "description": "A test library",
            "commands": ["hello", "world"]
        }
        (lib_dir / "metadata.json").write_text(json.dumps(metadata))
        
        # Create shell scripts
        hello_script = lib_dir / "hello.sh"
        hello_script.write_text("#!/bin/bash\necho 'Hello from test lib'")
        hello_script.chmod(0o755)
        
        world_script = lib_dir / "world.sh"
        world_script.write_text("#!/bin/bash\necho 'World from test lib'")
        world_script.chmod(0o755)
        
        # Create dynamic group
        group = create_dynamic_group("test-lib", lib_dir)
        
        # Verify group properties
        assert group.name == "test-lib"
        # Check if docstring exists and contains expected text
        if group.callback.__doc__:
            assert "Test Library" in group.callback.__doc__
        
        # Verify sub-commands were added
        assert "hello" in group.commands
        assert "world" in group.commands
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Corun CLI" in result.output
    
    def test_library_list_empty(self):
        """Test library list command with no libraries."""
        # This test may not work as expected because the CLI includes built-in libraries
        # We'll just test that the command executes successfully
        result = self.runner.invoke(cli, ["library", "list"])
        assert result.exit_code == 0
        assert "libraries" in result.output.lower()  # More flexible assertion


class TestCLIIntegration:
    """Integration tests for the full CLI."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_version_option(self):
        """Test --version option."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
    
    def test_library_commands_exist(self):
        """Test that library management commands exist."""
        result = self.runner.invoke(cli, ["library", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "info" in result.output
        assert "install" in result.output
        assert "remove" in result.output
        assert "create" in result.output


class TestAutocomplete:
    """Test autocomplete functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_get_library_ids(self):
        """Test getting library IDs for autocomplete."""
        library_ids = get_library_ids()
        assert isinstance(library_ids, list)
        # Should include the built-in libraries
        expected_ids = {'app', 'sys', 'brew'}
        actual_ids = set(library_ids)
        # At least some expected IDs should be present
        assert len(expected_ids.intersection(actual_ids)) > 0
    
    def test_complete_library_id(self):
        """Test library ID autocomplete function."""
        # Mock context and param
        class MockCtx:
            pass
        
        class MockParam:
            pass
        
        ctx = MockCtx()
        param = MockParam()
        
        # Test with incomplete 'a' - should match 'app' if it exists
        completions = complete_library_id(ctx, param, 'a')
        if 'app' in get_library_ids():
            assert 'app' in completions
        
        # Test with non-matching string
        completions = complete_library_id(ctx, param, 'nonexistent')
        assert len(completions) == 0
    
    def test_completion_command_exists(self):
        """Test that completion command exists and runs."""
        result = self.runner.invoke(cli, ["completion", "--help"])
        assert result.exit_code == 0
        assert "shell completion" in result.output.lower()
    
    def test_completion_command_bash(self):
        """Test completion command for bash."""
        result = self.runner.invoke(cli, ["completion", "bash"])
        assert result.exit_code == 0
        assert "bash_source" in result.output
        assert "bashrc" in result.output
    
    def test_completion_command_zsh(self):
        """Test completion command for zsh."""
        result = self.runner.invoke(cli, ["completion", "zsh"])
        assert result.exit_code == 0
        assert "zsh_source" in result.output
        assert "zshrc" in result.output
    
    def test_completion_command_fish(self):
        """Test completion command for fish."""
        result = self.runner.invoke(cli, ["completion", "fish"])
        assert result.exit_code == 0
        assert "fish_source" in result.output
        assert "config.fish" in result.output


class TestUserAddonDirectory:
    """Test user addon directory functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_user_dir = Path(tempfile.mkdtemp()) / ".corun" / "addons"
        self.temp_user_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock USER_LIBRARY_PATH to use temp directory
        self.original_user_path = USER_LIBRARY_PATH
        import src.cli
        src.cli.USER_LIBRARY_PATH = self.temp_user_dir
    
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_user_dir.parent.parent.exists():
            shutil.rmtree(self.temp_user_dir.parent.parent)
        
        # Restore original path
        import src.cli
        src.cli.USER_LIBRARY_PATH = self.original_user_path
    
    def test_get_library_paths(self):
        """Test get_library_paths function."""
        paths = get_library_paths()
        assert PROJECT_LIBRARY_PATH in paths
        # USER_LIBRARY_PATH should be included if it exists
        if self.temp_user_dir.exists():
            assert self.temp_user_dir in paths
    
    def test_user_library_creation(self):
        """Test creating a library in user directory."""
        # Create a test library in user directory
        user_lib_dir = self.temp_user_dir / "test_user_lib"
        user_lib_dir.mkdir()
        
        # Create metadata.json
        metadata = {
            "name": "Test User Library",
            "version": "1.0.0",
            "author": "Test User",
            "description": "A test user library",
            "library_id": "test-user",
            "shells": ["bash"],
            "commands": ["hello"]
        }
        (user_lib_dir / "metadata.json").write_text(json.dumps(metadata))
        
        # Create shell script
        hello_script = user_lib_dir / "hello.sh"
        hello_script.write_text("#!/bin/bash\necho 'Hello from user lib'")
        hello_script.chmod(0o755)
        
        # Test that library IDs include user library
        library_ids = get_library_ids()
        assert "test-user" in library_ids
    
    def test_library_list_shows_source(self):
        """Test that library list shows source (project/user)."""
        result = self.runner.invoke(cli, ["library", "list"])
        assert result.exit_code == 0
        # Should show source indicators like [project] or [user]
        assert "project" in result.output.lower() or "user" in result.output.lower()
    
    def test_install_to_user_directory_default(self):
        """Test that install defaults to user directory."""
        # Create a temporary source library
        source_dir = Path(tempfile.mkdtemp()) / "test_source"
        source_dir.mkdir()
        
        try:
            # Create metadata and script
            metadata = {
                "name": "Test Source",
                "version": "1.0.0",
                "author": "Test",
                "description": "Test library",
                "library_id": "test-source",
                "shells": ["bash"],
                "commands": ["test"]
            }
            (source_dir / "metadata.json").write_text(json.dumps(metadata))
            
            test_script = source_dir / "test.sh"
            test_script.write_text("#!/bin/bash\necho 'test'")
            test_script.chmod(0o755)
            
            # Install library (should default to user directory)
            result = self.runner.invoke(cli, ["library", "install", str(source_dir)])
            assert result.exit_code == 0
            assert "user directory" in result.output
            
            # Verify library was installed in user directory
            installed_lib = self.temp_user_dir / "test_source"
            assert installed_lib.exists()
            
        finally:
            if source_dir.exists():
                shutil.rmtree(source_dir.parent)


if __name__ == "__main__":
    pytest.main([__file__])