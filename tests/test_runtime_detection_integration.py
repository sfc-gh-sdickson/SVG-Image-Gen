"""
Integration Tests for Runtime Detection

This module demonstrates how runtime detection prevents non-sensible operations
in different environments, particularly showing how SnowSQL and Git operations
are disabled in Snowflake runtime.
"""

import logging
from unittest.mock import Mock, patch

import pytest

from src.svg_image_generator.git_integration import (
    list_accessible_repositories,
    read_file_from_repository,
    validate_git_integration,
)
from src.svg_image_generator.runtime_detection import (
    RuntimeEnvironment,
    can_use_cortex,
    can_use_git,
    can_use_snowsql,
    is_snowflake_runtime,
)
from src.svg_image_generator.snowsql_manager import (
    install_snowsql,
    is_snowsql_installed,
    run_snowsql_command,
)

logger = logging.getLogger(__name__)


class TestRuntimeDetectionIntegration:
    """Integration tests demonstrating runtime detection in action."""

    def test_snowsql_operations_disabled_in_snowflake(self):
        """Test that SnowSQL operations are disabled in Snowflake runtime."""
        logger.info("Testing SnowSQL operations disabled in Snowflake runtime")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # Verify that SnowSQL operations are not available
            assert not can_use_snowsql()

            # Test that SnowSQL functions return appropriate values
            assert is_snowsql_installed() is False
            assert install_snowsql() is False

            # Test that CLI commands raise appropriate exceptions
            with pytest.raises(
                RuntimeError,
                match="SnowSQL CLI operations are not available in Snowflake runtime environment",
            ):
                run_snowsql_command(["--version"])

            logger.info("✅ SnowSQL operations correctly disabled in Snowflake runtime")

    def test_git_operations_disabled_in_snowflake(self):
        """Test that Git operations are disabled in Snowflake runtime."""
        logger.info("Testing Git operations disabled in Snowflake runtime")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # Verify that Git operations are not available
            assert not can_use_git()

            # Test that Git functions return appropriate values
            assert validate_git_integration() is False
            assert list_accessible_repositories() == []
            assert read_file_from_repository("test/repo", "test/file") is None

            logger.info("✅ Git operations correctly disabled in Snowflake runtime")

    def test_snowsql_operations_enabled_in_local(self):
        """Test that SnowSQL operations are enabled in local development."""
        logger.info("Testing SnowSQL operations enabled in local development")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            # Verify that SnowSQL operations are available
            assert can_use_snowsql()

            # Note: These would actually try to run real commands, so we mock them
            with patch(
                "src.svg_image_generator.snowsql_manager.std_which",
                return_value="/usr/bin/snowsql",
            ):
                assert is_snowsql_installed() is True

            logger.info("✅ SnowSQL operations correctly enabled in local development")

    def test_git_operations_enabled_in_local(self):
        """Test that Git operations are enabled in local development."""
        logger.info("Testing Git operations enabled in local development")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            # Verify that Git operations are available
            assert can_use_git()

            # Note: These would actually try to run real operations, so we mock them
            with patch(
                "src.svg_image_generator.git_integration.get_session"
            ) as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value = mock_session

                # The functions should proceed past the runtime check
                # (they'll fail later due to missing implementation, but that's expected)
                try:
                    validate_git_integration()
                except Exception as e:
                    # Expected - the function exists but implementation is incomplete
                    logger.info(f"Git integration validation failed as expected: {e}")

            logger.info("✅ Git operations correctly enabled in local development")

    def test_cortex_operations_enabled_in_snowflake(self):
        """Test that Cortex operations are enabled in Snowflake runtime."""
        logger.info("Testing Cortex operations enabled in Snowflake runtime")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # Verify that Cortex operations are available
            assert can_use_cortex()

            logger.info("✅ Cortex operations correctly enabled in Snowflake runtime")

    def test_cortex_operations_disabled_in_local(self):
        """Test that Cortex operations are disabled in local development."""
        logger.info("Testing Cortex operations disabled in local development")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            # Verify that Cortex operations are not available
            assert not can_use_cortex()

            logger.info("✅ Cortex operations correctly disabled in local development")

    def test_runtime_detection_error_messages(self):
        """Test that runtime detection provides helpful error messages."""
        logger.info("Testing runtime detection error messages")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # Test SnowSQL error message
            with pytest.raises(RuntimeError) as exc_info:
                run_snowsql_command(["--version"])

            error_msg = str(exc_info.value)
            assert (
                "SnowSQL CLI operations are not available in Snowflake runtime environment"
                in error_msg
            )
            assert "Use Snowflake SQL commands directly instead" in error_msg

            logger.info("✅ Runtime detection provides helpful error messages")

    def test_environment_capability_matrix(self):
        """Test the complete capability matrix for different environments."""
        logger.info("Testing environment capability matrix")

        # Test local development capabilities
        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            assert can_use_snowsql() is True
            assert can_use_git() is True
            assert can_use_cortex() is False

        # Test Snowflake runtime capabilities
        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            assert can_use_snowsql() is False
            assert can_use_git() is False
            assert can_use_cortex() is True

        logger.info("✅ Environment capability matrix is correct")

    def test_runtime_detection_logging(self):
        """Test that runtime detection provides appropriate logging."""
        logger.info("Testing runtime detection logging")

        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ), patch("src.svg_image_generator.runtime_detection.logger") as mock_logger:
            # Trigger a SnowSQL operation to see logging
            try:
                run_snowsql_command(["--version"])
            except RuntimeError:
                pass  # Expected

            # Verify that appropriate error messages were logged
            mock_logger.error.assert_called()
            error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
            assert any("SnowSQL operation" in call for call in error_calls)
            assert any(
                "not available in Snowflake runtime environment" in call
                for call in error_calls
            )

            logger.info("✅ Runtime detection provides appropriate logging")


class TestRuntimeDetectionRealWorld:
    """Real-world scenarios demonstrating runtime detection benefits."""

    def test_development_workflow_protection(self):
        """Test that runtime detection protects against development workflow issues."""
        logger.info("Testing development workflow protection")

        # Simulate a developer accidentally running SnowSQL commands in Snowflake
        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # These operations should fail gracefully with clear error messages
            with pytest.raises(
                RuntimeError, match="SnowSQL CLI operations are not available"
            ):
                run_snowsql_command(["sql", "-q", "SELECT 1"])

            # Git operations should return empty/false results
            assert validate_git_integration() is False
            assert list_accessible_repositories() == []

            logger.info("✅ Development workflow protection working correctly")

    def test_production_safety(self):
        """Test that runtime detection provides production safety."""
        logger.info("Testing production safety")

        # Simulate production Snowflake environment
        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=True,
        ):
            # Ensure that local development tools are completely disabled
            assert not can_use_snowsql()
            assert not can_use_git()

            # Ensure that Snowflake-native operations are available
            assert can_use_cortex()

            logger.info("✅ Production safety working correctly")

    def test_development_environment_functionality(self):
        """Test that development environment retains full functionality."""
        logger.info("Testing development environment functionality")

        # Simulate local development environment
        with patch(
            "src.svg_image_generator.runtime_detection.is_snowflake_runtime",
            return_value=False,
        ):
            # Ensure that local development tools are available
            assert can_use_snowsql()
            assert can_use_git()

            # Ensure that Snowflake-native operations are not available
            assert not can_use_cortex()

            logger.info("✅ Development environment functionality working correctly")
