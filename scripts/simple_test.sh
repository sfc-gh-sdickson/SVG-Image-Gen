#!/bin/bash

# Simple test for volume control
echo "=== Simple Volume Control Test ==="

# Get device IDs directly
echo "Getting device IDs..."
device_ids=$(pw-cli list-objects | grep -A 10 "media.class.*Audio/Sink" | grep "id:" | cut -d: -f2 | tr '\n' ' ')

echo "Found device IDs: $device_ids"

# Test volume changes
echo ""
echo "=== Testing Volume Changes ==="

for volume in 0.2 0.5 0.8 0.3; do
    echo "Setting volume to $volume..."

    success_count=0
    for device_id in $device_ids; do
        # Get device name
        device_info=$(pw-cli info "$device_id" 2>/dev/null)
        device_name=$(echo "$device_info" | grep "node.name" | cut -d'"' -f2)

        if [[ -n "$device_name" ]]; then
            echo "  Testing: $device_name (ID: $device_id)"

            # Set volume
            if pw-cli set-volume "$device_id" "$volume" 2>/dev/null; then
                echo "    ✓ Set to $volume"
                success_count=$((success_count + 1))
            else
                echo "    ✗ Failed"
            fi
        fi
    done

    echo "Successfully set volume on $success_count devices"
    echo ""
    sleep 2
done

echo "=== Test Complete ==="
echo "If you heard volume changes, the system is working!"
