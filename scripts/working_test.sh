#!/bin/bash

# Working test for volume control
echo "=== Working Volume Control Test ==="

# Get the actual device structure
echo "Analyzing PipeWire device structure..."

# Find the actual sink nodes (not just the client interfaces)
sink_nodes=$(pw-cli list-objects | grep -B 10 "media.class.*Audio/Sink" | grep "id" | head -10 | grep -o 'id [0-9]*' | awk '{print $2}')

echo "Found sink nodes: $sink_nodes"

# Test volume on each sink
echo ""
echo "=== Testing Volume Control ==="

for volume in 0.3 0.6 0.9 0.5; do
    echo "Setting volume to $volume..."

    success_count=0
    for node_id in $sink_nodes; do
        # Get node info
        node_info=$(pw-cli info "$node_id" 2>/dev/null)
        node_name=$(echo "$node_info" | grep "node.name" | cut -d'"' -f2)

        if [[ -n "$node_name" ]]; then
            echo "  Testing: $node_name (ID: $node_id)"

            # Try to set volume
            if pw-cli set-volume "$node_id" "$volume" 2>/dev/null; then
                echo "    ✓ Set to $volume"
                success_count=$((success_count + 1))
            else
                echo "    ✗ Failed to set volume"
            fi
        fi
    done

    echo "Successfully set volume on $success_count devices"
    echo ""
    sleep 2
done

echo "=== Test Complete ==="
echo "If you heard volume changes, the system is working!"
