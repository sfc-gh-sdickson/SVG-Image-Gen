#!/usr/bin/env python3
"""
CLI test script to verify SQL approach for reading SVG files from Snowflake stages.
This tests the LISTAGG method that concatenates file lines into a single result.
"""

import os
import sys

import snowflake.snowpark.session

from svg_image_generator.session_manager import get_session


def test_sql_svg_reading():
    """Test reading SVG files using SQL LISTAGG approach."""

    print("=== SQL SVG Reading Test ===")

    # Get session
    try:
        session = get_session()
        print(f"✓ Created Snowflake session: {session}")
    except Exception as e:
        print(f"✗ Failed to create Snowflake session: {e}")
        return False

    # Test stage listing first
    stage_name = "CONTAINER_DB.PUBLIC.SPECS"
    print(f"\n--- Testing stage listing for {stage_name} ---")

    try:
        list_query = f"LIST @{stage_name}"
        print(f"Executing: {list_query}")
        result = session.sql(list_query).collect()
        print(f"✓ Stage listing successful, found {len(result)} files")

        # Show first few files
        for i, row in enumerate(result[:5]):
            print(f"  {i+1}. {row['name']}")

        if len(result) > 5:
            print(f"  ... and {len(result) - 5} more files")

    except Exception as e:
        print(f"✗ Stage listing failed: {e}")
        return False

    # Test SQL reading for a specific file
    test_file = "Data_Share_Logo.svg"  # Root level file
    print(f"\n--- Testing SQL reading for {test_file} ---")

    try:
        # SQL query to read file using LISTAGG
        sql_query = f"""
        SELECT LISTAGG($1, '\n') WITHIN GROUP (ORDER BY METADATA$FILE_ROW_NUMBER) as file_content
        FROM @{stage_name}/{test_file}
        """

        print(f"Executing SQL query:")
        print(f"  {sql_query}")

        result = session.sql(sql_query).collect()

        if result and len(result) > 0:
            file_content = result[0]["FILE_CONTENT"]
            if file_content:
                print(f"✓ SQL reading successful!")
                print(f"  Content length: {len(file_content)} characters")
                print(f"  First 100 chars: {file_content[:100]}...")
                print(f"  Last 100 chars: ...{file_content[-100:]}")

                # Check if it looks like SVG
                if file_content.strip().startswith("<svg"):
                    print(f"✓ Content appears to be valid SVG")
                else:
                    print(f"⚠ Content doesn't start with <svg tag")

                return True
            else:
                print(f"✗ SQL query returned empty content")
                return False
        else:
            print(f"✗ SQL query returned no results")
            return False

    except Exception as e:
        print(f"✗ SQL reading failed: {e}")
        return False


def test_sql_svg_reading_subdirectory():
    """Test reading SVG files from subdirectories using SQL."""

    print("\n=== SQL SVG Reading from Subdirectory Test ===")

    try:
        session = get_session()
    except Exception as e:
        print(f"✗ Failed to create Snowflake session: {e}")
        return False

    # Test subdirectory file
    test_file = "specs/Data_Share_Logo.svg"  # Subdirectory file
    stage_name = "CONTAINER_DB.PUBLIC.SPECS"

    print(f"\n--- Testing SQL reading for {test_file} ---")

    try:
        # SQL query to read file using LISTAGG
        sql_query = f"""
        SELECT LISTAGG($1, '\n') WITHIN GROUP (ORDER BY METADATA$FILE_ROW_NUMBER) as file_content
        FROM @{stage_name}/{test_file}
        """

        print(f"Executing SQL query:")
        print(f"  {sql_query}")

        result = session.sql(sql_query).collect()

        if result and len(result) > 0:
            file_content = result[0]["FILE_CONTENT"]
            if file_content:
                print(f"✓ SQL reading from subdirectory successful!")
                print(f"  Content length: {len(file_content)} characters")
                print(f"  First 100 chars: {file_content[:100]}...")
                return True
            else:
                print(f"✗ SQL query returned empty content")
                return False
        else:
            print(f"✗ SQL query returned no results")
            return False

    except Exception as e:
        print(f"✗ SQL reading from subdirectory failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting SQL SVG reading tests...")

    # Test root file
    root_success = test_sql_svg_reading()

    # Test subdirectory file
    subdir_success = test_sql_svg_reading_subdirectory()

    print(f"\n=== Test Results ===")
    print(f"Root file SQL reading: {'✓ PASS' if root_success else '✗ FAIL'}")
    print(f"Subdirectory SQL reading: {'✓ PASS' if subdir_success else '✗ FAIL'}")

    if root_success and subdir_success:
        print(
            f"\n✓ All tests passed! SQL approach works for both root and subdirectory files."
        )
        sys.exit(0)
    elif root_success:
        print(f"\n⚠ SQL approach works for root files only.")
        sys.exit(1)
    else:
        print(f"\n✗ SQL approach failed completely.")
        sys.exit(1)
