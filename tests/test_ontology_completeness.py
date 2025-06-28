# Generated following ontology framework rules
"""
Comprehensive ontology validation tests to ensure our ontology model
correctly represents all existing cursor rules (LKG MDC files).
"""

import os
import re
from pathlib import Path

import pytest

# Ontology framework constants
ONTOLOGY_PATH = (
    Path(__file__).parent.parent / "ontologies" / "cursor_rules_ontology.ttl"
)
CURSOR_RULES_PATH = Path(__file__).parent.parent / ".cursor" / "rules"


def onto_model_discover_mdc_files() -> list:
    """
    Discover all MDC files in the cursor rules directory.

    Returns:
        list: List of MDC file paths
    """
    mdc_files = []
    if CURSOR_RULES_PATH.exists():
        for file_path in CURSOR_RULES_PATH.glob("*.mdc"):
            mdc_files.append(file_path)
    return mdc_files


def onto_model_extract_rule_name_from_mdc(file_path: Path) -> str:
    """
    Extract the rule name from an MDC file path.

    Args:
        file_path: Path to the MDC file

    Returns:
        str: Rule name in camelCase format
    """
    # Convert filename to camelCase rule name
    # e.g., "ban-edit-tool-enhanced.mdc" -> "banEditToolEnhanced"
    filename = file_path.stem  # Remove .mdc extension
    parts = filename.split("-")
    rule_name = parts[0] + "".join(part.capitalize() for part in parts[1:])
    return rule_name


def onto_model_validate_ontology_completeness():
    """
    Validate that all MDC files are represented in the ontology.
    """
    print("Testing ontology completeness against all MDC files...")

    # Discover all MDC files
    mdc_files = onto_model_discover_mdc_files()
    print(f"Found {len(mdc_files)} MDC files: {[f.name for f in mdc_files]}")

    # Read ontology content
    with open(ONTOLOGY_PATH, "r") as f:
        ontology_content = f.read()

    # Check each MDC file is represented in ontology
    missing_rules = []
    for mdc_file in mdc_files:
        rule_name = onto_model_extract_rule_name_from_mdc(mdc_file)
        expected_rule_pattern = f":{rule_name}\\s+a\\s+:CursorRule"

        if not re.search(expected_rule_pattern, ontology_content):
            missing_rules.append((mdc_file.name, rule_name))
            print(f"❌ Missing rule: {mdc_file.name} -> {rule_name}")
        else:
            print(f"✅ Found rule: {mdc_file.name} -> {rule_name}")

    # Assert all rules are present
    assert len(missing_rules) == 0, f"Missing rules in ontology: {missing_rules}"

    print("✅ All MDC files are represented in ontology")


def onto_model_validate_ontology_consistency():
    """
    Validate that ontology rules have consistent structure and properties.
    """
    print("Testing ontology consistency...")

    with open(ONTOLOGY_PATH, "r") as f:
        ontology_content = f.read()

    # Find all rule instances
    rule_instances = re.findall(r":(\w+)\s+a\s+:CursorRule", ontology_content)
    print(f"Found {len(rule_instances)} rules in ontology: {rule_instances}")

    # Validate each rule has required properties
    required_properties = [
        "rdfs:label",
        "dct:description",
        ":fileLocation",
        ":appliesTo",
        ":rationale",
    ]

    for rule_name in rule_instances:
        # Extract rule content using the same logic as our existing test
        rule_start = ontology_content.find(f":{rule_name}")
        assert rule_start != -1, f"Rule {rule_name} not found in content"

        # Find the next rule or end of file
        next_rule_start = -1
        for other_rule in rule_instances:
            if other_rule != rule_name:
                other_start = ontology_content.find(f":{other_rule}", rule_start + 1)
                if other_start != -1 and (
                    next_rule_start == -1 or other_start < next_rule_start
                ):
                    next_rule_start = other_start

        # Extract the rule content
        if next_rule_start != -1:
            rule_content = ontology_content[rule_start:next_rule_start].strip()
        else:
            rule_content = ontology_content[rule_start:].strip()

        # Check each required property
        for prop in required_properties:
            assert prop in rule_content, f"Rule {rule_name} missing property: {prop}"

        print(f"✅ Rule {rule_name} has all required properties")

    print("✅ All rules have consistent structure")


def onto_model_validate_file_location_accuracy():
    """
    Validate that file locations in ontology match actual MDC files.
    """
    print("Testing file location accuracy...")

    mdc_files = onto_model_discover_mdc_files()
    mdc_file_names = {f.name for f in mdc_files}

    with open(ONTOLOGY_PATH, "r") as f:
        ontology_content = f.read()

    # Extract file locations from ontology
    file_location_pattern = r':fileLocation\s+"([^"]+)"'
    file_locations = re.findall(file_location_pattern, ontology_content)

    for file_location in file_locations:
        # Extract filename from path
        filename = os.path.basename(file_location)
        assert (
            filename in mdc_file_names
        ), f"File location {file_location} does not match actual MDC file"
        print(f"✅ File location verified: {filename}")

    print("✅ All file locations are accurate")


def test_ontology_completeness():
    """
    Test that our ontology is complete and accurate.
    """
    onto_model_validate_ontology_completeness()
    onto_model_validate_ontology_consistency()
    onto_model_validate_file_location_accuracy()


def test_ontology_discovery_accuracy():
    """
    Test that our discovery logic correctly identifies all rules.
    """
    print("Testing discovery accuracy...")

    # Test our discovery function
    mdc_files = onto_model_discover_mdc_files()
    assert len(mdc_files) > 0, "No MDC files found"

    # Test rule name extraction
    for mdc_file in mdc_files:
        rule_name = onto_model_extract_rule_name_from_mdc(mdc_file)
        assert rule_name, f"Failed to extract rule name from {mdc_file.name}"
        assert re.match(
            r"^[a-z][a-zA-Z0-9]*$", rule_name
        ), f"Invalid rule name format: {rule_name}"
        print(f"✅ Rule name extraction: {mdc_file.name} -> {rule_name}")

    print("✅ Discovery logic is accurate")
