# Corun CLI

A dynamic command-line tool that uses metaprogramming to automatically generate command groups and sub-commands from shell scripts organized in a library structure.

## Features

- **Dynamic Command Generation**: Automatically creates CLI commands from shell scripts
- **Metaprogramming Architecture**: No manual command registration required
- **Community Libraries**: Easy installation and management of command libraries
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Extensible**: Simple library structure for adding new commands

## Installation

```bash
# Install from source
git clone https://github.com/corun-community/corun.git
cd corun
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Usage

### Basic Commands

```bash
# Show available command groups
corun --help

# List installed libraries
corun library list

# Show library information
corun library info sys-info
```

### Example Commands (with default libraries)

```bash
# Application management
corun app-list ls     # List applications
corun app-list size   # Show application sizes

# System information
corun sys-info cpu    # Display CPU information
corun sys-info mem    # Display memory information
```

### Library Management

Corun supports both project-level and user-level addon libraries:
- **Project libraries**: Located in `./addons/` (bundled with the project)
- **User libraries**: Located in `~/.corun/addons/` (personal libraries)

```bash
# List all installed libraries (shows source: [project] or [user])
corun library list

# Install a library to user directory (default)
corun library install /path/to/my-library --id my-lib
corun library install /path/to/my-library --user

# Install a library to project directory
corun library install /path/to/my-library --global

# Create a new library template in user directory (default)
corun library create network-tools "Network Tools" "Network utility commands"
corun library create network-tools "Network Tools" "Network utility commands" --user

# Create a new library template in project directory
corun library create network-tools "Network Tools" "Network utility commands" --global

# Remove a library (automatically finds the correct location)
corun library remove my-lib

# Show detailed library information (including source location)
corun library info my-lib
```

### Shell Completion (Autocomplete)

Corun supports shell autocompletion for commands and library IDs. To enable it:

```bash
# Set up completion for your shell
corun completion          # Auto-detect shell and show instructions
corun completion bash     # Show bash-specific setup instructions
corun completion zsh      # Show zsh-specific setup instructions
corun completion fish     # Show fish-specific setup instructions
```

After setting up, you can use TAB completion:

```bash
corun <TAB>               # Show all available commands
corun library <TAB>       # Show library management commands  
corun library info <TAB>  # Autocomplete library IDs
corun app <TAB>           # Show commands in app library
corun sys <TAB>           # Show commands in sys library
```

**Quick Setup Examples:**

For Bash:
```bash
echo 'eval "$(_CORUN_COMPLETE=bash_source corun)"' >> ~/.bashrc
source ~/.bashrc
```

For Zsh:
```bash
echo 'eval "$(_CORUN_COMPLETE=zsh_source corun)"' >> ~/.zshrc
source ~/.zshrc
```

## Creating Addons

### User Addons (Recommended)
Create personal addons in your user directory:

#### Option 1: Full Library Structure
1. Create a new library template:
   ```bash
   corun library create my-tools "My Tools" "Personal utility commands"
   ```
2. Edit the generated files in `~/.corun/addons/my-tools/`
3. Add shell scripts with executable permissions

#### Option 2: Standalone Scripts (Simple)
1. Corun will automatically create `~/.corun/addons/` when needed
2. Copy any `.sh` script directly to `~/.corun/addons/`:
   ```bash
   cp my_script.sh ~/.corun/addons/
   chmod +x ~/.corun/addons/my_script.sh
   ```
3. The script becomes available as `corun my_script`

**Example Standalone Script:**
```bash
# ~/.corun/addons/hello.sh
#!/bin/bash
echo "Hello from standalone script!"
echo "Current directory: $(pwd)"
```

After adding, use: `corun hello`

### Project Addons
Create addons bundled with the project:

#### Option 1: Full Library Structure
1. Create a directory in `addons/` with your addon name (e.g., `addons/network_tools/`)
2. Add `metadata.json`:
   ```json
   {
     "name": "Network Tools",
     "version": "1.0.0",
     "author": "Your Name",
     "description": "Network utility commands",
     "library_id": "network",
     "shells": ["bash", "zsh"],
     "commands": ["ping", "trace"]
   }
   ```
3. Add shell scripts (e.g., `ping.sh`, `trace.sh`) with executable permissions
4. Install using `corun library install ./addons/network_tools --global`

#### Option 2: Standalone Scripts
1. Place `.sh` scripts directly in `addons/` directory
2. Scripts become available immediately (no restart needed)
3. Example: `addons/deploy.sh` becomes `corun deploy`

### Priority System
- **Project scripts/libraries** (./addons/) take precedence over user scripts/libraries
- **Library commands** take precedence over standalone scripts (if names conflict)
- **Standalone scripts** in project directory override user directory scripts
- This allows projects to override user addons when needed

**Priority Order:**
1. Project library commands (highest)
2. User library commands  
3. Project standalone scripts
4. User standalone scripts (lowest)

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run CLI in development mode
python -m corun.cli --help
```

## Architecture

- **src/cli.py**: Main CLI with metaprogramming for dynamic command generation
- **src/utils/shell.py**: Shell script execution with cross-platform support
- **src/utils/library_manager.py**: Library installation and management
- **addons/**: Directory containing command addons (at project root)
  - Each subdirectory becomes a command group
  - Each `.sh` file becomes a sub-command

## License

MIT License - see LICENSE file for details.