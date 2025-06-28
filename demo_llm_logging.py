#!/usr/bin/env python3
"""
LLM-Friendly Logging Demonstration

This script demonstrates how the LLM-friendly logging system works
and produces structured, parseable logs that can be consumed by LLM assistants.
"""

import json
import logging
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from svg_image_generator.llm_logging import (
    ErrorCode,
    LLMLogger,
    LogLevel,
    get_llm_logger,
    log_environment_summary,
    log_operation_attempt,
)
from svg_image_generator.runtime_detection import (
    RuntimeEnvironment,
    get_environment_info,
)


def setup_logging():
    """Setup logging to show structured output."""
    # Configure logging to show the structured JSON
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def demonstrate_basic_logging():
    """Demonstrate basic LLM-friendly logging."""
    print("\n" + "=" * 60)
    print("BASIC LLM-FRIENDLY LOGGING DEMONSTRATION")
    print("=" * 60)

    logger = get_llm_logger("demo.basic")

    # Basic info log with context
    logger.info(
        "Starting application initialization",
        context={
            "application": "SVG Image Generator",
            "version": "1.0.0",
            "initialization_step": "basic_setup",
        },
    )

    # Warning log with structured data
    logger.warning(
        "Configuration file not found, using defaults",
        context={
            "config_file": "config.yaml",
            "default_config": True,
            "fallback_behavior": "use_defaults",
        },
    )

    # Error log with error code and guidance
    logger.error(
        "Failed to connect to external service",
        error_code=ErrorCode.NETWORK_ERROR,
        context={
            "service": "git_api",
            "endpoint": "https://api.github.com/repos",
            "timeout": 30,
        },
        action_guidance=[
            "Check network connectivity",
            "Verify service endpoint is accessible",
            "Consider using alternative service",
        ],
        llm_api_suggestions=[
            "Use Snowflake external functions for API calls",
            "Implement retry logic with exponential backoff",
            "Use Snowflake stages for data storage",
        ],
    )


def demonstrate_runtime_detection():
    """Demonstrate runtime detection logging."""
    print("\n" + "=" * 60)
    print("RUNTIME DETECTION LOGGING DEMONSTRATION")
    print("=" * 60)

    logger = get_llm_logger("demo.runtime")

    # Get environment info
    env_info = get_environment_info()

    # Log environment detection
    logger.info(
        "Runtime environment detected",
        context={
            "environment_type": env_info["environment"],
            "capabilities": env_info["capabilities"],
            "available_operations": [
                op for op, available in env_info["capabilities"].items() if available
            ],
            "unavailable_operations": [
                op
                for op, available in env_info["capabilities"].items()
                if not available
            ],
        },
    )

    # Demonstrate capability checks
    logger.info(
        "Capability assessment completed",
        context={
            "can_use_snowsql": env_info["capabilities"].get("cli_tools", False),
            "can_use_git": env_info["capabilities"].get("git_operations", False),
            "can_use_cortex": env_info["capabilities"].get("cortex_ai", False),
            "can_use_local_files": env_info["capabilities"].get(
                "filesystem_read", False
            ),
        },
    )


def demonstrate_operation_validation():
    """Demonstrate operation validation logging."""
    print("\n" + "=" * 60)
    print("OPERATION VALIDATION LOGGING DEMONSTRATION")
    print("=" * 60)

    logger = get_llm_logger("demo.validation")

    # Test SnowSQL operation
    log_operation_attempt("run_snowsql_command", ["cli_tools", "subprocess_execution"])

    # Test Git operation
    log_operation_attempt(
        "list_accessible_repositories", ["git_operations", "external_network_access"]
    )

    # Test file operation
    log_operation_attempt("read_local_file", ["filesystem_read"])


def demonstrate_error_scenarios():
    """Demonstrate error scenario logging."""
    print("\n" + "=" * 60)
    print("ERROR SCENARIO LOGGING DEMONSTRATION")
    print("=" * 60)

    logger = get_llm_logger("demo.errors")

    # Simulate SnowSQL unavailability
    logger.snowsql_unavailable(
        "install_snowsql",
        context={
            "requested_method": "pip",
            "environment": "streamlit_in_snowflake",
            "reason": "cli_tools_not_available",
        },
    )

    # Simulate Git unavailability
    logger.git_unavailable(
        "push_to_repository",
        context={
            "repository": "https://github.com/example/repo",
            "branch": "main",
            "reason": "external_network_access_restricted",
        },
    )

    # Simulate authentication failure
    auth_error = ConnectionError("Failed to connect to Snowflake: Invalid credentials")
    logger.authentication_failed(
        "environment_variables",
        auth_error,
        context={
            "connection_string": "snowflake://user@account/database",
            "error_type": "credential_validation_failed",
        },
    )


def demonstrate_llm_consumption():
    """Demonstrate how an LLM would consume these logs."""
    print("\n" + "=" * 60)
    print("LLM CONSUMPTION DEMONSTRATION")
    print("=" * 60)

    # Create a sample log entry
    logger = get_llm_logger("demo.llm_consumption")

    # Generate a structured log entry
    log_entry = logger._create_llm_log_entry(
        LogLevel.ERROR,
        "Operation failed due to runtime constraints",
        error_code=ErrorCode.RUNTIME_MISMATCH,
        context={
            "operation": "git_push",
            "required_capabilities": ["git_operations", "external_network_access"],
            "available_capabilities": {
                "git_operations": False,
                "external_network_access": False,
            },
        },
        action_guidance=[
            "Use Snowflake stages for file storage instead of Git",
            "Use Snowflake external functions for external API calls",
            "Consider using Snowflake streams for data pipelines",
        ],
        llm_api_suggestions=[
            "Use session.sql() for database operations",
            "Use SNOWFLAKE.CORTEX.COMPLETE() for AI operations",
            "Use Snowflake stages for file operations",
        ],
    )

    # Show the structured log entry
    print("STRUCTURED LOG ENTRY (JSON format for LLM consumption):")
    print(json.dumps(log_entry, indent=2))

    print("\nLLM CONSUMPTION ANALYSIS:")
    print("-" * 40)

    # Simulate LLM parsing the log
    print(f"1. ERROR CODE: {log_entry['error_code']}")
    print(f"2. OPERATION: {log_entry['context']['operation']}")
    print(
        f"3. MISSING CAPABILITIES: {[cap for cap, available in log_entry['context']['available_capabilities'].items() if not available]}"
    )
    print(f"4. ENVIRONMENT: {log_entry['environment']['environment']}")

    print("\n5. ACTIONABLE GUIDANCE:")
    for i, guidance in enumerate(log_entry["action_guidance"], 1):
        print(f"   {i}. {guidance}")

    print("\n6. LLM API SUGGESTIONS:")
    for i, suggestion in enumerate(log_entry["llm_api_suggestions"], 1):
        print(f"   {i}. {suggestion}")


def main():
    """Run the LLM logging demonstration."""
    print("LLM-FRIENDLY LOGGING SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demonstration shows how the logging system provides")
    print("structured, parseable information for LLM consumption.")
    print()

    setup_logging()

    # Run demonstrations
    demonstrate_basic_logging()
    demonstrate_runtime_detection()
    demonstrate_operation_validation()
    demonstrate_error_scenarios()
    demonstrate_llm_consumption()

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("The LLM-friendly logging system provides:")
    print("✓ Structured, JSON-formatted log entries")
    print("✓ Error codes for programmatic parsing")
    print("✓ Complete context information")
    print("✓ Actionable guidance for developers")
    print("✓ LLM API suggestions for alternatives")
    print("✓ Environment-aware logging")
    print("✓ Machine-readable error patterns")


if __name__ == "__main__":
    main()
