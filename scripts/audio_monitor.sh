#!/bin/bash

# audio_monitor.sh - Real-time audio system monitoring
# Detects frame drops, loopback issues, and performance problems

LOG_FILE="audio_monitor.log"
FRAME_DROP_LOG="frame_drops.log"
UNDERRUN_LOG="underrun_events.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Initialize logs
echo "=== Audio System Monitoring Started ===" > "$LOG_FILE"
echo "=== Frame Drop Detection ===" > "$FRAME_DROP_LOG"
echo "=== Buffer Underrun Events ===" > "$UNDERRUN_LOG"

log "Starting audio system monitoring..."

# Monitor PipeWire logs for frame drops and underruns
journalctl --user -u pipewire -f | while read line; do
    # Check for frame drops
    if echo "$line" | grep -q -E "(underrun|overrun|drop|error)"; then
        echo "[$(date)] FRAME DROP/UNDERRUN: $line" | tee -a "$FRAME_DROP_LOG"
        log "FRAME DROP DETECTED: $line"
    fi

    # Check for loopback errors
    if echo "$line" | grep -q -E "(loopback|connection.*failed)"; then
        echo "[$(date)] LOOPBACK ERROR: $line" | tee -a "$LOG_FILE"
        log "LOOPBACK ERROR: $line"
    fi

    # Check for performance issues
    if echo "$line" | grep -q -E "(starvation|timeout|buffer.*full)"; then
        echo "[$(date)] PERFORMANCE ISSUE: $line" | tee -a "$LOG_FILE"
        log "PERFORMANCE ISSUE: $line"
    fi
done
