# Audio System Observability Framework

## Critical Issues Analysis

### 1. Loopback Behavior Investigation
**Problem**: Loopback modules create unexpected connections with no error reporting
**Symptoms**:
- Source/sink mismatch between specification and reality
- No error messages for failed connections
- Inconsistent behavior across runs

**Observability Requirements**:
```bash
# Real-time loopback monitoring
pactl list modules | grep -A 10 -B 5 "module-loopback"
pactl list sink-inputs | grep -A 5 "loopback"
pactl list source-outputs | grep -A 5 "loopback"

# Connection validation
pactl list sinks | grep -A 20 "jamesdsp-delay-sink"
pactl list sources | grep -A 20 "jamesdsp-delay-sink.monitor"
```

### 2. Frame Dropping Detection
**Problem**: Stochastic white static indicates dropped frames
**Causes**:
- CPU starvation
- Buffer underruns
- Timecode drift
- Logic errors in PipeWire

**Detection Tools**:
```bash
# Real-time frame monitoring
pw-top  # PipeWire topology and performance
pw-cli info all | grep -E "(underrun|overrun|drop)"
journalctl --user -u pipewire -f | grep -E "(error|warning|drop)"

# Audio buffer analysis
pactl list sinks | grep -A 10 -B 5 "Latency:"
pactl list sink-inputs | grep -A 5 -B 5 "Buffer Latency:"
```

### 3. Sound Server Comparison

| Server | Pros | Cons | Use Case |
|--------|------|------|----------|
| **PipeWire** | Modern, flexible | Complex, buggy | General purpose |
| **JACK** | Real-time, precise | Complex setup | Professional audio |
| **PulseAudio** | Stable, mature | Legacy, limited | Desktop audio |
| **ALSA** | Direct, fast | Low-level, complex | Hardware control |

**Recommendation**: Consider JACK for precise timing requirements

### 4. CPU Performance Analysis
**Problem**: Loopback runs every second (excessive for subwoofer)
**Optimization**:
```bash
# CPU usage monitoring
top -p $(pgrep pipewire)
htop -p $(pgrep -d, pipewire)

# Process-specific monitoring
ps aux | grep pipewire
cat /proc/$(pgrep pipewire)/status | grep -E "(VmRSS|VmSize)"
```

## Comprehensive Observability Tools

### 1. Real-Time Audio Monitoring
```bash
#!/bin/bash
# audio_monitor.sh - Real-time audio system monitoring

echo "=== Audio System Observability ==="
echo "Timestamp: $(date)"
echo

echo "=== Active Sinks ==="
pactl list sinks short | grep RUNNING
echo

echo "=== Active Sources ==="
pactl list sources short | grep RUNNING
echo

echo "=== Loopback Modules ==="
pactl list modules short | grep loopback
echo

echo "=== Sink Inputs ==="
pactl list sink-inputs short
echo

echo "=== Source Outputs ==="
pactl list source-outputs short
echo

echo "=== PipeWire Performance ==="
pw-top --once 2>/dev/null || echo "pw-top not available"
echo

echo "=== System Resources ==="
ps aux | grep -E "(pipewire|pulseaudio)" | grep -v grep
echo

echo "=== Audio Latency ==="
pactl list sinks | grep -A 5 -B 5 "Latency:"
echo

echo "=== Buffer Status ==="
pactl list sink-inputs | grep -A 10 -B 5 "Buffer Latency:"
echo
```

### 2. Frame Drop Detection
```bash
#!/bin/bash
# frame_drop_detector.sh - Detect audio frame drops

LOG_FILE="frame_drops.log"
echo "=== Frame Drop Detection ===" > "$LOG_FILE"

# Monitor PipeWire logs for frame drops
journalctl --user -u pipewire -f | while read line; do
    if echo "$line" | grep -q -E "(underrun|overrun|drop|error)"; then
        echo "[$(date)] FRAME DROP DETECTED: $line" | tee -a "$LOG_FILE"
    fi
done
```

### 3. Loopback Connection Validator
```bash
#!/bin/bash
# loopback_validator.sh - Validate loopback connections

echo "=== Loopback Connection Validation ==="

# Check all loopback modules
pactl list modules short | grep loopback | while read module_id rest; do
    echo "Module $module_id: $rest"

    # Get detailed module info
    pactl list modules | grep -A 20 "Module #$module_id" | grep -E "(source|sink|latency)"
    echo
done

# Check actual connections
echo "=== Actual Connections ==="
pactl list sink-inputs | grep -A 10 -B 5 "loopback"
pactl list source-outputs | grep -A 10 -B 5 "loopback"
```

### 4. Performance Profiler
```bash
#!/bin/bash
# audio_performance_profiler.sh - Profile audio system performance

echo "=== Audio Performance Profile ==="
echo "Timestamp: $(date)"
echo

echo "=== CPU Usage ==="
ps aux | grep -E "(pipewire|pulseaudio)" | grep -v grep | awk '{print $3, $11}'
echo

echo "=== Memory Usage ==="
ps aux | grep -E "(pipewire|pulseaudio)" | grep -v grep | awk '{print $4, $11}'
echo

echo "=== Buffer Statistics ==="
pactl list sinks | grep -A 5 -B 5 "Buffer Latency:"
echo

echo "=== Active Streams ==="
pactl list sink-inputs short | wc -l | xargs echo "Active sink inputs:"
pactl list source-outputs short | wc -l | xargs echo "Active source outputs:"
echo
```

### 5. Sound Server Comparison Tool
```bash
#!/bin/bash
# sound_server_analyzer.sh - Analyze sound server options

echo "=== Sound Server Analysis ==="
echo

echo "=== Current Server: PipeWire ==="
systemctl --user status pipewire
echo

echo "=== JACK Availability ==="
which jackd && echo "JACK available" || echo "JACK not installed"
echo

echo "=== PulseAudio Status ==="
systemctl --user status pulseaudio 2>/dev/null || echo "PulseAudio not running"
echo

echo "=== ALSA Status ==="
lsmod | grep snd
echo

echo "=== Performance Comparison ==="
echo "PipeWire: $(ps aux | grep pipewire | grep -v grep | awk '{print $3}')% CPU"
echo "PulseAudio: $(ps aux | grep pulseaudio | grep -v grep | awk '{print $3}')% CPU"
```

## Advanced Debugging Tools

### 1. Timecode Drift Analysis
```bash
#!/bin/bash
# timecode_drift_analyzer.sh - Analyze timecode drift

echo "=== Timecode Drift Analysis ==="

# Monitor latency changes over time
for i in {1..10}; do
    echo "Sample $i: $(pactl list sinks | grep 'Latency:' | head -1)"
    sleep 1
done
```

### 2. Buffer Underrun Detector
```bash
#!/bin/bash
# buffer_underrun_detector.sh - Detect buffer underruns

echo "=== Buffer Underrun Detection ==="

# Monitor for underrun events
journalctl --user -u pipewire -f | grep -i underrun | while read line; do
    echo "[$(date)] UNDERRUN: $line"
    # Log to file for analysis
    echo "[$(date)] UNDERRUN: $line" >> underrun_events.log
done
```

### 3. Cross-Over Implementation
```bash
#!/bin/bash
# crossover_implementation.sh - Implement audio crossover

FREQUENCY=80  # Hz - typical subwoofer crossover

echo "=== Audio Crossover Implementation ==="

# Create low-pass filter for subwoofer
pactl load-module module-ladspa-sink sink_name=subwoofer-lpf \
    plugin=lowpass_1200 label=lowpass_1200 control=0,$FREQUENCY

# Create high-pass filter for main speakers
pactl load-module module-ladspa-sink sink_name=main-hpf \
    plugin=highpass_1200 label=highpass_1200 control=0,$FREQUENCY

echo "Crossover implemented at ${FREQUENCY}Hz"
```

## Observability Dashboard

### Real-Time Monitoring Commands
```bash
# Continuous monitoring
watch -n 1 'pactl list sinks short | grep RUNNING'

# Performance monitoring
watch -n 1 'ps aux | grep pipewire | grep -v grep'

# Frame drop monitoring
journalctl --user -u pipewire -f | grep -E "(error|warning|drop)"
```

### Log Analysis
```bash
# Analyze frame drops
grep "FRAME DROP" frame_drops.log | tail -20

# Analyze underruns
grep "UNDERRUN" underrun_events.log | tail -20

# Performance trends
ps aux | grep pipewire | awk '{print $3}' | tail -100 > cpu_usage.log
```

## Recommendations

### 1. Immediate Actions
- **Implement frame drop detection**
- **Monitor loopback connections**
- **Profile CPU usage**
- **Log all audio events**

### 2. Sound Server Evaluation
- **Test JACK for precise timing**
- **Compare performance metrics**
- **Evaluate stability vs. precision**

### 3. Optimization
- **Reduce loopback polling frequency**
- **Implement crossover filtering**
- **Optimize buffer sizes**

### 4. Debugging
- **Trace frame drops to source**
- **Analyze timecode drift**
- **Monitor buffer underruns**

This observability framework will help identify the root causes of the distortion and optimize the audio system for better performance.
