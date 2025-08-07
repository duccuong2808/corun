#!/bin/bash
# Display memory information

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "=== Memory Information (macOS) ==="
    system_profiler SPHardwareDataType | grep "Memory:"
    echo ""
    echo "Current memory usage:"
    vm_stat | head -6
    echo ""
    echo "Memory pressure:"
    memory_pressure 2>/dev/null || echo "memory_pressure command not available"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "=== Memory Information (Linux) ==="
    if command -v free &> /dev/null; then
        free -h
    else
        echo "free command not available, using /proc/meminfo:"
        grep -E "(MemTotal|MemFree|MemAvailable|Buffers|Cached)" /proc/meminfo
    fi
    echo ""
    echo "Memory usage by top processes:"
    if command -v ps &> /dev/null; then
        ps aux --sort=-%mem | head -6 2>/dev/null || ps aux | head -6
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo "=== Memory Information (Windows) ==="
    if command -v systeminfo &> /dev/null; then
        systeminfo | findstr /C:"Memory"
    else
        echo "systeminfo not available in this environment"
        echo "Basic memory info not available through bash on Windows"
        echo "Try running 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory' in Command Prompt"
    fi
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Basic system info:"
    uname -a 2>/dev/null || echo "uname not available"
fi