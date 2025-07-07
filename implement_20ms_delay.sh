#!/bin/bash
# Generated following ontology framework rules
# Implementation script for 20ms delay on main speakers
# This script implements the target state from LKG state

set -e  # Exit on any error

# Step 1: Verify current LKG state
python3 audio_routing_graph.py

# Step 2: Create 20ms delay sink
DELAY_MODULE_ID=$(pactl load-module module-loopback \
    source=jamesdsp_sink.monitor \
    sink=alsa_output.pci-0000_0b_00.4.analog-stereo \
    latency_msec=20)
echo "Delay module ID: $DELAY_MODULE_ID"

# Step 3: Verify delay sink creation
pactl list modules | grep -A 5 -B 5 'loopback'

# Step 4: Verify new routing topology
python3 audio_routing_graph.py

# Step 5: Test audio synchronization
echo "Play test audio to verify 20ms delay synchronization"

# Step 6: Rollback command (if needed)
echo "To rollback: pactl unload-module $DELAY_MODULE_ID"
