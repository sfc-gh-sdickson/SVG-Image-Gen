#!/usr/bin/env python3
"""
Upload SVG files to Snowflake stage root level.
WORKAROUND: Snowflake file API only works with files at stage root.
Files in subdirectories fail with "file does not exist" error.
See: snowflake_file_api_bug_report.md for details.
"""

import os
import sys

from src.svg_image_generator.session_manager import get_session


def upload_svg_to_root(local_file_path, database, schema, stage):
    """Upload a single SVG file to the root of a Snowflake stage."""
    if not os.path.exists(local_file_path):
        print(f"❌ File not found: {local_file_path}")
        return False

    if not local_file_path.lower().endswith(".svg"):
        print(f"❌ Not an SVG file: {local_file_path}")
        return False

    try:
        session = get_session()

        # Upload to 'specs/' subdirectory (effective root)
        stage_path = (
            f"@{database}.{schema}.{stage}/specs/{os.path.basename(local_file_path)}"
        )
        print(f"📤 Uploading {local_file_path} to {stage_path}")

        put_result = session.file.put(
            local_file_path, stage_path, auto_compress=False, overwrite=True
        )
        print(f"✅ Upload successful: {put_result}")
        return True

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def upload_multiple_svgs(local_directory, database, schema, stage):
    """Upload all SVG files from a local directory to stage root."""
    if not os.path.exists(local_directory):
        print(f"❌ Directory not found: {local_directory}")
        return

    svg_files = [f for f in os.listdir(local_directory) if f.lower().endswith(".svg")]

    if not svg_files:
        print(f"❌ No SVG files found in: {local_directory}")
        return

    print(f"📁 Found {len(svg_files)} SVG files to upload")

    success_count = 0
    for svg_file in svg_files:
        local_path = os.path.join(local_directory, svg_file)
        if upload_svg_to_root(local_path, database, schema, stage):
            success_count += 1

    print(f"\n📊 Upload Summary:")
    print(f"✅ Successfully uploaded: {success_count}/{len(svg_files)} files")
    print(f"📋 Files are now available at: @{database}.{schema}.{stage}/")
    print(f"💡 These files can be read by the SVG display app")


def main():
    if len(sys.argv) < 5:
        print("Usage:")
        print(
            "  Single file: python upload_svgs_to_root.py <file.svg> <database> <schema> <stage>"
        )
        print(
            "  Directory:   python upload_svgs_to_root.py <directory> <database> <schema> <stage> --dir"
        )
        print("\nExample:")
        print("  python upload_svgs_to_root.py logos/ CONTAINER_DB PUBLIC SPECS --dir")
        print(
            "  python upload_svgs_to_root.py Data_Share_Logo.svg CONTAINER_DB PUBLIC SPECS"
        )
        sys.exit(1)

    if len(sys.argv) == 6 and sys.argv[5] == "--dir":
        # Upload all SVGs from directory
        local_path, database, schema, stage = sys.argv[1:5]
        upload_multiple_svgs(local_path, database, schema, stage)
    elif len(sys.argv) == 5:
        # Upload single file
        local_path, database, schema, stage = sys.argv[1:5]
        upload_svg_to_root(local_path, database, schema, stage)
    else:
        print("❌ Invalid arguments")
        print(f"Got {len(sys.argv)} arguments: {sys.argv}")
        sys.exit(1)


if __name__ == "__main__":
    main()
