#!/bin/bash
# Display CPU information with color-coded output

# Color definitions
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    BLUE=$(tput setaf 4)
    MAGENTA=$(tput setaf 5)
    CYAN=$(tput setaf 6)
    WHITE=$(tput setaf 7)
    BOLD=$(tput bold)
    RESET=$(tput sgr0)
else
    # Fallback to ANSI codes if tput is not available
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    WHITE='\033[0;37m'
    BOLD='\033[1m'
    RESET='\033[0m'
fi

# Function to colorize CPU usage based on percentage
colorize_cpu_usage() {
    local line="$1"
    
    # Extract CPU usage percentage (handles various formats)
    local usage=$(echo "$line" | grep -oE '[0-9]+(\.[0-9]+)?%' | head -1 | sed 's/%//')
    
    if [[ -n "$usage" ]]; then
        local int_usage=$(echo "$usage" | awk '{printf "%.0f", $1}' 2>/dev/null || echo "0")
        
        if [[ $int_usage -ge 80 ]]; then
            # Critical usage (80%+) - Red
            echo -e "${RED}$line${RESET}"
        elif [[ $int_usage -ge 60 ]]; then
            # High usage (60-79%) - Yellow
            echo -e "${YELLOW}$line${RESET}"
        elif [[ $int_usage -ge 30 ]]; then
            # Moderate usage (30-59%) - Blue
            echo -e "${BLUE}$line${RESET}"
        else
            # Low usage (<30%) - Green
            echo -e "${GREEN}$line${RESET}"
        fi
    else
        # No percentage found, use default color
        echo -e "${WHITE}$line${RESET}"
    fi
}

# Function to colorize system information
colorize_info() {
    local line="$1"
    
    if [[ "$line" == *"==="* ]]; then
        # Headers
        echo -e "${BOLD}${CYAN}$line${RESET}"
    elif [[ "$line" == *":"* ]]; then
        # Key-value pairs
        local key=$(echo "$line" | cut -d':' -f1)
        local value=$(echo "$line" | cut -d':' -f2-)
        echo -e "${BOLD}${MAGENTA}$key:${RESET}${WHITE}$value${RESET}"
    else
        # Regular text
        echo -e "${WHITE}$line${RESET}"
    fi
}

# Display color legend if --help or -h is passed
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "${BOLD}${CYAN}CPU Information Display with Colors${RESET}"
    echo
    echo -e "${BOLD}CPU Usage Color Legend:${RESET}"
    echo -e "  ${RED}Red${RESET}     - Critical usage (80%+)"
    echo -e "  ${YELLOW}Yellow${RESET}  - High usage (60-79%)"
    echo -e "  ${BLUE}Blue${RESET}    - Moderate usage (30-59%)"
    echo -e "  ${GREEN}Green${RESET}   - Low usage (<30%)"
    echo
    echo -e "${BOLD}Information Color Legend:${RESET}"
    echo -e "  ${CYAN}Cyan${RESET}    - Section headers"
    echo -e "  ${MAGENTA}Magenta${RESET} - Field names"
    echo -e "  ${WHITE}White${RESET}   - Field values"
    echo
    echo -e "${BOLD}Usage:${RESET} $0 [--help|-h]"
    exit 0
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    colorize_info "=== CPU Information (macOS) ==="
    system_profiler SPHardwareDataType | grep -E "(Processor|Cores|Speed)" | while IFS= read -r line; do
        colorize_info "$line"
    done
    echo ""
    colorize_info "Current CPU usage:"
    top -l 1 -n 0 | grep "CPU usage" | while IFS= read -r line; do
        colorize_cpu_usage "$line"
    done
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    colorize_info "=== CPU Information (Linux) ==="
    if command -v lscpu &> /dev/null; then
        lscpu | grep -E "(Model name|CPU\(s\)|Thread|Core|MHz|Architecture)" | while IFS= read -r line; do
            colorize_info "$line"
        done
    else
        colorize_info "lscpu not available, using /proc/cpuinfo:"
        grep -E "(model name|processor|cpu cores|cpu MHz)" /proc/cpuinfo | head -10 | while IFS= read -r line; do
            colorize_info "$line"
        done
    fi
    echo ""
    colorize_info "Current CPU usage:"
    if command -v top &> /dev/null; then
        (top -bn1 | grep "Cpu(s)" || top -n1 | head -3) | while IFS= read -r line; do
            if [[ "$line" == *"Cpu(s)"* ]]; then
                colorize_cpu_usage "$line"
            else
                colorize_info "$line"
            fi
        done
    else
        colorize_info "top command not available"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    colorize_info "=== CPU Information (Windows) ==="
    if command -v systeminfo &> /dev/null; then
        systeminfo | findstr /C:"Processor" | while IFS= read -r line; do
            colorize_info "$line"
        done
    else
        colorize_info "systeminfo not available in this environment"
        colorize_info "Processor info from environment:"
        colorize_info "PROCESSOR_IDENTIFIER: $PROCESSOR_IDENTIFIER"
        colorize_info "NUMBER_OF_PROCESSORS: $NUMBER_OF_PROCESSORS"
    fi
else
    colorize_info "Unsupported operating system: $OSTYPE"
    colorize_info "Basic system info:"
    uname -a 2>/dev/null | while IFS= read -r line; do
        colorize_info "$line"
    done || colorize_info "uname not available"
fi