#!/bin/bash
# Display application sizes

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Application sizes in /Applications:"
    du -sh /Applications/* 2>/dev/null | sort -hr | head -10 || echo "Could not access /Applications directory"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Disk usage of common application directories:"
    echo "/usr/bin:"
    du -sh /usr/bin 2>/dev/null || echo "Could not access /usr/bin"
    echo "/usr/local/bin:"
    du -sh /usr/local/bin 2>/dev/null || echo "Could not access /usr/local/bin"
    echo "/opt (if exists):"
    du -sh /opt/* 2>/dev/null | head -5 || echo "No /opt directory or could not access"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo "Program Files sizes:"
    du -sh "C:/Program Files"/* 2>/dev/null | sort -hr | head -10 || echo "Could not access Program Files"
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Current directory size:"
    du -sh . 2>/dev/null || echo "Could not determine directory size"
fi