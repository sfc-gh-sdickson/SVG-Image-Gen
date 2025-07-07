#!/bin/bash

# audio_crossover.sh - Implement audio crossover filtering
# Separates subwoofer frequencies from main speakers for optimal performance

LOG_FILE="crossover.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=== Audio Crossover Implementation ===" | tee "$LOG_FILE"
log "Setting up audio crossover filtering..."

# Crossover frequency (typical subwoofer crossover)
FREQUENCY=${1:-80}  # Hz - default 80Hz, can be overridden

log "Crossover frequency: ${FREQUENCY}Hz"

# Create low-pass filter for subwoofer
log "Creating low-pass filter for subwoofer..."
pactl load-module module-ladspa-sink sink_name=subwoofer-lpf \
    plugin=lowpass_1200 label=lowpass_1200 control=0,$FREQUENCY

if [ $? -eq 0 ]; then
    log "Low-pass filter created successfully"
else
    log "WARNING: Low-pass filter creation failed"
fi

# Create high-pass filter for main speakers
log "Creating high-pass filter for main speakers..."
pactl load-module module-ladspa-sink sink_name=main-hpf \
    plugin=highpass_1200 label=highpass_1200 control=0,$FREQUENCY

if [ $? -eq 0 ]; then
    log "High-pass filter created successfully"
else
    log "WARNING: High-pass filter creation failed"
fi

# Alternative: Use LADSPA plugins directly
log "Setting up LADSPA crossover plugins..."

# Check for available LADSPA plugins
if [ -d "/usr/lib/ladspa" ]; then
    log "Available LADSPA plugins:"
    ls /usr/lib/ladspa/*.so 2>/dev/null | head -10 | tee -a "$LOG_FILE"
else
    log "LADSPA plugins directory not found"
fi

# Create crossover using LADSPA
log "Creating LADSPA-based crossover..."

# Low-pass for subwoofer (below crossover frequency)
pactl load-module module-ladspa-sink sink_name=subwoofer-crossover \
    plugin=lowpass_1200 label=lowpass_1200 control=0,$FREQUENCY

# High-pass for main speakers (above crossover frequency)
pactl load-module module-ladspa-sink sink_name=main-crossover \
    plugin=highpass_1200 label=highpass_1200 control=0,$FREQUENCY

# Verify crossover setup
log "Verifying crossover setup..."
echo "=== Crossover Sinks ===" | tee -a "$LOG_FILE"
pactl list sinks short | grep -E "(subwoofer|main)" | tee -a "$LOG_FILE"

echo "=== Crossover Configuration ===" | tee -a "$LOG_FILE"
echo "Frequency: ${FREQUENCY}Hz" | tee -a "$LOG_FILE"
echo "Subwoofer: Low-pass filter (0-${FREQUENCY}Hz)" | tee -a "$LOG_FILE"
echo "Main speakers: High-pass filter (${FREQUENCY}Hz+)" | tee -a "$LOG_FILE"

# Performance optimization
log "Optimizing crossover performance..."

# Reduce buffer sizes for lower latency
log "Setting buffer sizes for optimal performance..."

# For subwoofer (low frequencies, can use larger buffers)
pactl set-sink-properties subwoofer-lpf device.buffering.buffer_size=1024

# For main speakers (higher frequencies, need smaller buffers)
pactl set-sink-properties main-hpf device.buffering.buffer_size=512

log "Crossover implementation complete."
log "Subwoofer: subwoofer-lpf (0-${FREQUENCY}Hz)"
log "Main speakers: main-hpf (${FREQUENCY}Hz+)"
