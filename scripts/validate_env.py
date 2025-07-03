#!/usr/bin/env python3
"""
Environment variable validation script.

This script validates that all required environment variables are present
and provides clear error messages when they're missing.
"""

import os
import sys
from typing import Dict, List, Optional

from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from .env file if it exists."""
    load_dotenv()


def get_required_variables() -> Dict[str, str]:
    """Get the list of required environment variables with descriptions."""
    return {
        "SNOWFLAKE_ACCOUNT": "Snowflake account identifier (e.g., xy12345.us-east-1)",
        "SNOWFLAKE_USER": "Snowflake username",
        "SNOWFLAKE_PASSWORD": "Snowflake password",
        "SNOWFLAKE_WAREHOUSE": "Snowflake warehouse name",
    }


def get_optional_variables() -> Dict[str, str]:
    """Get the list of optional environment variables with descriptions."""
    return {
        "SNOWFLAKE_DATABASE": "Snowflake database name",
        "SNOWFLAKE_SCHEMA": "Snowflake schema name",
        "SNOWFLAKE_ROLE": "Snowflake role name",
        "STREAMLIT_SERVER_PORT": "Streamlit server port (default: 8501)",
        "STREAMLIT_SERVER_ADDRESS": "Streamlit server address (default: 0.0.0.0)",
        "STREAMLIT_SERVER_HEADLESS": "Streamlit headless mode (default: true)",
    }


def validate_environment() -> bool:
    """
    Validate that all required environment variables are present.

    Returns:
        bool: True if all required variables are present, False otherwise
    """
    load_environment()

    required_vars = get_required_variables()
    optional_vars = get_optional_variables()

    missing_required = []
    missing_optional = []

    # Check required variables
    for var_name, description in required_vars.items():
        if not os.getenv(var_name):
            missing_required.append((var_name, description))

    # Check optional variables (just for information)
    for var_name, description in optional_vars.items():
        if not os.getenv(var_name):
            missing_optional.append((var_name, description))

    # Report results
    if missing_required:
        print("❌ Missing required environment variables:")
        for var_name, description in missing_required:
            print(f"   - {var_name}: {description}")
        print()
        print("💡 To fix this:")
        print("   1. See the README for required environment variables.")
        print(
            "   2. Set them in your shell or a local .env file (never tracked or committed)."
        )
        print(
            "   3. Never commit .env files to version control or include them in the project directory."
        )
        print()
        return False

    if missing_optional:
        print("⚠️  Missing optional environment variables (these are not required):")
        for var_name, description in missing_optional:
            print(f"   - {var_name}: {description}")
        print()

    print("✅ All required environment variables are present!")
    return True


def main() -> int:
    """Main function to run environment validation."""
    try:
        if validate_environment():
            return 0
        else:
            return 1
    except Exception as e:
        print(f"❌ Error during environment validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
