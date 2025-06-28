"""
Tests for GitHub Personal Access Token generation script.

This module tests the token generation functionality with proper mocking
to avoid actual API calls during testing.
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_github_token import (
    create_personal_access_token,
    get_github_token,
    update_sql_script,
)


class TestGitHubTokenGeneration:
    """Test cases for GitHub token generation functionality."""

    @patch("subprocess.run")
    def test_get_github_token_success(self, mock_run):
        """Test successful retrieval of GitHub token from gh CLI."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "ghp_test_token_12345\n"
        mock_run.return_value = mock_result

        token = get_github_token()

        assert token == "ghp_test_token_12345"
        mock_run.assert_called_once_with(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_get_github_token_failure(self, mock_run):
        """Test failure to get GitHub token from gh CLI."""
        # Mock failed subprocess run
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh auth token")

        token = get_github_token()

        assert token is None

    @patch("subprocess.run")
    def test_create_personal_access_token_success(self, mock_run):
        """Test successful creation of Personal Access Token using GitHub CLI."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "ghp_new_token_67890\n"
        mock_run.return_value = mock_result

        result = create_personal_access_token()

        assert result is not None
        assert result["token"] == "ghp_new_token_67890"
        assert result["scopes"] == ["repo", "read:org"]

        # Verify GitHub CLI command was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "auth"
        assert cmd[2] == "token"
        assert cmd[3] == "create"
        assert "--scopes" in cmd
        assert "--expiry" in cmd
        assert "--note" in cmd

    @patch("subprocess.run")
    def test_create_personal_access_token_failure(self, mock_run):
        """Test failure to create Personal Access Token."""
        # Mock failed subprocess run
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh auth token create")

        result = create_personal_access_token()

        assert result is None

    @patch("builtins.open", create=True)
    def test_update_sql_script(self, mock_open):
        """Test updating SQL script with new token."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        token = "ghp_test_token_12345"
        username = "testuser"

        update_sql_script(token, username)

        # Verify file was opened for writing
        mock_open.assert_called_once_with("svggen_git_integration.sql", "w")

        # Verify write was called with SQL content
        mock_file.write.assert_called_once()
        sql_content = mock_file.write.call_args[0][0]

        # Check that token and username are in the SQL
        assert token in sql_content
        assert username in sql_content
        assert "CREATE OR REPLACE SECRET svggen_git_secret" in sql_content
        assert "CREATE OR REPLACE API INTEGRATION git_api_integration" in sql_content

    @patch("subprocess.run")
    def test_create_personal_access_token_default_scopes(self, mock_run):
        """Test that default scopes are applied when none provided."""
        mock_result = MagicMock()
        mock_result.stdout = "ghp_test_token_12345\n"
        mock_run.return_value = mock_result

        create_personal_access_token()

        # Verify default scopes were used
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        scopes_index = cmd.index("--scopes") + 1
        scopes = cmd[scopes_index].split(",")
        assert scopes == ["repo", "read:org"]

    @patch("subprocess.run")
    def test_create_personal_access_token_custom_scopes(self, mock_run):
        """Test that custom scopes are applied when provided."""
        mock_result = MagicMock()
        mock_result.stdout = "ghp_test_token_12345\n"
        mock_run.return_value = mock_result

        custom_scopes = ["repo", "user", "admin:org"]
        create_personal_access_token(scopes=custom_scopes)

        # Verify custom scopes were used
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        scopes_index = cmd.index("--scopes") + 1
        scopes = cmd[scopes_index].split(",")
        assert scopes == custom_scopes

    @patch("subprocess.run")
    def test_create_personal_access_token_expiration(self, mock_run):
        """Test that token expiration is calculated correctly."""
        mock_result = MagicMock()
        mock_result.stdout = "ghp_test_token_12345\n"
        mock_run.return_value = mock_result

        # Test with 30 days expiration
        create_personal_access_token(expires_in_days=30)

        # Verify expiration date was calculated
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        expiry_index = cmd.index("--expiry") + 1
        expiry_date = cmd[expiry_index]

        # Should be approximately 30 days from now
        expected_expires = datetime.now() + timedelta(days=30)
        actual_expires = datetime.strptime(expiry_date, "%Y-%m-%d")
        assert (
            abs((actual_expires - expected_expires).days) <= 1
        )  # Allow 1 day tolerance

    @patch("subprocess.run")
    def test_create_personal_access_token_invalid_output(self, mock_run):
        """Test handling of invalid token output from GitHub CLI."""
        # Mock output that doesn't look like a token
        mock_result = MagicMock()
        mock_result.stdout = "Some error message\n"
        mock_run.return_value = mock_result

        result = create_personal_access_token()

        assert result is None


@pytest.mark.integration
class TestGitHubTokenIntegration:
    """Integration tests for GitHub token generation (require actual GitHub access)."""

    @pytest.mark.skipif(
        not os.getenv("GITHUB_TOKEN"),
        reason="GITHUB_TOKEN environment variable not set",
    )
    def test_real_github_token_creation(self):
        """Test actual GitHub token creation (requires GITHUB_TOKEN env var)."""
        # This test only runs if GITHUB_TOKEN is set
        token = os.getenv("GITHUB_TOKEN")
        result = create_personal_access_token(
            name="Test Token - Delete Me",
            expires_in_days=1,  # Short expiration for test
        )

        assert result is not None
        assert "token" in result
        assert result["token"].startswith("ghp_")  # Should be a valid token format
