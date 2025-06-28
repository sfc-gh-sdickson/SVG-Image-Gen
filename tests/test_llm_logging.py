"""
Tests for LLM-Friendly Logging System

This test file demonstrates how the LLM-friendly logging system works
and how the structured logs can be parsed by LLM assistants.
"""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from src.svg_image_generator.llm_logging import (
    ErrorCode,
    LLMLogger,
    LogLevel,
    get_llm_logger,
    log_environment_summary,
    log_operation_attempt,
)
from src.svg_image_generator.runtime_detection import RuntimeEnvironment


class TestLLMLogger:
    """Test the LLM-friendly logger functionality."""

    def test_llm_logger_creation(self):
        """Test creating an LLM logger instance."""
        logger = LLMLogger("test.logger")
        assert logger.name == "test.logger"
        assert logger.log_level == LogLevel.INFO

    def test_llm_logger_with_custom_level(self):
        """Test creating an LLM logger with custom log level."""
        logger = LLMLogger("test.logger", LogLevel.DEBUG)
        assert logger.log_level == LogLevel.DEBUG

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_create_llm_log_entry(self, mock_env_info):
        """Test creating a structured log entry."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")
        log_entry = logger._create_llm_log_entry(
            LogLevel.INFO,
            "Test message",
            error_code=ErrorCode.RUNTIME_MISMATCH,
            context={"test": "data"},
            action_guidance=["Action 1", "Action 2"],
            llm_api_suggestions=["API 1", "API 2"],
        )

        assert log_entry["logger"] == "test.logger"
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Test message"
        assert log_entry["error_code"] == "RUNTIME_MISMATCH"
        assert log_entry["context"]["test"] == "data"
        assert log_entry["action_guidance"] == ["Action 1", "Action 2"]
        assert log_entry["llm_api_suggestions"] == ["API 1", "API 2"]
        assert "timestamp" in log_entry
        assert "environment" in log_entry

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_create_llm_log_entry_with_exception(self, mock_env_info):
        """Test creating a log entry with exception information."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")
        test_exception = ValueError("Test error")

        log_entry = logger._create_llm_log_entry(
            LogLevel.ERROR, "Test error message", exception=test_exception
        )

        assert log_entry["exception"]["type"] == "ValueError"
        assert log_entry["exception"]["message"] == "Test error"
        assert "traceback" in log_entry["exception"]

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    @patch("logging.getLogger")
    def test_log_methods(self, mock_get_logger, mock_env_info):
        """Test the main logging methods."""
        mock_env_info.return_value = {"environment": "test"}
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = LLMLogger("test.logger")

        # Test info logging
        logger.info("Test info message", context={"test": "info"})
        assert mock_logger.info.called

        # Test error logging
        logger.error("Test error message", error_code=ErrorCode.UNEXPECTED_ERROR)
        assert mock_logger.error.called

        # Test warning logging
        logger.warning("Test warning message")
        assert mock_logger.warning.called

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_runtime_mismatch_logging(self, mock_env_info):
        """Test runtime mismatch logging."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")

        with patch.object(logger, "error") as mock_error:
            logger.runtime_mismatch(
                "test_operation",
                ["capability1", "capability2"],
                {"capability1": False, "capability2": True},
            )

            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert (
                call_args[0][0]
                == "Runtime capability mismatch for operation 'test_operation'"
            )
            assert call_args[1]["error_code"] == ErrorCode.RUNTIME_MISMATCH
            assert "missing_capabilities" in call_args[1]["context"]

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_snowsql_unavailable_logging(self, mock_env_info):
        """Test SnowSQL unavailability logging."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")

        with patch.object(logger, "error") as mock_error:
            logger.snowsql_unavailable("test_operation")

            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "SnowSQL operation 'test_operation' not available" in call_args[0][0]
            assert call_args[1]["error_code"] == ErrorCode.SNOWSQL_RUNTIME_UNAVAILABLE

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_git_unavailable_logging(self, mock_env_info):
        """Test Git unavailability logging."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")

        with patch.object(logger, "error") as mock_error:
            logger.git_unavailable("test_operation")

            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "Git operation 'test_operation' not available" in call_args[0][0]
            assert call_args[1]["error_code"] == ErrorCode.GIT_RUNTIME_UNAVAILABLE

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_authentication_failed_logging(self, mock_env_info):
        """Test authentication failure logging."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")
        test_exception = ConnectionError("Auth failed")

        with patch.object(logger, "error") as mock_error:
            logger.authentication_failed("tier1", test_exception)

            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "Authentication failed at tier tier1" in call_args[0][0]
            assert call_args[1]["error_code"] == ErrorCode.AUTHENTICATION_FAILED
            assert call_args[1]["exception"] == test_exception

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_environment_detected_logging(self, mock_env_info):
        """Test environment detection logging."""
        mock_env_info.return_value = {"environment": "test"}

        logger = LLMLogger("test.logger")

        with patch.object(logger, "info") as mock_info:
            logger.environment_detected(
                RuntimeEnvironment.LOCAL_DEVELOPMENT,
                {"capability1": True, "capability2": False},
            )

            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert "Runtime environment detected: local_development" in call_args[0][0]
            assert "available_operations" in call_args[1]["context"]
            assert "unavailable_operations" in call_args[1]["context"]


class TestLLMLoggingFunctions:
    """Test the utility functions for LLM logging."""

    def test_get_llm_logger(self):
        """Test getting an LLM logger instance."""
        logger = get_llm_logger("test.module")
        assert isinstance(logger, LLMLogger)
        assert logger.name == "test.module"

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    @patch("src.svg_image_generator.llm_logging.llm_logger")
    def test_log_environment_summary(self, mock_llm_logger, mock_env_info):
        """Test logging environment summary."""
        mock_env_info.return_value = {
            "environment": "local_development",
            "capabilities": {
                "filesystem_read": True,
                "filesystem_write": True,
                "git_operations": False,
                "snowflake_session": False,
            },
        }

        log_environment_summary()

        mock_llm_logger.info.assert_called_once()
        call_args = mock_llm_logger.info.call_args
        assert "Environment summary for LLM assistant" in call_args[0][0]
        assert "available_operations" in call_args[1]["context"]
        assert "unavailable_operations" in call_args[1]["context"]
        assert "recommended_approaches" in call_args[1]["context"]

    @patch("src.svg_image_generator.llm_logging.get_environment_capabilities")
    @patch("src.svg_image_generator.llm_logging.validate_operation_for_environment")
    @patch("src.svg_image_generator.llm_logging.llm_logger")
    def test_log_operation_attempt_success(
        self, mock_llm_logger, mock_validate, mock_capabilities
    ):
        """Test logging successful operation attempt."""
        mock_capabilities.return_value = {"capability1": True, "capability2": True}
        mock_validate.return_value = True

        log_operation_attempt("test_operation", ["capability1", "capability2"])

        mock_llm_logger.info.assert_called_once()
        call_args = mock_llm_logger.info.call_args
        assert (
            "Operation 'test_operation' validated for current environment"
            in call_args[0][0]
        )

    @patch("src.svg_image_generator.llm_logging.get_environment_capabilities")
    @patch("src.svg_image_generator.llm_logging.validate_operation_for_environment")
    @patch("src.svg_image_generator.llm_logger.runtime_mismatch")
    def test_log_operation_attempt_failure(
        self, mock_runtime_mismatch, mock_validate, mock_capabilities
    ):
        """Test logging failed operation attempt."""
        mock_capabilities.return_value = {"capability1": False, "capability2": True}
        mock_validate.return_value = False

        log_operation_attempt("test_operation", ["capability1", "capability2"])

        mock_runtime_mismatch.assert_called_once()
        call_args = mock_runtime_mismatch.call_args
        assert call_args[0][0] == "test_operation"
        assert call_args[0][1] == ["capability1", "capability2"]


class TestLLMLoggingIntegration:
    """Test LLM logging integration with other modules."""

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_structured_log_output_format(self, mock_env_info):
        """Test that structured logs are properly formatted for LLM consumption."""
        mock_env_info.return_value = {
            "environment": "local_development",
            "capabilities": {"test": True},
        }

        logger = LLMLogger("test.logger")

        with patch.object(logger, "_log_llm_entry") as mock_log:
            logger.info("Test message", context={"key": "value"})

            mock_log.assert_called_once()
            log_entry = mock_log.call_args[0][1]  # Second argument is the log entry

            # Verify the structure is LLM-friendly
            assert "timestamp" in log_entry
            assert "logger" in log_entry
            assert "level" in log_entry
            assert "message" in log_entry
            assert "environment" in log_entry
            assert "context" in log_entry

            # Verify JSON serialization works
            json_str = json.dumps(log_entry)
            assert isinstance(json_str, str)

            # Verify we can parse it back
            parsed = json.loads(json_str)
            assert parsed["message"] == "Test message"
            assert parsed["context"]["key"] == "value"

    def test_error_codes_enumeration(self):
        """Test that all error codes are properly defined."""
        error_codes = [
            ErrorCode.RUNTIME_MISMATCH,
            ErrorCode.CAPABILITY_UNAVAILABLE,
            ErrorCode.ENVIRONMENT_DETECTION_FAILED,
            ErrorCode.SNOWSQL_NOT_INSTALLED,
            ErrorCode.SNOWSQL_INSTALLATION_FAILED,
            ErrorCode.SNOWSQL_COMMAND_FAILED,
            ErrorCode.SNOWSQL_RUNTIME_UNAVAILABLE,
            ErrorCode.GIT_RUNTIME_UNAVAILABLE,
            ErrorCode.GIT_INTEGRATION_FAILED,
            ErrorCode.GIT_REPOSITORY_ACCESS_FAILED,
            ErrorCode.AUTHENTICATION_FAILED,
            ErrorCode.SESSION_CREATION_FAILED,
            ErrorCode.CREDENTIALS_MISSING,
            ErrorCode.UNEXPECTED_ERROR,
            ErrorCode.CONFIGURATION_ERROR,
            ErrorCode.NETWORK_ERROR,
            ErrorCode.PERMISSION_ERROR,
        ]

        for error_code in error_codes:
            assert isinstance(error_code.value, str)
            assert len(error_code.value) > 0

    def test_log_levels_enumeration(self):
        """Test that all log levels are properly defined."""
        log_levels = [
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]

        for log_level in log_levels:
            assert isinstance(log_level.value, str)
            assert len(log_level.value) > 0


class TestLLMLoggingExamples:
    """Test examples of how LLM logging would work in practice."""

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_snowsql_operation_example(self, mock_env_info):
        """Test example of SnowSQL operation logging."""
        mock_env_info.return_value = {
            "environment": "streamlit_in_snowflake",
            "capabilities": {"cli_tools": False, "subprocess_execution": False},
        }

        logger = LLMLogger("snowsql_manager")

        with patch.object(logger, "_log_llm_entry") as mock_log:
            logger.snowsql_unavailable("run_snowsql_command")

            mock_log.assert_called_once()
            log_entry = mock_log.call_args[0][1]

            # Verify LLM-friendly structure
            assert log_entry["error_code"] == "SNOWSQL_RUNTIME_UNAVAILABLE"
            assert "action_guidance" in log_entry
            assert "llm_api_suggestions" in log_entry
            assert "context" in log_entry

            # Verify actionable guidance
            action_guidance = log_entry["action_guidance"]
            assert any("Snowflake SQL commands" in action for action in action_guidance)

            # Verify API suggestions
            api_suggestions = log_entry["llm_api_suggestions"]
            assert any("session.sql()" in suggestion for suggestion in api_suggestions)

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_git_operation_example(self, mock_env_info):
        """Test example of Git operation logging."""
        mock_env_info.return_value = {
            "environment": "streamlit_in_snowflake",
            "capabilities": {"git_operations": False, "external_network_access": False},
        }

        logger = LLMLogger("git_integration")

        with patch.object(logger, "_log_llm_entry") as mock_log:
            logger.git_unavailable("list_accessible_repositories")

            mock_log.assert_called_once()
            log_entry = mock_log.call_args[0][1]

            # Verify LLM-friendly structure
            assert log_entry["error_code"] == "GIT_RUNTIME_UNAVAILABLE"
            assert "action_guidance" in log_entry
            assert "llm_api_suggestions" in log_entry

            # Verify Snowflake alternatives
            api_suggestions = log_entry["llm_api_suggestions"]
            assert any(
                "Snowflake stages" in suggestion for suggestion in api_suggestions
            )
            assert any(
                "Snowflake external functions" in suggestion
                for suggestion in api_suggestions
            )

    @patch("src.svg_image_generator.llm_logging.get_environment_info")
    def test_authentication_example(self, mock_env_info):
        """Test example of authentication failure logging."""
        mock_env_info.return_value = {
            "environment": "local_development",
            "capabilities": {"snowflake_session": False},
        }

        logger = LLMLogger("session_manager")
        auth_error = ConnectionError("Failed to connect to Snowflake")

        with patch.object(logger, "_log_llm_entry") as mock_log:
            logger.authentication_failed("active_session", auth_error)

            mock_log.assert_called_once()
            log_entry = mock_log.call_args[0][1]

            # Verify LLM-friendly structure
            assert log_entry["error_code"] == "AUTHENTICATION_FAILED"
            assert "exception" in log_entry
            assert log_entry["exception"]["type"] == "ConnectionError"
            assert "action_guidance" in log_entry
            assert "llm_api_suggestions" in log_entry

            # Verify authentication tier information
            context = log_entry["context"]
            assert context["authentication_tier"] == "active_session"
            assert "available_tiers" in context
