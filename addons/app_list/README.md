# App List

View installed applications and their sizes with colorized output.

## Commands

### `ls` - List Applications
Lists installed applications on your system.

```bash
corun app ls
```

- **macOS**: Applications in `/Applications`
- **Linux**: Installed packages (dpkg/rpm)
- **Windows**: Programs in `Program Files`

### `size` - Application Sizes
Shows application sizes with color coding.

```bash
corun app size
```

- Color-coded by size (Red: 5GB+, Yellow: 1GB+, Blue: 100MB+, Green: MB)
- Top 10 largest applications displayed

## Usage

```bash
corun app ls       # List applications
corun app size     # Show sizes
corun app ls -h    # Help
```

## Requirements

- Bash/Zsh shell
- Works on macOS, Linux, Windows (Git Bash)