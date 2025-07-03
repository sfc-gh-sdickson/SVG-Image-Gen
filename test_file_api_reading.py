#!/usr/bin/env python3
"""
CLI test script to verify Snowpark file API (session.file.get_stream) for reading SVG files from Snowflake stages.
"""

import sys

from svg_image_generator.session_manager import get_session


def test_file_api_reading():
    print("=== Snowpark File API Reading Test ===")
    try:
        session = get_session()
        print(f"✓ Created Snowflake session: {session}")
    except Exception as e:
        print(f"✗ Failed to create Snowflake session: {e}")
        return False

    # Test root file
    root_path = "@CONTAINER_DB.PUBLIC.SPECS/Data_Share_Logo.svg"
    print(f"\n--- Testing file API reading for root file: {root_path} ---")
    try:
        with session.file.get_stream(root_path) as f:
            content = f.read().decode("utf-8")
            print(f"✓ File API reading successful!")
            print(f"  Content length: {len(content)} characters")
            print(f"  First 100 chars: {content[:100]}...")
            print(f"  Last 100 chars: ...{content[-100:]}")
            if content.strip().startswith("<svg"):
                print(f"✓ Content appears to be valid SVG")
            else:
                print(f"⚠ Content doesn't start with <svg tag")
    except Exception as e:
        print(f"✗ File API reading failed for root file: {e}")

    # Test subdirectory file
    subdir_path = "@CONTAINER_DB.PUBLIC.SPECS/specs/Data_Share_Logo.svg"
    print(f"\n--- Testing file API reading for subdirectory file: {subdir_path} ---")
    try:
        with session.file.get_stream(subdir_path) as f:
            content = f.read().decode("utf-8")
            print(f"✓ File API reading from subdirectory successful!")
            print(f"  Content length: {len(content)} characters")
            print(f"  First 100 chars: {content[:100]}...")
    except Exception as e:
        print(f"✗ File API reading failed for subdirectory file: {e}")


if __name__ == "__main__":
    test_file_api_reading()
