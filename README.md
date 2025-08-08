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

```bash
# Install a library from local path
corun library install /path/to/my-library --id my-lib

# Create a new library template
corun library create network-tools "Network Tools" "Network utility commands"

# Remove a library
corun library remove my-lib
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

1. Create a directory in `addons/` with your addon name (e.g., `addons/network_tools/`)
2. Add `metadata.json`:
   ```json
   {
     "name": "Network Tools",
     "version": "1.0.0",
     "author": "Your Name",
     "description": "Network utility commands",
     "shells": ["bash", "zsh"],
     "commands": ["ping", "trace"]
   }
   ```
3. Add shell scripts (e.g., `ping.sh`, `trace.sh`) with executable permissions
4. Install using `corun library install ./addons/network_tools`

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