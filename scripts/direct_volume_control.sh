#!/bin/bash

# Direct Volume Control for All Audio Devices
# Monitors the default sink and applies volume changes to all physical audio devices

set -e

# Configuration
PID_FILE="/tmp/direct_volume_control.pid"
MONITOR_SCRIPT="/tmp/volume_monitor_direct.sh"

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

# Get all physical audio sink devices (exclude virtual sinks)
get_physical_sinks() {
    pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | while IFS= read -r line; do
        if echo "$line" | grep -q "id:"; then
            local sink_id=$(echo "$line" | grep -o 'id:[0-9]*' | cut -d: -f2)
            if [[ -n "$sink_id" ]]; then
                local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
                local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)

                # Skip virtual sinks (JamesDSP, null-audio, etc.)
                if [[ -n "$sink_name" ]] && ! echo "$sink_name" | grep -q -E "(jamesdsp|null-audio|unified)"; then
                    echo "$sink_id"
                fi
            fi
        fi
    done
}

# Get current volume of a sink
get_sink_volume() {
    local sink_id="$1"
    pw-cli get-volume "$sink_id" 2>/dev/null | grep -o '[0-9.]*' | head -1
}

# Set volume of a sink
set_sink_volume() {
    local sink_id="$1"
    local volume="$2"
    pw-cli set-volume "$sink_id" "$volume" 2>/dev/null || true
}

# Create volume monitoring script
create_monitor_script() {
    log "Creating direct volume monitoring script..."

    cat > "$MONITOR_SCRIPT" << 'EOF'
#!/bin/bash
# Direct volume monitoring script

# Get list of physical sinks
get_physical_sinks() {
    pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | while IFS= read -r line; do
        if echo "$line" | grep -q "id:"; then
            local sink_id=$(echo "$line" | grep -o 'id:[0-9]*' | cut -d: -f2)
            if [[ -n "$sink_id" ]]; then
                local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
                local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)

                # Skip virtual sinks
                if [[ -n "$sink_name" ]] && ! echo "$sink_name" | grep -q -E "(jamesdsp|null-audio|unified)"; then
                    echo "$sink_id"
                fi
            fi
        fi
    done
}

# Get default sink volume
get_default_volume() {
    # Try to get volume from the default sink
    local default_sink=$(pw-cli list-objects | grep -A 5 "media.class.*Audio/Sink" | grep "id:" | head -1 | cut -d: -f2)
    if [[ -n "$default_sink" ]]; then
        pw-cli get-volume "$default_sink" 2>/dev/null | grep -o '[0-9.]*' | head -1
    fi
}

# Main monitoring loop
last_volume=""
while true; do
    current_volume=$(get_default_volume)

    if [[ -n "$current_volume" ]] && [[ "$current_volume" != "$last_volume" ]]; then
        echo "Volume changed to: $current_volume"

        # Apply to all physical sinks
        sinks=$(get_physical_sinks)
        for sink_id in $sinks; do
            pw-cli set-volume "$sink_id" "$current_volume" 2>/dev/null || true
        done

        last_volume="$current_volume"
    fi

    sleep 0.1
done
EOF

    chmod +x "$MONITOR_SCRIPT"
    success "Volume monitoring script created"
}

# Start volume monitoring
start_monitoring() {
    log "Starting direct volume monitoring..."

    "$MONITOR_SCRIPT" &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    success "Direct volume monitoring started (PID: $pid)"
}

# Stop volume monitoring
stop_monitoring() {
    log "Stopping direct volume monitoring..."

    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        kill "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi

    rm -f "$MONITOR_SCRIPT"
    success "Direct volume monitoring stopped"
}

# Check status
check_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "Direct volume control is active (PID: $pid)"
        else
            warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        warning "Direct volume control is not active"
    fi

    echo ""
    echo "Physical audio devices:"
    get_physical_sinks | while read -r sink_id; do
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)
        local volume=$(get_sink_volume "$sink_id")
        echo "  $sink_name (ID: $sink_id) - Volume: $volume"
    done
}

# Test volume control
test_volume() {
    log "Testing volume control on all devices..."

    local sinks=$(get_physical_sinks)
    for sink_id in $sinks; do
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)
        log "Testing: $sink_name (ID: $sink_id)"

        # Test volume change
        set_sink_volume "$sink_id" "0.5"
        sleep 0.1
        set_sink_volume "$sink_id" "0.3"
        sleep 0.1
        set_sink_volume "$sink_id" "0.5"
    done

    success "Volume test completed"
}

# Main functions
start() {
    log "Starting direct volume control for all physical audio devices..."

    check_pipewire
    create_monitor_script
    start_monitoring

    success "Direct volume control setup complete"
    echo ""
    echo "Now your system volume control will affect all physical audio devices directly."
    echo "Test by changing volume with your keyboard/media keys."
}

stop() {
    log "Stopping direct volume control..."
    stop_monitoring
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
    test)
        test_volume
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|test}"
        echo ""
        echo "Direct Volume Control for PipeWire"
        echo "Controls volume for all physical audio devices directly"
        exit 1
        ;;
esac
