#!/usr/bin/env python3
"""
Test script: Upload a local SVG to the root of a Snowflake stage and read it back using the file API.
"""
import sys

from src.svg_image_generator.session_manager import get_session


def upload_file_to_stage_root(session, local_path, database, schema, stage):
    stage_path = f"@{database}.{schema}.{stage}/{local_path.split('/')[-1]}"
    print(f"Uploading {local_path} to {stage_path} (root of stage)...")
    put_result = session.file.put(
        local_path, stage_path, auto_compress=False, overwrite=True
    )
    print(f"PUT result: {put_result}")
    return stage_path


def read_file_from_stage(session, stage_path):
    try:
        with session.file.get_stream(stage_path, decompress=False) as f:
            content = f.read().decode("utf-8")
            return content
    except Exception as e:
        return f"ERROR: {e}"


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: python test_file_api_root_upload_and_read.py <local_svg_path> <database> <schema> <stage>"
        )
        print(
            "Example: python test_file_api_root_upload_and_read.py Data_Share_Logo.svg CONTAINER_DB PUBLIC SPECS"
        )
        sys.exit(1)
    local_path, database, schema, stage = sys.argv[1:5]
    session = get_session()
    stage_path = upload_file_to_stage_root(session, local_path, database, schema, stage)
    print(f"\nAttempting to read back: {stage_path}")
    result = read_file_from_stage(session, stage_path)
    if isinstance(result, str) and not result.startswith("ERROR"):
        print(f"SUCCESS: Read {len(result)} chars. First 100: {result[:100]!r}")
    else:
        print(f"FAIL: {result}")


if __name__ == "__main__":
    main()
