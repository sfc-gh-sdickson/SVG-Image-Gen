#!/bin/bash

# Unified Volume Control Setup for PipeWire
# Makes system volume control affect all audio devices simultaneously

set -e

# Configuration
PIPEWIRE_CONFIG_DIR="${HOME}/.config/pipewire"
PIPEWIRE_CLIENT_CONFIG="${PIPEWIRE_CONFIG_DIR}/pipewire.conf.d"
PID_FILE="/tmp/unified_volume.pid"

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

# Create unified volume sink
create_unified_sink() {
    log "Creating unified volume sink..."

    # Create a virtual sink that combines all audio outputs
    pw-cli create-node adapter "{ factory.name=support.null-audio-sink node.name=unified-volume-sink media.class=Audio/Sink }" || {
        error "Failed to create unified volume sink"
        return 1
    }

    success "Unified volume sink created"
}

# Get all audio sink devices
get_audio_sinks() {
    pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2 | tr '\n' ' '
}

# Link all sinks to unified control
link_sinks_to_unified() {
    local sinks=$(get_audio_sinks)
    log "Linking all audio sinks to unified volume control..."

    for sink_id in $sinks; do
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)

        if [[ -n "$sink_name" ]]; then
            log "Linking: $sink_name (ID: $sink_id)"

            # Create a link to the unified sink
            pw-cli link "$sink_id" "unified-volume-sink" || {
                warning "Could not link $sink_name to unified control"
            }
        fi
    done

    success "All sinks linked to unified volume control"
}

# Set up volume monitoring
setup_volume_monitoring() {
    log "Setting up volume monitoring..."

    # Create a script that monitors volume changes and applies to all devices
    cat > /tmp/volume_monitor.sh << 'EOF'
#!/bin/bash
# Volume monitoring script

while true; do
    # Get current unified sink volume
    current_volume=$(pw-cli get-volume "unified-volume-sink" 2>/dev/null | grep -o '[0-9.]*' | head -1)

    if [[ -n "$current_volume" ]]; then
        # Apply to all audio sinks
        sinks=$(pw-cli list-objects | grep -A 5 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2)
        for sink_id in $sinks; do
            pw-cli set-volume "$sink_id" "$current_volume" 2>/dev/null || true
        done
    fi

    sleep 0.1
done
EOF

    chmod +x /tmp/volume_monitor.sh
    /tmp/volume_monitor.sh &
    echo $! > "$PID_FILE"

    success "Volume monitoring started"
}

# Remove unified volume setup
remove_unified_volume() {
    log "Removing unified volume setup..."

    # Kill volume monitor
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        kill "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi

    # Remove unified sink
    local unified_sink_id=$(pw-cli list-objects | grep "unified-volume-sink" | grep "id:" | cut -d: -f2)
    if [[ -n "$unified_sink_id" ]]; then
        pw-cli destroy "$unified_sink_id" 2>/dev/null || true
    fi

    success "Unified volume setup removed"
}

# Check status
check_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "Unified volume control is active (PID: $pid)"
        else
            warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        warning "Unified volume control is not active"
    fi

    local unified_sink=$(pw-cli list-objects | grep -c "unified-volume-sink" || echo "0")
    if [[ "$unified_sink" -gt 0 ]]; then
        success "Unified volume sink is active"
    else
        warning "Unified volume sink is not active"
    fi
}

# Main functions
start() {
    log "Setting up unified volume control for all audio devices..."

    check_pipewire
    create_unified_sink
    link_sinks_to_unified
    setup_volume_monitoring

    success "Unified volume control setup complete"
    echo ""
    echo "Now your system volume control will affect all audio devices simultaneously."
    echo "Test by changing volume with your keyboard/media keys."
}

stop() {
    log "Stopping unified volume control..."
    remove_unified_volume
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
        echo "Unified Volume Control for PipeWire"
        echo "Makes system volume control affect all audio devices simultaneously"
        exit 1
        ;;
esac
