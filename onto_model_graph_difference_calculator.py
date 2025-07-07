# Generated following ontology framework rules
"""
Graph Difference Calculator for Audio System Models
Calculates semantic differences between current LKG state and target state graphs.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Set, Tuple

import networkx as nx


class DifferenceType(Enum):
    """Semantic difference types for ontological analysis"""

    NODE_ADDED = "node_added"
    NODE_REMOVED = "node_removed"
    EDGE_ADDED = "edge_added"
    EDGE_REMOVED = "edge_removed"
    ATTRIBUTE_CHANGED = "attribute_changed"
    ROUTING_CHANGED = "routing_changed"


@dataclass
class GraphDifference:
    """Ontological difference representation"""

    difference_type: DifferenceType
    element_id: str
    current_value: Any = None
    target_value: Any = None
    description: str = ""
    impact_level: str = "medium"  # low, medium, high, critical


class OntologyGraphDifferenceCalculator:
    """Calculates semantic differences between audio system graph models"""

    def __init__(self):
        self.current_graph = nx.DiGraph()
        self.target_graph = nx.DiGraph()
        self.differences: List[GraphDifference] = []

    def onto_model_load_current_state(self, graph_data: Dict) -> None:
        """Load current LKG state graph data"""
        self.current_graph.clear()

        # Add nodes with attributes
        for node in graph_data.get("nodes", []):
            node_id = str(node.get("id"))
            self.current_graph.add_node(node_id, **node)

        # Add edges
        for edge in graph_data.get("edges", []):
            source = str(edge.get("source"))
            target = str(edge.get("target"))
            self.current_graph.add_edge(source, target, **edge)

    def onto_model_load_target_state(self, graph_data: Dict) -> None:
        """Load target state graph data"""
        self.target_graph.clear()

        # Add nodes with attributes
        for node in graph_data.get("nodes", []):
            node_id = str(node.get("id"))
            self.target_graph.add_node(node_id, **node)

        # Add edges
        for edge in graph_data.get("edges", []):
            source = str(edge.get("source"))
            target = str(edge.get("target"))
            self.target_graph.add_edge(source, target, **edge)

    def onto_model_calculate_differences(self) -> List[GraphDifference]:
        """Calculate semantic differences between current and target graphs"""
        self.differences.clear()

        # Node differences
        current_nodes = set(self.current_graph.nodes())
        target_nodes = set(self.target_graph.nodes())

        # Added nodes
        for node_id in target_nodes - current_nodes:
            node_data = self.target_graph.nodes[node_id]
            self.differences.append(
                GraphDifference(
                    difference_type=DifferenceType.NODE_ADDED,
                    element_id=node_id,
                    target_value=node_data,
                    description=f"New node added: {node_data.get('label', node_id)}",
                    impact_level="high"
                    if "delay" in node_data.get("label", "").lower()
                    else "medium",
                )
            )

        # Removed nodes
        for node_id in current_nodes - target_nodes:
            node_data = self.current_graph.nodes[node_id]
            self.differences.append(
                GraphDifference(
                    difference_type=DifferenceType.NODE_REMOVED,
                    element_id=node_id,
                    current_value=node_data,
                    description=f"Node removed: {node_data.get('label', node_id)}",
                    impact_level="medium",
                )
            )

        # Edge differences
        current_edges = set(self.current_graph.edges())
        target_edges = set(self.target_graph.edges())

        # Added edges
        for source, target in target_edges - current_edges:
            edge_data = self.target_graph.edges[source, target]
            self.differences.append(
                GraphDifference(
                    difference_type=DifferenceType.EDGE_ADDED,
                    element_id=f"{source}->{target}",
                    target_value=edge_data,
                    description=f"New connection: {source} -> {target}",
                    impact_level="high"
                    if "delay" in str(edge_data).lower()
                    else "medium",
                )
            )

        # Removed edges
        for source, target in current_edges - target_edges:
            edge_data = self.current_graph.edges[source, target]
            self.differences.append(
                GraphDifference(
                    difference_type=DifferenceType.EDGE_REMOVED,
                    element_id=f"{source}->{target}",
                    current_value=edge_data,
                    description=f"Connection removed: {source} -> {target}",
                    impact_level="medium",
                )
            )

        # Attribute changes for common nodes
        common_nodes = current_nodes & target_nodes
        for node_id in common_nodes:
            current_attrs = self.current_graph.nodes[node_id]
            target_attrs = self.target_graph.nodes[node_id]

            for attr, target_value in target_attrs.items():
                current_value = current_attrs.get(attr)
                if current_value != target_value:
                    self.differences.append(
                        GraphDifference(
                            difference_type=DifferenceType.ATTRIBUTE_CHANGED,
                            element_id=node_id,
                            current_value=current_value,
                            target_value=target_value,
                            description=f"Attribute '{attr}' changed for {node_id}",
                            impact_level="low",
                        )
                    )

        return self.differences

    def onto_model_analyze_routing_changes(self) -> List[GraphDifference]:
        """Analyze specific routing changes for audio system"""
        routing_differences = []

        # Check for JamesDSP routing changes
        jamesdsp_id = "91"  # JamesDSP Sink ID

        if jamesdsp_id in self.current_graph and jamesdsp_id in self.target_graph:
            current_targets = set(self.current_graph.successors(jamesdsp_id))
            target_targets = set(self.target_graph.successors(jamesdsp_id))

            # Check if direct KM Speakers connection is removed
            km_speakers_id = "69"
            if (jamesdsp_id, km_speakers_id) in self.current_graph.edges() and (
                jamesdsp_id,
                km_speakers_id,
            ) not in self.target_graph.edges():
                routing_differences.append(
                    GraphDifference(
                        difference_type=DifferenceType.ROUTING_CHANGED,
                        element_id=f"{jamesdsp_id}->{km_speakers_id}",
                        current_value="direct",
                        target_value="delayed",
                        description="JamesDSP to KM Speakers: direct connection removed, will route through delay",
                        impact_level="high",
                    )
                )

            # Check for new delay sink connection
            delay_sinks = [
                node
                for node in self.target_graph.nodes()
                if "delay" in self.target_graph.nodes[node].get("label", "").lower()
            ]
            for delay_sink in delay_sinks:
                if (jamesdsp_id, delay_sink) in self.target_graph.edges():
                    routing_differences.append(
                        GraphDifference(
                            difference_type=DifferenceType.ROUTING_CHANGED,
                            element_id=f"{jamesdsp_id}->{delay_sink}",
                            current_value="none",
                            target_value="new_delay_path",
                            description=f"JamesDSP to {delay_sink}: new delay path added",
                            impact_level="high",
                        )
                    )

        return routing_differences

    def onto_model_generate_difference_report(self) -> Dict[str, Any]:
        """Generate comprehensive difference report"""
        differences = self.onto_model_calculate_differences()
        routing_changes = self.onto_model_analyze_routing_changes()

        # Categorize differences
        by_type = {}
        by_impact = {}

        for diff in differences + routing_changes:
            # By type
            if diff.difference_type.value not in by_type:
                by_type[diff.difference_type.value] = []
            by_type[diff.difference_type.value].append(diff)

            # By impact
            if diff.impact_level not in by_impact:
                by_impact[diff.impact_level] = []
            by_impact[diff.impact_level].append(diff)

        return {
            "summary": {
                "total_differences": len(differences) + len(routing_changes),
                "nodes_added": len(
                    [
                        d
                        for d in differences
                        if d.difference_type == DifferenceType.NODE_ADDED
                    ]
                ),
                "nodes_removed": len(
                    [
                        d
                        for d in differences
                        if d.difference_type == DifferenceType.NODE_REMOVED
                    ]
                ),
                "edges_added": len(
                    [
                        d
                        for d in differences
                        if d.difference_type == DifferenceType.EDGE_ADDED
                    ]
                ),
                "edges_removed": len(
                    [
                        d
                        for d in differences
                        if d.difference_type == DifferenceType.EDGE_REMOVED
                    ]
                ),
                "routing_changes": len(routing_changes),
            },
            "differences_by_type": by_type,
            "differences_by_impact": by_impact,
            "all_differences": [
                diff.__dict__ for diff in differences + routing_changes
            ],
            "critical_changes": [
                diff.__dict__
                for diff in differences + routing_changes
                if diff.impact_level == "critical"
            ],
            "high_impact_changes": [
                diff.__dict__
                for diff in differences + routing_changes
                if diff.impact_level == "high"
            ],
        }


def onto_model_create_current_state_data() -> Dict[str, Any]:
    """Create current LKG state graph data"""
    return {
        "nodes": [
            {
                "id": "91",
                "label": "JamesDSP Sink",
                "type": "ProcessingNode",
                "deviceID": "91",
            },
            {
                "id": "69",
                "label": "KM Speakers",
                "type": "HardwareOutput",
                "deviceID": "69",
            },
            {
                "id": "146",
                "label": "Fosi Subwoofer",
                "type": "HardwareOutput",
                "deviceID": "146",
            },
            {
                "id": "175",
                "label": "Chromium",
                "type": "StreamOutput",
                "deviceID": "175",
            },
            {
                "id": "334",
                "label": "Firefox",
                "type": "StreamOutput",
                "deviceID": "334",
            },
            {
                "id": "246",
                "label": "PulseAudio Volume Control",
                "type": "MixerSink",
                "deviceID": "246",
            },
        ],
        "edges": [
            {"source": "91", "target": "69", "label": "JamesDSP_to_KM"},
            {"source": "91", "target": "146", "label": "JamesDSP_to_Fosi"},
            {"source": "175", "target": "91", "label": "Chromium_to_JamesDSP"},
            {"source": "334", "target": "91", "label": "Firefox_to_JamesDSP"},
            {"source": "246", "target": "91", "label": "PulseAudio_to_JamesDSP"},
        ],
    }


def onto_model_create_target_state_data() -> Dict[str, Any]:
    """Create target state graph data with 20ms delay"""
    return {
        "nodes": [
            {
                "id": "91",
                "label": "JamesDSP Sink",
                "type": "ProcessingNode",
                "deviceID": "91",
            },
            {
                "id": "delay_20ms",
                "label": "20ms Delay Sink",
                "type": "DelaySink",
                "deviceID": "TBD",
                "delay": "20ms",
            },
            {
                "id": "69",
                "label": "KM Speakers",
                "type": "HardwareOutput",
                "deviceID": "69",
                "note": "DELAYED by 20ms",
            },
            {
                "id": "146",
                "label": "Fosi Subwoofer",
                "type": "HardwareOutput",
                "deviceID": "146",
                "note": "NO DELAY - direct connection",
            },
            {
                "id": "175",
                "label": "Chromium",
                "type": "StreamOutput",
                "deviceID": "175",
            },
            {
                "id": "334",
                "label": "Firefox",
                "type": "StreamOutput",
                "deviceID": "334",
            },
            {
                "id": "246",
                "label": "PulseAudio Volume Control",
                "type": "MixerSink",
                "deviceID": "246",
            },
        ],
        "edges": [
            {"source": "91", "target": "delay_20ms", "label": "JamesDSP_to_Delay"},
            {"source": "delay_20ms", "target": "69", "label": "Delay_to_KM"},
            {"source": "91", "target": "146", "label": "JamesDSP_to_Fosi_Direct"},
            {"source": "175", "target": "91", "label": "Chromium_to_JamesDSP"},
            {"source": "334", "target": "91", "label": "Firefox_to_JamesDSP"},
            {"source": "246", "target": "91", "label": "PulseAudio_to_JamesDSP"},
        ],
    }


def onto_model_main():
    """Main function to calculate and report graph differences"""
    calculator = OntologyGraphDifferenceCalculator()

    # Load current and target states
    current_data = onto_model_create_current_state_data()
    target_data = onto_model_create_target_state_data()

    calculator.onto_model_load_current_state(current_data)
    calculator.onto_model_load_target_state(target_data)

    # Calculate differences
    report = calculator.onto_model_generate_difference_report()

    # Print summary
    print("=== AUDIO SYSTEM GRAPH DIFFERENCE ANALYSIS ===")
    print(f"Total differences: {report['summary']['total_differences']}")
    print(f"Nodes added: {report['summary']['nodes_added']}")
    print(f"Nodes removed: {report['summary']['nodes_removed']}")
    print(f"Edges added: {report['summary']['edges_added']}")
    print(f"Edges removed: {report['summary']['edges_removed']}")
    print(f"Routing changes: {report['summary']['routing_changes']}")

    print("\n=== HIGH IMPACT CHANGES ===")
    for change in report["high_impact_changes"]:
        print(f"- {change['description']} ({change['difference_type']})")

    print("\n=== ALL DIFFERENCES ===")
    for diff in report["all_differences"]:
        print(
            f"- {diff['description']} ({diff['difference_type']}, Impact: {diff['impact_level']})"
        )

    return report


if __name__ == "__main__":
    onto_model_main()
