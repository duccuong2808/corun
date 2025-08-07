# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Corun is a dynamic CLI tool that uses metaprogramming to automatically generate command groups and sub-commands from shell scripts organized in an addon structure. The CLI scans the `addons/` directory and dynamically creates command groups based on folder structure, with each `.sh` file becoming a sub-command.

## Architecture

### Core Components

- **src/cli.py**: Main entry point using Click framework with metaprogramming to dynamically create command groups
- **src/utils/shell.py**: Shell script execution handler with error management
- **src/utils/library_manager.py**: Library management for installing/uninstalling community libraries
- **addons/**: Directory structure where each subfolder becomes a command group (located at project root)
  - Each subfolder contains `.sh` scripts (sub-commands) and `metadata.json`
  - Example: `addons/app_list/ls.sh` becomes `corun app ls`

### Dynamic Command Generation

The CLI uses metaprogramming patterns:
1. Scans `addons/` directory for subfolders with `metadata.json`
2. Each folder name becomes a command group (app_list � app)
3. Each `.sh` file in the folder becomes a sub-command
4. Commands are dynamically registered using Click's programmatic API

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running the CLI
```bash
# Run CLI directly
python -m src.cli

# After installation
corun --help
corun app ls
corun sys cpu
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_cli.py
python -m pytest tests/test_library.py

# Run with verbose output
python -m pytest -v
```

### Adding New Libraries

1. Create a new directory in `addons/` (e.g., `addons/network_tools/`)
2. Add `metadata.json` with library information:
   ```json
   {
     "name": "Network Tools",
     "version": "1.0.0",
     "author": "Contributor Name",
     "description": "Network utility commands",
     "shells": ["bash", "zsh"],
     "commands": ["ping", "port"]
   }
   ```
3. Add shell scripts (e.g., `ping.sh`, `port.sh`) with executable permissions
4. The CLI will automatically detect and register the new command group

## Code Conventions

### Shell Scripts
- All shell scripts must be executable (`chmod +x`)
- Include shebang: `#!/bin/bash` or `#!/bin/zsh`
- Handle cross-platform compatibility where possible
- Use proper error handling and exit codes
- Output should be user-friendly

### Python Code
- Follow PEP 8 style guidelines
- Use Click framework for CLI components
- Handle exceptions gracefully with user-friendly error messages
- Use pathlib for file system operations
- Include docstrings for all functions

### Library Structure
- Each library directory must contain `metadata.json`
- Shell scripts should have descriptive names matching their function
- Metadata should accurately reflect available commands
- Version libraries appropriately for community sharing

## Key Implementation Details

### Metaprogramming Pattern
The core innovation is in `create_dynamic_group()` and `create_dynamic_command()` functions that:
- Dynamically create Click command groups from directory names
- Generate Click commands from shell script files
- Automatically register commands without manual declaration

### Cross-Platform Considerations
Shell scripts should handle both Unix-like and Windows environments where possible, using conditional logic like:
```bash
ls -l /Applications 2>/dev/null || dir  # macOS/Linux or Windows
```

### Library Management
The `library_manager.py` component handles:
- Installing libraries from community sources (GitHub)
- Removing installed libraries
- Validating library structure and metadata
- Managing dependencies between libraries

## Testing Strategy

- **test_cli.py**: Test dynamic command generation and CLI functionality
- **test_library.py**: Test library management operations
- Mock shell script execution for reliable testing
- Test cross-platform compatibility scenarios
- Validate metadata parsing and validation

## Future Development

The project roadmap includes:
1. Permission checking for shell scripts before execution
2. Community library repository integration via GitHub
3. Library dependency management
4. Enhanced error handling and user feedback
5. Configuration management through `config.json`