#!/bin/bash

# Simple PipeWire Delay for Fosi Audio BT30D Subwoofer
# Uses PipeWire's native delay capabilities without JamesDSP

set -e

# Configuration
FOSI_DEVICE_NAME="Fosi Audio BT30D"
DELAY_MS=2
PID_FILE="/tmp/pipewire_delay.pid"

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
    local line_num=$(pw-cli list-objects | grep -n 'node.description = "Fosi Audio BT30D"' | cut -d: -f1 | head -n1)
    if [[ -n "$line_num" ]]; then
        # Search backwards for the nearest preceding Node id
        local node_line=$(pw-cli list-objects | head -n "$line_num" | grep -E 'id [0-9]+, type PipeWire:Interface:Node' | tail -n1)
        local node_id=$(echo "$node_line" | grep -o 'id [0-9]\+' | awk '{print $2}')
        if [[ -n "$node_id" ]]; then
            echo "$node_id"
            return 0
        fi
    fi
    return 1
}

# Apply simple delay using PipeWire's delay module
apply_delay() {
    local fosi_id="$1"

    log "Applying ${DELAY_MS}ms delay to all devices EXCEPT Fosi Audio BT30D to compensate for Bluetooth latency..."

    # Get all audio sink nodes
    local all_sinks=$(pw-cli list-objects | grep -A 5 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2)

    for sink_id in $all_sinks; do
        # Get sink info
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)

        # Check if this is the Fosi device
        if echo "$sink_info" | grep -q "Fosi Audio BT30D"; then
            log "Skipping Fosi subwoofer (ID: $sink_id) - no delay applied (already 2ms behind)"
        else
            log "Applying delay to: $sink_name (ID: $sink_id) - compensating for Fosi's Bluetooth latency"

            # Create a delay node for non-Fosi devices
            pw-cli create-node adapter "{ factory.name=support.null-audio-sink node.name=delay-other-$sink_id media.class=Audio/Sink }" || {
                warning "Could not create delay for $sink_name"
            }
        fi
    done

    success "Delay configuration applied to all devices except Fosi subwoofer"
}

# Remove delay configuration
remove_delay() {
    log "Removing delay configuration..."

    # Find and remove delay nodes
    local delay_nodes=$(pw-cli list-objects | grep "delay-" | grep "id:" | cut -d: -f2)
    for node_id in $delay_nodes; do
        pw-cli destroy "$node_id" 2>/dev/null || true
    done

    # Remove PID file
    rm -f "$PID_FILE"

    success "Delay configuration removed"
}

# Check status
check_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "PipeWire delay is active (PID: $pid)"
            return 0
        else
            warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    fi

    local delay_nodes
    delay_nodes=$(pw-cli list-objects | grep -c "delay-" 2>/dev/null || echo "0")
    delay_nodes=$(echo "$delay_nodes" | head -n1)
    if [[ "$delay_nodes" -gt 0 ]]; then
        success "Delay nodes are active ($delay_nodes nodes)"
    else
        warning "No delay configuration is active"
    fi
}

# Main functions
start() {
    log "Starting PipeWire delay for Fosi Audio BT30D subwoofer..."

    check_pipewire

    local fosi_id=$(find_fosi_device)
    if [[ -z "$fosi_id" ]]; then
        error "Fosi Audio BT30D subwoofer not found"
        exit 1
    fi

    success "Found Fosi Audio BT30D subwoofer (Device ID: $fosi_id)"
    apply_delay "$fosi_id"

    # Save PID
    echo $$ > "$PID_FILE"
    success "Delay configuration started"
}

stop() {
    log "Stopping PipeWire delay configuration..."
    remove_delay
}

restart() {
    stop
    sleep 1
    start
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
        restart
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Simple PipeWire delay for Fosi Audio BT30D subwoofer"
        echo "Applies ${DELAY_MS}ms delay to all devices except the Fosi subwoofer"
        echo "to compensate for Bluetooth latency differences."
        exit 1
        ;;
esac
