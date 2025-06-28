#!/usr/bin/env python3
"""
Test Snowflake Capabilities

This script tests what we can actually do from within Snowflake,
including runtime detection, session management, and available operations.
"""

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_snowflake_capabilities():
    """Test what capabilities are available in Snowflake."""

    print("=== Testing Snowflake Capabilities ===")

    try:
        # Test 1: Runtime Detection
        print("\n1. Testing Runtime Detection...")
        from src.svg_image_generator.runtime_detection import (
            detect_runtime_environment,
            get_environment_capabilities,
            is_snowflake_runtime,
        )

        runtime_env = detect_runtime_environment()
        capabilities = get_environment_capabilities()
        is_snowflake = is_snowflake_runtime()

        print(f"   Runtime Environment: {runtime_env}")
        print(f"   Is Snowflake Runtime: {is_snowflake}")
        print(f"   Capabilities: {capabilities}")

        # Test 2: Session Management
        print("\n2. Testing Session Management...")
        from src.svg_image_generator.session_manager import get_session

        session = get_session()
        print(f"   Session Type: {type(session).__name__}")

        # Test 3: Basic SQL Operations
        print("\n3. Testing Basic SQL Operations...")
        try:
            result = session.sql(
                "SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()"
            ).collect()
            print(f"   Current Role: {result[0][0]}")
            print(f"   Current Database: {result[0][1]}")
            print(f"   Current Schema: {result[0][2]}")
        except Exception as e:
            print(f"   SQL Error: {e}")

        # Test 4: Git Integration (if available)
        print("\n4. Testing Git Integration...")
        from src.svg_image_generator.git_integration import validate_git_integration

        git_available = validate_git_integration()
        print(f"   Git Integration Available: {git_available}")

        # Test 5: LLM Logging
        print("\n5. Testing LLM Logging...")
        from src.svg_image_generator.llm_logging import get_llm_logger

        llm_logger = get_llm_logger("snowflake_capability_test")
        llm_logger.info(
            "Testing LLM logging from Snowflake",
            context={
                "runtime_environment": str(runtime_env),
                "capabilities": capabilities,
                "git_available": git_available,
            },
        )
        print("   LLM Logging: ✅ Working")

        # Test 6: File System Access (if any)
        print("\n6. Testing File System Access...")
        try:
            current_dir = Path.cwd()
            print(f"   Current Directory: {current_dir}")
            print(f"   Directory Exists: {current_dir.exists()}")
            print(f"   Directory Contents: {list(current_dir.iterdir())[:5]}...")
        except Exception as e:
            print(f"   File System Error: {e}")

        # Test 7: Environment Variables
        print("\n7. Testing Environment Variables...")
        import os

        env_vars = {
            "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT"),
            "SNOWFLAKE_USER": os.getenv("SNOWFLAKE_USER"),
            "SNOWFLAKE_ROLE": os.getenv("SNOWFLAKE_ROLE"),
            "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE"),
            "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA"),
        }
        for key, value in env_vars.items():
            print(f"   {key}: {value if value else 'Not Set'}")

        print("\n=== Snowflake Capability Test Complete ===")

    except Exception as e:
        print(f"Error testing Snowflake capabilities: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_snowflake_capabilities()
