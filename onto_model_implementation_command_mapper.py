# Generated following ontology framework rules
"""
Implementation Command Mapper for Audio System Graph Differences
Maps each semantic difference to specific PipeWire/PulseAudio commands.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple


class CommandType(Enum):
    """Types of implementation commands"""

    PACTL_LOAD_MODULE = "pactl_load_module"
    PACTL_UNLOAD_MODULE = "pactl_unload_module"
    PACTL_MOVE_SINK_INPUT = "pactl_move_sink_input"
    PACTL_SET_SINK_VOLUME = "pactl_set_sink_volume"
    PACTL_SET_SINK_MUTE = "pactl_set_sink_mute"
    PW_LINK = "pw_link"
    PW_UNLINK = "pw_unlink"
    VERIFICATION = "verification"


@dataclass
class ImplementationCommand:
    """Command to implement a specific graph difference"""

    difference_id: str
    command_type: CommandType
    command: str
    description: str
    verification_command: str
    rollback_command: str = ""
    dependencies: List[str] = None


class OntologyImplementationMapper:
    """Maps graph differences to implementation commands"""

    def __init__(self):
        self.implementation_commands: List[ImplementationCommand] = []
        self.command_sequence: List[str] = []

    def onto_model_map_differences_to_commands(
        self, differences: List[Dict]
    ) -> List[ImplementationCommand]:
        """Map each difference to specific implementation commands"""
        self.implementation_commands.clear()

        for diff in differences:
            if diff["difference_type"] == "NODE_ADDED":
                self.onto_model_handle_node_addition(diff)
            elif diff["difference_type"] == "EDGE_ADDED":
                self.onto_model_handle_edge_addition(diff)
            elif diff["difference_type"] == "EDGE_REMOVED":
                self.onto_model_handle_edge_removal(diff)
            elif diff["difference_type"] == "ROUTING_CHANGED":
                self.onto_model_handle_routing_change(diff)

        return self.implementation_commands

    def onto_model_handle_node_addition(self, diff: Dict) -> None:
        """Handle addition of new nodes (like delay sinks)"""
        if "delay" in diff.get("target_value", {}).get("label", "").lower():
            # Create 20ms delay sink
            command = ImplementationCommand(
                difference_id=diff["element_id"],
                command_type=CommandType.PACTL_LOAD_MODULE,
                command="pactl load-module module-loopback source=jamesdsp_sink.monitor sink=alsa_output.pci-0000_0b_00.4.analog-stereo latency_msec=20",
                description="Create 20ms delay sink for main speakers",
                verification_command="pactl list modules | grep -A 5 -B 5 'loopback'",
                rollback_command="pactl unload-module <module_id>",
                dependencies=[],
            )
            self.implementation_commands.append(command)

    def onto_model_handle_edge_addition(self, diff: Dict) -> None:
        """Handle addition of new edges (connections)"""
        source, target = diff["element_id"].split("->")

        if "delay" in target:
            # This is handled by the node addition (delay sink creation)
            return
        elif target == "69":  # KM Speakers
            # This is the delay->KM connection, handled by delay sink creation
            return
        else:
            # Generic connection - use pw-link
            command = ImplementationCommand(
                difference_id=diff["element_id"],
                command_type=CommandType.PW_LINK,
                command=f"pw-link jamesdsp_sink:output_FL {target}:playback_FL",
                description=f"Create connection from {source} to {target}",
                verification_command="pw-top",
                rollback_command=f"pw-unlink jamesdsp_sink:output_FL {target}:playback_FL",
                dependencies=[],
            )
            self.implementation_commands.append(command)

    def onto_model_handle_edge_removal(self, diff: Dict) -> None:
        """Handle removal of edges (connections)"""
        source, target = diff["element_id"].split("->")

        if source == "91" and target == "69":  # JamesDSP to KM Speakers
            # This is handled by the routing change - direct connection removed
            # when delay sink is created
            return
        else:
            # Generic connection removal
            command = ImplementationCommand(
                difference_id=diff["element_id"],
                command_type=CommandType.PW_UNLINK,
                command=f"pw-unlink {source}:output_FL {target}:playback_FL",
                description=f"Remove connection from {source} to {target}",
                verification_command="pw-top",
                rollback_command=f"pw-link {source}:output_FL {target}:playback_FL",
                dependencies=[],
            )
            self.implementation_commands.append(command)

    def onto_model_handle_routing_change(self, diff: Dict) -> None:
        """Handle routing changes (like JamesDSP routing modifications)"""
        if "JamesDSP to KM Speakers" in diff["description"]:
            # This is handled by the delay sink creation
            # The direct connection removal happens automatically
            return
        elif "JamesDSP to delay" in diff["description"]:
            # This is handled by the delay sink creation
            return
        else:
            # Generic routing change
            command = ImplementationCommand(
                difference_id=diff["element_id"],
                command_type=CommandType.PACTL_MOVE_SINK_INPUT,
                command=f"pactl move-sink-input <input_id> {diff.get('target_value', 'default')}",
                description=f"Change routing: {diff['description']}",
                verification_command="pactl list sink-inputs",
                rollback_command=f"pactl move-sink-input <input_id> {diff.get('current_value', 'default')}",
                dependencies=[],
            )
            self.implementation_commands.append(command)

    def onto_model_generate_implementation_sequence(self) -> List[str]:
        """Generate ordered sequence of commands to implement all changes"""
        sequence = []

        # Step 1: Verify current state
        sequence.append("# Step 1: Verify current LKG state")
        sequence.append("python3 audio_routing_graph.py")
        sequence.append("")

        # Step 2: Create delay sink (handles node addition and routing changes)
        sequence.append("# Step 2: Create 20ms delay sink")
        sequence.append("DELAY_MODULE_ID=$(pactl load-module module-loopback \\")
        sequence.append("    source=jamesdsp_sink.monitor \\")
        sequence.append("    sink=alsa_output.pci-0000_0b_00.4.analog-stereo \\")
        sequence.append("    latency_msec=20)")
        sequence.append('echo "Delay module ID: $DELAY_MODULE_ID"')
        sequence.append("")

        # Step 3: Verify delay sink creation
        sequence.append("# Step 3: Verify delay sink creation")
        sequence.append("pactl list modules | grep -A 5 -B 5 'loopback'")
        sequence.append("")

        # Step 4: Verify new routing
        sequence.append("# Step 4: Verify new routing topology")
        sequence.append("python3 audio_routing_graph.py")
        sequence.append("")

        # Step 5: Test audio synchronization
        sequence.append("# Step 5: Test audio synchronization")
        sequence.append('echo "Play test audio to verify 20ms delay synchronization"')
        sequence.append("")

        # Step 6: Rollback command (if needed)
        sequence.append("# Step 6: Rollback command (if needed)")
        sequence.append('echo "To rollback: pactl unload-module $DELAY_MODULE_ID"')

        return sequence

    def onto_model_generate_rollback_sequence(self) -> List[str]:
        """Generate rollback sequence for all changes"""
        sequence = []

        sequence.append("# Rollback Sequence for 20ms Delay Implementation")
        sequence.append("")
        sequence.append("# Step 1: Find delay module ID")
        sequence.append(
            "DELAY_MODULE_ID=$(pactl list modules | grep -B 2 'loopback' | grep 'Module #' | tail -1 | awk '{print $2}')"
        )
        sequence.append('echo "Found delay module ID: $DELAY_MODULE_ID"')
        sequence.append("")

        sequence.append("# Step 2: Unload delay module")
        sequence.append('if [ ! -z "$DELAY_MODULE_ID" ]; then')
        sequence.append("    pactl unload-module $DELAY_MODULE_ID")
        sequence.append('    echo "Delay module unloaded"')
        sequence.append("else")
        sequence.append('    echo "No delay module found"')
        sequence.append("fi")
        sequence.append("")

        sequence.append("# Step 3: Verify return to LKG state")
        sequence.append("python3 audio_routing_graph.py")
        sequence.append("")

        sequence.append("# Step 4: Test audio (should be back to original state)")
        sequence.append('echo "Audio should now be back to original state"')

        return sequence

    def onto_model_create_implementation_script(
        self, filename: str = "implement_20ms_delay.sh"
    ) -> None:
        """Create executable implementation script"""
        sequence = self.onto_model_generate_implementation_sequence()

        with open(filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Generated following ontology framework rules\n")
            f.write("# Implementation script for 20ms delay on main speakers\n")
            f.write("# This script implements the target state from LKG state\n")
            f.write("\n")
            f.write("set -e  # Exit on any error\n")
            f.write("\n")

            for line in sequence:
                f.write(f"{line}\n")

        # Make executable
        import os

        os.chmod(filename, 0o755)

    def onto_model_create_rollback_script(
        self, filename: str = "rollback_20ms_delay.sh"
    ) -> None:
        """Create executable rollback script"""
        sequence = self.onto_model_generate_rollback_sequence()

        with open(filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Generated following ontology framework rules\n")
            f.write("# Rollback script for 20ms delay implementation\n")
            f.write("# This script returns to LKG state\n")
            f.write("\n")
            f.write("set -e  # Exit on any error\n")
            f.write("\n")

            for line in sequence:
                f.write(f"{line}\n")

        # Make executable
        import os

        os.chmod(filename, 0o755)


def onto_model_main():
    """Main function to generate implementation commands"""
    # Load the differences from our previous analysis
    differences = [
        {
            "element_id": "delay_20ms",
            "difference_type": "NODE_ADDED",
            "target_value": {"label": "20ms Delay Sink", "type": "DelaySink"},
            "description": "New node added: 20ms Delay Sink",
        },
        {
            "element_id": "91->delay_20ms",
            "difference_type": "EDGE_ADDED",
            "description": "New connection: 91 -> delay_20ms",
        },
        {
            "element_id": "delay_20ms->69",
            "difference_type": "EDGE_ADDED",
            "description": "New connection: delay_20ms -> 69",
        },
        {
            "element_id": "91->69",
            "difference_type": "EDGE_REMOVED",
            "description": "Connection removed: 91 -> 69",
        },
        {
            "element_id": "91->69",
            "difference_type": "ROUTING_CHANGED",
            "current_value": "direct",
            "target_value": "delayed",
            "description": "JamesDSP to KM Speakers: direct connection removed, will route through delay",
        },
        {
            "element_id": "91->delay_20ms",
            "difference_type": "ROUTING_CHANGED",
            "current_value": "none",
            "target_value": "new_delay_path",
            "description": "JamesDSP to delay_20ms: new delay path added",
        },
    ]

    mapper = OntologyImplementationMapper()
    commands = mapper.onto_model_map_differences_to_commands(differences)

    print("=== IMPLEMENTATION COMMANDS FOR EACH DIFFERENCE ===")
    for cmd in commands:
        print(f"\n--- {cmd.difference_id} ---")
        print(f"Type: {cmd.command_type.value}")
        print(f"Command: {cmd.command}")
        print(f"Description: {cmd.description}")
        print(f"Verification: {cmd.verification_command}")
        if cmd.rollback_command:
            print(f"Rollback: {cmd.rollback_command}")

    # Generate implementation script
    mapper.onto_model_create_implementation_script()
    mapper.onto_model_create_rollback_script()

    print(f"\n=== GENERATED SCRIPTS ===")
    print("✅ implement_20ms_delay.sh - Implementation script")
    print("✅ rollback_20ms_delay.sh - Rollback script")

    # Show implementation sequence
    print(f"\n=== IMPLEMENTATION SEQUENCE ===")
    sequence = mapper.onto_model_generate_implementation_sequence()
    for line in sequence:
        print(line)

    return commands


if __name__ == "__main__":
    onto_model_main()
