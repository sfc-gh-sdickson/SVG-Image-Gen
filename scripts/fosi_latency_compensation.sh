#!/bin/bash

# Fosi BT30D Latency Compensation Script
# Applies 2ms delay to compensate for Bluetooth latency
# Uses PipeWire's native delay capabilities

set -e

LOGFILE="fosi_latency_compensation.log"
FOSI_SINK_ID="503"
DELAY_MS="2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOGFILE"
}

error() {
    echo -e "${RED}ERROR:${NC} $1" | tee -a "$LOGFILE" >&2
}

success() {
    echo -e "${GREEN}SUCCESS:${NC} $1" | tee -a "$LOGFILE"
}

# Check if Fosi BT30D is connected
check_fosi_connection() {
    local fosi_line=$(pactl list sinks short | grep "$FOSI_SINK_ID")
    if [[ -n "$fosi_line" ]]; then
        # The status is in the last column, so get the last field
        local fosi_status=$(echo "$fosi_line" | awk '{print $NF}')
        if [[ "$fosi_status" == "RUNNING" ]]; then
            log "Fosi BT30D is connected and running"
            return 0
        else
            error "Fosi BT30D is not running (status: $fosi_status)"
            return 1
        fi
    else
        error "Fosi BT30D is not connected"
        return 1
    fi
}

# Get Fosi sink name
get_fosi_sink_name() {
    pactl list sinks short | grep "$FOSI_SINK_ID" | awk '{print $2}'
}

# Apply 2ms delay using PipeWire's delay module
apply_delay_compensation() {
    local sink_name=$(get_fosi_sink_name)
    if [[ -z "$sink_name" ]]; then
        error "Could not find Fosi sink name"
        return 1
    fi

    log "Applying ${DELAY_MS}ms delay compensation to Fosi BT30D"
    log "Sink: $sink_name"

    # Create a virtual sink for delay
    local virtual_sink=$(pactl load-module module-null-sink sink_name=fosi-delay-sink sink_properties=device.name=fosi-delay-sink)

    if [[ $? -eq 0 ]]; then
        log "Created virtual sink for delay: $virtual_sink"

        # Set the virtual sink as the default for Fosi routing
        pactl set-default-sink fosi-delay-sink

        # Route audio from virtual sink to Fosi with delay
        # This creates a 2ms buffer delay
        pactl load-module module-loopback source=fosi-delay-sink.monitor sink="$sink_name" latency_msec=2

        log "Applied 2ms delay compensation to Fosi BT30D"
        success "Delay compensation applied successfully"
    else
        error "Failed to create virtual sink for delay"
        return 1
    fi
}

# Remove delay compensation
remove_delay_compensation() {
    log "Removing delay compensation from Fosi BT30D"

    # Disconnect delay sink
    pw-link -d fosi-delay-sink:play_FL bluez_output.F4_4E_FD_04_2B_CF.1:playback_FL 2>/dev/null || true
    pw-link -d fosi-delay-sink:play_FR bluez_output.F4_4E_FD_04_2B_CF.1:playback_FR 2>/dev/null || true

    # Destroy delay sink module
    pw-cli destroy $(pw-cli list-objects | grep fosi-delay-sink | awk '{print $1}') 2>/dev/null || true

    success "Delay compensation removed from Fosi BT30D"
}

# Check delay compensation status
check_delay_status() {
    local delay_module=$(pw-cli list-objects | grep fosi-delay-sink)
    if [[ -n "$delay_module" ]]; then
        success "Delay compensation is ACTIVE"
        echo "Delay module: $delay_module"
    else
        log "Delay compensation is INACTIVE"
    fi
}

# Main function
main() {
    log "=== Fosi BT30D Latency Compensation ==="

    case "${1:-apply}" in
        apply)
            if check_fosi_connection; then
                apply_delay_compensation
            else
                exit 1
            fi
            ;;
        remove)
            remove_delay_compensation
            ;;
        status)
            check_delay_status
            ;;
        *)
            echo "Usage: $0 {apply|remove|status}"
            echo ""
            echo "Fosi BT30D Latency Compensation"
            echo "Applies 2ms delay to compensate for Bluetooth latency"
            echo ""
            echo "Commands:"
            echo "  apply   - Apply 2ms delay compensation"
            echo "  remove  - Remove delay compensation"
            echo "  status  - Check delay compensation status"
            exit 1
            ;;
    esac
}

main "$@"
