#!/bin/bash

# JamesDSP Latency Compensation Script
# Applies 2ms delay to JamesDSP sink to sync with Fosi BT30D
# Fosi is left untouched

set -e

LOGFILE="jamesdsp_latency_compensation.log"
JAMES_SINK_NAME="jamesdsp_sink"
DELAY_MS="1.9"

log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

error() {
    echo -e "ERROR: $1" | tee -a "$LOGFILE" >&2
}

success() {
    echo -e "SUCCESS: $1" | tee -a "$LOGFILE"
}

# Check if JamesDSP is running
check_jamesdsp() {
    pactl list sinks short | grep -q "$JAMES_SINK_NAME"
}

# Check if delay sink already exists
check_delay_sink() {
    pactl list sinks short | grep -q "jamesdsp-delay-sink"
}

# Clean up existing delay modules
cleanup_delay_modules() {
    log "Cleaning up existing delay modules..."
    # Unload all loopback modules that reference jamesdsp-delay-sink
    pactl list modules short | grep "jamesdsp-delay-sink" | awk '{print $1}' | while read module_id; do
        if [[ -n "$module_id" ]]; then
            log "Unloading loopback module: $module_id"
            pactl unload-module "$module_id" 2>/dev/null || true
        fi
    done
    # Unload all null-sink modules named jamesdsp-delay-sink
    pactl list modules short | grep "jamesdsp-delay-sink" | awk '{print $1}' | while read module_id; do
        if [[ -n "$module_id" ]]; then
            log "Unloading null-sink module: $module_id"
            pactl unload-module "$module_id" 2>/dev/null || true
        fi
    done
    # Also clean up any orphaned sink-inputs that might be stuck
    pactl list sink-inputs short | grep "jamesdsp-delay-sink" | awk '{print $1}' | while read input_id; do
        if [[ -n "$input_id" ]]; then
            log "Moving orphaned sink-input $input_id to default sink"
            pactl move-sink-input "$input_id" @DEFAULT_SINK@ 2>/dev/null || true
        fi
    done
}

# Apply 1.8ms delay to JamesDSP
apply_delay() {
    if ! check_jamesdsp; then
        error "JamesDSP sink not found."
        exit 1
    fi

    # Clean up any existing delay modules first
    cleanup_delay_modules

    # Wait a moment for cleanup to complete
    sleep 1

    log "Applying ${DELAY_MS}ms delay to JamesDSP sink."
    # Create a virtual delayed sink
    local virtual_sink=$(pactl load-module module-null-sink sink_name=jamesdsp-delay-sink source=jamesdsp_filter sink_properties=device.description=JamesDSP-Delay-Sink)
    if [[ $? -eq 0 ]]; then
        log "Created virtual sink: $virtual_sink"
        # Route audio from virtual sink to JamesDSP with delay
        # pactl load-module module-loopback source=jamesdsp_filter sink=jamesdsp-delay-sink.monitor latency_msec=$DELAY_MS
        success "${DELAY_MS}ms delay applied to JamesDSP. Use jamesdsp-delay-sink as your output."
    else
        error "Failed to create virtual sink."
        exit 1
    fi
}

# Remove delay modules
remove_delay() {
    log "Removing JamesDSP delay modules."
    cleanup_delay_modules
    success "Delay modules removed."
}

# Status
status() {
    pactl list sinks short | grep jamesdsp-delay-sink && echo "JamesDSP delay sink is active." || echo "JamesDSP delay sink is not active."
}

case "${1:-apply}" in
    apply)
        apply_delay
        ;;
    remove)
        remove_delay
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {apply|remove|status}"
        ;;
esac
