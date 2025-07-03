#!/usr/bin/env python3
"""
Test script: List files in Snowflake stage
Mirrors the get_svg_file_paths_in_stage function from display_svg_from_stage.py
"""

import sys

from src.svg_image_generator.session_manager import get_session


def test_list_stage_files(database_name, schema_name, stage_name):
    """Test listing files in a stage - mirrors app function"""
    print(
        f"=== Testing LIST command for @{database_name}.{schema_name}.{stage_name} ==="
    )

    try:
        session = get_session()

        # Use the fully qualified stage name that matches the upload script
        stage_path = f"@{database_name}.{schema_name}.{stage_name}"
        list_command = f"LIST {stage_path}"
        print(f"Executing: {list_command}")

        files_df = session.sql(list_command).collect()
        print(f"Raw LIST results: {len(files_df)} items")

        svg_full_paths = []
        for i, row in enumerate(files_df):
            # The row['name'] contains the relative path within the stage
            relative_path = row["name"]
            print(f"  [{i}] Found file: {relative_path}")

            # Only include .svg files, not the compressed .csv.gz versions
            if relative_path.lower().endswith(
                ".svg"
            ) and not relative_path.lower().endswith(".csv.gz"):
                # Construct the full stage path
                full_stage_path = f"{stage_path}/{relative_path}"
                svg_full_paths.append(full_stage_path)
                print(f"    -> Added SVG: {full_stage_path}")
            else:
                print(f"    -> Skipped (not SVG or compressed)")

        print(f"\nFinal SVG files found: {len(svg_full_paths)}")
        for i, path in enumerate(svg_full_paths):
            print(f"  [{i}] {path}")

        return svg_full_paths

    except Exception as e:
        print(f"ERROR: {e}")
        return []


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python test_stage_listing.py <database> <schema> <stage>")
        print("Example: python test_stage_listing.py CONTAINER_DB PUBLIC SPECS")
        sys.exit(1)

    database = sys.argv[1]
    schema = sys.argv[2]
    stage = sys.argv[3]

    files = test_list_stage_files(database, schema, stage)
    print(f"\n=== RESULT: {len(files)} SVG files found ===")
