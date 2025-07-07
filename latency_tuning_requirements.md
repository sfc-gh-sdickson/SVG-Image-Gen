# Latency Tuning Requirements

## Current State Analysis

### Manual Tuning Process (Inefficient)
- **Method**: Manual trial-and-error with script modifications
- **Process**: Edit script → Apply → Test → Remove → Repeat
- **Time**: 5-10 minutes per iteration
- **Precision**: Limited by manual script editing
- **User Fatigue**: Tedious and error-prone

### Achieved Results
- **Optimal Value**: 1.9ms delay compensation
- **Precision**: User can detect 0.1ms differences
- **Perceptual Threshold**: Beyond user's ability to hear differences
- **Current Method**: Manual script editing and testing

## Problems with Current Approach

### 1. Manual Script Editing
```bash
# Current process:
vim scripts/jamesdsp_latency_compensation.sh  # Edit DELAY_MS
scripts/jamesdsp_latency_compensation.sh apply
# Listen and test
scripts/jamesdsp_latency_compensation.sh remove
# Repeat for each value
```

### 2. No Real-Time Adjustment
- Cannot adjust latency while audio is playing
- Must stop audio, modify script, restart
- No immediate feedback

### 3. Limited Precision
- Script only accepts integer milliseconds
- No sub-millisecond precision
- No automated measurement

### 4. No Calibration Tools
- No automated latency measurement
- No phase coherence testing
- No frequency-specific testing

## Required Solutions

### 1. Real-Time Latency Adjustment
**Requirements:**
- Adjustable delay while audio is playing
- Immediate feedback on changes
- No script editing required
- GUI or CLI interface

**Proposed Implementation:**
```bash
# Real-time adjustment
latency-tuner --delay 1.9 --live
latency-tuner --adjust +0.1  # Increment by 0.1ms
latency-tuner --adjust -0.05 # Decrement by 0.05ms
latency-tuner --fine-tune    # Interactive mode
```

### 2. Automated Calibration
**Requirements:**
- Generate test tones
- Measure phase differences
- Calculate optimal compensation
- Validate results

**Proposed Implementation:**
```bash
# Automated calibration
latency-calibrator --test-tone 1000Hz
latency-calibrator --measure-phase
latency-calibrator --auto-tune
latency-calibrator --validate
```

### 3. Sub-Millisecond Precision
**Requirements:**
- 0.1ms precision (current user threshold)
- 0.01ms granularity for future testing
- Microsecond-level adjustments

**Technical Challenges:**
- PipeWire delay module limitations
- Audio buffer constraints
- Real-time processing requirements

### 4. Measurement and Validation
**Requirements:**
- Phase coherence measurement
- Frequency response testing
- Distortion detection
- Performance metrics

**Proposed Tools:**
```bash
# Measurement tools
phase-analyzer --input main --input subwoofer
frequency-analyzer --range 20-20000Hz
distortion-detector --threshold -60dB
latency-meter --precision 0.1ms
```

## Proposed Architecture

### 1. Latency Tuner Application
```python
class LatencyTuner:
    def __init__(self):
        self.current_delay = 1.9
        self.precision = 0.1
        self.audio_active = False

    def adjust_delay(self, delta_ms):
        """Real-time delay adjustment"""
        pass

    def fine_tune(self):
        """Interactive fine-tuning mode"""
        pass

    def measure_phase(self):
        """Measure phase coherence"""
        pass
```

### 2. Calibration Engine
```python
class LatencyCalibrator:
    def generate_test_tone(self, frequency, duration):
        """Generate calibration test tone"""
        pass

    def measure_latency(self):
        """Measure actual latency differences"""
        pass

    def calculate_optimal_delay(self):
        """Calculate optimal compensation"""
        pass

    def validate_results(self):
        """Validate calibration results"""
        pass
```

### 3. Measurement Tools
```python
class AudioAnalyzer:
    def measure_phase_coherence(self):
        """Measure phase alignment between outputs"""
        pass

    def detect_distortion(self):
        """Detect audio artifacts"""
        pass

    def frequency_response(self):
        """Measure frequency response"""
        pass
```

## Implementation Priority

### Phase 1: Real-Time Adjustment (High Priority)
- Interactive CLI tool for delay adjustment
- Real-time feedback
- No script editing required
- Immediate testing capability

### Phase 2: Automated Calibration (Medium Priority)
- Test tone generation
- Phase measurement
- Optimal delay calculation
- Validation tools

### Phase 3: Advanced Features (Low Priority)
- Sub-millisecond precision
- Frequency-specific compensation
- Machine learning optimization
- Automated tuning

## Technical Requirements

### 1. PipeWire Integration
- Direct module management
- Real-time parameter adjustment
- Audio stream monitoring
- Performance optimization

### 2. Audio Analysis
- FFT for phase measurement
- Cross-correlation for latency
- Distortion analysis
- Frequency response measurement

### 3. User Interface
- CLI for automation
- GUI for interactive use
- Real-time visualization
- Immediate feedback

## Success Criteria

### 1. Efficiency
- Reduce tuning time from 10 minutes to 2 minutes
- Real-time adjustment capability
- Immediate feedback on changes

### 2. Precision
- 0.1ms precision (current user threshold)
- Sub-millisecond capability
- Automated measurement

### 3. Usability
- No script editing required
- Interactive fine-tuning
- Automated calibration
- Validation tools

### 4. Reliability
- Consistent results
- Error handling
- Performance monitoring
- Backup/restore capability

## Current Limitations

### 1. PipeWire Constraints
- Module-based delay implementation
- Limited real-time adjustment
- Buffer size constraints
- Performance overhead

### 2. Audio Hardware
- Bluetooth latency variability
- Buffer pre-reading behavior
- Codec-specific limitations
- Hardware-specific optimizations

### 3. Measurement Precision
- User perceptual threshold: 0.1ms
- Current tools: 1ms precision
- Need: 0.01ms precision
- Challenge: Hardware limitations

## Next Steps

### Immediate (This Week)
1. Document current manual process
2. Create real-time adjustment prototype
3. Test PipeWire module limitations
4. Design CLI interface

### Short Term (Next Month)
1. Implement real-time tuner
2. Add measurement capabilities
3. Create calibration tools
4. Validate with user testing

### Long Term (Next Quarter)
1. Automated calibration
2. Advanced measurement tools
3. Machine learning optimization
4. Production deployment

## Conclusion

The current manual tuning process is inefficient and error-prone. A real-time latency adjustment tool with automated calibration capabilities would significantly improve the user experience and enable more precise optimization of audio system latency compensation.

**Priority**: Implement real-time adjustment capability to eliminate manual script editing and enable immediate feedback during tuning.
