#!/bin/bash
# List applications in the system with color support

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

# Display color legend if --help or -h is passed
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "${BOLD}${CYAN}Application Listing with Colors${RESET}"
    echo
    echo -e "${BOLD}Color Legend:${RESET}"
    echo -e "  ${GREEN}Green${RESET}   - Directories and installed packages"
    echo -e "  ${BLUE}Blue${RESET}    - Application files and executables"
    echo -e "  ${YELLOW}Yellow${RESET}  - System information and headers"
    echo -e "  ${RED}Red${RESET}     - Errors and uninstalled packages"
    echo -e "  ${MAGENTA}Magenta${RESET} - Package manager headers"
    echo -e "  ${WHITE}White${RESET}   - Regular files and default text"
    echo
    echo -e "${BOLD}Usage:${RESET} $0 [--help|-h]"
    exit 0
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${BOLD}${CYAN}Applications in /Applications:${RESET}"
    if ls /Applications &>/dev/null; then
        ls -la /Applications 2>/dev/null | while IFS= read -r line; do
            if [[ $line == total* ]]; then
                echo -e "${YELLOW}$line${RESET}"
            elif [[ $line == d* ]]; then
                # Directory (application bundle)
                echo -e "${GREEN}$line${RESET}"
            elif [[ $line == -* ]] && [[ $line == *\.app* ]]; then
                # Application file
                echo -e "${BLUE}$line${RESET}"
            else
                # Other files
                echo -e "${WHITE}$line${RESET}"
            fi
        done
    else
        echo -e "${RED}Could not access /Applications directory${RESET}"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${BOLD}${CYAN}Installed packages:${RESET}"
    if command -v dpkg &> /dev/null; then
        echo -e "${YELLOW}Using dpkg package manager${RESET}"
        dpkg -l | head -20 | while IFS= read -r line; do
            if [[ $line == Desired* ]] || [[ $line == \|\|* ]] || [[ $line == \+\+* ]]; then
                # Header lines
                echo -e "${MAGENTA}$line${RESET}"
            elif [[ $line == ii* ]]; then
                # Installed packages
                echo -e "${GREEN}$line${RESET}"
            elif [[ $line == un* ]] || [[ $line == rc* ]]; then
                # Uninstalled or removed packages
                echo -e "${RED}$line${RESET}"
            else
                echo -e "${WHITE}$line${RESET}"
            fi
        done
    elif command -v rpm &> /dev/null; then
        echo -e "${YELLOW}Using rpm package manager${RESET}"
        rpm -qa | head -20 | while IFS= read -r line; do
            echo -e "${GREEN}$line${RESET}"
        done
    else
        echo -e "${YELLOW}Package manager not found. Checking /usr/bin for executables:${RESET}"
        ls /usr/bin | head -20 | while IFS= read -r line; do
            echo -e "${BLUE}$line${RESET}"
        done
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash or similar)
    echo -e "${BOLD}${CYAN}Program Files contents:${RESET}"
    if ls "C:/Program Files" &>/dev/null 2>&1; then
        ls "C:/Program Files" 2>/dev/null | while IFS= read -r line; do
            if [[ -d "C:/Program Files/$line" ]]; then
                # Directory (likely an application)
                echo -e "${GREEN}$line${RESET}"
            else
                # File
                echo -e "${BLUE}$line${RESET}"
            fi
        done
    elif ls "C:\\Program Files" &>/dev/null 2>&1; then
        ls "C:\\Program Files" 2>/dev/null | while IFS= read -r line; do
            if [[ -d "C:\\Program Files\\$line" ]]; then
                # Directory (likely an application)
                echo -e "${GREEN}$line${RESET}"
            else
                # File
                echo -e "${BLUE}$line${RESET}"
            fi
        done
    else
        echo -e "${RED}Could not access Program Files directory${RESET}"
    fi
else
    echo -e "${BOLD}${YELLOW}Unsupported operating system: ${RESET}${RED}$OSTYPE${RESET}"
    echo -e "${YELLOW}Available commands in PATH:${RESET}"
    which -a ls cat grep awk sed 2>/dev/null | head -10 | while IFS= read -r line; do
        echo -e "${BLUE}$line${RESET}"
    done
fi