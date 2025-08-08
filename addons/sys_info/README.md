# System Info

View CPU and memory information with color-coded output.

## Commands

### `cpu` - CPU Information
Shows processor details and current usage.

```bash
corun sys cpu
```

- Processor model, cores, speed
- Current CPU usage with color coding
- Color legend: Red (80%+), Yellow (60-79%), Blue (30-59%), Green (<30%)

### `mem` - Memory Information
Displays memory statistics and usage.

```bash
corun sys mem
```

- Total, used, and available memory
- Color-coded by usage level
- Color legend: Red (85%+), Yellow (70-84%), Blue (50-69%), Green (<50%)

## Usage

```bash
corun sys cpu      # CPU info and usage
corun sys mem      # Memory info and usage
corun sys cpu -h   # Help
```

## Requirements

- Bash/Zsh shell
- Works on macOS, Linux, Windows (Git Bash)
