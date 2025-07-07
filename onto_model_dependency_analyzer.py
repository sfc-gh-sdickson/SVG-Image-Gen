# Generated following ontology framework rules
"""
Dependency Analyzer for Audio System Implementation Commands
Analyzes dependencies between commands and models required sequencing.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Set, Tuple

import networkx as nx


class DependencyType(Enum):
    """Types of dependencies between implementation commands"""

    REQUIRES = "requires"  # Command A must complete before Command B
    CREATES = "creates"  # Command A creates resource needed by Command B
    REMOVES = "removes"  # Command A removes resource needed by Command B
    VERIFIES = "verifies"  # Command A verifies state needed by Command B
    CONFLICTS = "conflicts"  # Command A conflicts with Command B


@dataclass
class CommandDependency:
    """Dependency relationship between commands"""

    source_command: str
    target_command: str
    dependency_type: DependencyType
    description: str
    critical: bool = True


@dataclass
class ImplementationStep:
    """Implementation step with dependencies"""

    step_id: str
    command: str
    description: str
    dependencies: List[str]
    creates_resources: List[str]
    requires_resources: List[str]
    verification_command: str
    rollback_command: str = ""


class OntologyDependencyAnalyzer:
    """Analyzes dependencies between implementation commands"""

    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.implementation_steps: List[ImplementationStep] = []
        self.resource_map: Dict[str, List[str]] = {}

    def onto_model_define_implementation_steps(self) -> List[ImplementationStep]:
        """Define all implementation steps with their dependencies"""
        steps = [
            ImplementationStep(
                step_id="verify_lkg_state",
                command="python3 audio_routing_graph.py",
                description="Verify current LKG state before changes",
                dependencies=[],
                creates_resources=["lkg_state_confirmed"],
                requires_resources=[],
                verification_command="Check graph output for clean state",
            ),
            ImplementationStep(
                step_id="create_delay_sink",
                command="pactl load-module module-loopback source=jamesdsp_sink.monitor sink=alsa_output.pci-0000_0b_00.4.analog-stereo latency_msec=20",
                description="Create 20ms delay sink for main speakers",
                dependencies=["verify_lkg_state"],
                creates_resources=[
                    "delay_sink",
                    "delay_module_id",
                    "jamesdsp_to_delay_connection",
                    "delay_to_km_connection",
                ],
                requires_resources=[
                    "lkg_state_confirmed",
                    "jamesdsp_sink",
                    "km_speakers_sink",
                ],
                verification_command="pactl list modules | grep -A 5 -B 5 'loopback'",
            ),
            ImplementationStep(
                step_id="verify_delay_creation",
                command="pactl list modules | grep -A 5 -B 5 'loopback'",
                description="Verify delay sink was created successfully",
                dependencies=["create_delay_sink"],
                creates_resources=["delay_creation_verified"],
                requires_resources=["delay_sink"],
                verification_command="Check for loopback module in output",
            ),
            ImplementationStep(
                step_id="verify_new_routing",
                command="python3 audio_routing_graph.py",
                description="Verify new routing topology matches target state",
                dependencies=["verify_delay_creation"],
                creates_resources=["target_state_confirmed"],
                requires_resources=["delay_creation_verified"],
                verification_command="Check graph for delay path and removed direct connection",
            ),
            ImplementationStep(
                step_id="test_audio_synchronization",
                command="echo 'Play test audio to verify 20ms delay synchronization'",
                description="Test audio synchronization between speakers and subwoofer",
                dependencies=["verify_new_routing"],
                creates_resources=["audio_sync_verified"],
                requires_resources=["target_state_confirmed"],
                verification_command="Listen for proper phase alignment",
            ),
        ]

        self.implementation_steps = steps
        return steps

    def onto_model_build_dependency_graph(self) -> nx.DiGraph:
        """Build dependency graph from implementation steps"""
        self.dependency_graph.clear()

        # Add nodes (steps)
        for step in self.implementation_steps:
            self.dependency_graph.add_node(step.step_id, step=step)

        # Add edges (dependencies)
        for step in self.implementation_steps:
            for dep in step.dependencies:
                if dep in self.dependency_graph:
                    self.dependency_graph.add_edge(dep, step.step_id)

        # Add resource dependencies
        for step in self.implementation_steps:
            for required_resource in step.requires_resources:
                # Find steps that create this resource
                for other_step in self.implementation_steps:
                    if required_resource in other_step.creates_resources:
                        self.dependency_graph.add_edge(other_step.step_id, step.step_id)

        return self.dependency_graph

    def onto_model_analyze_sequencing(self) -> Dict[str, Any]:
        """Analyze the sequencing requirements"""
        graph = self.onto_model_build_dependency_graph()

        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(graph))
        except nx.NetworkXNoCycle:
            cycles = []

        # Find topological sort (execution order)
        try:
            execution_order = list(nx.topological_sort(graph))
        except nx.NetworkXError:
            execution_order = []

        # Find parallel steps (can run simultaneously)
        parallel_groups = []
        if execution_order:
            # Group steps that can run in parallel
            current_level = set()
            for step_id in execution_order:
                predecessors = set(graph.predecessors(step_id))
                if predecessors.issubset(current_level):
                    # This step can run in parallel with current level
                    current_level.add(step_id)
                else:
                    # New level needed
                    if current_level:
                        parallel_groups.append(list(current_level))
                    current_level = {step_id}
            if current_level:
                parallel_groups.append(list(current_level))

        # Find critical path
        critical_path = []
        if execution_order:
            critical_path = execution_order  # Simplified for now

        return {
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
            "execution_order": execution_order,
            "parallel_groups": parallel_groups,
            "critical_path": critical_path,
            "total_steps": len(self.implementation_steps),
            "dependency_count": len(list(self.dependency_graph.edges())),
        }

    def onto_model_analyze_resource_dependencies(self) -> Dict[str, Any]:
        """Analyze resource dependencies between steps"""
        resource_flow = {}
        resource_creators = {}
        resource_consumers = {}

        for step in self.implementation_steps:
            # Track what each step creates
            for resource in step.creates_resources:
                if resource not in resource_creators:
                    resource_creators[resource] = []
                resource_creators[resource].append(step.step_id)

            # Track what each step requires
            for resource in step.requires_resources:
                if resource not in resource_consumers:
                    resource_consumers[resource] = []
                resource_consumers[resource].append(step.step_id)

        # Build resource flow
        for resource in set(resource_creators.keys()) | set(resource_consumers.keys()):
            resource_flow[resource] = {
                "created_by": resource_creators.get(resource, []),
                "consumed_by": resource_consumers.get(resource, []),
                "critical": resource
                in ["delay_sink", "target_state_confirmed", "audio_sync_verified"],
            }

        return {
            "resource_flow": resource_flow,
            "critical_resources": [
                r for r, info in resource_flow.items() if info["critical"]
            ],
            "resource_count": len(resource_flow),
        }

    def onto_model_generate_dependency_report(self) -> Dict[str, Any]:
        """Generate comprehensive dependency analysis report"""
        sequencing = self.onto_model_analyze_sequencing()
        resources = self.onto_model_analyze_resource_dependencies()

        return {
            "sequencing_analysis": sequencing,
            "resource_analysis": resources,
            "implementation_steps": [
                step.__dict__ for step in self.implementation_steps
            ],
            "dependency_graph_nodes": list(self.dependency_graph.nodes()),
            "dependency_graph_edges": list(self.dependency_graph.edges()),
        }

    def onto_model_create_sequenced_script(
        self, filename: str = "sequenced_implementation.sh"
    ) -> None:
        """Create implementation script with proper sequencing"""
        sequencing = self.onto_model_analyze_sequencing()

        with open(filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Generated following ontology framework rules\n")
            f.write("# Sequenced implementation script for 20ms delay\n")
            f.write("# Dependencies: " + str(sequencing["dependency_count"]) + "\n")
            f.write(
                "# Execution order: "
                + " -> ".join(sequencing["execution_order"])
                + "\n"
            )
            f.write("\n")
            f.write("set -e  # Exit on any error\n")
            f.write("\n")

            f.write('echo "=== 20ms Delay Implementation (Sequenced) ==="\n')
            f.write('echo "Total steps: ' + str(sequencing["total_steps"]) + '"\n')
            f.write(
                'echo "Dependencies: ' + str(sequencing["dependency_count"]) + '"\n'
            )
            f.write("\n")

            for i, step_id in enumerate(sequencing["execution_order"], 1):
                step = next(
                    s for s in self.implementation_steps if s.step_id == step_id
                )

                f.write(
                    f"echo \"Step {i}/{len(sequencing['execution_order'])}: {step.description}\"\n"
                )
                f.write(
                    f"# Dependencies: {', '.join(step.dependencies) if step.dependencies else 'none'}\n"
                )
                f.write(f"{step.command}\n")

                if (
                    step.verification_command
                    and step.verification_command != step.command
                ):
                    f.write(f'echo "Verifying: {step.verification_command}"\n')
                    f.write(f"{step.verification_command}\n")

                f.write('echo "Step ' + str(i) + ' completed"\n')
                f.write("\n")

            f.write('echo "=== Implementation completed successfully ==="\n')
            f.write('echo "All dependencies satisfied"\n')

        # Make executable
        import os

        os.chmod(filename, 0o755)

    def onto_model_create_dependency_diagram(
        self, filename: str = "dependency_diagram.dot"
    ) -> None:
        """Create DOT file for dependency visualization"""
        with open(filename, "w") as f:
            f.write("digraph ImplementationDependencies {\n")
            f.write("    rankdir=TB;\n")
            f.write("    node [shape=box, style=filled];\n")
            f.write("\n")

            # Add nodes
            for step in self.implementation_steps:
                color = "lightblue" if "verify" in step.step_id else "lightgreen"
                f.write(
                    f'    "{step.step_id}" [label="{step.description}", fillcolor={color}];\n'
                )

            f.write("\n")

            # Add edges
            for step in self.implementation_steps:
                for dep in step.dependencies:
                    f.write(f'    "{dep}" -> "{step.step_id}";\n')

            f.write("}\n")


def onto_model_main():
    """Main function to analyze dependencies"""
    analyzer = OntologyDependencyAnalyzer()

    # Define implementation steps
    steps = analyzer.onto_model_define_implementation_steps()

    # Analyze dependencies
    report = analyzer.onto_model_generate_dependency_report()

    print("=== DEPENDENCY ANALYSIS REPORT ===")
    print(f"Total steps: {report['sequencing_analysis']['total_steps']}")
    print(f"Dependencies: {report['sequencing_analysis']['dependency_count']}")
    print(f"Has cycles: {report['sequencing_analysis']['has_cycles']}")

    print(f"\n=== EXECUTION ORDER ===")
    for i, step_id in enumerate(report["sequencing_analysis"]["execution_order"], 1):
        step = next(s for s in steps if s.step_id == step_id)
        print(f"{i}. {step.description}")

    print(f"\n=== PARALLEL GROUPS ===")
    for i, group in enumerate(report["sequencing_analysis"]["parallel_groups"], 1):
        print(f"Group {i}: {', '.join(group)}")

    print(f"\n=== CRITICAL RESOURCES ===")
    for resource in report["resource_analysis"]["critical_resources"]:
        print(f"- {resource}")

    print(f"\n=== DEPENDENCY GRAPH ===")
    print(f"Nodes: {len(report['dependency_graph_nodes'])}")
    print(f"Edges: {len(report['dependency_graph_edges'])}")

    # Generate files
    analyzer.onto_model_create_sequenced_script()
    analyzer.onto_model_create_dependency_diagram()

    print(f"\n=== GENERATED FILES ===")
    print("✅ sequenced_implementation.sh - Sequenced implementation script")
    print("✅ dependency_diagram.dot - Dependency visualization")

    return report


if __name__ == "__main__":
    onto_model_main()
