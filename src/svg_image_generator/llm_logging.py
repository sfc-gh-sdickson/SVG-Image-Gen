"""
LLM-Friendly Logging System

This module provides structured, parseable logging designed for LLM consumption.
LLM assistants can parse these logs to understand the runtime environment,
diagnose issues, and provide actionable guidance.
"""

import json
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .runtime_detection import RuntimeEnvironment, get_environment_info


class LogLevel(Enum):
    """Standardized log levels for LLM consumption."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorCode(Enum):
    """Structured error codes for LLM parsing."""

    # Runtime Environment Errors
    RUNTIME_MISMATCH = "RUNTIME_MISMATCH"
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    ENVIRONMENT_DETECTION_FAILED = "ENVIRONMENT_DETECTION_FAILED"

    # SnowSQL Errors
    SNOWSQL_NOT_INSTALLED = "SNOWSQL_NOT_INSTALLED"
    SNOWSQL_INSTALLATION_FAILED = "SNOWSQL_INSTALLATION_FAILED"
    SNOWSQL_COMMAND_FAILED = "SNOWSQL_COMMAND_FAILED"
    SNOWSQL_RUNTIME_UNAVAILABLE = "SNOWSQL_RUNTIME_UNAVAILABLE"

    # Git Integration Errors
    GIT_RUNTIME_UNAVAILABLE = "GIT_RUNTIME_UNAVAILABLE"
    GIT_INTEGRATION_FAILED = "GIT_INTEGRATION_FAILED"
    GIT_REPOSITORY_ACCESS_FAILED = "GIT_REPOSITORY_ACCESS_FAILED"

    # Authentication Errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    SESSION_CREATION_FAILED = "SESSION_CREATION_FAILED"
    CREDENTIALS_MISSING = "CREDENTIALS_MISSING"

    # General Errors
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    PERMISSION_ERROR = "PERMISSION_ERROR"


class LLMLogger:
    """LLM-friendly logger that provides structured, parseable output."""

    def __init__(self, name: str, log_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.log_level = log_level
        self.logger = logging.getLogger(name)

    def _create_llm_log_entry(
        self,
        level: LogLevel,
        message: str,
        error_code: Optional[ErrorCode] = None,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        action_guidance: Optional[List[str]] = None,
        llm_api_suggestions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a structured log entry for LLM consumption."""

        # Get current environment info
        try:
            env_info = get_environment_info()
        except Exception:
            env_info = {"error": "Failed to get environment info"}

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "logger": self.name,
            "level": level.value,
            "message": message,
            "environment": env_info,
            "context": context or {},
        }

        if error_code:
            log_entry["error_code"] = error_code.value

        if exception:
            log_entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc(),
            }

        if action_guidance:
            log_entry["action_guidance"] = action_guidance

        if llm_api_suggestions:
            log_entry["llm_api_suggestions"] = llm_api_suggestions

        return log_entry

    def _log_llm_entry(self, level: LogLevel, log_entry: Dict[str, Any]):
        """Log the structured entry."""
        # Convert to JSON for LLM parsing
        json_log = json.dumps(log_entry, indent=2)

        # Use standard logging levels
        if level == LogLevel.DEBUG:
            self.logger.debug(json_log)
        elif level == LogLevel.INFO:
            self.logger.info(json_log)
        elif level == LogLevel.WARNING:
            self.logger.warning(json_log)
        elif level == LogLevel.ERROR:
            self.logger.error(json_log)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(json_log)

    def debug(self, message: str, **kwargs):
        """Log debug message with LLM-friendly structure."""
        if self.log_level.value <= LogLevel.DEBUG.value:
            log_entry = self._create_llm_log_entry(LogLevel.DEBUG, message, **kwargs)
            self._log_llm_entry(LogLevel.DEBUG, log_entry)

    def info(self, message: str, **kwargs):
        """Log info message with LLM-friendly structure."""
        if self.log_level.value <= LogLevel.INFO.value:
            log_entry = self._create_llm_log_entry(LogLevel.INFO, message, **kwargs)
            self._log_llm_entry(LogLevel.INFO, log_entry)

    def warning(self, message: str, **kwargs):
        """Log warning message with LLM-friendly structure."""
        if self.log_level.value <= LogLevel.WARNING.value:
            log_entry = self._create_llm_log_entry(LogLevel.WARNING, message, **kwargs)
            self._log_llm_entry(LogLevel.WARNING, log_entry)

    def error(self, message: str, **kwargs):
        """Log error message with LLM-friendly structure."""
        if self.log_level.value <= LogLevel.ERROR.value:
            log_entry = self._create_llm_log_entry(LogLevel.ERROR, message, **kwargs)
            self._log_llm_entry(LogLevel.ERROR, log_entry)

    def critical(self, message: str, **kwargs):
        """Log critical message with LLM-friendly structure."""
        if self.log_level.value <= LogLevel.CRITICAL.value:
            log_entry = self._create_llm_log_entry(LogLevel.CRITICAL, message, **kwargs)
            self._log_llm_entry(LogLevel.CRITICAL, log_entry)

    def runtime_mismatch(
        self,
        operation: str,
        required_capabilities: List[str],
        available_capabilities: Dict[str, bool],
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log runtime capability mismatch for LLM consumption."""
        missing_capabilities = [
            cap
            for cap in required_capabilities
            if not available_capabilities.get(cap, False)
        ]

        action_guidance = [
            f"Operation '{operation}' requires capabilities: {required_capabilities}",
            f"Missing capabilities: {missing_capabilities}",
            "Consider using alternative approaches suitable for current environment",
        ]

        llm_api_suggestions = [
            "Use SNOWFLAKE.CORTEX.COMPLETE() for AI operations in Snowflake",
            "Use Snowflake SQL commands instead of CLI tools",
            "Use Snowflake stages for file operations",
            "Use Snowflake external functions for network operations",
        ]

        self.error(
            f"Runtime capability mismatch for operation '{operation}'",
            error_code=ErrorCode.RUNTIME_MISMATCH,
            context={
                "operation": operation,
                "required_capabilities": required_capabilities,
                "available_capabilities": available_capabilities,
                "missing_capabilities": missing_capabilities,
                **(context or {}),
            },
            action_guidance=action_guidance,
            llm_api_suggestions=llm_api_suggestions,
        )

    def snowsql_unavailable(
        self, operation: str, context: Optional[Dict[str, Any]] = None
    ):
        """Log SnowSQL unavailability for LLM consumption."""
        action_guidance = [
            "SnowSQL CLI operations are not available in Snowflake runtime",
            "Use Snowflake SQL commands directly instead",
            "For local development, install SnowSQL with: make install-dev",
        ]

        llm_api_suggestions = [
            "Use session.sql() for SQL operations",
            "Use Snowflake stages for file operations",
            "Use Snowflake external functions for external API calls",
        ]

        self.error(
            f"SnowSQL operation '{operation}' not available in current environment",
            error_code=ErrorCode.SNOWSQL_RUNTIME_UNAVAILABLE,
            context={
                "operation": operation,
                "suggested_alternatives": [
                    "session.sql() for SQL operations",
                    "Snowflake stages for file operations",
                    "Snowflake external functions for API calls",
                ],
                **(context or {}),
            },
            action_guidance=action_guidance,
            llm_api_suggestions=llm_api_suggestions,
        )

    def git_unavailable(self, operation: str, context: Optional[Dict[str, Any]] = None):
        """Log Git unavailability for LLM consumption."""
        action_guidance = [
            "Git operations are not available in Snowflake runtime",
            "Use Snowflake stages for file storage",
            "Use Snowflake external functions for external repository access",
        ]

        llm_api_suggestions = [
            "Use Snowflake stages for file storage",
            "Use Snowflake external functions for Git API access",
            "Use Snowflake streams for data pipeline operations",
        ]

        self.error(
            f"Git operation '{operation}' not available in current environment",
            error_code=ErrorCode.GIT_RUNTIME_UNAVAILABLE,
            context={
                "operation": operation,
                "suggested_alternatives": [
                    "Snowflake stages for file storage",
                    "Snowflake external functions for Git API",
                    "Snowflake streams for data pipelines",
                ],
                **(context or {}),
            },
            action_guidance=action_guidance,
            llm_api_suggestions=llm_api_suggestions,
        )

    def authentication_failed(
        self, tier: str, error: Exception, context: Optional[Dict[str, Any]] = None
    ):
        """Log authentication failure for LLM consumption."""
        action_guidance = [
            f"Authentication failed at tier: {tier}",
            "Check environment variables and configuration",
            "Verify Snowflake connection parameters",
        ]

        llm_api_suggestions = [
            "Use session_manager.get_session() for session management",
            "Check SNOWFLAKE_* environment variables",
            "Verify connections.toml configuration",
        ]

        self.error(
            f"Authentication failed at tier {tier}",
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            exception=error,
            context={
                "authentication_tier": tier,
                "available_tiers": [
                    "active_session",
                    "connections_toml",
                    "environment_variables",
                ],
                **(context or {}),
            },
            action_guidance=action_guidance,
            llm_api_suggestions=llm_api_suggestions,
        )

    def environment_detected(
        self, environment: RuntimeEnvironment, capabilities: Dict[str, bool]
    ):
        """Log environment detection for LLM consumption."""
        self.info(
            f"Runtime environment detected: {environment.value}",
            context={
                "environment": environment.value,
                "capabilities": capabilities,
                "available_operations": [
                    op for op, available in capabilities.items() if available
                ],
                "unavailable_operations": [
                    op for op, available in capabilities.items() if not available
                ],
            },
        )


# Global LLM logger instance
llm_logger = LLMLogger("svg_image_generator.llm")


def get_llm_logger(name: str) -> LLMLogger:
    """Get an LLM logger instance for a specific module."""
    return LLMLogger(name)


def log_environment_summary():
    """Log a comprehensive environment summary for LLM consumption."""
    try:
        env_info = get_environment_info()
        capabilities = env_info.get("capabilities", {})

        available_ops = [op for op, available in capabilities.items() if available]
        unavailable_ops = [
            op for op, available in capabilities.items() if not available
        ]

        llm_logger.info(
            "Environment summary for LLM assistant",
            context={
                "environment_summary": env_info,
                "available_operations": available_ops,
                "unavailable_operations": unavailable_ops,
                "recommended_approaches": {
                    "local_development": [
                        "Use SnowSQL CLI for database operations",
                        "Use Git for version control",
                        "Use local file system for file operations",
                    ],
                    "snowflake_runtime": [
                        "Use session.sql() for database operations",
                        "Use Snowflake stages for file storage",
                        "Use SNOWFLAKE.CORTEX.COMPLETE() for AI operations",
                    ],
                },
            },
        )

    except Exception as e:
        llm_logger.error(
            "Failed to generate environment summary",
            error_code=ErrorCode.ENVIRONMENT_DETECTION_FAILED,
            exception=e,
        )


def log_operation_attempt(operation: str, required_capabilities: List[str]):
    """Log an operation attempt for LLM consumption."""
    try:
        from .runtime_detection import (
            get_environment_capabilities,
            validate_operation_for_environment,
        )

        capabilities = get_environment_capabilities()
        is_valid = validate_operation_for_environment(operation, required_capabilities)

        if is_valid:
            llm_logger.info(
                f"Operation '{operation}' validated for current environment",
                context={
                    "operation": operation,
                    "required_capabilities": required_capabilities,
                    "capabilities_available": True,
                },
            )
        else:
            llm_logger.runtime_mismatch(operation, required_capabilities, capabilities)

    except Exception as e:
        llm_logger.error(
            f"Failed to validate operation '{operation}'",
            error_code=ErrorCode.UNEXPECTED_ERROR,
            exception=e,
            context={
                "operation": operation,
                "required_capabilities": required_capabilities,
            },
        )
