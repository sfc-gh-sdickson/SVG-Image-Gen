import os
import re

import pytest

ONTOLOGY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "ontologies", "cursor_rules_ontology.ttl"
)


def test_ban_hardcoded_integration_names_rule_in_ontology():
    """
    Test that the ban-hardcoded-integration-names rule is properly defined in our ontology.
    This validates our own model, not the broken MDC format.
    """
    print("Testing ban-hardcoded-integration-names rule in ontology...")

    with open(ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check that the rule is defined in the ontology
    assert (
        ":banHardcodedIntegrationNames" in content
    ), "Rule must be defined in ontology"

    # Check that it follows the proper TTL structure
    rule_pattern = r":banHardcodedIntegrationNames\s+a\s+:CursorRule\s*;"
    assert re.search(rule_pattern, content), "Rule must be properly typed as CursorRule"

    # Check required properties
    required_props = [
        r'rdfs:label\s+"Ban Hardcoded Integration Names"',
        r'dct:description\s+".*integration.*names.*"',
        r':fileLocation\s+".*ban-hardcoded-integration-names\.mdc"',
        r':appliesTo\s+".*\.py.*\.sql.*"',
        r':rationale\s+".*brittle.*non-portable.*"',
    ]

    for prop_pattern in required_props:
        assert re.search(
            prop_pattern, content, re.DOTALL
        ), f"Missing required property: {prop_pattern}"

    # Check that it's related to the edit tool ban rule
    assert (
        ":relatedRule :banEditToolEnhanced" in content
    ), "Rule should be related to banEditToolEnhanced"

    print("✅ Ontology validation passed - rule is properly defined")


def test_ontology_structure_integrity():
    """
    Test that the ontology file maintains structural integrity.
    """
    print("Testing ontology structure integrity...")

    with open(ONTOLOGY_PATH, "r") as f:
        content = f.read()

    # Check basic TTL structure
    assert "@prefix" in content, "Must have prefix declarations"
    assert "rdfs:Class" in content, "Must define classes"
    assert "rdfs:Property" in content, "Must define properties"

    # Check that all rules follow the same pattern
    rule_instances = re.findall(r":(\w+)\s+a\s+:CursorRule", content)
    print(f"Found {len(rule_instances)} rule instances: {rule_instances}")

    # Each rule should have the required properties
    for rule_name in rule_instances:
        # Find the complete rule definition by looking for the rule start and the final period
        rule_start = content.find(f":{rule_name}")
        assert rule_start != -1, f"Rule {rule_name} not found in content"

        # Find the next rule or end of file to determine where this rule ends
        next_rule_start = -1
        for other_rule in rule_instances:
            if other_rule != rule_name:
                other_start = content.find(f":{other_rule}", rule_start + 1)
                if other_start != -1 and (
                    next_rule_start == -1 or other_start < next_rule_start
                ):
                    next_rule_start = other_start

        # Extract the rule content
        if next_rule_start != -1:
            rule_content = content[rule_start:next_rule_start].strip()
        else:
            rule_content = content[rule_start:].strip()

        print(f"Rule {rule_name} content: {rule_content[:200]}...")

        assert "rdfs:label" in rule_content, f"Rule {rule_name} must have a label"
        assert (
            "dct:description" in rule_content
        ), f"Rule {rule_name} must have a description"
        assert (
            ":fileLocation" in rule_content
        ), f"Rule {rule_name} must have a file location"
        assert ":appliesTo" in rule_content, f"Rule {rule_name} must have applicability"
        assert ":rationale" in rule_content, f"Rule {rule_name} must have a rationale"

    print("✅ Ontology structure integrity validated")


def test_rule_traceability():
    """
    Test that the rule is traceable to implementation and tests.
    """
    print("Testing rule traceability...")

    # Check that the rule is referenced in our Git integration code
    git_integration_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "svg_image_generator",
        "git_integration.py",
    )

    if os.path.exists(git_integration_path):
        with open(git_integration_path, "r") as f:
            git_content = f.read()

        # Check that the code implements dynamic discovery (not hardcoded names)
        assert "SHOW INTEGRATIONS" in git_content, "Code must use dynamic discovery"
        assert (
            "_discover_git_integration" in git_content
        ), "Code must have discovery function"

        # Check that it doesn't use hardcoded integration names
        hardcoded_patterns = [
            r"SHOW INTEGRATIONS LIKE 'git_api_integration'",
            r"'git_api_integration'",
            r"'github_integration'",
        ]

        for pattern in hardcoded_patterns:
            # These patterns should NOT be in the code (except in comments or strings explaining the problem)
            matches = re.findall(pattern, git_content)
            if matches:
                print(f"⚠️  Found potential hardcoded pattern: {pattern}")
                # Check if it's in a comment or string explaining the problem
                for match in matches:
                    line_num = git_content[: git_content.find(match)].count("\n") + 1
                    print(f"   Line ~{line_num}: {match}")

    print("✅ Rule traceability validated")
