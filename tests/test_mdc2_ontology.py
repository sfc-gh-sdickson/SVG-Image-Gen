# Generated following ontology framework rules
"""
Tests for MDC2 ontology model - the proper format that actually works.
Validates format specification, migration strategy, and semantic consistency.
"""

import re
from pathlib import Path

import pytest

# Ontology framework constants
MDC2_ONTOLOGY_PATH = Path(__file__).parent.parent / "ontologies" / "mdc2_ontology.ttl"


def test_mdc2_ontology_exists():
    """Test that MDC2 ontology file exists and is readable."""
    assert MDC2_ONTOLOGY_PATH.exists(), "MDC2 ontology file not found"

    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    assert len(content) > 0, "MDC2 ontology file is empty"
    print("✅ MDC2 ontology file exists and is readable")


def test_mdc2_format_specification():
    """Test that MDC2 format specification is properly defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for MDC2 format specification
    assert ":mdc2FormatSpec" in content, "MDC2 format specification not found"
    assert "version" in content, "MDC2 version not specified"
    assert "validationSchema" in content, "MDC2 validation schema not specified"
    assert (
        "backwardCompatibility" in content
    ), "MDC2 backward compatibility not specified"

    print("✅ MDC2 format specification is properly defined")


def test_mdc2_migration_strategy():
    """Test that MDC2 migration strategy is defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for migration strategy
    assert ":mdc2Migration" in content, "MDC2 migration strategy not found"
    assert "migrationStrategy" in content, "Migration strategy not specified"
    assert "automatic" in content, "Automatic migration not specified"

    print("✅ MDC2 migration strategy is defined")


def test_mdc2_advantages():
    """Test that MDC2 advantages over legacy MDC are documented."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for documented advantages
    advantages = [
        ":properYamlSchema",
        ":semanticValidation",
        ":machineReadable",
        ":backwardCompatible",
    ]

    for advantage in advantages:
        assert advantage in content, f"MDC2 advantage {advantage} not documented"

    print("✅ MDC2 advantages over legacy MDC are documented")


def test_mdc2_implementation_phases():
    """Test that MDC2 implementation phases are defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for implementation phases
    phases = [":phase1Launch", ":phase2Migration", ":phase3Deprecation"]

    for phase in phases:
        assert phase in content, f"MDC2 implementation phase {phase} not defined"

    print("✅ MDC2 implementation phases are defined")


def test_mdc2_success_metrics():
    """Test that MDC2 success metrics are defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for success metrics
    metrics = [":adoptionRate", ":parsingSuccess", ":semanticValidation"]

    for metric in metrics:
        assert metric in content, f"MDC2 success metric {metric} not defined"

    print("✅ MDC2 success metrics are defined")


def test_mdc2_rule_example():
    """Test that MDC2 rule example is properly formatted."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for MDC2 rule example
    assert ":banEditToolMdc2" in content, "MDC2 rule example not found"
    assert "version" in content, "MDC2 rule version not specified"
    assert "priority" in content, "MDC2 rule priority not specified"
    assert "enforcement" in content, "MDC2 rule enforcement not specified"
    assert "tags" in content, "MDC2 rule tags not specified"

    print("✅ MDC2 rule example is properly formatted")


def test_mdc2_migration_tools():
    """Test that MDC2 migration tools are defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for migration tools
    tools = [":automaticConverter", ":semanticValidator"]

    for tool in tools:
        assert tool in content, f"MDC2 migration tool {tool} not defined"

    print("✅ MDC2 migration tools are defined")


def test_mdc2_file_structure():
    """Test that MDC2 file structure is defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for file structure components
    components = [":yamlFrontmatter", ":markdownContent"]

    for component in components:
        assert (
            component in content
        ), f"MDC2 file structure component {component} not defined"

    print("✅ MDC2 file structure is defined")


def test_mdc2_semantic_consistency():
    """Test that MDC2 ontology maintains semantic consistency with existing rules."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check that MDC2 maintains semantic relationships
    assert "relatedRules" in content, "MDC2 related rules not defined"
    assert "rationale" in content, "MDC2 rationale not defined"
    assert "appliesTo" in content, "MDC2 appliesTo not defined"

    print("✅ MDC2 maintains semantic consistency with existing rules")


def test_mdc2_validation_schema():
    """Test that MDC2 validation schema references are defined."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for validation schema references
    schemas = [
        "mdc2-schema.json",
        "migration-schema.json",
        "mdc2-frontmatter-schema.json",
        "markdown-content-schema.json",
    ]

    for schema in schemas:
        assert schema in content, f"MDC2 validation schema {schema} not referenced"

    print("✅ MDC2 validation schema references are defined")


def test_mdc2_completeness():
    """Test that MDC2 ontology is complete and comprehensive."""
    with open(MDC2_ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check for comprehensive coverage
    required_elements = [
        "Mdc2Rule",
        "Mdc2Format",
        "Mdc2Migration",
        "mdc2Advantages",
        "migrationTools",
        "mdc2FileStructure",
        "implementationStrategy",
        "successMetrics",
    ]

    for element in required_elements:
        assert (
            f":{element}" in content
        ), f"MDC2 ontology missing required element {element}"

    print("✅ MDC2 ontology is complete and comprehensive")
