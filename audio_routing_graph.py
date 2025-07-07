#!/usr/bin/env python3
"""
Audio Routing Graph Builder
Builds a comprehensive graph of current PipeWire audio routing state
with loop detection and visualization.
"""

import json
import re
import subprocess
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx


def get_pipewire_objects():
    """Get all PipeWire objects and their connections."""
    try:
        result = subprocess.run(
            ["pw-cli", "list-objects"], capture_output=True, text=True, timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        print("Timeout getting PipeWire objects")
        return ""
    except Exception as e:
        print(f"Error getting PipeWire objects: {e}")
        return ""


def parse_pipewire_state(output):
    """Parse PipeWire output into structured data."""
    nodes = {}
    links = {}
    current_node = None
    current_link = None

    lines = output.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Node section
        if line.startswith("id ") and "type PipeWire:Interface:Node" in line:
            node_id = line.split()[1].rstrip(",")
            current_node = {"id": node_id, "type": "node"}
            nodes[node_id] = current_node
            current_link = None

        # Link section
        elif line.startswith("id ") and "type PipeWire:Interface:Link" in line:
            link_id = line.split()[1].rstrip(",")
            current_link = {"id": link_id, "type": "link"}
            links[link_id] = current_link
            current_node = None

        # Node properties
        elif current_node and "=" in line:
            if "node.description" in line:
                current_node["description"] = line.split("=", 1)[1].strip().strip('"')
            elif "node.name" in line:
                current_node["name"] = line.split("=", 1)[1].strip().strip('"')
            elif "media.class" in line:
                current_node["media_class"] = line.split("=", 1)[1].strip().strip('"')

        # Link properties
        elif current_link and "=" in line:
            if "link.output.node" in line:
                current_link["output_node"] = line.split("=", 1)[1].strip().strip('"')
            elif "link.input.node" in line:
                current_link["input_node"] = line.split("=", 1)[1].strip().strip('"')
            elif "link.output.port" in line:
                current_link["output_port"] = line.split("=", 1)[1].strip().strip('"')
            elif "link.input.port" in line:
                current_link["input_port"] = line.split("=", 1)[1].strip().strip('"')

    return nodes, links


def build_audio_graph(nodes, links):
    """Build NetworkX graph from audio nodes and links."""
    G = nx.DiGraph()

    # Add nodes
    for node_id, node_data in nodes.items():
        if node_data.get("type") == "node":
            name = node_data.get("name", f"node_{node_id}")
            description = node_data.get("description", name)
            media_class = node_data.get("media_class", "unknown")

            G.add_node(
                node_id, name=name, description=description, media_class=media_class
            )

    # Add edges
    for link_id, link_data in links.items():
        if link_data.get("type") == "link":
            output_node = link_data.get("output_node")
            input_node = link_data.get("input_node")

            if output_node and input_node and output_node in G and input_node in G:
                G.add_edge(
                    output_node,
                    input_node,
                    link_id=link_id,
                    output_port=link_data.get("output_port"),
                    input_port=link_data.get("input_port"),
                )

    return G


def detect_loops(G):
    """Detect loops in the audio graph."""
    loops = []

    # Find all cycles
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            loop_info = {
                "nodes": cycle,
                "path": " -> ".join([G.nodes[node]["description"] for node in cycle]),
                "length": len(cycle),
            }
            loops.append(loop_info)
    except nx.NetworkXNoCycle:
        pass

    return loops


def analyze_audio_routing(G):
    """Analyze the audio routing structure."""
    analysis = {
        "total_nodes": len(G.nodes()),
        "total_edges": len(G.edges()),
        "node_types": defaultdict(int),
        "sources": [],
        "sinks": [],
        "loops": detect_loops(G),
    }

    for node_id, node_data in G.nodes(data=True):
        media_class = node_data.get("media_class", "unknown")
        analysis["node_types"][media_class] += 1

        # Identify sources and sinks
        if "Sink" in media_class:
            analysis["sinks"].append(
                {
                    "id": node_id,
                    "name": node_data.get("description", node_data.get("name")),
                    "media_class": media_class,
                }
            )
        elif "Source" in media_class:
            analysis["sources"].append(
                {
                    "id": node_id,
                    "name": node_data.get("description", node_data.get("name")),
                    "media_class": media_class,
                }
            )

    return analysis


def visualize_graph(G, filename="audio_routing_graph.png"):
    """Create a visual representation of the audio graph."""
    plt.figure(figsize=(16, 12))

    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50)

    # Color nodes by media class
    node_colors = []
    for node in G.nodes():
        media_class = G.nodes[node].get("media_class", "unknown")
        if "Sink" in media_class:
            node_colors.append("red")
        elif "Source" in media_class:
            node_colors.append("blue")
        elif "Stream" in media_class:
            node_colors.append("green")
        else:
            node_colors.append("gray")

    # Draw the graph
    nx.draw(
        G,
        pos,
        node_color=node_colors,
        node_size=1000,
        font_size=8,
        font_weight="bold",
        arrows=True,
        edge_color="black",
        width=1,
        alpha=0.7,
    )

    # Add labels
    labels = {
        node: G.nodes[node].get("description", G.nodes[node].get("name", node))
        for node in G.nodes()
    }
    nx.draw_networkx_labels(G, pos, labels, font_size=6)

    plt.title("Audio Routing Graph", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Graph saved as {filename}")


def print_analysis(analysis):
    """Print detailed analysis of the audio routing."""
    print("\n" + "=" * 60)
    print("AUDIO ROUTING ANALYSIS")
    print("=" * 60)

    print(f"\nTotal Nodes: {analysis['total_nodes']}")
    print(f"Total Connections: {analysis['total_edges']}")

    print(f"\nNode Types:")
    for media_class, count in analysis["node_types"].items():
        print(f"  {media_class}: {count}")

    print(f"\nAudio Sinks ({len(analysis['sinks'])}):")
    for sink in analysis["sinks"]:
        print(f"  - {sink['name']} ({sink['media_class']})")

    print(f"\nAudio Sources ({len(analysis['sources'])}):")
    for source in analysis["sources"]:
        print(f"  - {source['name']} ({source['media_class']})")

    if analysis["loops"]:
        print(f"\n🚨 LOOPS DETECTED ({len(analysis['loops'])}):")
        for i, loop in enumerate(analysis["loops"], 1):
            print(f"  Loop {i} ({loop['length']} nodes): {loop['path']}")
    else:
        print(f"\n✅ No loops detected")


def export_to_dot(G, filename="audio_routing_graph.dot"):
    """Export the audio graph to Graphviz DOT format for better layout."""
    try:
        from networkx.drawing.nx_pydot import write_dot
    except ImportError:
        print(
            "networkx.drawing.nx_pydot.write_dot not available. Please install pydot."
        )
        return
    # Create a copy of the graph with 'label' instead of 'name' to avoid pydot conflict
    H = G.copy()
    for n, d in H.nodes(data=True):
        if "name" in d:
            d["label"] = d["name"]
            del d["name"]
    write_dot(H, filename)
    print(f"DOT file saved as {filename}")


def main():
    """Main function to build and analyze audio routing graph."""
    print("Building audio routing graph...")

    # Get PipeWire state
    pw_output = get_pipewire_objects()
    if not pw_output:
        print("Failed to get PipeWire objects")
        return

    # Parse the state
    nodes, links = parse_pipewire_state(pw_output)
    print(f"Found {len(nodes)} objects and {len(links)} connections")

    # Build graph
    G = build_audio_graph(nodes, links)
    print(f"Built graph with {len(G.nodes())} nodes and {len(G.edges())} edges")

    # Analyze routing
    analysis = analyze_audio_routing(G)
    print_analysis(analysis)

    # Visualize
    if len(G.nodes()) > 0:
        visualize_graph(G)
        print("\nGraph visualization created!")
        export_to_dot(G)
        print("\nTo render with Graphviz, run:")
        print("  dot -Tpng audio_routing_graph.dot -o audio_routing_graph_dot.png")
        print("Or use xdot, graphviz, or web viewers for best layout.")
    else:
        print("\nNo nodes to visualize")


if __name__ == "__main__":
    main()
