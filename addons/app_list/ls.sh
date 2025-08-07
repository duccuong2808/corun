#!/bin/bash
# List applications in the system

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Applications in /Applications:"
    ls -la /Applications 2>/dev/null || echo "Could not access /Applications directory"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Installed packages (using dpkg if available):"
    if command -v dpkg &> /dev/null; then
        dpkg -l | head -20
    elif command -v rpm &> /dev/null; then
        rpm -qa | head -20
    else
        echo "Package manager not found. Checking /usr/bin for executables:"
        ls /usr/bin | head -20
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo "Program Files contents:"
    ls "C:/Program Files" 2>/dev/null || ls "C:\\Program Files" 2>/dev/null || echo "Could not access Program Files"
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Available commands in PATH:"
    which -a ls cat grep awk sed 2>/dev/null | head -10
fi