"""
Git Integration Module for SVG Image Generator.

This module provides Git repository operations using Snowflake's API integration
capabilities, leveraging the existing three-tier authentication system.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Import the session manager for authentication
from .session_manager import get_session

# Set up logging
logger = logging.getLogger(__name__)


class GitIntegration:
    """
    Handles Git repository operations via Snowflake API integration.

    This class provides methods to interact with GitHub repositories through
    Snowflake's API integration capabilities, using the existing authentication
    system instead of hardcoded credentials.
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize Git integration with a Snowflake session.

        Args:
            session: Snowflake session. If None, will use get_session().
        """
        if session is None:
            self.session = get_session()
        else:
            self.session = session
        self.api_integration = "git_api_integration"
        logger.info("GitIntegration initialized with session")

    def validate_integration(self) -> bool:
        """
        Validate that the Git API integration exists and is accessible.

        Returns:
            True if integration exists and is accessible, False otherwise.
        """
        try:
            logger.info("Validating Git API integration")

            # Check if the integration exists
            df = self.session.sql(f"SHOW INTEGRATIONS LIKE '{self.api_integration}'")
            result = df.collect()

            if result and len(result) > 0:
                logger.info(
                    f"Git API integration '{self.api_integration}' found and accessible"
                )
                return True
            else:
                logger.warning(
                    f"Git API integration '{self.api_integration}' not found"
                )
                return False

        except Exception as e:
            logger.error(f"Error validating Git integration: {e}")
            return False

    def read_file(self, repo: str, path: str, branch: str = "main") -> Optional[str]:
        """
        Read a file from a Git repository.

        Args:
            repo: Repository name (e.g., 'owner/repo')
            path: File path within the repository
            branch: Branch name (default: 'main')

        Returns:
            File content as string, or None if file not found
        """
        try:
            logger.info(f"Reading file {path} from {repo} (branch: {branch})")

            # Use Snowflake API integration to read file
            query = f"""
            SELECT content
            FROM TABLE(FLATTEN(input => PARSE_JSON(
                EXTERNAL_FUNCTION_CALL(
                    '{self.api_integration}',
                    'GET',
                    'https://api.github.com/repos/{repo}/contents/{path}?ref={branch}'
                )
            )))
            WHERE key = 'content'
            """

            df = self.session.sql(query)
            result = df.collect()

            if result and len(result) > 0:
                content = result[0][0]
                logger.info(f"Successfully read file {path} from {repo}")
                return content
            else:
                logger.warning(f"File {path} not found in {repo}")
                return None

        except Exception as e:
            logger.error(f"Error reading file {path} from {repo}: {e}")
            return None

    def write_file(
        self,
        repo: str,
        path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
    ) -> bool:
        """
        Write a file to a Git repository.

        Args:
            repo: Repository name (e.g., 'owner/repo')
            path: File path within the repository
            content: File content to write
            commit_message: Commit message
            branch: Branch name (default: 'main')

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Writing file {path} to {repo} (branch: {branch})")

            # Use Snowflake API integration to write file
            query = f"""
            SELECT EXTERNAL_FUNCTION_CALL(
                '{self.api_integration}',
                'PUT',
                'https://api.github.com/repos/{repo}/contents/{path}',
                PARSE_JSON('{{
                    "message": "{commit_message}",
                    "content": "{content}",
                    "branch": "{branch}"
                }}')
            ) as result
            """

            df = self.session.sql(query)
            result = df.collect()

            if result and len(result) > 0:
                logger.info(f"Successfully wrote file {path} to {repo}")
                return True
            else:
                logger.warning(f"Failed to write file {path} to {repo}")
                return False

        except Exception as e:
            logger.error(f"Error writing file {path} to {repo}: {e}")
            return False

    def create_branch(self, repo: str, base_branch: str, new_branch: str) -> bool:
        """
        Create a new branch in a Git repository.

        Args:
            repo: Repository name (e.g., 'owner/repo')
            base_branch: Base branch to create from
            new_branch: Name of the new branch

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Creating branch {new_branch} from {base_branch} in {repo}")

            # First get the SHA of the base branch
            sha_query = f"""
            SELECT content:sha as sha
            FROM TABLE(FLATTEN(input => PARSE_JSON(
                EXTERNAL_FUNCTION_CALL(
                    '{self.api_integration}',
                    'GET',
                    'https://api.github.com/repos/{repo}/git/refs/heads/{base_branch}'
                )
            )))
            WHERE key = 'object'
            """

            df = self.session.sql(sha_query)
            result = df.collect()

            if not result or len(result) == 0:
                logger.error(f"Could not get SHA for base branch {base_branch}")
                return False

            sha = result[0][0]

            # Create the new branch
            create_query = f"""
            SELECT EXTERNAL_FUNCTION_CALL(
                '{self.api_integration}',
                'POST',
                'https://api.github.com/repos/{repo}/git/refs',
                PARSE_JSON('{{
                    "ref": "refs/heads/{new_branch}",
                    "sha": "{sha}"
                }}')
            ) as result
            """

            df = self.session.sql(create_query)
            result = df.collect()

            if result and len(result) > 0:
                logger.info(f"Successfully created branch {new_branch} in {repo}")
                return True
            else:
                logger.warning(f"Failed to create branch {new_branch} in {repo}")
                return False

        except Exception as e:
            logger.error(f"Error creating branch {new_branch} in {repo}: {e}")
            return False

    def list_repositories(self) -> List[str]:
        """
        List accessible repositories.

        Returns:
            List of repository names
        """
        try:
            logger.info("Listing accessible repositories")

            # Use Snowflake API integration to list repositories
            query = f"""
            SELECT content:full_name as repo_name
            FROM TABLE(FLATTEN(input => PARSE_JSON(
                EXTERNAL_FUNCTION_CALL(
                    '{self.api_integration}',
                    'GET',
                    'https://api.github.com/user/repos'
                )
            )))
            """

            df = self.session.sql(query)
            result = df.collect()

            repositories = [row[0] for row in result if row[0]]
            logger.info(f"Found {len(repositories)} accessible repositories")
            return repositories

        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return []

    def get_file_info(
        self, repo: str, path: str, branch: str = "main"
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a file in a Git repository.

        Args:
            repo: Repository name (e.g., 'owner/repo')
            path: File path within the repository
            branch: Branch name (default: 'main')

        Returns:
            Dictionary with file information, or None if file not found
        """
        try:
            logger.info(f"Getting file info for {path} in {repo} (branch: {branch})")

            query = f"""
            SELECT PARSE_JSON(
                EXTERNAL_FUNCTION_CALL(
                    '{self.api_integration}',
                    'GET',
                    'https://api.github.com/repos/{repo}/contents/{path}?ref={branch}'
                )
            ) as file_info
            """

            df = self.session.sql(query)
            result = df.collect()

            if result and len(result) > 0:
                file_info = result[0][0]
                logger.info(f"Successfully retrieved file info for {path}")
                return file_info
            else:
                logger.warning(f"File {path} not found in {repo}")
                return None

        except Exception as e:
            logger.error(f"Error getting file info for {path} in {repo}: {e}")
            return None


def validate_git_integration(session: Optional[Session] = None) -> bool:
    """
    Validate Git integration using existing authentication.

    This function uses the existing session manager instead of hardcoded credentials
    to validate that the Git API integration is properly configured and accessible.

    Args:
        session: Optional Snowflake session. If None, will use get_session().

    Returns:
        True if integration is valid and accessible, False otherwise.
    """
    try:
        logger.info("=== GIT INTEGRATION VALIDATION START ===")

        # Use the existing session manager or provided session
        git_integration = GitIntegration(session=session)

        # Validate the integration
        is_valid = git_integration.validate_integration()

        if is_valid:
            logger.info("✅ Git integration validation successful")
            return True
        else:
            logger.error("❌ Git integration validation failed")
            return False

    except Exception as e:
        logger.error(f"❌ Git integration validation error: {e}")
        return False


def commit_svg_file(
    repo: str,
    file_path: str,
    svg_content: str,
    commit_message: str,
    branch: str = "main",
) -> bool:
    """
    Commit an SVG file to a Git repository.

    This is a convenience function that combines file writing with proper
    commit message formatting for SVG files.

    Args:
        repo: Repository name (e.g., 'owner/repo')
        file_path: Path where the SVG file should be stored
        svg_content: SVG content to commit
        commit_message: Commit message
        branch: Branch name (default: 'main')

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Committing SVG file to {repo}: {file_path}")

        git_integration = GitIntegration()

        # Ensure the file path ends with .svg
        if not file_path.endswith(".svg"):
            file_path += ".svg"

        # Write the file
        success = git_integration.write_file(
            repo=repo,
            path=file_path,
            content=svg_content,
            commit_message=commit_message,
            branch=branch,
        )

        if success:
            logger.info(f"✅ Successfully committed SVG file to {repo}: {file_path}")
        else:
            logger.error(f"❌ Failed to commit SVG file to {repo}: {file_path}")

        return success

    except Exception as e:
        logger.error(f"❌ Error committing SVG file to {repo}: {e}")
        return False


def list_accessible_repositories(session: Optional[Session] = None) -> List[str]:
    """
    List all accessible GitHub repositories via the Snowflake API integration.
    Args:
        session: Optional Snowflake session. If None, will use get_session().
    Returns:
        List of repository names as strings.
    """
    logger.info("=== LIST ACCESSIBLE REPOSITORIES START ===")
    session = session or get_session()
    query = "SELECT repo_name FROM TABLE(FLATTEN(input => PARSE_JSON(EXTERNAL_FUNCTION_CALL('git_api_integration', 'GET', 'https://api.github.com/user/repos'))))"
    logger.info(f"Running query: {query}")
    try:
        df = session.sql(query)
        result = df.collect()
        repo_names = [row[0] for row in result if row[0]]
        logger.info(f"Accessible repositories: {repo_names}")
        return repo_names
    except Exception as e:
        logger.error(f"Error listing accessible repositories: {e}")
        return []


def read_repository_file(
    repo: str, path: str, branch: str = "main", session: Optional[Session] = None
) -> Optional[str]:
    """
    Read file content from a GitHub repository via the Snowflake API integration.
    Args:
        repo: Repository name (e.g., 'owner/repo')
        path: File path within the repository
        branch: Branch name (default: 'main')
        session: Optional Snowflake session. If None, will use get_session().
    Returns:
        File content as string, or None if file not found.
    """
    logger.info(f"=== READ REPOSITORY FILE START: {repo}/{path} (branch: {branch}) ===")
    session = session or get_session()
    query = f"""
    SELECT content
    FROM TABLE(FLATTEN(input => PARSE_JSON(
        EXTERNAL_FUNCTION_CALL(
            'git_api_integration',
            'GET',
            'https://api.github.com/repos/{repo}/contents/{path}?ref={branch}'
        )
    )))
    WHERE key = 'content'
    """
    logger.info(f"Running query: {query}")
    try:
        df = session.sql(query)
        result = df.collect()
        if result and len(result) > 0:
            content = result[0][0]
            logger.info(f"Successfully read file {path} from {repo}")
            return content
        else:
            logger.warning(f"File {path} not found in {repo}")
            return None
    except Exception as e:
        logger.error(f"Error reading file {path} from {repo}: {e}")
        return None


def write_repository_file(
    repo: str,
    path: str,
    content: str,
    commit_message: str,
    branch: str = "main",
    session: Optional[Session] = None,
) -> bool:
    """
    Write/commit file content to a GitHub repository via the Snowflake API integration.
    Args:
        repo: Repository name (e.g., 'owner/repo')
        path: File path within the repository
        content: File content to write
        commit_message: Commit message
        branch: Branch name (default: 'main')
        session: Optional Snowflake session. If None, will use get_session().
    Returns:
        True if successful, False otherwise.
    """
    logger.info(
        f"=== WRITE REPOSITORY FILE START: {repo}/{path} (branch: {branch}) ==="
    )
    session = session or get_session()
    query = f"""
    SELECT EXTERNAL_FUNCTION_CALL(
        'git_api_integration',
        'PUT',
        'https://api.github.com/repos/{repo}/contents/{path}',
        PARSE_JSON('{{
            "message": "{commit_message}",
            "content": "{content}",
            "branch": "{branch}"
        }}')
    ) as result
    """
    logger.info(f"Running query: {query}")
    try:
        df = session.sql(query)
        result = df.collect()
        if result and len(result) > 0:
            logger.info(f"Successfully wrote file {path} to {repo}")
            return True
        else:
            logger.warning(f"Failed to write file {path} to {repo}")
            return False
    except Exception as e:
        logger.error(f"Error writing file {path} to {repo}: {e}")
        return False


def create_repository_branch(
    repo: str, base_branch: str, new_branch: str, session: Optional[Session] = None
) -> bool:
    """
    Create a new branch in a GitHub repository via the Snowflake API integration.
    Args:
        repo: Repository name (e.g., 'owner/repo')
        base_branch: Base branch to create from
        new_branch: Name of the new branch
        session: Optional Snowflake session. If None, will use get_session().
    Returns:
        True if successful, False otherwise.
    """
    logger.info(
        f"=== CREATE REPOSITORY BRANCH START: {repo} {base_branch} -> {new_branch} ==="
    )
    session = session or get_session()

    # First get the SHA of the base branch
    sha_query = f"""
    SELECT content:sha as sha
    FROM TABLE(FLATTEN(input => PARSE_JSON(
        EXTERNAL_FUNCTION_CALL(
            'git_api_integration',
            'GET',
            'https://api.github.com/repos/{repo}/git/refs/heads/{base_branch}'
        )
    )))
    WHERE key = 'object'
    """
    logger.info(f"Getting SHA for base branch: {sha_query}")
    try:
        df = session.sql(sha_query)
        result = df.collect()
        if not result or len(result) == 0:
            logger.error(f"Could not get SHA for base branch {base_branch}")
            return False
        sha = result[0][0]
        logger.info(f"Got SHA for base branch {base_branch}: {sha}")

        # Create the new branch
        create_query = f"""
        SELECT EXTERNAL_FUNCTION_CALL(
            'git_api_integration',
            'POST',
            'https://api.github.com/repos/{repo}/git/refs',
            PARSE_JSON('{{
                "ref": "refs/heads/{new_branch}",
                "sha": "{sha}"
            }}')
        ) as result
        """
        logger.info(f"Creating new branch: {create_query}")
        df = session.sql(create_query)
        result = df.collect()
        if result and len(result) > 0:
            logger.info(f"Successfully created branch {new_branch} in {repo}")
            return True
        else:
            logger.warning(f"Failed to create branch {new_branch} in {repo}")
            return False
    except Exception as e:
        logger.error(f"Error creating branch {new_branch} in {repo}: {e}")
        return False
