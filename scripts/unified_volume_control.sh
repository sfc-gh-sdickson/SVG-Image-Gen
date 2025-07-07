#!/bin/bash

# Unified Volume Control Script (Safe, Auditable)
# Sets all output devices to a safe, moderate volume (default 30%, max 50%)
# Logs all actions to volume_control.log

set -e

LOGFILE="volume_control.log"
DEFAULT_VOLUME=30%
MAX_VOLUME=50%

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

# Get all output device IDs and names
get_sinks() {
    pactl list sinks short | awk '{print $1":"$2}'
}

# Get current volume for a sink
get_sink_volume() {
    local sink_id="$1"
    pactl get-sink-volume "$sink_id" | grep -oP '\d+%' | head -1
}

# Set volume for a sink (capped at MAX_VOLUME)
set_sink_volume() {
    local sink_id="$1"
    local target_vol="$2"
    # Cap at MAX_VOLUME
    local vol_num=$(echo "$target_vol" | grep -oP '\d+')
    local max_num=$(echo "$MAX_VOLUME" | grep -oP '\d+')
    if (( vol_num > max_num )); then
        target_vol="$MAX_VOLUME"
    fi
    pactl set-sink-volume "$sink_id" "$target_vol"
}

# Main logic
main() {
    local target_vol="${1:-$DEFAULT_VOLUME}"
    log "Setting all output devices to $target_vol (max $MAX_VOLUME)"

    get_sinks | while IFS= read -r line; do
        sink_id=$(echo "$line" | cut -d: -f1)
        sink_name=$(echo "$line" | cut -d: -f2)
        old_vol=$(get_sink_volume "$sink_id")
        log "Device: $sink_name (ID: $sink_id) | Old Volume: $old_vol"
        set_sink_volume "$sink_id" "$target_vol"
        new_vol=$(get_sink_volume "$sink_id")
        log "Device: $sink_name (ID: $sink_id) | New Volume: $new_vol"
    done
    success "All output devices set to $target_vol (max $MAX_VOLUME)"
}

main "$@"
