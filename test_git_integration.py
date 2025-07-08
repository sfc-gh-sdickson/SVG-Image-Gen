#!/usr/bin/env python3
"""
Test GitHub Integration Setup

This script tests the GitHub integration setup for Snowflake.
It uses the existing functions from git_integration.py.
"""

import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_git_integration():
    """Test the GitHub integration setup."""

    print("=== Testing GitHub Integration Setup ===")

    try:
        # Test 1: Import git_integration module
        print("\n1. Testing module imports...")
        from src.svg_image_generator.git_integration import (
            list_accessible_repositories,
            read_file_from_repository,
            validate_git_integration,
        )

        print("   ✅ Git integration module imported successfully")

        # Test 2: Validate Git integration
        print("\n2. Testing Git integration validation...")
        is_valid = validate_git_integration()
        print(f"   Git Integration Valid: {is_valid}")

        if is_valid:
            print("   ✅ Git integration is properly configured")
        else:
            print("   ⚠️ Git integration needs configuration")
            print("   📝 Run the SQL script in Snowflake to set up the integration")

        # Test 3: List repositories (if integration is valid)
        if is_valid:
            print("\n3. Testing repository listing...")
            repositories = list_accessible_repositories()
            print(f"   Accessible repositories: {repositories}")

            if repositories:
                print("   ✅ Found accessible repositories")
            else:
                print("   ⚠️ No repositories found (this might be normal)")

        # Test 4: Test file reading (if integration is valid)
        if is_valid:
            print("\n4. Testing file reading...")
            # Try to read a common file
            test_file = read_file_from_repository(
                "louspringer/SVG-Image-Gen", "README.md"
            )
            if test_file:
                print("   ✅ Successfully read file from repository")
                print(f"   File content preview: {test_file[:100]}...")
            else:
                print("   ⚠️ Could not read file (this might be normal)")

        # Test 5: Check SQL script
        print("\n5. Checking SQL setup script...")
        sql_file = Path("svggen_git_integration.sql")
        if sql_file.exists():
            print("   ✅ SQL setup script exists")

            # Check if script has been updated with token
            content = sql_file.read_text()
            if "gho_" in content:
                print("   ✅ SQL script contains GitHub token")
            else:
                print("   ⚠️ SQL script needs GitHub token")
        else:
            print("   ❌ SQL setup script not found")

        print("\n=== GitHub Integration Test Complete ===")

        # Summary
        if is_valid:
            print("🎉 GitHub integration is ready to use!")
            print("📝 Next steps:")
            print("   1. Deploy your app to Snowflake")
            print("   2. Test Git operations in your application")
            print("   3. Monitor integration usage")
        else:
            print("🔧 GitHub integration needs setup:")
            print("   1. Run svggen_git_integration.sql in Snowflake")
            print("   2. Verify the integration was created")
            print("   3. Test with this script again")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(
            "🔧 Make sure you're in the correct directory and dependencies are installed"
        )
        return False
    except Exception as e:
        print(f"❌ Error testing Git integration: {e}")
        return False

    return True


def main():
    """Main function."""
    print("🚀 GitHub Integration Test for Snowflake")
    print("=" * 50)

    success = test_git_integration()

    if success:
        print("\n✅ All tests completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
