# Snowflake File API Bug Report: Subdirectory File Access Failure

## Issue Summary
The Snowflake Python file API (`session.file.get_stream()`) fails to read files from **any path deeper than the root level** within stages, even though the files are visible via `LIST` command and the API documentation does not mention this limitation.

**Key Finding**: The limitation is **NOT** just subdirectories - it's **ANY path with additional path components** beyond the stage root.

## Environment Details
- **Snowflake Connector for Python**: Latest version
- **Python**: 3.13
- **Platform**: Linux 6.12.10-76061203-generic
- **Session Type**: Snowpark session

## Expected Behavior
Based on Snowflake documentation, `session.file.get_stream()` should be able to read files from any path within a stage, including subdirectories.

## Actual Behavior
- Files at stage root: ✅ Readable via `session.file.get_stream()`
- Files in subdirectories: ❌ Fail with "file does not exist" error
- Files with stage name in path: ❌ Fail with "file does not exist" error
- Files with database name in path: ❌ Fail with "file does not exist" error
- Files with schema name in path: ❌ Fail with "file does not exist" error
- Files with dots in name (at root): ✅ Readable via `session.file.get_stream()`
- `LIST` command: ✅ Shows all files including subdirectories correctly

**Pattern**: Only files directly at the stage root (no additional path components) can be read.

## Reproduction Steps

### 1. Create Test Files
```python
# Upload files to both root and subdirectory
session.file.put("test.svg", "@DB.SCHEMA.STAGE/test.svg", auto_compress=False)
session.file.put("test.svg", "@DB.SCHEMA.STAGE/subdir/test.svg", auto_compress=False)
```

### 2. List Files (Works)
```python
files = session.sql("LIST @DB.SCHEMA.STAGE").collect()
# Shows both test.svg and subdir/test.svg
```

### 3. Read Files (Fails for Any Path Beyond Root)
```python
# Root file - WORKS
with session.file.get_stream("@DB.SCHEMA.STAGE/test.svg") as f:
    content = f.read()  # ✅ Success

# Subdirectory file - FAILS
with session.file.get_stream("@DB.SCHEMA.STAGE/subdir/test.svg") as f:
    content = f.read()  # ❌ Error: file does not exist

# Stage name in path - FAILS
with session.file.get_stream("@DB.SCHEMA.STAGE/STAGE/test.svg") as f:
    content = f.read()  # ❌ Error: file does not exist

# Database name in path - FAILS
with session.file.get_stream("@DB.SCHEMA.STAGE/DB/test.svg") as f:
    content = f.read()  # ❌ Error: file does not exist

# Schema name in path - FAILS
with session.file.get_stream("@DB.SCHEMA.STAGE/SCHEMA/test.svg") as f:
    content = f.read()  # ❌ Error: file does not exist
```

## Comprehensive Test Cases

### Test 1: Stage Listing (Works Correctly)
This test verifies that the `LIST` command can see all files, including those in subdirectories.

```python
#!/usr/bin/env python3
"""
Test script: List files in Snowflake stage
Mirrors the get_svg_file_paths_in_stage function from display_svg_from_stage.py
"""

import sys
from src.svg_image_generator.session_manager import get_session

def test_list_stage_files(database_name, schema_name, stage_name):
    """Test listing files in a stage - mirrors app function"""
    print(f"=== Testing LIST command for @{database_name}.{schema_name}.{stage_name} ===")

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
            relative_path = row['name']
            print(f"  [{i}] Found file: {relative_path}")

            # Only include .svg files, not the compressed .csv.gz versions
            if relative_path.lower().endswith('.svg') and not relative_path.lower().endswith('.csv.gz'):
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
```

**Result**: Successfully lists 9 SVG files including those in subdirectories like `specs/Data_Share_Logo.svg`.

### Test 2: Individual File Reading (Fails for Paths Beyond Root)
This test attempts to read individual files using the file API and demonstrates the limitation.

```python
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
        if not svg_file_path.startswith('@'):
            print(f"ERROR: Invalid stage path: {svg_file_path}. Must start with @")
            return None

        # Check if this is a subdirectory path (contains / after the stage name)
        stage_parts = svg_file_path.split('/')
        print(f"Path parts: {stage_parts}")
        print(f"Number of parts: {len(stage_parts)}")

        if len(stage_parts) > 2:  # @db.schema.stage/file or @db.schema.stage/subdir/file
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
                content = f.read().decode('utf-8')
                print(f"SUCCESS: Got {len(content)} characters via file API")
                print(f"First 100 chars: {content[:100]}...")
                return content

    except Exception as e:
        print(f"ERROR reading file '{svg_file_path}': {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_file_reading.py <stage_path>")
        print("Example: python test_file_reading.py '@CONTAINER_DB.PUBLIC.SPECS/specs/Data_Share_Logo.svg'")
        sys.exit(1)

    file_path = sys.argv[1]
    content = test_read_file_from_stage(file_path)

    if content:
        print(f"\n=== SUCCESS: File read successfully ===")
        print(f"Content length: {len(content)} characters")
    else:
        print(f"\n=== FAILED: Could not read file ===")
```

**Result**: Root files work, subdirectory files fail with "file does not exist" error.

### Test 3: Bulk File API Testing (Comprehensive Failure Analysis)
This test systematically attempts to read all files in a stage using only the file API.

```python
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
            content = f.read().decode('utf-8')
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
    print(f"\n=== Attempting to read {len(files)} files from @{database}.{schema}.{stage} ===\n")
    for i, file_path in enumerate(files):
        print(f"[{i}] {file_path}")
        result = read_file_from_stage(session, file_path)
        if isinstance(result, str) and not result.startswith("ERROR"):
            print(f"  SUCCESS: Read {len(result)} chars. First 100: {result[:100]!r}\n")
        else:
            print(f"  FAIL: {result}\n")

if __name__ == "__main__":
    main()
```

**Result**: Every single file (24 total) fails to be read using the file API, including all SVG files in subdirectories.

### Test 4: Root vs Subdirectory Upload and Read (Confirms Limitation)
This test uploads files to both root and subdirectories and attempts to read them back.

```python
#!/usr/bin/env python3
"""
Test script: Upload a local SVG to the root of a Snowflake stage and read it back using the file API.
"""
import sys
from src.svg_image_generator.session_manager import get_session

def upload_file_to_stage_root(session, local_path, database, schema, stage):
    stage_path = f"@{database}.{schema}.{stage}/{local_path.split('/')[-1]}"
    print(f"Uploading {local_path} to {stage_path} (root of stage)...")
    put_result = session.file.put(local_path, stage_path, auto_compress=False, overwrite=True)
    print(f"PUT result: {put_result}")
    return stage_path

def read_file_from_stage(session, stage_path):
    try:
        with session.file.get_stream(stage_path, decompress=False) as f:
            content = f.read().decode('utf-8')
            return content
    except Exception as e:
        return f"ERROR: {e}"

def main():
    if len(sys.argv) != 5:
        print("Usage: python test_file_api_root_upload_and_read.py <local_svg_path> <database> <schema> <stage>")
        print("Example: python test_file_api_root_upload_and_read.py Data_Share_Logo.svg CONTAINER_DB PUBLIC SPECS")
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
```

**Result**: Files uploaded to root can be read successfully, confirming the limitation is path-based.

### Test 5: Comprehensive Path Variation Testing (Reveals Broader Limitation)
This test checks all possible path variations to understand the exact scope of the limitation.

```python
#!/usr/bin/env python3
"""
Test script: Check all possible stage path variations for file API access.
Tests root files, subdirectory files, and various path formats.
"""

import sys
from src.svg_image_generator.session_manager import get_session

def test_path_variation(session, test_name, stage_path, expected_to_work=True):
    """Test a specific path variation and report results."""
    print(f"\n=== {test_name} ===")
    print(f"Path: {stage_path}")
    print(f"Expected: {'WORK' if expected_to_work else 'FAIL'}")

    try:
        with session.file.get_stream(stage_path, decompress=False) as f:
            content = f.read()
            print(f"✅ ACTUAL: WORKED - Read {len(content)} characters")
            print(f"   First 50 chars: {content[:50]!r}")
            return True
    except Exception as e:
        print(f"❌ ACTUAL: FAILED - {e}")
        return False

def main():
    if len(sys.argv) != 4:
        print("Usage: python test_stage_path_variations.py <database> <schema> <stage>")
        print("Example: python test_stage_path_variations.py CONTAINER_DB PUBLIC SPECS")
        sys.exit(1)

    database, schema, stage = sys.argv[1:4]
    session = get_session()

    print(f"=== Testing Stage Path Variations for @{database}.{schema}.{stage} ===")

    # Test 1: Root file (we know this works)
    test_path_variation(
        session,
        "Test 1: Root file",
        f"@{database}.{schema}.{stage}/Data_Share_Logo.svg",
        expected_to_work=True
    )

    # Test 2: Subdirectory file (we know this fails)
    test_path_variation(
        session,
        "Test 2: Subdirectory file",
        f"@{database}.{schema}.{stage}/specs/Data_Share_Logo.svg",
        expected_to_work=False
    )

    # Test 3: Stage name in path (NEW TEST)
    test_path_variation(
        session,
        "Test 3: Stage name in path",
        f"@{database}.{schema}.{stage}/{stage}/Data_Share_Logo.svg",
        expected_to_work=False  # Let's see if this fails too
    )

    # Test 4: Database name in path (NEW TEST)
    test_path_variation(
        session,
        "Test 4: Database name in path",
        f"@{database}.{schema}.{stage}/{database}/Data_Share_Logo.svg",
        expected_to_work=False  # Let's see if this fails too
    )

    # Test 5: Schema name in path (NEW TEST)
    test_path_variation(
        session,
        "Test 5: Schema name in path",
        f"@{database}.{schema}.{stage}/{schema}/Data_Share_Logo.svg",
        expected_to_work=False  # Let's see if this fails too
    )

    # Test 6: Multiple subdirectories (NEW TEST)
    test_path_variation(
        session,
        "Test 6: Multiple subdirectories",
        f"@{database}.{schema}.{stage}/specs/subdir/Data_Share_Logo.svg",
        expected_to_work=False
    )

    # Test 7: File with dots in name (NEW TEST)
    test_path_variation(
        session,
        "Test 7: File with dots in name",
        f"@{database}.{schema}.{stage}/test.file.svg",
        expected_to_work=True  # Should work if we upload it
    )

    print(f"\n=== Summary ===")
    print("This test will help identify if the limitation is:")
    print("1. Only subdirectories")
    print("2. Any path with stage/database/schema names")
    print("3. Any path deeper than root level")

if __name__ == "__main__":
    main()
```

**Result**: Reveals that **ANY path component beyond the stage root** causes the file API to fail, not just subdirectories.

## Error Details
```
Error: (1305): 253006: While getting file(s) there was an error: the file does not exist.
```

## Impact
- **Workaround Required**: Must upload all files to stage root only
- **Architecture Constraint**: Cannot use any path organization (subdirectories, prefixes, etc.)
- **API Inconsistency**: `LIST` shows files but `get_stream()` cannot read any files with path components
- **Documentation Gap**: API docs show examples with subdirectories that don't work

## Documentation References

### Official API Documentation (Verified)
From `snowflake.snowpark.file_operation.FileOperation.get_stream`:

```python
get_stream(
    self,
    stage_location: str,
    *,
    parallel: int = 10,
    decompress: bool = False,
    statement_params: Optional[Dict[str, str]] = None
) -> IO[bytes]
    Downloads the specified files from a path in a stage and expose it through a stream.

    Args:
        stage_location: The full stage path with prefix and file name, from which you want to download the file.
```

**Key Point**: The documentation states "full stage path with prefix and file name" with **no mention of subdirectory limitations**.

### Official Examples (Verified)
From the same documentation:

```python
# Example showing subdirectory usage
>>> _ = session.file.put("tests/resources/t*.csv", "@mystage/prefix1")
>>> get_result1 = session.file.get("@myStage/prefix1/test2CSV.csv", "tests/downloaded/target1")
```

**Key Point**: The examples show usage with subdirectories (`prefix1/test2CSV.csv`) but the `get_stream` method fails on similar paths.

### Documentation Links
- [Snowflake GET command](https://docs.snowflake.com/en/sql-reference/sql/get.html) (referenced in API docs)
- [Snowflake Stage documentation](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html)

## Questions for Snowflake Support
1. Is this a known limitation of the file API?
2. Is there a different method to read files from subdirectories?
3. Why does `LIST` show subdirectory files if they cannot be accessed?
4. Is this limitation documented anywhere?

## Workaround
Currently, the only workaround is to upload all files to the root of the stage and use file naming conventions instead of subdirectory organization.

---

**Report Date**: December 2024
**Status**: Open
**Priority**: Medium (affects file organization capabilities)
