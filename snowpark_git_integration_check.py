"""
Git Integration Check using Session Manager

This script validates Git integration using the existing three-tier authentication
system instead of hardcoded credentials.
"""

import logging
from pathlib import Path

# Import the Git integration module that uses session manager
from src.svg_image_generator.git_integration import validate_git_integration

# Set up logging
logger = logging.getLogger(__name__)


def main() -> bool:
    """Main function to validate Git integration."""
    logger.info("=== GIT INTEGRATION CHECK START ===")

    try:
        # Use the validate_git_integration function that leverages session manager
        is_valid = validate_git_integration()

        if is_valid:
            logger.info("✅ Git integration is properly configured and accessible")
            print("✅ Git integration validation successful")
            return True
        else:
            logger.error("❌ Git integration validation failed")
            print("❌ Git integration validation failed")
            return False

    except Exception as e:
        logger.error(f"❌ Git integration check error: {e}")
        print(f"❌ Git integration check error: {e}")
        return False


if __name__ == "__main__":
    main()
