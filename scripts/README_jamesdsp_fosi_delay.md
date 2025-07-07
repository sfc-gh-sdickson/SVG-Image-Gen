# JamesDSP Fosi Audio BT30D Delay Script

This script configures JamesDSP to delay all audio output except for the Fosi Audio BT30D by 2ms to compensate for Bluetooth latency differences.

## Prerequisites

### 1. Install JamesDSP

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install jamesdsp
```

**Arch Linux:**
```bash
sudo pacman -S jamesdsp
```

**Manual installation (if not available in repos):**
```bash
# Clone the repository
git clone https://github.com/Audio4Linux/JDSP4Linux.git
cd JDSP4Linux

# Build and install
mkdir build && cd build
cmake ..
make
sudo make install
```

### 2. Ensure PipeWire is running
```bash
# Start PipeWire services
systemctl --user start pipewire pipewire-pulse

# Check if it's running
pw-cli info
```

### 3. Install jq (for JSON processing)
```bash
# Ubuntu/Debian
sudo apt install jq

# Arch Linux
sudo pacman -S jq
```

## Usage

### Basic Usage

1. **Start the delay configuration:**
   ```bash
   ./scripts/jamesdsp_fosi_bt30d_delay.sh start
   ```

2. **Check status:**
   ```bash
   ./scripts/jamesdsp_fosi_bt30d_delay.sh status
   ```

3. **Stop JamesDSP:**
   ```bash
   ./scripts/jamesdsp_fosi_bt30d_delay.sh stop
   ```

### Available Commands

- `start` - Start JamesDSP with delay configuration (default)
- `stop` - Stop JamesDSP
- `restart` - Restart JamesDSP
- `status` - Show current status
- `devices` - List available audio devices
- `help` - Show help message

### Examples

**List your audio devices to verify Fosi Audio BT30D is detected:**
```bash
./scripts/jamesdsp_fosi_bt30d_delay.sh devices
```

**Start with automatic device detection:**
```bash
./scripts/jamesdsp_fosi_bt30d_delay.sh start
```

**Check if it's working:**
```bash
./scripts/jamesdsp_fosi_bt30d_delay.sh status
```

## Configuration

The script automatically:
- Detects your Fosi Audio BT30D device
- Applies a 2ms delay to all other audio devices
- Leaves the Fosi Audio BT30D without delay
- Creates configuration in `~/.config/JamesDSP/config.json`

## Troubleshooting

### JamesDSP not found
If you get an error that JamesDSP is not installed:
```bash
# Check if it's in your PATH
which jamesdsp

# If not found, you may need to install it manually
# Follow the manual installation instructions above
```

### PipeWire not running
```bash
# Start PipeWire services
systemctl --user start pipewire pipewire-pulse

# Check if it's running
pw-cli info
```

### Fosi Audio BT30D not detected
1. Make sure your device is connected via Bluetooth
2. Check if it appears in the device list:
   ```bash
   ./scripts/jamesdsp_fosi_bt30d_delay.sh devices
   ```
3. If it's not listed, try reconnecting the device

### Audio issues
If you experience audio problems:
1. Stop JamesDSP: `./scripts/jamesdsp_fosi_bt30d_delay.sh stop`
2. Restart PipeWire: `systemctl --user restart pipewire pipewire-pulse`
3. Try starting again: `./scripts/jamesdsp_fosi_bt30d_delay.sh start`

## How It Works

1. **Device Detection**: The script uses PipeWire to detect your Fosi Audio BT30D
2. **Configuration**: Creates a JamesDSP configuration that applies different processing to different devices
3. **Delay Application**: Applies a 2ms delay to all devices except the Fosi Audio BT30D
4. **Process Management**: Manages JamesDSP as a background process with PID tracking

## Customization

To modify the delay time, edit the script and change the `DELAY_MS` variable:
```bash
# In the script, change this line:
DELAY_MS=2
```

## Files Created

- `~/.config/JamesDSP/config.json` - JamesDSP configuration
- `/tmp/jamesdsp_fosi_delay.pid` - Process ID tracking

## Notes

- The script automatically kills any existing JamesDSP processes before starting
- If the Fosi Audio BT30D is not detected, the script will apply delay to all devices
- The configuration is persistent and will be reused on restart
- The script includes comprehensive error checking and logging
