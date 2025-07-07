#!/bin/bash

# JamesDSP Script for Fosi Audio BT30D Bluetooth Latency Compensation
# This script delays all audio output except for the Fosi Audio BT30D by 2ms
# to compensate for Bluetooth latency differences

set -e

# Configuration
FOSI_DEVICE_NAME="Fosi Audio BT30D"
DELAY_MS=2
JAMESDSP_CONFIG_DIR="${HOME}/.config/JamesDSP"
CONFIG_FILE="${JAMESDSP_CONFIG_DIR}/config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Check if JamesDSP is installed
check_jamesdsp() {
    if ! command -v jamesdsp &> /dev/null; then
        error "JamesDSP is not installed. Please install it first."
        echo "Installation instructions:"
        echo "  Ubuntu/Debian: sudo apt install jamesdsp"
        echo "  Arch Linux: sudo pacman -S jamesdsp"
        echo "  Or build from source: https://github.com/Audio4Linux/JDSP4Linux"
        exit 1
    fi
    success "JamesDSP found"
}

# Check if PipeWire is running
check_pipewire() {
    if ! pw-cli info &> /dev/null; then
        error "PipeWire is not running. Please start PipeWire first."
        echo "Start PipeWire with: systemctl --user start pipewire pipewire-pulse"
        exit 1
    fi
    success "PipeWire is running"
}

# Get list of audio devices
get_audio_devices() {
    pw-cli list-objects | grep -A 20 -B 5 "media.class.*Audio/Sink" | while IFS= read -r line; do
        # Look for node.id lines
        if [[ "$line" =~ node\.id[[:space:]]*=[[:space:]]*\"([0-9]+)\" ]]; then
            node_id="${BASH_REMATCH[1]}"
            # Get the next few lines to extract name and description
            node_info=$(pw-cli info "$node_id" 2>/dev/null)
            if [[ -n "$node_info" ]]; then
                name=$(echo "$node_info" | grep "node.name" | sed 's/.*node\.name[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/')
                description=$(echo "$node_info" | grep "node.description" | sed 's/.*node\.description[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/')
                if [[ -n "$name" ]]; then
                    echo "$node_id|$name|$description"
                fi
            fi
        fi
    done
}

# Check if Fosi Audio BT30D is connected
find_fosi_device() {
    local fosi_device=""
    while IFS='|' read -r sink_id sink_name sink_description; do
        if [[ "$sink_description" == *"$FOSI_DEVICE_NAME"* ]]; then
            fosi_device="$sink_id"
            break
        fi
    done < <(get_audio_devices)
    echo "$fosi_device"
}

# Create JamesDSP configuration for delayed devices
create_delayed_config() {
    local config_content=$(cat <<EOF
{
  "devices": {
    "delayed": {
      "enabled": true,
      "processing": {
        "delay": {
          "enabled": true,
          "time": ${DELAY_MS}
        }
      }
    },
    "fosi_bt30d": {
      "enabled": true,
      "processing": {
        "delay": {
          "enabled": false
        }
      }
    }
  }
}
EOF
)
    echo "$config_content"
}

# Create JamesDSP configuration directory
setup_config_directory() {
    if [[ ! -d "$JAMESDSP_CONFIG_DIR" ]]; then
        log "Creating JamesDSP config directory: $JAMESDSP_CONFIG_DIR"
        mkdir -p "$JAMESDSP_CONFIG_DIR"
    fi
}

# Apply JamesDSP configuration
apply_configuration() {
    local fosi_device_id="$1"

    if [[ -z "$fosi_device_id" ]]; then
        warning "Fosi Audio BT30D not found. Applying delay to all devices."
        # Create config that delays all devices
        create_delayed_config | jq '.devices.delayed.processing.delay.enabled = true' > "$CONFIG_FILE"
    else
        log "Fosi Audio BT30D found (ID: $fosi_device_id). Creating selective delay configuration."
        # Create config that delays all devices except Fosi
        create_delayed_config > "$CONFIG_FILE"
    fi

    success "JamesDSP configuration created: $CONFIG_FILE"
}

# Start JamesDSP with configuration
start_jamesdsp() {
    log "Starting JamesDSP with delay configuration..."

    # Kill existing JamesDSP processes
    pkill -f jamesdsp || true

    # Start JamesDSP with our configuration
    jamesdsp --config "$CONFIG_FILE" &
    local jamesdsp_pid=$!

    # Wait a moment for JamesDSP to start
    sleep 2

    # Check if JamesDSP is running
    if kill -0 "$jamesdsp_pid" 2>/dev/null; then
        success "JamesDSP started successfully (PID: $jamesdsp_pid)"
        echo "$jamesdsp_pid" > /tmp/jamesdsp_fosi_delay.pid
    else
        error "Failed to start JamesDSP"
        exit 1
    fi
}

# Stop JamesDSP
stop_jamesdsp() {
    local pid_file="/tmp/jamesdsp_fosi_delay.pid"
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            log "Stopping JamesDSP (PID: $pid)..."
            kill "$pid"
            rm -f "$pid_file"
            success "JamesDSP stopped"
        else
            warning "JamesDSP process not found"
            rm -f "$pid_file"
        fi
    else
        warning "No JamesDSP PID file found"
    fi
}

# Show status
show_status() {
    local pid_file="/tmp/jamesdsp_fosi_delay.pid"
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            success "JamesDSP is running (PID: $pid)"
            echo "Configuration: $CONFIG_FILE"
            echo "Delay: ${DELAY_MS}ms for all devices except Fosi Audio BT30D"
        else
            warning "JamesDSP PID file exists but process is not running"
            rm -f "$pid_file"
        fi
    else
        warning "JamesDSP is not running"
    fi
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            log "Starting JamesDSP Fosi BT30D delay configuration..."
            check_jamesdsp
            check_pipewire
            setup_config_directory

            local fosi_device=$(find_fosi_device)
            if [[ -n "$fosi_device" ]]; then
                success "Found Fosi Audio BT30D (Device ID: $fosi_device)"
            else
                warning "Fosi Audio BT30D not found - will apply delay to all devices"
            fi

            apply_configuration "$fosi_device"
            start_jamesdsp
            ;;
        "stop")
            log "Stopping JamesDSP..."
            stop_jamesdsp
            ;;
        "restart")
            log "Restarting JamesDSP..."
            stop_jamesdsp
            sleep 1
            main start
            ;;
        "status")
            show_status
            ;;
        "devices")
            log "Available audio devices:"
            get_audio_devices | while IFS='|' read -r sink_id sink_name sink_description; do
                echo "  ID: $sink_id | Name: $sink_name | Description: $sink_description"
            done
            ;;
        "help"|"-h"|"--help")
            echo "JamesDSP Fosi Audio BT30D Delay Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start     Start JamesDSP with delay configuration (default)"
            echo "  stop      Stop JamesDSP"
            echo "  restart   Restart JamesDSP"
            echo "  status    Show current status"
            echo "  devices   List available audio devices"
            echo "  help      Show this help message"
            echo ""
            echo "Configuration:"
            echo "  Delay: ${DELAY_MS}ms for all devices except Fosi Audio BT30D"
            echo "  Config file: $CONFIG_FILE"
            ;;
        *)
            error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
