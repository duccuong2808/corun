#!/bin/bash
# Display application sizes with color-coded output

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

# Function to colorize size based on magnitude
colorize_size() {
    local size_line="$1"
    local size=$(echo "$size_line" | awk '{print $1}')
    local path=$(echo "$size_line" | cut -f2-)
    
    # Extract numeric value and unit
    local num=$(echo "$size" | sed 's/[^0-9.]//g')
    local unit=$(echo "$size" | sed 's/[0-9.]//g' | tr '[:lower:]' '[:upper:]')
    
    # Convert to integer for comparison (multiply by 10 to handle decimals)
    local int_num=$(echo "$num" | awk '{printf "%.0f", $1*10}' 2>/dev/null || echo "0")
    
    # Color coding based on size
    if [[ "$unit" == "G" ]] && [[ $int_num -ge 50 ]]; then
        # Very large (5GB+) - Red
        echo -e "${RED}${size}${RESET}\t${BOLD}${path}${RESET}"
    elif [[ "$unit" == "G" ]] && [[ $int_num -ge 10 ]]; then
        # Large (1GB+) - Yellow
        echo -e "${YELLOW}${size}${RESET}\t${CYAN}${path}${RESET}"
    elif [[ "$unit" == "M" ]] && [[ $int_num -ge 1000 ]]; then
        # Medium (100MB+) - Blue
        echo -e "${BLUE}${size}${RESET}\t${WHITE}${path}${RESET}"
    elif [[ "$unit" == "M" ]]; then
        # Small-Medium (MB) - Green
        echo -e "${GREEN}${size}${RESET}\t${WHITE}${path}${RESET}"
    else
        # Very small (KB or B) - White
        echo -e "${WHITE}${size}\t${path}${RESET}"
    fi
}

# Display color legend if --help or -h is passed
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "${BOLD}${CYAN}Application Size Display with Colors${RESET}"
    echo
    echo -e "${BOLD}Size Color Legend:${RESET}"
    echo -e "  ${RED}Red${RESET}     - Very large (5GB+)"
    echo -e "  ${YELLOW}Yellow${RESET}  - Large (1GB+)"
    echo -e "  ${BLUE}Blue${RESET}    - Medium (100MB+)"
    echo -e "  ${GREEN}Green${RESET}   - Small-Medium (MB)"
    echo -e "  ${WHITE}White${RESET}   - Very small (KB or B)"
    echo
    echo -e "${BOLD}Usage:${RESET} $0 [--help|-h]"
    exit 0
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${BOLD}${CYAN}Application sizes in /Applications (top 10):${RESET}"
    if du -sh /Applications/* 2>/dev/null | sort -hr | head -10 > /tmp/app_sizes.tmp 2>/dev/null; then
        while IFS= read -r line; do
            colorize_size "$line"
        done < /tmp/app_sizes.tmp
        rm -f /tmp/app_sizes.tmp
        
        # Show total size
        echo
        echo -e "${BOLD}${MAGENTA}Total /Applications size:${RESET}"
        if total_size=$(du -sh /Applications 2>/dev/null); then
            colorize_size "$total_size"
        else
            echo -e "${RED}Could not calculate total size${RESET}"
        fi
    else
        echo -e "${RED}Could not access /Applications directory${RESET}"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${BOLD}${CYAN}Disk usage of common application directories:${RESET}"
    
    echo -e "${BOLD}${YELLOW}/usr/bin:${RESET}"
    if du -sh /usr/bin 2>/dev/null > /tmp/linux_sizes.tmp; then
        while IFS= read -r line; do
            colorize_size "$line"
        done < /tmp/linux_sizes.tmp
        rm -f /tmp/linux_sizes.tmp
    else
        echo -e "${RED}Could not access /usr/bin${RESET}"
    fi
    
    echo -e "${BOLD}${YELLOW}/usr/local/bin:${RESET}"
    if du -sh /usr/local/bin 2>/dev/null > /tmp/linux_sizes.tmp; then
        while IFS= read -r line; do
            colorize_size "$line"
        done < /tmp/linux_sizes.tmp
        rm -f /tmp/linux_sizes.tmp
    else
        echo -e "${RED}Could not access /usr/local/bin${RESET}"
    fi
    
    echo -e "${BOLD}${YELLOW}/opt (if exists):${RESET}"
    if du -sh /opt/* 2>/dev/null | head -5 > /tmp/linux_sizes.tmp 2>/dev/null; then
        while IFS= read -r line; do
            colorize_size "$line"
        done < /tmp/linux_sizes.tmp
        rm -f /tmp/linux_sizes.tmp
    else
        echo -e "${RED}No /opt directory or could not access${RESET}"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo -e "${BOLD}${CYAN}Program Files sizes:${RESET}"
    if du -sh "C:/Program Files"/* 2>/dev/null | sort -hr | head -10 > /tmp/win_sizes.tmp 2>/dev/null; then
        while IFS= read -r line; do
            colorize_size "$line"
        done < /tmp/win_sizes.tmp
        rm -f /tmp/win_sizes.tmp
    else
        echo -e "${RED}Could not access Program Files${RESET}"
    fi
else
    echo -e "${BOLD}${YELLOW}Unsupported operating system: ${RESET}${RED}$OSTYPE${RESET}"
    echo -e "${YELLOW}Current directory size:${RESET}"
    if du -sh . 2>/dev/null > /tmp/current_size.tmp; then
        while IFS= read -r line; do
            colorize_size "$line"
        done < /tmp/current_size.tmp
        rm -f /tmp/current_size.tmp
    else
        echo -e "${RED}Could not determine directory size${RESET}"
    fi
fi