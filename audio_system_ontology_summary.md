# Audio System Ontology and UML Visualization

## Overview
This document describes the audio system ontology built from the current PipeWire configuration snapshot, along with a PlantUML visualization of the network topology.

## Ontology Structure

### Core Classes
- **AudioDevice**: Base class for all audio devices
- **AudioSink**: Audio output devices (hardware or virtual)
- **AudioSource**: Audio input devices
- **VirtualSink**: Software-created audio sinks
- **HardwareSink**: Physical audio output devices
- **AudioConnection**: Connections between devices
- **ProcessingChain**: Groups of devices that process audio together

### Key Relationships
- `hasConnection`: Links devices to their connections
- `hasInput/hasOutput`: Device input/output relationships
- `processesAudio`: Processing relationships between devices
- `belongsToChain`: Device membership in processing chains
- `hasSource/hasTarget`: Connection source and target devices

## Device Instances

### Hardware Sinks (6 devices)
1. **KM Audio** (ID: 69) - USB audio, 100% volume, 48000Hz
2. **Fosi BT30D** (ID: 209) - Bluetooth subwoofer, 32% volume, 48000Hz
3. **Thunderbolt Display** (ID: 70) - USB audio, 34% volume, 44100Hz
4. **PCM2912A Codec** (ID: 71) - USB audio, 36% volume, 44100Hz
5. **Built-in Audio** (ID: 72) - PCI audio, 36% volume, 44100Hz (IDLE)
6. **Tonga HDMI** (ID: 270629) - HDMI audio, 32% volume, 44100Hz

### Virtual Sinks (3 devices)
1. **JamesDSP Sink** (ID: 273555) - DSP processing sink, 30% volume, 48000Hz
2. **JamesDSP Delay Sink** (ID: 274119) - Delay processing sink, 100% volume, 44100Hz
3. **Combined Output** (ID: 919) - Combined sink, 33% volume, 48000Hz

## Processing Chains

### JamesDSP Processing Chain
- **Path**: Applications → JamesDSP Sink → Delay Sink → KM Audio
- **Purpose**: DSP processing for main speakers
- **Devices**: JamesDSP Sink, JamesDSP Delay Sink, KM Audio
- **Applications**: Firefox, Chromium

### Combined Output Chain
- **Path**: Combined Sink → KM Audio + Fosi BT30D
- **Purpose**: Direct output bypassing JamesDSP
- **Devices**: Combined Output, KM Audio, Fosi BT30D
- **Key Feature**: Fosi subwoofer separated from DSP processing

## Key Configuration Features

### Fosi Subwoofer Separation
- **Status**: Successfully separated from JamesDSP processing
- **Routing**: Direct connection via combined sink
- **Benefit**: Avoids DSP processing artifacts on subwoofer
- **Volume**: Independently controlled (32%)

### Dual Output Architecture
- **Main Speakers**: Processed through JamesDSP chain
- **Subwoofer**: Direct output via combined sink
- **Simultaneous**: Both chains active simultaneously
- **Volume Balance**: KM Audio 100%, Fosi 32%

### System State
- **QJackCtl**: Active (for additional routing)
- **Volume Sync Daemon**: Stopped (needs restart)
- **PipeWire**: Running
- **JamesDSP**: Running

## PlantUML Diagram Features

### Color Coding
- **Blue (#E8F4FD)**: Hardware devices
- **Yellow (#FFF2CC)**: Virtual sinks
- **Green (#D5E8D4)**: Applications
- **Red (#F8CECC)**: Processing chains

### Connection Types
- **Solid arrows**: Direct audio connections
- **Dotted arrows**: Membership relationships
- **Labels**: Connection descriptions and data flow

### Information Display
- **Device IDs**: Unique PipeWire identifiers
- **Volume levels**: Current volume percentages
- **Sample rates**: Device sample rates (44100Hz/48000Hz)
- **States**: RUNNING/IDLE status

## Ontology Benefits

### Query Capabilities
The ontology enables queries such as:
- "Which devices are in the JamesDSP processing chain?"
- "What is the volume level of the Fosi subwoofer?"
- "Which applications are connected to JamesDSP?"
- "What is the sample rate of each device?"

### Analysis Capabilities
- **Device relationships**: Track audio flow through the system
- **Processing chains**: Understand DSP processing paths
- **Volume management**: Monitor volume levels across devices
- **State monitoring**: Track device states and system health

### Documentation
- **Current configuration**: Snapshot of working audio setup
- **Connection topology**: Visual representation of audio routing
- **Device attributes**: Complete device specifications
- **System state**: Current operational status

## Files Created

1. **audio_system_ontology.ttl**: Turtle RDF ontology with device instances and relationships
2. **audio_system_uml.puml**: PlantUML diagram for network visualization
3. **audio_system_ontology_summary.md**: This summary document

## Usage

### Viewing the Diagram
```bash
# Install PlantUML (if not already installed)
sudo apt install plantuml

# Generate PNG from PlantUML
plantuml audio_system_uml.puml
```

### Querying the Ontology
```bash
# Using rdflib or similar RDF tools
python -c "
import rdflib
g = rdflib.Graph()
g.parse('audio_system_ontology.ttl', format='turtle')
# Query examples...
"
```

## Future Enhancements

### Potential Extensions
- **Latency tracking**: Add latency measurements to connections
- **Quality metrics**: Include audio quality measurements
- **Historical tracking**: Track configuration changes over time
- **Automated monitoring**: Real-time ontology updates

### Integration Possibilities
- **Monitoring systems**: Integrate with audio monitoring tools
- **Configuration management**: Version control for audio configurations
- **Troubleshooting**: Automated diagnosis using ontology queries
- **Documentation**: Auto-generate system documentation

This ontology provides a comprehensive model of the audio system that can be used for analysis, documentation, and automated management of the complex multi-device audio setup.
