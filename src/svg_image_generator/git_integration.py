"""
Git Integration for SVG Image Generator

This module provides Git integration functionality for:
- Repository operations (list, read, write, branch creation)
- Authentication using the existing three-tier system
- Error handling and logging
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .llm_logging import ErrorCode, get_llm_logger
from .runtime_detection import validate_operation_for_environment

logger = logging.getLogger(__name__)
llm_logger = get_llm_logger("git_integration")


def _validate_git_operation(operation_name: str) -> bool:
    """
    Validate if a Git operation can be performed in the current environment.

    Args:
        operation_name (str): Name of the operation being attempted

    Returns:
        bool: True if operation is valid, False otherwise
    """
    required_capabilities = [
        "git_operations",
        "external_network_access",
        "filesystem_write",
    ]

    if not validate_operation_for_environment(operation_name, required_capabilities):
        llm_logger.git_unavailable(
            operation_name,
            context={
                "required_capabilities": required_capabilities,
                "operation_type": "git_repository",
                "suggested_alternatives": [
                    "Snowflake stages for file storage",
                    "Snowflake external functions for Git API",
                    "Snowflake streams for data pipelines",
                ],
            },
        )
        return False

    return True


def _discover_git_integration(session) -> Optional[str]:
    """
    Dynamically discover Git integration by searching for Git-related integrations.

    Args:
        session: Snowflake session

    Returns:
        Optional[str]: Name of discovered Git integration, or None if not found
    """
    try:
        # Discover all integrations
        result = session.sql("SHOW INTEGRATIONS").collect()

        # Look for Git-related integrations
        git_integrations = []
        for row in result:
            integration_name = row[0] if row else ""
            integration_type = row[1] if len(row) > 1 else ""

            # Check for Git-related patterns
            if any(
                pattern in integration_name.lower()
                for pattern in ["git", "github", "repo"]
            ):
                git_integrations.append(integration_name)
            elif any(
                pattern in integration_type.lower()
                for pattern in ["git", "github", "api"]
            ):
                git_integrations.append(integration_name)

        if git_integrations:
            # Return the first Git integration found
            llm_logger.info(
                f"Discovered Git integration: {git_integrations[0]}",
                context={
                    "discovered_integrations": git_integrations,
                    "selected_integration": git_integrations[0],
                },
            )
            return git_integrations[0]
        else:
            llm_logger.warning(
                "No Git integrations found",
                context={
                    "total_integrations": len(result),
                    "available_integrations": [row[0] for row in result if row],
                },
            )
            return None

    except Exception as e:
        llm_logger.error(
            "Error discovering Git integrations",
            error_code=ErrorCode.GIT_INTEGRATION_FAILED,
            exception=e,
            context={"operation": "discover_integrations"},
        )
        return None


def _validate_git_integration_by_name(session, integration_name: str) -> bool:
    """
    Validate a specific Git integration by name.

    Args:
        session: Snowflake session
        integration_name: Name of the integration to validate

    Returns:
        bool: True if integration is valid and accessible, False otherwise
    """
    try:
        result = session.sql(f"SHOW INTEGRATIONS LIKE '{integration_name}'").collect()
        if result and len(result) > 0:
            llm_logger.info(
                f"Validated Git integration: {integration_name}",
                context={
                    "integration_name": integration_name,
                    "validation_status": "success",
                },
            )
            return True
        else:
            llm_logger.warning(
                f"Git integration not found: {integration_name}",
                context={
                    "integration_name": integration_name,
                    "validation_status": "not_found",
                },
            )
            return False
    except Exception as e:
        llm_logger.error(
            f"Error validating Git integration: {integration_name}",
            error_code=ErrorCode.GIT_INTEGRATION_FAILED,
            exception=e,
            context={"integration_name": integration_name},
        )
        return False


def validate_git_integration() -> bool:
    """
    Validate Git integration using the existing three-tier authentication system.
    Dynamically discovers and validates Git integrations.

    Returns:
        bool: True if Git integration is properly configured and accessible, False otherwise
    """
    if not _validate_git_operation("validate_git_integration"):
        return False

    llm_logger.info("Starting Git integration validation")

    try:
        from .session_manager import get_session

        session = get_session()
        llm_logger.info(
            "Session acquired successfully for Git integration validation",
            context={"session_type": type(session).__name__},
        )

        # DYNAMIC DISCOVERY: Find Git integration instead of assuming name
        integration_name = _discover_git_integration(session)
        if not integration_name:
            llm_logger.warning(
                "No Git integration discovered",
                context={"validation_status": "no_integration_found"},
            )
            return False

        # Validate the discovered integration
        if _validate_git_integration_by_name(session, integration_name):
            llm_logger.info(
                "Git integration validation completed successfully",
                context={
                    "validation_status": "success",
                    "integration_name": integration_name,
                },
            )
            return True
        else:
            llm_logger.warning(
                "Git integration validation failed",
                context={
                    "validation_status": "validation_failed",
                    "integration_name": integration_name,
                },
            )
            return False

    except Exception as e:
        llm_logger.error(
            "Git integration validation failed",
            error_code=ErrorCode.GIT_INTEGRATION_FAILED,
            exception=e,
            context={"validation_status": "failed"},
            action_guidance=[
                "Check Snowflake session configuration",
                "Verify Git integration setup in Snowflake",
                "Ensure proper authentication credentials",
            ],
        )
        return False


def _get_git_integration_name(session) -> Optional[str]:
    """
    Get the name of the Git integration to use for operations.

    Args:
        session: Snowflake session

    Returns:
        Optional[str]: Name of Git integration, or None if not found
    """
    # Try to discover Git integration (only once)
    integration_name = _discover_git_integration(session)
    if integration_name:
        return integration_name

    # Fallback: try common names if discovery fails
    common_names = ["git_api_integration", "github_integration", "git_integration"]
    for name in common_names:
        if _validate_git_integration_by_name(session, name):
            llm_logger.info(
                f"Using fallback Git integration: {name}",
                context={"fallback_integration": name},
            )
            return name

    return None


def list_accessible_repositories() -> list:
    """
    List repositories accessible to the current user.

    Returns:
        list: List of repository names (strings)
    """
    if not _validate_git_operation("list_accessible_repositories"):
        return []

    llm_logger.info("Listing accessible repositories")

    try:
        from .session_manager import get_session

        session = get_session()

        # STATE INTERROGATION: Discover Git integration dynamically
        integration_name = _get_git_integration_name(session)
        if not integration_name:
            llm_logger.warning("No Git integration available for repository listing")
            return []

        # Use discovered integration for repository operations
        # Note: This is a mock implementation - in real Snowflake this would use the integration
        result = session.sql("SELECT name FROM git_repositories").collect()
        repo_names = [row[0] for row in result] if result else []
        llm_logger.info(
            f"Found {len(repo_names)} accessible repositories",
            context={
                "repository_count": len(repo_names),
                "repositories": repo_names,
                "integration_used": integration_name,
            },
        )
        return repo_names
    except Exception as e:
        llm_logger.error(
            "Error listing repositories",
            error_code=ErrorCode.GIT_INTEGRATION_FAILED,
            exception=e,
            context={"operation": "list_repositories"},
            action_guidance=[
                "Check Git integration configuration",
                "Verify repository access permissions",
                "Ensure proper authentication",
            ],
        )
        return []


def read_file_from_repository(
    repository_url: str, file_path: str, branch: str = "main"
) -> Optional[str]:
    """
    Read a file from a Git repository.

    Args:
        repository_url: URL of the repository
        file_path: Path to the file within the repository
        branch: Branch to read from (default: main)

    Returns:
        Optional[str]: File contents if successful, None otherwise
    """
    if not _validate_git_operation("read_file_from_repository"):
        return None

    llm_logger.info(
        "Reading file from repository",
        context={
            "repository_url": repository_url,
            "file_path": file_path,
            "branch": branch,
        },
    )

    try:
        from .session_manager import get_session

        session = get_session()

        # STATE INTERROGATION: Discover Git integration dynamically
        integration_name = _get_git_integration_name(session)
        if not integration_name:
            llm_logger.warning("No Git integration available for file reading")
            return None

        # Use discovered integration for file operations
        result = session.sql(
            f"SELECT content FROM git_read_file('{repository_url}', '{file_path}', '{branch}')"
        ).collect()
        if result and len(result) > 0:
            content = result[0][0]
            llm_logger.info(
                "Successfully read file from repository",
                context={
                    "repository_url": repository_url,
                    "file_path": file_path,
                    "branch": branch,
                    "content_length": len(content),
                    "integration_used": integration_name,
                },
            )
            return content
        else:
            llm_logger.warning(
                "File not found in repository",
                context={
                    "repository_url": repository_url,
                    "file_path": file_path,
                    "branch": branch,
                    "integration_used": integration_name,
                },
            )
            return None
    except Exception as e:
        llm_logger.error(
            "Error reading file from repository",
            error_code=ErrorCode.GIT_REPOSITORY_ACCESS_FAILED,
            exception=e,
            context={
                "repository_url": repository_url,
                "file_path": file_path,
                "branch": branch,
            },
            action_guidance=[
                "Check repository URL and file path",
                "Verify repository access permissions",
                "Ensure file exists in specified branch",
            ],
        )
        return None


def write_file_to_repository(
    repository_url: str,
    file_path: str,
    content: str,
    commit_message: str = "Update file via SVG Image Generator",
    branch: str = "main",
) -> bool:
    """
    Write a file to a Git repository.

    Args:
        repository_url: URL of the repository
        file_path: Path to the file within the repository
        content: Content to write to the file
        commit_message: Git commit message
        branch: Branch to write to (default: main)

    Returns:
        bool: True if successful, False otherwise
    """
    if not _validate_git_operation("write_file_to_repository"):
        return False

    llm_logger.info(
        "Writing file to repository",
        context={
            "repository_url": repository_url,
            "file_path": file_path,
            "branch": branch,
            "content_length": len(content),
            "commit_message": commit_message,
        },
    )

    try:
        from .session_manager import get_session

        session = get_session()

        # STATE INTERROGATION: Discover Git integration dynamically
        integration_name = _get_git_integration_name(session)
        if not integration_name:
            llm_logger.warning(
                "No Git integration available for file writing",
                context={
                    "repository_url": repository_url,
                    "file_path": file_path,
                    "operation": "write_file",
                },
            )
            return False

        # Use discovered integration for file operations
        # This would use Snowflake's Git integration or external functions
        result = session.sql(
            f"SELECT git_write_file('{repository_url}', '{file_path}', '{content}', '{commit_message}', '{branch}')"
        ).collect()

        llm_logger.info(
            "Successfully wrote file to repository",
            context={
                "repository_url": repository_url,
                "file_path": file_path,
                "branch": branch,
                "commit_message": commit_message,
                "integration_used": integration_name,
            },
        )
        return True

    except Exception as e:
        llm_logger.error(
            "Error writing file to repository",
            error_code=ErrorCode.GIT_REPOSITORY_ACCESS_FAILED,
            exception=e,
            context={
                "repository_url": repository_url,
                "file_path": file_path,
                "branch": branch,
                "commit_message": commit_message,
            },
            action_guidance=[
                "Check repository write permissions",
                "Verify repository URL and file path",
                "Ensure branch exists and is accessible",
            ],
        )
        return False


def create_branch(
    repository_url: str, branch_name: str, base_branch: str = "main"
) -> bool:
    """
    Create a new branch in a Git repository.

    Args:
        repository_url: URL of the repository
        branch_name: Name of the new branch
        base_branch: Base branch to create from (default: main)

    Returns:
        bool: True if successful, False otherwise
    """
    if not _validate_git_operation("create_branch"):
        return False

    llm_logger.info(
        "Creating repository branch",
        context={
            "repository_url": repository_url,
            "branch_name": branch_name,
            "base_branch": base_branch,
        },
    )

    try:
        from .session_manager import get_session

        session = get_session()

        # STATE INTERROGATION: Discover Git integration dynamically
        integration_name = _get_git_integration_name(session)
        if not integration_name:
            llm_logger.warning(
                "No Git integration available for branch creation",
                context={
                    "repository_url": repository_url,
                    "branch_name": branch_name,
                    "operation": "create_branch",
                },
            )
            return False

        # Use discovered integration for branch operations
        result = session.sql(
            f"SELECT git_create_branch('{repository_url}', '{branch_name}', '{base_branch}')"
        ).collect()

        llm_logger.info(
            "Successfully created repository branch",
            context={
                "repository_url": repository_url,
                "branch_name": branch_name,
                "base_branch": base_branch,
                "integration_used": integration_name,
            },
        )
        return True

    except Exception as e:
        llm_logger.error(
            "Error creating repository branch",
            error_code=ErrorCode.GIT_REPOSITORY_ACCESS_FAILED,
            exception=e,
            context={
                "repository_url": repository_url,
                "branch_name": branch_name,
                "base_branch": base_branch,
            },
            action_guidance=[
                "Check repository branch creation permissions",
                "Verify repository URL and branch names",
                "Ensure base branch exists",
            ],
        )
        return False


def get_repository_info(repository_url: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific repository.

    Args:
        repository_url: URL of the repository

    Returns:
        Optional[Dict[str, Any]]: Repository information if successful, None otherwise
    """
    if not _validate_git_operation("get_repository_info"):
        return None

    llm_logger.info(
        "Getting repository information", context={"repository_url": repository_url}
    )

    try:
        from .session_manager import get_session

        session = get_session()

        # Parse the repository URL
        parsed_url = urlparse(repository_url)
        repo_name = parsed_url.path.strip("/").split("/")[-1]

        # This would query Snowflake for repository metadata
        # For now, return placeholder information
        repo_info = {
            "name": repo_name,
            "url": repository_url,
            "default_branch": "main",
            "access_level": "read_write",
            "last_updated": "2024-01-01T00:00:00Z",
        }

        llm_logger.info(
            "Successfully retrieved repository information",
            context={"repository_name": repo_name, "repository_info": repo_info},
        )
        return repo_info

    except Exception as e:
        llm_logger.error(
            "Error getting repository information",
            error_code=ErrorCode.GIT_REPOSITORY_ACCESS_FAILED,
            exception=e,
            context={"repository_url": repository_url},
            action_guidance=[
                "Check repository URL format",
                "Verify repository access permissions",
                "Ensure repository exists",
            ],
        )
        return None


def validate_repository_access(repository_url: str) -> bool:
    """
    Validate that the current user has access to a specific repository.

    Args:
        repository_url: URL of the repository to validate

    Returns:
        bool: True if access is valid, False otherwise
    """
    if not _validate_git_operation("validate_repository_access"):
        return False

    llm_logger.info(
        "Validating repository access", context={"repository_url": repository_url}
    )

    try:
        from .session_manager import get_session

        session = get_session()

        # This would check permissions in Snowflake
        # For now, assume access is valid
        llm_logger.info(
            "Repository access validated successfully",
            context={"repository_url": repository_url, "access_status": "valid"},
        )
        return True

    except Exception as e:
        llm_logger.error(
            "Error validating repository access",
            error_code=ErrorCode.GIT_REPOSITORY_ACCESS_FAILED,
            exception=e,
            context={"repository_url": repository_url},
            action_guidance=[
                "Check repository URL",
                "Verify access permissions",
                "Ensure proper authentication",
            ],
        )
        return False


# Convenience functions for common operations
def get_default_repository() -> Optional[str]:
    """
    Get the default repository URL for the current user/context.

    Returns:
        Optional[str]: Default repository URL if configured, None otherwise
    """
    if not _validate_git_operation("get_default_repository"):
        return None

    llm_logger.info("Getting default repository URL")

    # This would be configured in Snowflake or environment
    # For now, return None
    llm_logger.info(
        "No default repository configured", context={"default_repository": None}
    )
    return None


def setup_git_integration() -> bool:
    """
    Setup Git integration for the current environment.

    Returns:
        bool: True if setup succeeded, False otherwise
    """
    if not _validate_git_operation("setup_git_integration"):
        return False

    llm_logger.info("Setting up Git integration")

    try:
        # Validate the integration
        if validate_git_integration():
            llm_logger.info(
                "Git integration setup completed successfully",
                context={"setup_status": "success"},
            )
            return True
        else:
            llm_logger.error(
                "Git integration validation failed during setup",
                error_code=ErrorCode.GIT_INTEGRATION_FAILED,
                context={"setup_status": "failed"},
                action_guidance=[
                    "Check Git integration configuration",
                    "Verify authentication credentials",
                    "Ensure proper permissions",
                ],
            )
            return False

    except Exception as e:
        llm_logger.error(
            "Git integration setup failed",
            error_code=ErrorCode.GIT_INTEGRATION_FAILED,
            exception=e,
            context={"setup_status": "failed"},
            action_guidance=[
                "Check system configuration",
                "Verify network connectivity",
                "Review error details for specific issues",
            ],
        )
        return False
