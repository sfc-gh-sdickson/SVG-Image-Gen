#!/bin/bash

# cleanup_pipewire.sh - Clean up excessive loopback modules
# Restore clean audio state and fix connection issues

LOG_FILE="pipewire_cleanup.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=== PipeWire Cleanup ===" | tee "$LOG_FILE"
log "Starting PipeWire cleanup..."

# Stop all loopback modules
log "Stopping all loopback modules..."
pactl list modules short | grep loopback | awk '{print $1}' | while read module_id; do
    log "Stopping module $module_id"
    pactl unload-module $module_id
done

# Stop JamesDSP delay sink
log "Stopping JamesDSP delay sink..."
pactl list modules short | grep "jamesdsp-delay-sink" | awk '{print $1}' | while read module_id; do
    log "Stopping JamesDSP module $module_id"
    pactl unload-module $module_id
done

# Verify cleanup
log "Verifying cleanup..."
echo "=== Remaining Loopback Modules ===" | tee -a "$LOG_FILE"
pactl list modules short | grep loopback | tee -a "$LOG_FILE"

echo "=== Remaining JamesDSP Modules ===" | tee -a "$LOG_FILE"
pactl list modules short | grep jamesdsp | tee -a "$LOG_FILE"

echo "=== Active Sinks ===" | tee -a "$LOG_FILE"
pactl list sinks short | tee -a "$LOG_FILE"

echo "=== Active Sources ===" | tee -a "$LOG_FILE"
pactl list sources short | tee -a "$LOG_FILE"

log "Cleanup complete. Audio system should be in clean state."
