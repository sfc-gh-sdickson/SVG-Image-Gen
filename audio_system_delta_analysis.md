# Audio System Delta Analysis: LKG → Target State

## Current State (LKG - Last Known Good)
- **JamesDSP Sink (91)** routes directly to **KM Speakers (69)** and **Fosi Subwoofer (146)**
- No delay processing in the main speakers path
- Subwoofer has 1.9ms compensation already applied
- Clean routing with no loops

## Target State
- **JamesDSP Sink (91)** routes to **20ms Delay Sink (TBD)** and **Fosi Subwoofer (146)**
- **20ms Delay Sink** routes to **KM Speakers (69)**
- Main speakers delayed by 20ms to sync with subwoofer
- Subwoofer gets direct connection (no additional delay)

## Required Changes

### 1. Create 20ms Delay Sink
```bash
# Create delay sink with 20ms latency
pactl load-module module-loopback \
    source=jamesdsp_sink.monitor \
    sink=alsa_output.pci-0000_0b_00.4.analog-stereo \
    latency_msec=20
```

### 2. Update Routing
- **Current**: JamesDSP → KM Speakers (direct)
- **Target**: JamesDSP → 20ms Delay → KM Speakers

### 3. Verify No Loops
- Ensure delay sink doesn't create feedback loops
- Maintain clean routing topology

## Implementation Steps

### Step 1: Verify Current State
```bash
# Confirm we're in LKG state
python3 audio_routing_graph.py
```

### Step 2: Create Delay Sink
```bash
# Create 20ms delay sink
pactl load-module module-loopback \
    source=jamesdsp_sink.monitor \
    sink=alsa_output.pci-0000_0b_00.4.analog-stereo \
    latency_msec=20
```

### Step 3: Verify Target State
```bash
# Confirm routing matches target model
python3 audio_routing_graph.py
```

### Step 4: Test Audio Synchronization
- Play test audio with bass content
- Verify main speakers and subwoofer are synchronized
- Check for phase alignment improvement

## Risk Assessment

### Low Risk
- Current state is stable (LKG)
- Delay sink is isolated from subwoofer path
- No feedback loops in target configuration

### Medium Risk
- 20ms delay might be too much or too little
- Need to test and potentially adjust delay value
- May need fine-tuning based on listening tests

### Mitigation
- Start with 20ms delay (user's estimate)
- Test with various audio content
- Adjust delay if needed (15-25ms range)
- Document final optimal delay value

## Success Criteria

1. **Routing**: JamesDSP → Delay → KM Speakers (main path)
2. **Direct**: JamesDSP → Fosi Subwoofer (subwoofer path)
3. **No Loops**: Clean routing topology maintained
4. **Synchronization**: Main speakers and subwoofer properly aligned
5. **Audio Quality**: No distortion or artifacts introduced

## Rollback Plan

If issues occur:
```bash
# Remove delay sink
pactl unload-module <delay_module_id>

# Verify return to LKG state
python3 audio_routing_graph.py
```

## Documentation Updates

After successful implementation:
- Update ontology with actual delay sink device ID
- Update PlantUML diagrams with final configuration
- Document optimal delay value and testing results
- Update research spore with successful implementation

---

**Status**: Ready for implementation
**Priority**: High (user requested 20ms delay)
**Dependencies**: Current LKG state confirmed
**Estimated Time**: 5-10 minutes for implementation + testing
