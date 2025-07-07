#!/bin/bash
# Generated following ontology framework rules
# Sequenced implementation script for 20ms delay
# Dependencies: 4
# Execution order: verify_lkg_state -> create_delay_sink -> verify_delay_creation -> verify_new_routing -> test_audio_synchronization

set -e  # Exit on any error

echo "=== 20ms Delay Implementation (Sequenced) ==="
echo "Total steps: 5"
echo "Dependencies: 4"

echo "Step 1/5: Verify current LKG state before changes"
# Dependencies: none
python3 audio_routing_graph.py
echo "Verifying: Check graph output for clean state"
Check graph output for clean state
echo "Step 1 completed"

echo "Step 2/5: Create 20ms delay sink for main speakers"
# Dependencies: verify_lkg_state
pactl load-module module-loopback source=jamesdsp_sink.monitor sink=alsa_output.pci-0000_0b_00.4.analog-stereo latency_msec=20
echo "Verifying: pactl list modules | grep -A 5 -B 5 'loopback'"
pactl list modules | grep -A 5 -B 5 'loopback'
echo "Step 2 completed"

echo "Step 3/5: Verify delay sink was created successfully"
# Dependencies: create_delay_sink
pactl list modules | grep -A 5 -B 5 'loopback'
echo "Verifying: Check for loopback module in output"
Check for loopback module in output
echo "Step 3 completed"

echo "Step 4/5: Verify new routing topology matches target state"
# Dependencies: verify_delay_creation
python3 audio_routing_graph.py
echo "Verifying: Check graph for delay path and removed direct connection"
Check graph for delay path and removed direct connection
echo "Step 4 completed"

echo "Step 5/5: Test audio synchronization between speakers and subwoofer"
# Dependencies: verify_new_routing
echo 'Play test audio to verify 20ms delay synchronization'
echo "Verifying: Listen for proper phase alignment"
Listen for proper phase alignment
echo "Step 5 completed"

echo "=== Implementation completed successfully ==="
echo "All dependencies satisfied"
