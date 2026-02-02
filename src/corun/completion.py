"""Shell completion utilities for Corun CLI."""

import os
import sys

from rich.console import Console
from rich.markdown import Markdown

console = Console()


def get_shell() -> str:
    """Detect current shell."""
    shell = os.environ.get("SHELL", "")
    if "bash" in shell:
        return "bash"
    elif "zsh" in shell:
        return "zsh"
    elif "fish" in shell:
        return "fish"
    return "unknown"


def get_completion_instructions(shell: str) -> str:
    """Get shell-specific completion instructions."""
    
    if shell == "bash":
        return """
# Bash Completion Setup

## Auto Install (Recommended)
```bash
corun --install-completion bash
source ~/.bashrc
```

## Manual Install
```bash
# Generate completion script
corun --show-completion bash > ~/.corun-complete.bash

# Add to ~/.bashrc
echo 'source ~/.corun-complete.bash' >> ~/.bashrc
source ~/.bashrc
```

## Test
```bash
corun <TAB>
corun library <TAB>
```
"""
    
    elif shell == "zsh":
        return """
# Zsh Completion Setup

## Auto Install (Recommended)
```bash
corun --install-completion zsh
source ~/.zshrc
```

## Manual Install
```bash
# Generate completion script
corun --show-completion zsh > ~/.corun-complete.zsh

# Add to ~/.zshrc
echo 'source ~/.corun-complete.zsh' >> ~/.zshrc
source ~/.zshrc
```

## Test
```bash
corun <TAB>
corun library <TAB>
```
"""
    
    elif shell == "fish":
        return """
# Fish Completion Setup

## Auto Install (Recommended)
```bash
corun --install-completion fish
```

## Manual Install
```bash
# Create completions directory if needed
mkdir -p ~/.config/fish/completions

# Generate completion script
corun --show-completion fish > ~/.config/fish/completions/corun.fish
```

## Test
```bash
corun <TAB>
corun library <TAB>
```
"""
    
    else:
        return """
# Shell Completion Setup

Your shell could not be detected. Please specify the shell:

```bash
corun --install-completion bash   # For Bash
corun --install-completion zsh    # For Zsh
corun --install-completion fish   # For Fish
```

Or use `--show-completion` to see the completion script:

```bash
corun --show-completion bash
corun --show-completion zsh
corun --show-completion fish
```
"""


def show_completion_help(shell: str = None):
    """Show completion setup instructions."""
    if shell is None:
        shell = get_shell()
    
    console.print("\n[bold cyan]🚀 Shell Autocomplete Setup[/bold cyan]\n")
    
    if shell != "unknown":
        console.print(f"[green]Detected shell: {shell}[/green]\n")
    
    instructions = get_completion_instructions(shell)
    md = Markdown(instructions)
    console.print(md)
    
    console.print("\n[bold]What you'll get:[/bold]")
    console.print("  • Tab completion for all commands")
    console.print("  • Library and command suggestions")
    console.print("  • Option and flag completion")
