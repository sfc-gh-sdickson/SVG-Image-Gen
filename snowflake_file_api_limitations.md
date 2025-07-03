# Snowflake File API Limitations - Technical Documentation

## Overview

This document details critical limitations discovered in Snowflake's `session.file.get_stream()` API during development of the SVG Image Generator application. These limitations significantly impact how files can be accessed within Snowflake stages.

## Key Finding: Subdirectory Access is Broken

### The Problem

The `session.file.get_stream()` method **cannot read files from subdirectories within stages**. This is a significant API limitation that forces architectural changes.

### Evidence from Testing

#### ❌ Files in Subdirectories Fail
```python
# This fails with "file does not exist"
session.file.get_stream("@CONTAINER_DB.PUBLIC.SPECS/specs/Data_Share_Logo.svg")
```

#### ✅ Files at Root Work
```python
# This works perfectly
session.file.get_stream("@CONTAINER_DB.PUBLIC.SPECS/Data_Share_Logo.svg")
```

#### ✅ SQL Queries Work for Subdirectories
```python
# This works for files in subdirectories
result = session.sql("SELECT LISTAGG($1, '') FROM @CONTAINER_DB.PUBLIC.SPECS/specs/Data_Share_Logo.svg").collect()
```

## Impact on Application Architecture

### Current Workarounds Required

1. **Flatten File Structure**: Upload all files to stage root, not in subdirectories
2. **Use SQL Queries**: For subdirectory access, use `SELECT $1 FROM @stage/file` with `LISTAGG`
3. **Mixed Approach**: Use file API for root files, SQL for subdirectory files

### Code Implications

#### Upload Strategy
```python
# ❌ Don't do this - creates subdirectories that can't be read
session.file.put("local_file.svg", "@stage/subdirectory/file.svg")

# ✅ Do this - upload to root
session.file.put("local_file.svg", "@stage/file.svg")
```

#### Read Strategy
```python
# For root files - use file API
try:
    with session.file.get_stream("@stage/file.svg") as stream:
        content = stream.read()
except:
    # Fallback to SQL for subdirectories
    result = session.sql("SELECT LISTAGG($1, '') FROM @stage/file.svg").collect()
    content = result[0][0]
```

## Technical Details

### API Behavior Analysis

1. **File API (`session.file.get_stream()`)**
   - ✅ Works for files at stage root
   - ❌ Fails for files in subdirectories
   - Error: "file does not exist"
   - No clear documentation of this limitation

2. **SQL File Access (`SELECT $1 FROM @stage/file`)**
   - ✅ Works for files at stage root
   - ✅ Works for files in subdirectories
   - Requires `LISTAGG` to concatenate lines
   - More complex but more reliable

3. **Stage Listing (`LIST @stage`)**
   - Returns relative paths within stage
   - Shows subdirectory structure correctly
   - Can be used to discover available files

### Environment Context Issues

Additional complications discovered:

1. **Database Context**: `session.get_current_database()` can fail if no current database is set
2. **Schema Context**: `session.get_current_schema()` can fail if no current schema is set
3. **Fully Qualified Names**: Always use fully qualified stage names to avoid context issues

## Recommendations for Stephen

### Immediate Actions

1. **Update Upload Scripts**: Ensure all file uploads go to stage root
2. **Update Read Logic**: Implement fallback from file API to SQL queries
3. **Document Limitations**: Add comments explaining why files must be at root

### Long-term Considerations

1. **File Organization**: Consider using file naming conventions instead of subdirectories
2. **API Monitoring**: Watch for Snowflake updates that might fix this limitation
3. **Alternative Approaches**: Evaluate if different file storage strategies are needed

### Code Patterns to Follow

```python
def read_svg_from_stage(session, stage_path):
    """
    Read SVG file from stage with fallback for subdirectories.

    Args:
        session: Snowflake session
        stage_path: Full stage path (e.g., "@CONTAINER_DB.PUBLIC.SPECS/file.svg")

    Returns:
        SVG content as string
    """
    # Try file API first (works for root files)
    try:
        with session.file.get_stream(stage_path) as stream:
            return stream.read().decode('utf-8')
    except Exception as e:
        if "file does not exist" in str(e):
            # Fallback to SQL for subdirectories
            result = session.sql(f"SELECT LISTAGG($1, '') FROM {stage_path}").collect()
            return result[0][0]
        else:
            raise
```

## Conclusion

The Snowflake `session.file.get_stream()` API has a significant limitation that prevents reading files from subdirectories within stages. This forces architectural changes to either:

1. Flatten file structures (recommended for simplicity)
2. Use SQL queries for subdirectory access (more complex but flexible)

This limitation should be documented in all Snowflake file handling code and considered when designing file organization strategies.

---

**Document Version**: 1.0
**Date**: December 2024
**Author**: Development Team
**Status**: Confirmed through testing
