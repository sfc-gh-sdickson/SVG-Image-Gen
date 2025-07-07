#!/bin/bash

# Simple Volume Control for All Audio Devices
# Directly controls volume for all physical audio devices

set -e

# Configuration
PID_FILE="/tmp/simple_volume_control.pid"
MONITOR_SCRIPT="/tmp/simple_volume_monitor.sh"

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

# Get device IDs for known audio devices
get_device_ids() {
    echo "Getting device IDs..."

    # Get all sink IDs
    local sink_ids=$(pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2 | tr '\n' ' ')

    for sink_id in $sink_ids; do
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)

        if [[ -n "$sink_name" ]]; then
            echo "Found: $sink_name (ID: $sink_id)"
        fi
    done
}

# Set volume for all devices
set_all_volumes() {
    local volume="$1"
    log "Setting volume to $volume for all devices..."

    # Get all sink IDs
    local sink_ids=$(pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2 | tr '\n' ' ')

    for sink_id in $sink_ids; do
        local sink_info=$(pw-cli info "$sink_id" 2>/dev/null)
        local sink_name=$(echo "$sink_info" | grep "node.name" | cut -d'"' -f2)

        if [[ -n "$sink_name" ]]; then
            log "Setting volume for: $sink_name (ID: $sink_id)"
            pw-cli set-volume "$sink_id" "$volume" 2>/dev/null || {
                warning "Could not set volume for $sink_name"
            }
        fi
    done

    success "Volume set to $volume for all devices"
}

# Create monitoring script
create_monitor_script() {
    log "Creating volume monitoring script..."

    cat > "$MONITOR_SCRIPT" << 'EOF'
#!/bin/bash
# Simple volume monitoring script

# Get current volume from default sink
get_current_volume() {
    # Try to get volume from any available sink
    local sink_ids=$(pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2 | tr '\n' ' ')
    for sink_id in $sink_ids; do
        local volume=$(pw-cli get-volume "$sink_id" 2>/dev/null | grep -o '[0-9.]*' | head -1)
        if [[ -n "$volume" ]]; then
            echo "$volume"
            return 0
        fi
    done
    echo ""
}

# Set volume for all devices
set_all_volumes() {
    local volume="$1"
    local sink_ids=$(pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2 | tr '\n' ' ')

    for sink_id in $sink_ids; do
        pw-cli set-volume "$sink_id" "$volume" 2>/dev/null || true
    done
}

# Main monitoring loop
last_volume=""
while true; do
    current_volume=$(get_current_volume)

    if [[ -n "$current_volume" ]] && [[ "$current_volume" != "$last_volume" ]]; then
        echo "Volume changed to: $current_volume"
        set_all_volumes "$current_volume"
        last_volume="$current_volume"
    fi

    sleep 0.2
done
EOF

    chmod +x "$MONITOR_SCRIPT"
    success "Volume monitoring script created"
}

# Start monitoring
start_monitoring() {
    log "Starting volume monitoring..."

    "$MONITOR_SCRIPT" &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    success "Volume monitoring started (PID: $pid)"
}

# Stop monitoring
stop_monitoring() {
    log "Stopping volume monitoring..."

    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        kill "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi

    rm -f "$MONITOR_SCRIPT"
    success "Volume monitoring stopped"
}

# Check status
check_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "Simple volume control is active (PID: $pid)"
        else
            warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        warning "Simple volume control is not active"
    fi

    echo ""
    echo "Available audio devices:"
    get_device_ids
}

# Test volume control
test_volume() {
    log "Testing volume control..."

    set_all_volumes "0.3"
    sleep 1
    set_all_volumes "0.5"
    sleep 1
    set_all_volumes "0.7"

    success "Volume test completed"
}

# Main functions
start() {
    log "Starting simple volume control for all audio devices..."

    create_monitor_script
    start_monitoring

    success "Simple volume control setup complete"
    echo ""
    echo "Now your system volume control will affect all audio devices."
    echo "Test by changing volume with your keyboard/media keys."
}

stop() {
    log "Stopping simple volume control..."
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
        echo "Simple Volume Control for PipeWire"
        echo "Controls volume for all audio devices"
        exit 1
        ;;
esac
