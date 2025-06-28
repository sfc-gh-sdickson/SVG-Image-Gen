"""
Tests for Runtime Environment Detection

This module tests the runtime environment detection functionality that determines
which operations are available and sensible in different environments.
"""

import logging
import os
from unittest.mock import Mock, patch

import pytest

from src.svg_image_generator.runtime_detection import (
    RuntimeEnvironment,
    can_use_cortex,
    can_use_git,
    can_use_local_files,
    can_use_snowsql,
    check_capability,
    detect_runtime_environment,
    get_environment_capabilities,
    get_environment_info,
    is_local_development,
    is_snowflake_runtime,
    validate_operation_for_environment,
)

logger = logging.getLogger(__name__)


class TestRuntimeEnvironmentDetection:
    """Test runtime environment detection functionality."""

    def test_detect_runtime_environment_local_development(self):
        """Test detection of local development environment."""
        logger.info("Testing local development environment detection")

        with patch(
            "src.svg_image_generator.runtime_detection.get_active_session"
        ) as mock_get_active:
            mock_get_active.side_effect = Exception("No active session")

            env = detect_runtime_environment()
            assert env == RuntimeEnvironment.LOCAL_DEVELOPMENT
            logger.info("✅ Local development environment detected correctly")

    def test_detect_runtime_environment_streamlit_in_snowflake(self):
        """Test detection of Streamlit in Snowflake environment."""
        logger.info("Testing Streamlit in Snowflake environment detection")

        mock_session = Mock()

        with patch(
            "src.svg_image_generator.runtime_detection.get_active_session",
            return_value=mock_session,
        ), patch.dict(os.environ, {"STREAMLIT_SERVER_PORT": "8501"}):
            env = detect_runtime_environment()
            assert env == RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE
            logger.info("✅ Streamlit in Snowflake environment detected correctly")

    def test_detect_runtime_environment_stored_procedure(self):
        """Test detection of Snowflake stored procedure environment."""
        logger.info("Testing Snowflake stored procedure environment detection")

        mock_session = Mock()

        with patch(
            "src.svg_image_generator.runtime_detection.get_active_session",
            return_value=mock_session,
        ), patch.dict(os.environ, {"SNOWFLAKE_PROCEDURE_NAME": "test_procedure"}):
            env = detect_runtime_environment()
            assert env == RuntimeEnvironment.SNOWFLAKE_STORED_PROCEDURE
            logger.info("✅ Snowflake stored procedure environment detected correctly")

    def test_is_snowflake_runtime(self):
        """Test is_snowflake_runtime function."""
        logger.info("Testing is_snowflake_runtime function")

        # Test local development
        with patch(
            "src.svg_image_generator.runtime_detection.detect_runtime_environment",
            return_value=RuntimeEnvironment.LOCAL_DEVELOPMENT,
        ):
            assert not is_snowflake_runtime()

        # Test Snowflake environment
        with patch(
            "src.svg_image_generator.runtime_detection.detect_runtime_environment",
            return_value=RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE,
        ):
            assert is_snowflake_runtime()

        logger.info("✅ is_snowflake_runtime function works correctly")

    def test_is_local_development(self):
        """Test is_local_development function."""
        logger.info("Testing is_local_development function")

        # Test local development
        with patch(
            "src.svg_image_generator.runtime_detection.detect_runtime_environment",
            return_value=RuntimeEnvironment.LOCAL_DEVELOPMENT,
        ):
            assert is_local_development()

        # Test Snowflake environment
        with patch(
            "src.svg_image_generator.runtime_detection.detect_runtime_environment",
            return_value=RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE,
        ):
            assert not is_local_development()

        logger.info("✅ is_local_development function works correctly")


class TestEnvironmentCapabilities:
    """Test environment capabilities detection."""

    def test_get_environment_capabilities_local_development(self):
        """Test capabilities in local development environment."""
        logger.info("Testing local development environment capabilities")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            capabilities = get_environment_capabilities()

            # Local development should have these capabilities
            assert capabilities["filesystem_read"] is True
            assert capabilities["filesystem_write"] is True
            assert capabilities["external_network_access"] is True
            assert capabilities["git_operations"] is True
            assert capabilities["subprocess_execution"] is True
            assert capabilities["cli_tools"] is True

            # Local development should NOT have these capabilities
            assert capabilities["snowflake_session"] is False
            assert capabilities["snowflake_sql"] is False
            assert capabilities["cortex_ai"] is False

            logger.info("✅ Local development capabilities detected correctly")

    def test_get_environment_capabilities_snowflake_runtime(self):
        """Test capabilities in Snowflake runtime environment."""
        logger.info("Testing Snowflake runtime environment capabilities")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            capabilities = get_environment_capabilities()

            # Snowflake runtime should have these capabilities
            assert capabilities["snowflake_session"] is True
            assert capabilities["snowflake_sql"] is True
            assert capabilities["cortex_ai"] is True
            assert capabilities["snowflake_stages"] is True

            # Snowflake runtime should NOT have these capabilities
            assert capabilities["filesystem_read"] is False
            assert capabilities["filesystem_write"] is False
            assert capabilities["external_network_access"] is False
            assert capabilities["git_operations"] is False
            assert capabilities["subprocess_execution"] is False
            assert capabilities["cli_tools"] is False

            logger.info("✅ Snowflake runtime capabilities detected correctly")

    def test_check_capability(self):
        """Test check_capability function."""
        logger.info("Testing check_capability function")

        with patch(
            "src.svg_image_generator.runtime_detection.get_environment_capabilities"
        ) as mock_capabilities:
            mock_capabilities.return_value = {
                "filesystem_read": True,
                "snowflake_session": False,
            }

            assert check_capability("filesystem_read") is True
            assert check_capability("snowflake_session") is False
            assert check_capability("nonexistent_capability") is False

            logger.info("✅ check_capability function works correctly")

    def test_validate_operation_for_environment(self):
        """Test validate_operation_for_environment function."""
        logger.info("Testing validate_operation_for_environment function")

        with patch(
            "src.svg_image_generator.runtime_detection.check_capability"
        ) as mock_check:
            # Test operation with all required capabilities available
            mock_check.side_effect = lambda cap: cap in [
                "filesystem_read",
                "filesystem_write",
            ]
            assert (
                validate_operation_for_environment(
                    "test_operation", ["filesystem_read", "filesystem_write"]
                )
                is True
            )

            # Test operation with missing capabilities
            mock_check.side_effect = lambda cap: cap == "filesystem_read"
            assert (
                validate_operation_for_environment(
                    "test_operation", ["filesystem_read", "filesystem_write"]
                )
                is False
            )

            logger.info("✅ validate_operation_for_environment function works correctly")


class TestConvenienceFunctions:
    """Test convenience functions for common capability checks."""

    def test_can_use_snowsql(self):
        """Test can_use_snowsql function."""
        logger.info("Testing can_use_snowsql function")

        with patch(
            "src.svg_image_generator.runtime_detection.check_capability"
        ) as mock_check:
            # Test when both capabilities are available
            mock_check.side_effect = lambda cap: cap in [
                "cli_tools",
                "subprocess_execution",
            ]
            assert can_use_snowsql() is True

            # Test when one capability is missing
            mock_check.side_effect = lambda cap: cap == "cli_tools"
            assert can_use_snowsql() is False

            logger.info("✅ can_use_snowsql function works correctly")

    def test_can_use_git(self):
        """Test can_use_git function."""
        logger.info("Testing can_use_git function")

        with patch(
            "src.svg_image_generator.runtime_detection.check_capability"
        ) as mock_check:
            # Test when both capabilities are available
            mock_check.side_effect = lambda cap: cap in [
                "git_operations",
                "external_network_access",
            ]
            assert can_use_git() is True

            # Test when one capability is missing
            mock_check.side_effect = lambda cap: cap == "git_operations"
            assert can_use_git() is False

            logger.info("✅ can_use_git function works correctly")

    def test_can_use_local_files(self):
        """Test can_use_local_files function."""
        logger.info("Testing can_use_local_files function")

        with patch(
            "src.svg_image_generator.runtime_detection.check_capability"
        ) as mock_check:
            # Test when both capabilities are available
            mock_check.side_effect = lambda cap: cap in [
                "filesystem_read",
                "filesystem_write",
            ]
            assert can_use_local_files() is True

            # Test when one capability is missing
            mock_check.side_effect = lambda cap: cap == "filesystem_read"
            assert can_use_local_files() is False

            logger.info("✅ can_use_local_files function works correctly")

    def test_can_use_cortex(self):
        """Test can_use_cortex function."""
        logger.info("Testing can_use_cortex function")

        with patch(
            "src.svg_image_generator.runtime_detection.check_capability"
        ) as mock_check:
            # Test when both capabilities are available
            mock_check.side_effect = lambda cap: cap in [
                "cortex_ai",
                "snowflake_session",
            ]
            assert can_use_cortex() is True

            # Test when one capability is missing
            mock_check.side_effect = lambda cap: cap == "cortex_ai"
            assert can_use_cortex() is False

            logger.info("✅ can_use_cortex function works correctly")


class TestEnvironmentInfo:
    """Test get_environment_info function."""

    def test_get_environment_info(self):
        """Test get_environment_info function."""
        logger.info("Testing get_environment_info function")

        with patch(
            "src.svg_image_generator.runtime_detection.detect_runtime_environment",
            return_value=RuntimeEnvironment.LOCAL_DEVELOPMENT,
        ), patch(
            "src.svg_image_generator.runtime_detection.get_environment_capabilities"
        ) as mock_capabilities:
            mock_capabilities.return_value = {
                "filesystem_read": True,
                "snowflake_session": False,
            }

            info = get_environment_info()

            assert info["environment"] == RuntimeEnvironment.LOCAL_DEVELOPMENT
            assert info["is_snowflake_runtime"] is False
            assert info["is_local_development"] is True
            assert info["capabilities"] == mock_capabilities.return_value
            assert info["snowflake_available"] in [
                True,
                False,
            ]  # Depends on test environment

            logger.info("✅ get_environment_info function works correctly")


class TestRuntimeDetectionIntegration:
    """Integration tests for runtime detection."""

    def test_snowsql_operations_in_snowflake_environment(self):
        """Test that SnowSQL operations are correctly disabled in Snowflake environment."""
        logger.info("Testing SnowSQL operations in Snowflake environment")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # SnowSQL operations should not be available in Snowflake
            assert not can_use_snowsql()

            # Git operations should not be available in Snowflake
            assert not can_use_git()

            # Local file operations should not be available in Snowflake
            assert not can_use_local_files()

            # Cortex operations should be available in Snowflake
            assert can_use_cortex()

            logger.info(
                "✅ SnowSQL operations correctly disabled in Snowflake environment"
            )

    def test_snowsql_operations_in_local_environment(self):
        """Test that SnowSQL operations are correctly enabled in local environment."""
        logger.info("Testing SnowSQL operations in local environment")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            # SnowSQL operations should be available locally
            assert can_use_snowsql()

            # Git operations should be available locally
            assert can_use_git()

            # Local file operations should be available locally
            assert can_use_local_files()

            # Cortex operations should not be available locally
            assert not can_use_cortex()

            logger.info("✅ SnowSQL operations correctly enabled in local environment")
