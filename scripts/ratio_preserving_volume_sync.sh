#!/bin/bash

# Ratio-Preserving Volume Sync Daemon
# Maintains user-established volume ratios when system volume changes
# Uses current levels as MAX ratios

# =============================================================================
# LESSONS LEARNED - Audio System Integration
# =============================================================================
#
# 1. JAMESDSP INTEGRATION:
#    - JamesDSP manages its own volume and should NOT be included in ratio calculations
#    - Excluding JamesDSP (ID 1140) prevents volume fighting between daemon and DSP
#    - JamesDSP auto-adjusts volume, which would trigger daemon recalculation loops
#
# 2. VOLUME RATIO STRATEGY:
#    - Use multiplication-based ratios (system_vol * max_ratio / 100)
#    - Remove artificial 100% caps to allow devices to reach their full potential
#    - KM Audio can exceed 100% (135% max) for proper amplification
#
# 3. DEVICE-SPECIFIC CONSIDERATIONS:
#    - KM Audio (ID 487): 135% ratio - highest level with external amp
#    - Built-in Audio (ID 53): 99% ratio - high level
#    - Fosi BT30D (ID 503): 62% ratio - subwoofer, adjusted down
#    - Thunderbolt Display (ID 6393): 53% ratio - medium-low
#    - PCM2912A (ID 51): 23% ratio - low level
#    - Tonga HDMI (ID 198): 23% ratio - non-responsive but preserved
#
# 4. TECHNICAL IMPLEMENTATION:
#    - Parse volume strings carefully (remove extra % signs)
#    - Use minimum volume threshold (5%) to prevent complete silence
#    - Monitor system volume changes, not individual device changes
#    - Separate JamesDSP volume management from ratio calculations
#
# 5. USER WORKFLOW:
#    - Set volumes manually first to establish MAX ratios
#    - Lock ratios in daemon configuration
#    - Let JamesDSP manage its own processing
#    - Use system volume control for overall level adjustment
#
# =============================================================================

set -e

LOGFILE="ratio_volume_sync.log"
PID_FILE="/tmp/ratio_volume_sync.pid"

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

# MAX ratios established by user (current levels as MAX) - ANTI-DISTORTION VERSION
declare -A MAX_RATIOS=(
    [51]="20"   # PCM2912A Audio Codec - Low level
    [53]="80"   # Built-in Audio - High but safe
    [198]="20"  # Tonga HDMI (non-responsive, but preserved)
    [487]="100" # KM Audio - Capped at 100% to prevent distortion
    [503]="50"  # Fosi BT30D - Subwoofer, conservative level
    [1140]="66" # JamesDSP (self-managed, excluded from ratios)
    [6393]="40" # Thunderbolt Display Audio - Medium-low
)

# Get all sink IDs
get_sink_ids() {
    pactl list sinks short | awk '{print $1}'
}

# Get current volume from default sink (system volume)
get_system_volume() {
    local default_sink=$(pactl info | grep "Default Sink" | cut -d: -f2 | xargs)
    if [[ -n "$default_sink" ]]; then
        local volume=$(pactl get-sink-volume "$default_sink" | grep -oP '\d+%' | head -1)
        # Remove any extra % signs
        echo "${volume//%/}"
    else
        # Fallback: get volume from any sink
        local volume=$(pactl list sinks short | head -1 | awk '{print $1}' | xargs -I {} pactl get-sink-volume {} | grep -oP '\d+%' | head -1)
        echo "${volume//%/}"
    fi
}

# Calculate ratio-preserving volume for a device
calculate_ratio_volume() {
    local sink_id="$1"
    local system_vol="$2"
    local max_ratio="${MAX_RATIOS[$sink_id]}"

    if [[ -n "$max_ratio" ]]; then
        # Use the max_ratio as a percentage of system volume
        # This maintains the relative relationship
        local ratio_volume=$(echo "scale=0; $system_vol * $max_ratio / 100" | bc -l)

        # Ensure we don't go below 0
        if [[ $ratio_volume -lt 0 ]]; then
            ratio_volume=0
        fi

        # Minimum volume threshold to prevent complete silence
        local min_volume=5
        if [[ $ratio_volume -lt $min_volume ]] && [[ $system_vol -gt 0 ]]; then
            ratio_volume=$min_volume
        fi

        echo "$ratio_volume"
    else
        # If no ratio defined, use system volume
        echo "$system_vol"
    fi
}

# Set ratio-preserving volumes for all sinks
set_ratio_volumes() {
    local system_vol="$1"
    log "System volume: $system_vol% - applying ratio-preserving volumes"

    local sink_ids=$(get_sink_ids)
    for sink_id in $sink_ids; do
        # Skip JamesDSP since it manages its own volume
        if [[ "$sink_id" == "1140" ]]; then
            log "Skipping JamesDSP (ID: $sink_id) - it manages its own volume"
            continue
        fi

        local sink_name=$(pactl list sinks short | grep "^$sink_id" | awk '{print $2}')
        local old_vol=$(pactl get-sink-volume "$sink_id" | grep -oP '\d+%' | head -1)
        local new_vol=$(calculate_ratio_volume "$sink_id" "$system_vol")

        log "Setting $sink_name (ID: $sink_id) from $old_vol to ${new_vol}% (ratio: ${MAX_RATIOS[$sink_id]:-system}%)"
        pactl set-sink-volume "$sink_id" "${new_vol}%"
    done
}

# Main monitoring loop
monitor_volume() {
    log "Starting ratio-preserving volume sync daemon..."
    log "MAX ratios: ${MAX_RATIOS[*]}"

    local last_volume=""
    local jamesdsp_last_volume=""

    while true; do
        local current_volume=$(get_system_volume)
        local jamesdsp_current=$(pactl get-sink-volume 1140 | grep -oP '\d+%' | head -1 | sed 's/%//')

        # Check if JamesDSP changed its own volume
        if [[ -n "$jamesdsp_last_volume" ]] && [[ "$jamesdsp_current" != "$jamesdsp_last_volume" ]]; then
            log "JamesDSP auto-adjusted from ${jamesdsp_last_volume}% to ${jamesdsp_current}% - skipping ratio update"
            jamesdsp_last_volume="$jamesdsp_current"
            sleep 0.5
            continue
        fi

        if [[ -n "$current_volume" ]] && [[ "$current_volume" != "$last_volume" ]]; then
            log "System volume changed to: $current_volume%"
            set_ratio_volumes "$current_volume"
            last_volume="$current_volume"
            jamesdsp_last_volume="$jamesdsp_current"
        fi

        sleep 0.5
    done
}

# Start daemon
start() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            error "Ratio-preserving volume sync daemon is already running (PID: $pid)"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi

    log "Starting ratio-preserving volume sync daemon..."
    monitor_volume &
    echo $! > "$PID_FILE"
    success "Ratio-preserving volume sync daemon started (PID: $(cat $PID_FILE))"
    log "Daemon will maintain volume ratios when system volume changes"
}

# Stop daemon
stop() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$PID_FILE"
            success "Ratio-preserving volume sync daemon stopped"
        else
            error "Daemon is not running"
            rm -f "$PID_FILE"
        fi
    else
        error "No PID file found"
    fi
}

# Check status
status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "Ratio-preserving volume sync daemon is running (PID: $pid)"
            echo "MAX ratios: ${MAX_RATIOS[*]}"
        else
            error "PID file exists but daemon is not running"
            rm -f "$PID_FILE"
        fi
    else
        error "Ratio-preserving volume sync daemon is not running"
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
        echo ""
        echo "Ratio-Preserving Volume Sync Daemon"
        echo "Maintains user-established volume ratios when system volume changes"
        echo "MAX ratios: ${MAX_RATIOS[*]}"
        exit 1
        ;;
esac
