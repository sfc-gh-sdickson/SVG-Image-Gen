#!/bin/bash

# install_audio_tools.sh - Install professional audio visualization tools
# Enhances audio system monitoring and editing capabilities

echo "=== Installing Professional Audio Tools ==="

# Professional JACK tools
echo "Installing JACK audio tools..."
sudo apt update
sudo apt install -y \
    patchage \
    jack-rack \
    jack-keyboard \
    jack-capture \
    jack-transport \
    jack-osc \
    jack-smf-utils \
    jack-midi-clock \
    jack-tools

# PipeWire visualization tools
echo "Installing PipeWire tools..."
sudo apt install -y \
    pipewire-utils \
    helvum \
    qpwgraph

# Audio analysis tools
echo "Installing audio analysis tools..."
sudo apt install -y \
    audacity \
    audacity-plugins \
    sox \
    sox-doc \
    libsox-fmt-all \
    ffmpeg \
    ffmpeg-doc

# Professional audio tools
echo "Installing professional audio tools..."
sudo apt install -y \
    ardour \
    ardour-plugins \
    hydrogen \
    lmms \
    qtractor \
    rosegarden \
    musescore

# Audio monitoring tools
echo "Installing monitoring tools..."
sudo apt install -y \
    gtk3-engines-breeze \
    pavucontrol \
    pulseaudio-utils \
    alsa-utils

echo "=== Installation Complete ==="
echo
echo "Available tools:"
echo "1. QJackCtl - JACK patchbay (already running)"
echo "2. Patchage - Alternative JACK patchbay"
echo "3. Helvum - PipeWire patchbay"
echo "4. qpwgraph - PipeWire graph editor"
echo "5. pw-top - PipeWire topology viewer"
echo "6. Audacity - Audio editing and analysis"
echo "7. Ardour - Professional DAW"
echo "8. pavucontrol - PulseAudio control"
echo
echo "To start visualization tools:"
echo "qjackctl &          # JACK patchbay"
echo "patchage &          # Alternative patchbay"
echo "helvum &            # PipeWire patchbay"
echo "qpwgraph &          # PipeWire graph editor"
echo "pw-top &            # PipeWire topology"
echo "pavucontrol &       # Audio control panel"
