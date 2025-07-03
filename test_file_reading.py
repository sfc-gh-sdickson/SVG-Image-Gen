#!/usr/bin/env python3
"""
Test script: Read individual files from Snowflake stage
Mirrors the read_svg_content_from_stage function from display_svg_from_stage.py
"""

import sys

from src.svg_image_generator.session_manager import get_session


def test_read_file_from_stage(svg_file_path):
    """Test reading a file from stage - mirrors app function"""
    print(f"=== Testing file read: {svg_file_path} ===")

    if not svg_file_path:
        print("ERROR: No file path provided")
        return None

    try:
        session = get_session()

        # Ensure we have a fully qualified stage path
        if not svg_file_path.startswith("@"):
            print(f"ERROR: Invalid stage path: {svg_file_path}. Must start with @")
            return None

        # Check if this is a subdirectory path (contains / after the stage name)
        stage_parts = svg_file_path.split("/")
        print(f"Path parts: {stage_parts}")
        print(f"Number of parts: {len(stage_parts)}")

        if (
            len(stage_parts) > 2
        ):  # @db.schema.stage/file or @db.schema.stage/subdir/file
            print(f"File is in subdirectory, using SQL fallback")
            # Use SQL query for subdirectory files (session.file.get_stream() doesn't work with subdirs)
            sql_query = f"SELECT LISTAGG($1, '') FROM {svg_file_path}"
            print(f"Executing SQL: {sql_query}")

            result = session.sql(sql_query).collect()
            print(f"SQL result: {result}")

            if result and result[0][0]:
                content = result[0][0]
                print(f"SUCCESS: Got {len(content)} characters via SQL")
                print(f"First 100 chars: {content[:100]}...")
                return content
            else:
                print(f"ERROR: No content returned from SQL query")
                return None
        else:
            # File is at root level, use file API
            print(f"File is at root level, using file API")
            print(f"Attempting session.file.get_stream({svg_file_path})")

            with session.file.get_stream(svg_file_path, decompress=False) as f:
                content = f.read().decode("utf-8")
                print(f"SUCCESS: Got {len(content)} characters via file API")
                print(f"First 100 chars: {content[:100]}...")
                return content

    except Exception as e:
        print(f"ERROR reading file '{svg_file_path}': {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_file_reading.py <stage_path>")
        print(
            "Example: python test_file_reading.py '@CONTAINER_DB.PUBLIC.SPECS/specs/Data_Share_Logo.svg'"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    content = test_read_file_from_stage(file_path)

    if content:
        print(f"\n=== SUCCESS: File read successfully ===")
        print(f"Content length: {len(content)} characters")
    else:
        print(f"\n=== FAILED: Could not read file ===")
