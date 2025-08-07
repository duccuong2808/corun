#!/bin/bash

# Script to show installed Homebrew packages sorted by installation time
# Usage: ./brew-packages-by-time.sh [--casks-only|--formulas-only]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored header
print_header() {
    echo -e "${CYAN}================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================${NC}"
}

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}$1${NC}"
    echo -e "${YELLOW}$(printf '%.0s-' {1..50})${NC}"
}

# Function to get formula packages with install times
get_formulas_by_time() {
    print_header "HOMEBREW FORMULA PACKAGES (Command Line Tools)"

    local temp_file=$(mktemp)

    # Get all formulas with their installation times
    brew list --formula | while read package; do
        install_time=$(find /opt/homebrew/Cellar/$package -name "INSTALL_RECEIPT.json" -exec stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" {} \; 2>/dev/null | head -1)
        if [ -n "$install_time" ]; then
            echo "$install_time $package"
        else
            echo "unknown $package"
        fi
    done | sort > "$temp_file"

    # Group by date and display
    local current_date=""
    local count=0

    while IFS=' ' read -r date time package; do
        if [ "$date" != "unknown" ]; then
            if [ "$date" != "$current_date" ]; then
                if [ -n "$current_date" ]; then
                    echo -e "${GREEN}  Total: $count packages${NC}\n"
                fi
                current_date="$date"
                count=0
                print_section "$date"
            fi
            echo -e "  ${BLUE}$time${NC} ${PURPLE}$package${NC}"
            ((count++))
        else
            if [ "$current_date" != "unknown" ]; then
                if [ -n "$current_date" ]; then
                    echo -e "${GREEN}  Total: $count packages${NC}\n"
                fi
                current_date="unknown"
                count=0
                print_section "Unknown Install Date"
            fi
            echo -e "  ${RED}unknown${NC} ${PURPLE}$package${NC}"
            ((count++))
        fi
    done < "$temp_file"

    if [ $count -gt 0 ]; then
        echo -e "${GREEN}  Total: $count packages${NC}"
    fi

    # Show total count
    local total_formulas=$(brew list --formula | wc -l | tr -d ' ')
    echo -e "\n${GREEN}Total Formula Packages: $total_formulas${NC}"

    rm "$temp_file"
}

# Function to get cask packages
get_casks_by_time() {
    print_header "HOMEBREW CASK PACKAGES (GUI Applications)"

    local casks=($(brew list --cask 2>/dev/null || true))

    if [ ${#casks[@]} -eq 0 ]; then
        echo -e "${RED}No casks installed${NC}"
        return
    fi

    local temp_file=$(mktemp)

    # Try to get installation times for casks
    for cask in "${casks[@]}"; do
        # Try multiple methods to get cask install time
        install_time=""

        # Method 1: Check .metadata.json files
        if [ -d "/opt/homebrew/Caskroom/$cask" ]; then
            install_time=$(find "/opt/homebrew/Caskroom/$cask" -name ".metadata.json" -exec stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" {} \; 2>/dev/null | head -1)
        fi

        # Method 2: Check directory modification time
        if [ -z "$install_time" ] && [ -d "/opt/homebrew/Caskroom/$cask" ]; then
            install_time=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "/opt/homebrew/Caskroom/$cask" 2>/dev/null)
        fi

        if [ -n "$install_time" ]; then
            echo "$install_time $cask"
        else
            echo "unknown unknown $cask"
        fi
    done | sort > "$temp_file"

    # Display casks
    local current_date=""
    local count=0

    while IFS=' ' read -r date time cask; do
        if [ "$date" != "unknown" ]; then
            if [ "$date" != "$current_date" ]; then
                if [ -n "$current_date" ]; then
                    echo -e "${GREEN}  Total: $count casks${NC}\n"
                fi
                current_date="$date"
                count=0
                print_section "$date"
            fi
            echo -e "  ${BLUE}$time${NC} ${PURPLE}$cask${NC}"
            ((count++))
        else
            if [ "$current_date" != "unknown" ]; then
                if [ -n "$current_date" ]; then
                    echo -e "${GREEN}  Total: $count casks${NC}\n"
                fi
                current_date="unknown"
                count=0
                print_section "Unknown Install Date"
            fi
            echo -e "  ${RED}unknown${NC} ${PURPLE}$cask${NC}"
            ((count++))
        fi
    done < "$temp_file"

    if [ $count -gt 0 ]; then
        echo -e "${GREEN}  Total: $count casks${NC}"
    fi

    echo -e "\n${GREEN}Total Cask Packages: ${#casks[@]}${NC}"

    rm "$temp_file"
}

# Function to show summary
show_summary() {
    print_header "SUMMARY"

    local formula_count=$(brew list --formula | wc -l | tr -d ' ')
    local cask_count=$(brew list --cask 2>/dev/null | wc -l | tr -d ' ')
    local total_count=$((formula_count + cask_count))

    echo -e "${GREEN}Formula Packages: $formula_count${NC}"
    echo -e "${GREEN}Cask Packages: $cask_count${NC}"
    echo -e "${YELLOW}Total Packages: $total_count${NC}"

    # Show most recent installations
    local recent_formulas=$(brew list --formula | while read package; do
        install_time=$(find /opt/homebrew/Cellar/$package -name "INSTALL_RECEIPT.json" -exec stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" {} \; 2>/dev/null | head -1)
        if [ -n "$install_time" ]; then
            echo "$install_time $package"
        fi
    done | sort | tail -5)

    if [ -n "$recent_formulas" ]; then
        echo -e "\n${CYAN}5 Most Recent Formula Installations:${NC}"
        echo "$recent_formulas" | while IFS=' ' read -r date time package; do
            echo -e "  ${BLUE}$date $time${NC} ${PURPLE}$package${NC}"
        done
    fi
}

# Main function
main() {
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}Error: Homebrew is not installed or not in PATH${NC}"
        exit 1
    fi

    case "${1:-}" in
        --casks-only)
            get_casks_by_time
            ;;
        --formulas-only)
            get_formulas_by_time
            ;;
        --help|-h)
            echo "Usage: $0 [--casks-only|--formulas-only|--help]"
            echo ""
            echo "Options:"
            echo "  --casks-only     Show only cask packages"
            echo "  --formulas-only  Show only formula packages"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Default: Show both formulas and casks with summary"
            exit 0
            ;;
        "")
            get_formulas_by_time
            echo ""
            get_casks_by_time
            echo ""
            show_summary
            ;;
        *)
            echo -e "${RED}Error: Unknown option '$1'${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
