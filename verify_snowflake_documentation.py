#!/usr/bin/env python3
"""
Script to verify Snowflake documentation and API behavior for file access.
"""

import re

import requests

from src.svg_image_generator.session_manager import get_session


def check_snowflake_docs():
    """Check official Snowflake documentation for file API limitations."""

    # Official Snowflake documentation URLs
    urls = [
        "https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/api/snowflake.snowpark.file.SnowflakeFile.html",
        "https://docs.snowflake.com/en/sql-reference/sql/select.html#file-format-options",
        "https://docs.snowflake.com/en/user-guide/data-load-snowpipe-rest-api.html",
        "https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage.html",
    ]

    print("=== Checking Official Snowflake Documentation ===\n")

    for url in urls:
        print(f"Checking: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text

                # Look for relevant content
                if "get_stream" in content.lower():
                    print("  ✅ get_stream method documented")
                if "subdirectory" in content.lower() or "directory" in content.lower():
                    print("  ✅ Subdirectory/directory content found")
                    # Extract relevant lines
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if (
                            "subdirectory" in line.lower()
                            or "directory" in line.lower()
                        ):
                            print(f"    Line {i}: {line.strip()[:100]}...")
                else:
                    print("  ❌ No subdirectory/directory content found")
            else:
                print(f"  ❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()


def check_api_documentation():
    """Check the actual Python API documentation."""
    print("=== Checking Python API Documentation ===\n")

    try:
        import snowflake.snowpark.file

        help_text = str(snowflake.snowpark.file.SnowflakeFile.get_stream.__doc__)
        print("get_stream method documentation:")
        print(help_text)

        # Look for limitations or restrictions
        if "subdirectory" in help_text.lower() or "directory" in help_text.lower():
            print("\n✅ Subdirectory/directory mentioned in API docs")
        else:
            print("\n❌ No subdirectory/directory limitations mentioned")

    except Exception as e:
        print(f"Error accessing API docs: {e}")


def test_actual_behavior():
    """Test the actual API behavior with documented examples."""
    print("\n=== Testing Actual API Behavior ===\n")

    try:
        session = get_session()

        # Test 1: Root file (should work)
        print("Test 1: Reading root file (should work)")
        try:
            with session.file.get_stream(
                "@CONTAINER_DB.PUBLIC.SPECS/Data_Share_Logo.svg"
            ) as f:
                content = f.read()
                print("  ✅ Root file read successful")
        except Exception as e:
            print(f"  ❌ Root file read failed: {e}")

        # Test 2: Subdirectory file (our issue)
        print("\nTest 2: Reading subdirectory file (our issue)")
        try:
            with session.file.get_stream(
                "@CONTAINER_DB.PUBLIC.SPECS/specs/Data_Share_Logo.svg"
            ) as f:
                content = f.read()
                print("  ✅ Subdirectory file read successful")
        except Exception as e:
            print(f"  ❌ Subdirectory file read failed: {e}")

    except Exception as e:
        print(f"Error in API test: {e}")


if __name__ == "__main__":
    check_snowflake_docs()
    check_api_documentation()
    test_actual_behavior()
