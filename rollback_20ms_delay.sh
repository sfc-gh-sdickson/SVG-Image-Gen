#!/bin/bash
# Generated following ontology framework rules
# Rollback script for 20ms delay implementation
# This script returns to LKG state

set -e  # Exit on any error

# Rollback Sequence for 20ms Delay Implementation

# Step 1: Find delay module ID
DELAY_MODULE_ID=$(pactl list modules | grep -B 2 'loopback' | grep 'Module #' | tail -1 | awk '{print $2}')
echo "Found delay module ID: $DELAY_MODULE_ID"

# Step 2: Unload delay module
if [ ! -z "$DELAY_MODULE_ID" ]; then
    pactl unload-module $DELAY_MODULE_ID
    echo "Delay module unloaded"
else
    echo "No delay module found"
fi

# Step 3: Verify return to LKG state
python3 audio_routing_graph.py

# Step 4: Test audio (should be back to original state)
echo "Audio should now be back to original state"
