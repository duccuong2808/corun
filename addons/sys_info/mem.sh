#!/bin/bash
# Display memory information with color-coded output

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

# Function to colorize memory usage based on percentage
colorize_memory_usage() {
    local line="$1"
    
    # Extract memory usage percentage (handles various formats)
    local usage=$(echo "$line" | grep -oE '[0-9]+(\.[0-9]+)?%' | head -1 | sed 's/%//')
    
    # Also check for memory values to determine usage level
    if [[ -z "$usage" ]] && [[ "$line" == *"used"* ]] && [[ "$line" == *"available"* ]]; then
        # Try to calculate percentage from available memory info
        local used=$(echo "$line" | grep -oE '[0-9]+(\.[0-9]+)?[KMG]' | head -1)
        local available=$(echo "$line" | grep -oE '[0-9]+(\.[0-9]+)?[KMG]' | tail -1)
        # Simplified estimation - if available is much less than used, usage is high
        if [[ -n "$used" ]] && [[ -n "$available" ]]; then
            usage="50" # Default to moderate if we can't calculate exactly
        fi
    fi
    
    if [[ -n "$usage" ]]; then
        local int_usage=$(echo "$usage" | awk '{printf "%.0f", $1}' 2>/dev/null || echo "0")
        
        if [[ $int_usage -ge 85 ]]; then
            # Critical memory usage (85%+) - Red
            echo -e "${RED}$line${RESET}"
        elif [[ $int_usage -ge 70 ]]; then
            # High memory usage (70-84%) - Yellow
            echo -e "${YELLOW}$line${RESET}"
        elif [[ $int_usage -ge 50 ]]; then
            # Moderate memory usage (50-69%) - Blue
            echo -e "${BLUE}$line${RESET}"
        else
            # Low memory usage (<50%) - Green
            echo -e "${GREEN}$line${RESET}"
        fi
    else
        # Special coloring for memory info lines
        if [[ "$line" == *"free"* ]] || [[ "$line" == *"available"* ]]; then
            echo -e "${GREEN}$line${RESET}"
        elif [[ "$line" == *"used"* ]] || [[ "$line" == *"active"* ]]; then
            echo -e "${YELLOW}$line${RESET}"
        elif [[ "$line" == *"total"* ]] || [[ "$line" == *"Memory"* ]]; then
            echo -e "${CYAN}$line${RESET}"
        else
            echo -e "${WHITE}$line${RESET}"
        fi
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
    echo -e "${BOLD}${CYAN}Memory Information Display with Colors${RESET}"
    echo
    echo -e "${BOLD}Memory Usage Color Legend:${RESET}"
    echo -e "  ${RED}Red${RESET}     - Critical usage (85%+)"
    echo -e "  ${YELLOW}Yellow${RESET}  - High usage (70-84%)"
    echo -e "  ${BLUE}Blue${RESET}    - Moderate usage (50-69%)"
    echo -e "  ${GREEN}Green${RESET}   - Low usage (<50%)"
    echo
    echo -e "${BOLD}Information Color Legend:${RESET}"
    echo -e "  ${CYAN}Cyan${RESET}    - Section headers and total memory"
    echo -e "  ${MAGENTA}Magenta${RESET} - Field names"
    echo -e "  ${YELLOW}Yellow${RESET}  - Used/active memory"
    echo -e "  ${GREEN}Green${RESET}   - Free/available memory"
    echo -e "  ${WHITE}White${RESET}   - General information"
    echo
    echo -e "${BOLD}Usage:${RESET} $0 [--help|-h]"
    exit 0
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    colorize_info "=== Memory Information (macOS) ==="
    system_profiler SPHardwareDataType | grep "Memory:" | while IFS= read -r line; do
        colorize_info "$line"
    done
    echo ""
    colorize_info "Current memory usage:"
    vm_stat | head -6 | while IFS= read -r line; do
        colorize_memory_usage "$line"
    done
    echo ""
    colorize_info "Memory pressure:"
    memory_pressure 2>/dev/null | while IFS= read -r line; do
        colorize_memory_usage "$line"
    done || colorize_info "memory_pressure command not available"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    colorize_info "=== Memory Information (Linux) ==="
    if command -v free &> /dev/null; then
        free -h | while IFS= read -r line; do
            colorize_memory_usage "$line"
        done
    else
        colorize_info "free command not available, using /proc/meminfo:"
        grep -E "(MemTotal|MemFree|MemAvailable|Buffers|Cached)" /proc/meminfo | while IFS= read -r line; do
            colorize_memory_usage "$line"
        done
    fi
    echo ""
    colorize_info "Memory usage by top processes:"
    if command -v ps &> /dev/null; then
        (ps aux --sort=-%mem | head -6 2>/dev/null || ps aux | head -6) | while IFS= read -r line; do
            if [[ "$line" == *"USER"* ]] || [[ "$line" == *"PID"* ]]; then
                # Header line
                colorize_info "$line"
            else
                # Process line with memory usage
                colorize_memory_usage "$line"
            fi
        done
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    colorize_info "=== Memory Information (Windows) ==="
    if command -v systeminfo &> /dev/null; then
        systeminfo | findstr /C:"Memory" | while IFS= read -r line; do
            colorize_memory_usage "$line"
        done
    else
        colorize_info "systeminfo not available in this environment"
        colorize_info "Basic memory info not available through bash on Windows"
        colorize_info "Try running 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory' in Command Prompt"
    fi
else
    colorize_info "Unsupported operating system: $OSTYPE"
    colorize_info "Basic system info:"
    uname -a 2>/dev/null | while IFS= read -r line; do
        colorize_info "$line"
    done || colorize_info "uname not available"
fi