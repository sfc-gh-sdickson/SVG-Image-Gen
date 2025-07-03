#!/usr/bin/env python3
"""
Test script: Check all possible stage path variations for file API access.
Tests root files, subdirectory files, and various path formats.
"""

import sys

from src.svg_image_generator.session_manager import get_session


def test_path_variation(session, test_name, stage_path, expected_to_work=True):
    """Test a specific path variation and report results."""
    print(f"\n=== {test_name} ===")
    print(f"Path: {stage_path}")
    print(f"Expected: {'WORK' if expected_to_work else 'FAIL'}")

    try:
        with session.file.get_stream(stage_path, decompress=False) as f:
            content = f.read()
            print(f"✅ ACTUAL: WORKED - Read {len(content)} characters")
            print(f"   First 50 chars: {content[:50]!r}")
            return True
    except Exception as e:
        print(f"❌ ACTUAL: FAILED - {e}")
        return False


def main():
    if len(sys.argv) != 4:
        print("Usage: python test_stage_path_variations.py <database> <schema> <stage>")
        print("Example: python test_stage_path_variations.py CONTAINER_DB PUBLIC SPECS")
        sys.exit(1)

    database, schema, stage = sys.argv[1:4]
    session = get_session()

    print(f"=== Testing Stage Path Variations for @{database}.{schema}.{stage} ===")

    # Test 1: Root file (we know this works)
    test_path_variation(
        session,
        "Test 1: Root file",
        f"@{database}.{schema}.{stage}/Data_Share_Logo.svg",
        expected_to_work=True,
    )

    # Test 2: Subdirectory file (we know this fails)
    test_path_variation(
        session,
        "Test 2: Subdirectory file",
        f"@{database}.{schema}.{stage}/specs/Data_Share_Logo.svg",
        expected_to_work=False,
    )

    # Test 3: Stage name in path (NEW TEST)
    test_path_variation(
        session,
        "Test 3: Stage name in path",
        f"@{database}.{schema}.{stage}/{stage}/Data_Share_Logo.svg",
        expected_to_work=False,  # Let's see if this fails too
    )

    # Test 4: Database name in path (NEW TEST)
    test_path_variation(
        session,
        "Test 4: Database name in path",
        f"@{database}.{schema}.{stage}/{database}/Data_Share_Logo.svg",
        expected_to_work=False,  # Let's see if this fails too
    )

    # Test 5: Schema name in path (NEW TEST)
    test_path_variation(
        session,
        "Test 5: Schema name in path",
        f"@{database}.{schema}.{stage}/{schema}/Data_Share_Logo.svg",
        expected_to_work=False,  # Let's see if this fails too
    )

    # Test 6: Multiple subdirectories (NEW TEST)
    test_path_variation(
        session,
        "Test 6: Multiple subdirectories",
        f"@{database}.{schema}.{stage}/specs/subdir/Data_Share_Logo.svg",
        expected_to_work=False,
    )

    # Test 7: File with dots in name (NEW TEST)
    test_path_variation(
        session,
        "Test 7: File with dots in name",
        f"@{database}.{schema}.{stage}/test.file.svg",
        expected_to_work=True,  # Should work if we upload it
    )

    print(f"\n=== Summary ===")
    print("This test will help identify if the limitation is:")
    print("1. Only subdirectories")
    print("2. Any path with stage/database/schema names")
    print("3. Any path deeper than root level")


if __name__ == "__main__":
    main()
