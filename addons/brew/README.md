# Homebrew Utils

View Homebrew packages sorted by installation time.

## Commands

### `package` - Package Timeline
Shows installed Homebrew packages grouped by installation date.

```bash
corun brew package                 # All packages
corun brew package --casks-only    # GUI apps only
corun brew package --formulas-only # CLI tools only
```

Features:
- Groups packages by installation date
- Separates formulas (CLI tools) and casks (GUI apps)
- Shows package counts and totals
- Color-coded output

## Usage

```bash
corun brew package               # Show all packages
corun brew package --casks-only  # GUI applications
corun brew package --formulas-only # Command line tools
corun brew package -h           # Help
```

## Requirements

- Homebrew installed
- macOS or Linux with Homebrew