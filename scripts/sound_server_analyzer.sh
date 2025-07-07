#!/bin/bash

# sound_server_analyzer.sh - Analyze sound server options
# Compares PipeWire, JACK, PulseAudio, and ALSA

LOG_FILE="sound_server_analysis.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=== Sound Server Analysis ===" | tee "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

# Current PipeWire Status
echo "=== Current Server: PipeWire ===" | tee -a "$LOG_FILE"
systemctl --user status pipewire | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

# JACK Availability and Status
echo "=== JACK Audio Connection Kit ===" | tee -a "$LOG_FILE"
if which jackd >/dev/null 2>&1; then
    echo "JACK available: $(which jackd)" | tee -a "$LOG_FILE"
    echo "JACK version: $(jackd --version 2>&1)" | tee -a "$LOG_FILE"

    # Check if JACK is running
    if pgrep jackd >/dev/null; then
        echo "JACK is running (PID: $(pgrep jackd))" | tee -a "$LOG_FILE"
        echo "JACK CPU usage: $(ps aux | grep jackd | grep -v grep | awk '{print $3}')%" | tee -a "$LOG_FILE"
    else
        echo "JACK is not running" | tee -a "$LOG_FILE"
    fi
else
    echo "JACK not installed" | tee -a "$LOG_FILE"
fi
echo | tee -a "$LOG_FILE"

# PulseAudio Status
echo "=== PulseAudio Status ===" | tee -a "$LOG_FILE"
if systemctl --user status pulseaudio >/dev/null 2>&1; then
    systemctl --user status pulseaudio | tee -a "$LOG_FILE"
else
    echo "PulseAudio not running" | tee -a "$LOG_FILE"
fi
echo | tee -a "$LOG_FILE"

# ALSA Status
echo "=== ALSA Status ===" | tee -a "$LOG_FILE"
echo "ALSA modules loaded:" | tee -a "$LOG_FILE"
lsmod | grep snd | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

# Performance Comparison
echo "=== Performance Comparison ===" | tee -a "$LOG_FILE"

# PipeWire performance
PIPEWIRE_CPU=$(ps aux | grep pipewire | grep -v grep | awk '{sum+=$3} END {print sum}')
PIPEWIRE_MEM=$(ps aux | grep pipewire | grep -v grep | awk '{sum+=$4} END {print sum}')
echo "PipeWire CPU: ${PIPEWIRE_CPU:-0}%" | tee -a "$LOG_FILE"
echo "PipeWire Memory: ${PIPEWIRE_MEM:-0}%" | tee -a "$LOG_FILE"

# JACK performance
if pgrep jackd >/dev/null; then
    JACK_CPU=$(ps aux | grep jackd | grep -v grep | awk '{sum+=$3} END {print sum}')
    JACK_MEM=$(ps aux | grep jackd | grep -v grep | awk '{sum+=$4} END {print sum}')
    echo "JACK CPU: ${JACK_CPU:-0}%" | tee -a "$LOG_FILE"
    echo "JACK Memory: ${JACK_MEM:-0}%" | tee -a "$LOG_FILE"
else
    echo "JACK CPU: N/A (not running)" | tee -a "$LOG_FILE"
    echo "JACK Memory: N/A (not running)" | tee -a "$LOG_FILE"
fi

# PulseAudio performance
if pgrep pulseaudio >/dev/null; then
    PULSE_CPU=$(ps aux | grep pulseaudio | grep -v grep | awk '{sum+=$3} END {print sum}')
    PULSE_MEM=$(ps aux | grep pulseaudio | grep -v grep | awk '{sum+=$4} END {print sum}')
    echo "PulseAudio CPU: ${PULSE_CPU:-0}%" | tee -a "$LOG_FILE"
    echo "PulseAudio Memory: ${PULSE_MEM:-0}%" | tee -a "$LOG_FILE"
else
    echo "PulseAudio CPU: N/A (not running)" | tee -a "$LOG_FILE"
    echo "PulseAudio Memory: N/A (not running)" | tee -a "$LOG_FILE"
fi
echo | tee -a "$LOG_FILE"

# Feature Comparison
echo "=== Feature Comparison ===" | tee -a "$LOG_FILE"
echo "Server          | Real-time | Low Latency | Professional | Stability" | tee -a "$LOG_FILE"
echo "PipeWire        |     Yes   |     Yes     |     Yes      |   Medium  " | tee -a "$LOG_FILE"
echo "JACK            |     Yes   |     Yes     |     Yes      |   High    " | tee -a "$LOG_FILE"
echo "PulseAudio      |     No    |     No      |     No       |   High    " | tee -a "$LOG_FILE"
echo "ALSA            |     Yes   |     Yes     |     Yes      |   High    " | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

# Recommendations
echo "=== Recommendations ===" | tee -a "$LOG_FILE"
echo "For precise timing requirements (like your 1.9ms latency compensation):" | tee -a "$LOG_FILE"
echo "1. JACK - Best for professional audio with precise timing" | tee -a "$LOG_FILE"
echo "2. ALSA - Direct hardware access, minimal latency" | tee -a "$LOG_FILE"
echo "3. PipeWire - Modern but may have stability issues" | tee -a "$LOG_FILE"
echo "4. PulseAudio - Not suitable for precise timing" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

echo "=== Analysis Complete ===" | tee -a "$LOG_FILE"
