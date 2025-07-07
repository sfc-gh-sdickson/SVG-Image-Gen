#!/usr/bin/env python3
"""
Test script for volume control across all audio devices
"""

import json
import subprocess
import sys
import time


def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


def get_audio_devices():
    """Get all audio sink devices"""
    stdout, stderr, code = run_command(
        "pw-cli list-objects | grep -A 10 'media.class.*Audio/Sink' | grep -E 'id:|node.name'"
    )
    if code != 0:
        print(f"Error getting devices: {stderr}")
        return []

    devices = []
    lines = stdout.split("\n")
    current_id = None

    for line in lines:
        if "id:" in line:
            current_id = line.split("id:")[1].strip().split(",")[0]
        elif "node.name" in line and current_id:
            name = line.split('node.name = "')[1].split('"')[0]
            devices.append({"id": current_id, "name": name})
            current_id = None

    return devices


def get_device_volume(device_id):
    """Get volume for a specific device"""
    stdout, stderr, code = run_command(f"pw-cli get-volume {device_id}")
    if code == 0 and stdout:
        try:
            # Extract volume value
            volume = stdout.split()[-1] if stdout.split() else "0"
            return float(volume)
        except:
            return 0.0
    return 0.0


def set_device_volume(device_id, volume):
    """Set volume for a specific device"""
    stdout, stderr, code = run_command(f"pw-cli set-volume {device_id} {volume}")
    return code == 0


def test_volume_control():
    """Test volume control on all devices"""
    print("=== Volume Control Test ===")

    # Get all audio devices
    devices = get_audio_devices()
    if not devices:
        print("No audio devices found!")
        return False

    print(f"Found {len(devices)} audio devices:")
    for device in devices:
        print(f"  {device['name']} (ID: {device['id']})")

    print("\n=== Testing Volume Changes ===")

    # Test volume levels
    test_volumes = [0.2, 0.5, 0.8, 0.3]

    for volume in test_volumes:
        print(f"\nSetting volume to {volume}...")

        # Set volume on all devices
        success_count = 0
        for device in devices:
            if set_device_volume(device["id"], volume):
                success_count += 1
                print(f"  ✓ {device['name']}: {volume}")
            else:
                print(f"  ✗ {device['name']}: failed")

        print(f"Successfully set volume on {success_count}/{len(devices)} devices")

        # Wait and verify
        time.sleep(1)

        # Verify volumes
        print("Verifying volumes:")
        for device in devices:
            actual_volume = get_device_volume(device["id"])
            print(f"  {device['name']}: {actual_volume:.2f}")

        time.sleep(1)

    print("\n=== Test Complete ===")
    return True


def test_volume_monitoring():
    """Test if volume monitoring is working"""
    print("=== Volume Monitoring Test ===")

    # Check if monitoring script is running
    stdout, stderr, code = run_command("ps aux | grep volume_monitor | grep -v grep")
    if code == 0:
        print("✓ Volume monitoring script is running")
        print(f"Process: {stdout}")
    else:
        print("✗ Volume monitoring script is not running")

    # Check PID files
    pid_files = [
        "/tmp/simple_volume_control.pid",
        "/tmp/direct_volume_control.pid",
        "/tmp/unified_volume.pid",
    ]
    for pid_file in pid_files:
        stdout, stderr, code = run_command(
            f"cat {pid_file} 2>/dev/null || echo 'not found'"
        )
        if stdout != "not found":
            print(f"✓ PID file {pid_file}: {stdout}")
        else:
            print(f"✗ PID file {pid_file}: not found")


def main():
    """Main test function"""
    print("Audio Volume Control Test")
    print("=" * 40)

    # Test 1: Check devices
    devices = get_audio_devices()
    print(f"Found {len(devices)} audio devices")

    # Test 2: Volume control
    if test_volume_control():
        print("✓ Volume control test passed")
    else:
        print("✗ Volume control test failed")

    # Test 3: Monitoring
    test_volume_monitoring()

    print("\n=== Summary ===")
    print("If you heard volume changes during the test, the system is working.")
    print("If not, there may be an issue with the volume control setup.")


if __name__ == "__main__":
    main()
