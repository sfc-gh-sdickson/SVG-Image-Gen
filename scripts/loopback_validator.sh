#!/bin/bash

# loopback_validator.sh - Validate loopback connections
# Detects mismatches between specified and actual connections

LOG_FILE="loopback_validation.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=== Loopback Connection Validation ===" | tee "$LOG_FILE"

# Check all loopback modules
echo "=== Loopback Modules ===" | tee -a "$LOG_FILE"
pactl list modules short | grep loopback | while read module_id rest; do
    echo "Module $module_id: $rest" | tee -a "$LOG_FILE"

    # Get detailed module info
    echo "Detailed info for module $module_id:" | tee -a "$LOG_FILE"
    pactl list modules | grep -A 20 "Module #$module_id" | grep -E "(source|sink|latency)" | tee -a "$LOG_FILE"
    echo | tee -a "$LOG_FILE"
done

# Check actual sink-input connections
echo "=== Sink Input Connections ===" | tee -a "$LOG_FILE"
pactl list sink-inputs | grep -A 10 -B 5 "loopback" | tee -a "$LOG_FILE"

# Check actual source-output connections
echo "=== Source Output Connections ===" | tee -a "$LOG_FILE"
pactl list source-outputs | grep -A 10 -B 5 "loopback" | tee -a "$LOG_FILE"

# Validate specific connections
echo "=== Specific Connection Validation ===" | tee -a "$LOG_FILE"

# Check jamesdsp-delay-sink connections
if pactl list sinks | grep -q "jamesdsp-delay-sink"; then
    echo "jamesdsp-delay-sink exists" | tee -a "$LOG_FILE"
    pactl list sinks | grep -A 20 "jamesdsp-delay-sink" | tee -a "$LOG_FILE"
else
    echo "WARNING: jamesdsp-delay-sink not found" | tee -a "$LOG_FILE"
fi

# Check jamesdsp-delay-sink.monitor connections
if pactl list sources | grep -q "jamesdsp-delay-sink.monitor"; then
    echo "jamesdsp-delay-sink.monitor exists" | tee -a "$LOG_FILE"
    pactl list sources | grep -A 20 "jamesdsp-delay-sink.monitor" | tee -a "$LOG_FILE"
else
    echo "WARNING: jamesdsp-delay-sink.monitor not found" | tee -a "$LOG_FILE"
fi

# Check for connection mismatches
echo "=== Connection Mismatch Detection ===" | tee -a "$LOG_FILE"

# Look for loopback connections that don't match expected patterns
pactl list sink-inputs | grep -A 5 "loopback" | while read line; do
    if echo "$line" | grep -q "Sink:"; then
        sink=$(echo "$line" | awk '{print $2}')
        echo "Loopback sink-input connected to: $sink" | tee -a "$LOG_FILE"

        # Check if this matches expected connections
        if [[ "$sink" != "jamesdsp_sink" ]]; then
            echo "WARNING: Unexpected loopback connection to $sink" | tee -a "$LOG_FILE"
        fi
    fi
done

echo "=== Validation Complete ===" | tee -a "$LOG_FILE"
