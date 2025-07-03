#!/usr/bin/env python3
"""
CLI test to prove the app's file reading logic works with the actual stage structure.
"""

import sys

from svg_image_generator.session_manager import get_session


def test_app_file_reading():
    print("=== App Integration Test ===")

    try:
        session = get_session()
        print(f"✓ Created Snowflake session: {session}")
    except Exception as e:
        print(f"✗ Failed to create Snowflake session: {e}")
        return False

    # Test the exact file paths the app will use
    stage_name = "CONTAINER_DB.PUBLIC.SPECS"

    print(f"\n--- Testing app's file listing logic ---")
    try:
        list_command = f"LIST @{stage_name}"
        print(f"Executing: {list_command}")
        files_df = session.sql(list_command).collect()
        print(f"✓ Stage listing successful, found {len(files_df)} files")

        # Show all SVG files found and extract filenames
        svg_files = []
        for row in files_df:
            relative_path = row["name"]
            if relative_path.lower().endswith(".svg"):
                # Extract filename from path (e.g., "specs/Data_Share_Logo.svg" -> "Data_Share_Logo.svg")
                filename = relative_path.split("/")[-1]
                svg_files.append(filename)
                print(f"  SVG: {relative_path} -> {filename}")

        print(f"\nFound {len(svg_files)} SVG files")

        if not svg_files:
            print("✗ No SVG files found - app will show empty list")
            return False

    except Exception as e:
        print(f"✗ Stage listing failed: {e}")
        return False

    # Test reading the first SVG file using app's exact path construction
    if svg_files:
        test_file = svg_files[0]
        app_file_path = f"@{stage_name}/{test_file}"

        print(f"\n--- Testing app's file reading logic ---")
        print(f"App will construct path: {app_file_path}")

        try:
            with session.file.get_stream(app_file_path) as f:
                content = f.read().decode("utf-8")
                print(f"✓ App's file reading successful!")
                print(f"  Content length: {len(content)} characters")
                print(f"  First 100 chars: {content[:100]}...")
                if content.strip().startswith("<svg"):
                    print(f"✓ Content is valid SVG")
                    return True
                else:
                    print(f"✗ Content is not valid SVG")
                    return False
        except Exception as e:
            print(f"✗ App's file reading failed: {e}")
            return False

    return False


if __name__ == "__main__":
    success = test_app_file_reading()
    print(f"\n=== Test Result ===")
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    sys.exit(0 if success else 1)
