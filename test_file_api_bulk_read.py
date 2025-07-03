#!/usr/bin/env python3
"""
Test script: Bulk read all files in a Snowflake stage using the file API only.
Lists all files, attempts to read each with session.file.get_stream, and reports results.
"""

import sys

from src.svg_image_generator.session_manager import get_session


def list_stage_files(session, database_name, schema_name, stage_name):
    stage_path = f"@{database_name}.{schema_name}.{stage_name}"
    files_df = session.sql(f"LIST {stage_path}").collect()
    return [f"{stage_path}/{row['name']}" for row in files_df]


def read_file_from_stage(session, stage_path):
    try:
        with session.file.get_stream(stage_path, decompress=False) as f:
            content = f.read().decode("utf-8")
            return content
    except Exception as e:
        return f"ERROR: {e}"


def main():
    if len(sys.argv) != 4:
        print("Usage: python test_file_api_bulk_read.py <database> <schema> <stage>")
        print("Example: python test_file_api_bulk_read.py CONTAINER_DB PUBLIC SPECS")
        sys.exit(1)
    database, schema, stage = sys.argv[1:4]
    session = get_session()
    files = list_stage_files(session, database, schema, stage)
    print(
        f"\n=== Attempting to read {len(files)} files from @{database}.{schema}.{stage} ===\n"
    )
    for i, file_path in enumerate(files):
        print(f"[{i}] {file_path}")
        result = read_file_from_stage(session, file_path)
        if isinstance(result, str) and not result.startswith("ERROR"):
            print(f"  SUCCESS: Read {len(result)} chars. First 100: {result[:100]!r}\n")
        else:
            print(f"  FAIL: {result}\n")


if __name__ == "__main__":
    main()
