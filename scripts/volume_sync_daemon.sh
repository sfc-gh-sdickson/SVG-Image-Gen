#!/bin/bash

# Volume Sync Daemon
# Monitors system volume changes and applies them to ALL audio devices in real-time
# Keeps everything in sync with the system volume control

set -e

LOGFILE="volume_sync_daemon.log"
PID_FILE="/tmp/volume_sync_daemon.pid"
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

# Get all sink IDs (including JamesDSP)
get_sink_ids() {
    pactl list sinks short | awk '{print $1}'
}

# Get current volume from default sink (system volume)
get_system_volume() {
    local default_sink=$(pactl info | grep "Default Sink" | cut -d: -f2 | xargs)
    if [[ -n "$default_sink" ]]; then
        pactl get-sink-volume "$default_sink" | grep -oP '\d+%' | head -1
    else
        # Fallback: get volume from any sink
        pactl list sinks short | head -1 | awk '{print $1}' | xargs -I {} pactl get-sink-volume {} | grep -oP '\d+%' | head -1
    fi
}

# Set volume for all sinks (no cap - user sets relative levels)
set_all_volumes() {
    local target_vol="$1"

    local sink_ids=$(get_sink_ids)
    for sink_id in $sink_ids; do
        local sink_name=$(pactl list sinks short | grep "^$sink_id" | awk '{print $2}')
        local old_vol=$(pactl get-sink-volume "$sink_id" | grep -oP '\d+%' | head -1)

        log "Setting $sink_name (ID: $sink_id) from $old_vol to $target_vol"
        pactl set-sink-volume "$sink_id" "$target_vol"
    done
}

# Main monitoring loop
monitor_volume() {
    log "Starting volume sync daemon..."
    log "Monitoring system volume changes and applying to all devices"

    local last_volume=""

    while true; do
        local current_volume=$(get_system_volume)

        if [[ -n "$current_volume" ]] && [[ "$current_volume" != "$last_volume" ]]; then
            log "System volume changed to: $current_volume"
            set_all_volumes "$current_volume"
            last_volume="$current_volume"
        fi

        sleep 0.5
    done
}

# Start daemon
start() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            error "Volume sync daemon is already running (PID: $pid)"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi

    log "Starting volume sync daemon..."
    monitor_volume &
    echo $! > "$PID_FILE"
    success "Volume sync daemon started (PID: $(cat $PID_FILE))"
    log "Daemon will keep all devices in sync with system volume control"
}

# Stop daemon
stop() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$PID_FILE"
            success "Volume sync daemon stopped"
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
            success "Volume sync daemon is running (PID: $pid)"
            echo "Monitoring system volume and keeping all devices in sync"
        else
            error "PID file exists but daemon is not running"
            rm -f "$PID_FILE"
        fi
    else
        error "Volume sync daemon is not running"
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
        echo "Volume Sync Daemon"
        echo "Monitors system volume changes and applies them to ALL audio devices"
        echo "Keeps everything in sync with your keyboard/media volume controls"
        exit 1
        ;;
esac
