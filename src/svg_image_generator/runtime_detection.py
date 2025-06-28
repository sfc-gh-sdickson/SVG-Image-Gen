"""
Runtime Environment Detection

This module provides functionality to detect the current runtime environment
and determine what capabilities are available. It helps prevent operations
that are not suitable for the current environment (e.g., CLI operations in Snowflake).

IMPORTANT: These restrictions exist primarily to protect Snowflake's platform liability,
not to protect your business or users. They prevent operations that could expose
Snowflake to legal/operational risk. The business owns the business—don't let
platform safety rules accidentally expand compliance/IT authority at the expense
of business agility.
"""

import logging
import os
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Check if Snowflake packages are available
try:
    from snowflake.snowpark.session import SnowparkSessionException, get_active_session

    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False


class RuntimeEnvironment(Enum):
    """Enumeration of possible runtime environments."""

    LOCAL_DEVELOPMENT = "local_development"
    STREAMLIT_IN_SNOWFLAKE = "streamlit_in_snowflake"
    SNOWFLAKE_STORED_PROCEDURE = "snowflake_stored_procedure"
    SNOWFLAKE_USER_DEFINED_FUNCTION = "snowflake_udf"
    SNOWFLAKE_TASK = "snowflake_task"
    UNKNOWN = "unknown"


def detect_runtime_environment() -> RuntimeEnvironment:
    """
    Detect the current runtime environment.

    Returns:
        RuntimeEnvironment: The detected runtime environment
    """
    logger.info("Starting runtime environment detection")

    if SNOWFLAKE_AVAILABLE:
        try:
            session = get_active_session()
            if session is not None:
                logger.info("Active Snowflake session detected")

                # Try to determine the specific Snowflake environment
                try:
                    # Check for Streamlit-specific environment variables
                    if os.environ.get("STREAMLIT_SERVER_PORT"):
                        logger.info(
                            "Streamlit in Snowflake (SiS) environment detected",
                            extra={"environment_type": "streamlit_in_snowflake"},
                        )
                        return RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE

                    # Check for stored procedure context
                    if os.environ.get("SNOWFLAKE_PROCEDURE_NAME"):
                        logger.info(
                            "Snowflake stored procedure environment detected",
                            extra={"environment_type": "snowflake_stored_procedure"},
                        )
                        return RuntimeEnvironment.SNOWFLAKE_STORED_PROCEDURE

                    # Check for UDF context
                    if os.environ.get("SNOWFLAKE_UDF_NAME"):
                        logger.info(
                            "Snowflake UDF environment detected",
                            extra={"environment_type": "snowflake_udf"},
                        )
                        return RuntimeEnvironment.SNOWFLAKE_USER_DEFINED_FUNCTION

                    # Check for task context
                    if os.environ.get("SNOWFLAKE_TASK_NAME"):
                        logger.info(
                            "Snowflake task environment detected",
                            extra={"environment_type": "snowflake_task"},
                        )
                        return RuntimeEnvironment.SNOWFLAKE_TASK

                    # Generic Snowflake environment
                    logger.info(
                        "Generic Snowflake environment detected",
                        extra={"environment_type": "generic_snowflake"},
                    )
                    return RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE

                except Exception as e:
                    logger.warning(
                        "Error determining specific Snowflake environment",
                        extra={"error": str(e)},
                    )
                    return RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE

        except SnowparkSessionException:
            logger.info(
                "No active Snowflake session - local development environment",
                extra={"environment_type": "local_development"},
            )
            return RuntimeEnvironment.LOCAL_DEVELOPMENT
        except Exception as e:
            logger.warning("Error checking Snowflake session", extra={"error": str(e)})
            return RuntimeEnvironment.LOCAL_DEVELOPMENT
    else:
        logger.info(
            "Snowflake packages not available - local development environment",
            extra={"environment_type": "local_development"},
        )
        return RuntimeEnvironment.LOCAL_DEVELOPMENT


def is_snowflake_runtime() -> bool:
    """
    Check if we're running inside a Snowflake runtime environment.

    Returns:
        bool: True if running inside Snowflake, False otherwise
    """
    env = detect_runtime_environment()
    is_snowflake = env in [
        RuntimeEnvironment.STREAMLIT_IN_SNOWFLAKE,
        RuntimeEnvironment.SNOWFLAKE_STORED_PROCEDURE,
        RuntimeEnvironment.SNOWFLAKE_USER_DEFINED_FUNCTION,
        RuntimeEnvironment.SNOWFLAKE_TASK,
    ]

    logger.info(
        f"Snowflake runtime check: {is_snowflake}",
        extra={"detected_environment": env.value, "is_snowflake_runtime": is_snowflake},
    )

    return is_snowflake


def is_local_development() -> bool:
    """
    Check if we're running in local development environment.

    Returns:
        bool: True if running locally, False otherwise
    """
    env = detect_runtime_environment()
    is_local = env == RuntimeEnvironment.LOCAL_DEVELOPMENT

    logger.info(
        f"Local development check: {is_local}",
        extra={"detected_environment": env.value, "is_local_development": is_local},
    )

    return is_local


def get_environment_capabilities() -> Dict[str, bool]:
    """
    Get a dictionary of capabilities available in the current environment.

    Returns:
        Dict[str, bool]: Dictionary mapping capability names to availability
    """
    is_snowflake = is_snowflake_runtime()

    capabilities = {
        # File system operations
        "filesystem_read": not is_snowflake,  # Limited in Snowflake
        "filesystem_write": not is_snowflake,  # Limited in Snowflake
        "local_file_access": not is_snowflake,  # Limited in Snowflake
        # Network operations
        "external_network_access": not is_snowflake,  # Restricted in Snowflake
        "git_operations": not is_snowflake,  # No external Git access in Snowflake
        "http_requests": not is_snowflake,  # Restricted in Snowflake
        # Process operations
        "subprocess_execution": not is_snowflake,  # No subprocess in Snowflake
        "cli_tools": not is_snowflake,  # No CLI tools in Snowflake
        "package_installation": not is_snowflake,  # No pip/uv in Snowflake
        # Environment operations
        "environment_variables": not is_snowflake,  # Different env in Snowflake
        "user_home_access": not is_snowflake,  # No user home in Snowflake
        # Snowflake-specific capabilities
        "snowflake_session": is_snowflake,  # Available in Snowflake
        "snowflake_sql": is_snowflake,  # Available in Snowflake
        "cortex_ai": is_snowflake,  # Available in Snowflake
        "snowflake_stages": is_snowflake,  # Available in Snowflake
    }

    available_ops = [op for op, available in capabilities.items() if available]
    unavailable_ops = [op for op, available in capabilities.items() if not available]

    logger.info(
        "Environment capabilities determined",
        extra={
            "capabilities": capabilities,
            "available_operations": available_ops,
            "unavailable_operations": unavailable_ops,
            "total_capabilities": len(capabilities),
            "available_count": len(available_ops),
            "unavailable_count": len(unavailable_ops),
        },
    )

    return capabilities


def check_capability(capability: str) -> bool:
    """
    Check if a specific capability is available in the current environment.

    Args:
        capability (str): Name of the capability to check

    Returns:
        bool: True if capability is available, False otherwise
    """
    capabilities = get_environment_capabilities()
    is_available = capabilities.get(capability, False)

    logger.info(
        f"Capability check: {capability} = {is_available}",
        extra={
            "capability": capability,
            "is_available": is_available,
            "all_capabilities": capabilities,
        },
    )

    return is_available


def validate_operation_for_environment(
    operation: str, required_capabilities: list
) -> bool:
    """
    Validate if an operation can be performed in the current environment.

    Args:
        operation (str): Name of the operation
        required_capabilities (list): List of required capabilities

    Returns:
        bool: True if operation can be performed, False otherwise
    """
    logger.info(
        f"Validating operation for environment",
        extra={"operation": operation, "required_capabilities": required_capabilities},
    )

    capabilities = get_environment_capabilities()
    missing_capabilities = []

    for capability in required_capabilities:
        if not check_capability(capability):
            missing_capabilities.append(capability)

    is_valid = len(missing_capabilities) == 0

    if is_valid:
        logger.info(
            f"Operation '{operation}' is valid for current environment",
            extra={
                "operation": operation,
                "validation_status": "valid",
                "required_capabilities": required_capabilities,
            },
        )
    else:
        logger.warning(
            f"Operation '{operation}' requires capabilities that are not available",
            extra={
                "operation": operation,
                "validation_status": "invalid",
                "required_capabilities": required_capabilities,
                "missing_capabilities": missing_capabilities,
                "available_capabilities": capabilities,
            },
        )

    return is_valid


def get_environment_info() -> Dict[str, Any]:
    """
    Get comprehensive information about the current runtime environment.

    Returns:
        Dict[str, Any]: Environment information
    """
    env = detect_runtime_environment()
    capabilities = get_environment_capabilities()

    info = {
        "environment": env.value,
        "is_snowflake_runtime": is_snowflake_runtime(),
        "is_local_development": is_local_development(),
        "capabilities": capabilities,
        "snowflake_available": SNOWFLAKE_AVAILABLE,
    }

    # Add environment-specific details
    if is_snowflake_runtime():
        try:
            session = get_active_session()
            info["session_available"] = session is not None
            info["session_type"] = type(session).__name__ if session else None
        except Exception as e:
            info["session_available"] = False
            info["session_error"] = str(e)

    logger.info(
        "Environment information collected",
        extra={
            "environment_info": info,
            "environment_summary": {
                "type": env.value,
                "capability_count": len(capabilities),
                "snowflake_available": SNOWFLAKE_AVAILABLE,
            },
        },
    )

    return info


# Convenience functions for common checks
def can_use_snowsql() -> bool:
    """Check if SnowSQL operations are available."""
    can_use = check_capability("cli_tools") and check_capability("subprocess_execution")

    logger.info(
        f"SnowSQL availability check: {can_use}",
        extra={
            "can_use_snowsql": can_use,
            "cli_tools_available": check_capability("cli_tools"),
            "subprocess_available": check_capability("subprocess_execution"),
        },
    )

    return can_use


def can_use_git() -> bool:
    """Check if Git operations are available."""
    can_use = check_capability("git_operations") and check_capability(
        "external_network_access"
    )

    logger.info(
        f"Git availability check: {can_use}",
        extra={
            "can_use_git": can_use,
            "git_operations_available": check_capability("git_operations"),
            "network_access_available": check_capability("external_network_access"),
        },
    )

    return can_use


def can_use_local_files() -> bool:
    """Check if local file operations are available."""
    can_use = check_capability("filesystem_read") and check_capability(
        "filesystem_write"
    )

    logger.info(
        f"Local file operations availability check: {can_use}",
        extra={
            "can_use_local_files": can_use,
            "filesystem_read_available": check_capability("filesystem_read"),
            "filesystem_write_available": check_capability("filesystem_write"),
        },
    )

    return can_use


def can_use_cortex() -> bool:
    """Check if Snowflake Cortex operations are available."""
    can_use = check_capability("cortex_ai") and check_capability("snowflake_session")

    logger.info(
        f"Cortex availability check: {can_use}",
        extra={
            "can_use_cortex": can_use,
            "cortex_ai_available": check_capability("cortex_ai"),
            "snowflake_session_available": check_capability("snowflake_session"),
        },
    )

    return can_use
