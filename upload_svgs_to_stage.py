#!/usr/bin/env python3
"""
Upload SVG files to Snowflake stage
"""

import glob
import os
from pathlib import Path

# Try to get active session first (for SiS)
try:
    from snowflake.snowpark.context import get_active_session

    session = get_active_session()
    print("Connected using active Snowflake session")
except Exception:
    # Fallback to local development
    from src.svg_image_generator.session_manager import get_session

    session = get_session()
    print("Connected using local session")


def upload_svg_to_stage(file_path, stage_name="@CONTAINER_DB.PUBLIC.SPECS"):
    """Upload a single SVG file to the stage"""
    try:
        file_name = os.path.basename(file_path)
        print(f"Uploading {file_name} to {stage_name}...")

        # Set database context - use fully qualified names to avoid current database issues
        # session.sql("USE DATABASE CONTAINER_DB").collect()
        # session.sql("USE SCHEMA PUBLIC").collect()

        # Use session.file.put() to upload the file directly
        session.file.put(file_path, stage_name, auto_compress=False, overwrite=True)

        print(f"✅ Successfully uploaded {file_name}")
        return True

    except Exception as e:
        print(f"❌ Error uploading {file_name}: {e}")
        return False


def main():
    """Upload all SVG files from logos directory"""
    logos_dir = Path("logos")
    svg_files = list(logos_dir.glob("*.svg"))

    if not svg_files:
        print("No SVG files found in logos directory")
        return

    print(f"Found {len(svg_files)} SVG files to upload:")
    for svg_file in svg_files:
        print(f"  - {svg_file.name}")

    print("\nStarting upload...")
    successful = 0
    failed = 0

    for svg_file in svg_files:
        if upload_svg_to_stage(str(svg_file)):
            successful += 1
        else:
            failed += 1

    print(f"\nUpload complete: {successful} successful, {failed} failed")

    # List files in stage
    print("\nFiles in stage:")
    try:
        files = session.sql("LIST @CONTAINER_DB.PUBLIC.SPECS").collect()
        for file in files:
            print(f"  {file[0]}")
    except Exception as e:
        print(f"Error listing stage contents: {e}")


if __name__ == "__main__":
    main()
