#!/bin/bash
# Display CPU information

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "=== CPU Information (macOS) ==="
    system_profiler SPHardwareDataType | grep -E "(Processor|Cores|Speed)"
    echo ""
    echo "Current CPU usage:"
    top -l 1 -n 0 | grep "CPU usage"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "=== CPU Information (Linux) ==="
    if command -v lscpu &> /dev/null; then
        lscpu | grep -E "(Model name|CPU\(s\)|Thread|Core|MHz|Architecture)"
    else
        echo "lscpu not available, using /proc/cpuinfo:"
        grep -E "(model name|processor|cpu cores|cpu MHz)" /proc/cpuinfo | head -10
    fi
    echo ""
    echo "Current CPU usage:"
    if command -v top &> /dev/null; then
        top -bn1 | grep "Cpu(s)" || top -n1 | head -3
    else
        echo "top command not available"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo "=== CPU Information (Windows) ==="
    if command -v systeminfo &> /dev/null; then
        systeminfo | findstr /C:"Processor"
    else
        echo "systeminfo not available in this environment"
        echo "Processor info from environment:"
        echo "PROCESSOR_IDENTIFIER: $PROCESSOR_IDENTIFIER"
        echo "NUMBER_OF_PROCESSORS: $NUMBER_OF_PROCESSORS"
    fi
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Basic system info:"
    uname -a 2>/dev/null || echo "uname not available"
fi