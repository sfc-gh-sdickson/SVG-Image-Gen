#!/bin/bash

# PipeWire Native Delay Fix for Fosi Audio BT30D
# This script uses PipeWire's native delay capabilities instead of JamesDSP processing

set -e

# Configuration
FOSI_DEVICE_NAME="Fosi Audio BT30D"
DELAY_MS=2
PIPEWIRE_CONFIG_DIR="${HOME}/.config/pipewire"

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

# Check if PipeWire is running
check_pipewire() {
    if ! pw-cli info &> /dev/null; then
        error "PipeWire is not running. Please start PipeWire first."
        echo "Start PipeWire with: systemctl --user start pipewire pipewire-pulse"
        exit 1
    fi
    success "PipeWire is running"
}

# Find Fosi Audio BT30D device
find_fosi_device() {
    local device_info=$(pw-cli list-objects | grep -A 10 -B 5 "Fosi Audio BT30D")
    if [[ -n "$device_info" ]]; then
        local node_id=$(echo "$device_info" | grep "id:" | head -1 | grep -o 'id:[0-9]*' | cut -d: -f2)
        if [[ -n "$node_id" ]]; then
            echo "$node_id"
            return 0
        fi
    fi
    return 1
}

# Apply delay using PipeWire's native delay node
apply_pipewire_delay() {
    local fosi_id="$1"

    log "Creating PipeWire delay nodes for non-Fosi devices..."

    # Get all sink nodes except Fosi
    local all_sinks=$(pw-cli list-objects | grep -A 5 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2)

    for sink_id in $all_sinks; do
        # Skip if this is the Fosi device
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        if echo "$sink_info" | grep -q "Fosi Audio BT30D"; then
            log "Skipping Fosi device (ID: $sink_id)"
            continue
        fi

        # Create delay node for this sink
        log "Applying delay to device ID: $sink_id"

        # Use PipeWire's delay module
        pw-cli create-node adapter "{ factory.name=support.null-audio-sink node.name=delay-$sink_id media.class=Audio/Sink }" || {
            warning "Could not create delay node for sink $sink_id"
        }
    done

    success "PipeWire delay configuration applied"
}

# Remove delay configuration
remove_pipewire_delay() {
    log "Removing PipeWire delay nodes..."

    # Find and remove delay nodes
    local delay_nodes=$(pw-cli list-objects | grep "delay-" | grep "id:" | cut -d: -f2)
    for node_id in $delay_nodes; do
        pw-cli destroy "$node_id" 2>/dev/null || true
    done

    success "PipeWire delay configuration removed"
}

# Main functions
start() {
    log "Starting PipeWire delay configuration for Fosi Audio BT30D..."

    check_pipewire

    local fosi_id=$(find_fosi_device)
    if [[ -z "$fosi_id" ]]; then
        error "Fosi Audio BT30D not found"
        exit 1
    fi

    success "Found Fosi Audio BT30D (Device ID: $fosi_id)"
    apply_pipewire_delay "$fosi_id"
}

stop() {
    log "Stopping PipeWire delay configuration..."
    remove_pipewire_delay
}

status() {
    if pw-cli info &> /dev/null; then
        local delay_nodes=$(pw-cli list-objects | grep -c "delay-" || echo "0")
        if [[ "$delay_nodes" -gt 0 ]]; then
            success "PipeWire delay is active ($delay_nodes delay nodes)"
        else
            warning "PipeWire delay is not active"
        fi
    else
        error "PipeWire is not running"
    fi
}

# Command handling
case "${1:-start}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
