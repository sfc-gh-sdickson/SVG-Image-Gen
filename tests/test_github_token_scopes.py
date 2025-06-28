"""
Tests for GitHub token scopes configuration.

This module tests the Python-based configuration for GitHub token scopes
to ensure business authority and auditability.
"""

import os
import sys

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from github_token_scopes import (
    GITHUB_TOKEN_CONFIG,
    get_all_scopes,
    get_required_scopes,
    get_scope_details,
    validate_scopes,
)


class TestGitHubTokenScopes:
    """Test cases for GitHub token scopes configuration."""

    def test_config_structure(self):
        """Test that the config has the expected structure."""
        assert hasattr(GITHUB_TOKEN_CONFIG, "description")
        assert hasattr(GITHUB_TOKEN_CONFIG, "rationale")
        assert hasattr(GITHUB_TOKEN_CONFIG, "last_reviewed")
        assert hasattr(GITHUB_TOKEN_CONFIG, "reviewed_by")
        assert hasattr(GITHUB_TOKEN_CONFIG, "scopes")

        assert isinstance(GITHUB_TOKEN_CONFIG.description, str)
        assert isinstance(GITHUB_TOKEN_CONFIG.rationale, str)
        assert isinstance(GITHUB_TOKEN_CONFIG.last_reviewed, str)
        assert isinstance(GITHUB_TOKEN_CONFIG.reviewed_by, str)
        assert isinstance(GITHUB_TOKEN_CONFIG.scopes, list)

    def test_required_scopes(self):
        """Test that required scopes are correctly identified."""
        required_scopes = get_required_scopes()

        assert isinstance(required_scopes, list)
        assert len(required_scopes) > 0

        # Check that all required scopes are valid GitHub scopes
        valid_scopes = ["repo", "read:org", "user", "admin:org", "workflow"]
        for scope in required_scopes:
            assert (
                scope in valid_scopes
                or scope.startswith("read:")
                or scope.startswith("write:")
            )

    def test_all_scopes(self):
        """Test that all scopes are returned correctly."""
        all_scopes = get_all_scopes()
        required_scopes = get_required_scopes()

        assert isinstance(all_scopes, list)
        assert len(all_scopes) >= len(required_scopes)

        # All required scopes should be in all scopes
        for scope in required_scopes:
            assert scope in all_scopes

    def test_scope_details(self):
        """Test that scope details are returned correctly."""
        # Test with a valid scope
        scope_details = get_scope_details("repo")
        assert scope_details is not None
        assert "name" in scope_details
        assert "description" in scope_details
        assert "rationale" in scope_details
        assert "required" in scope_details

        # Test with an invalid scope
        scope_details = get_scope_details("invalid_scope")
        assert scope_details is None

    def test_validate_scopes_valid(self):
        """Test scope validation with valid scopes."""
        required_scopes = get_required_scopes()
        validation = validate_scopes(required_scopes)

        assert validation["valid"] is True
        assert len(validation["missing_scopes"]) == 0
        assert validation["required_scopes"] == required_scopes
        assert validation["user_scopes"] == required_scopes

    def test_validate_scopes_missing(self):
        """Test scope validation with missing scopes."""
        required_scopes = get_required_scopes()
        user_scopes = required_scopes[:-1] if len(required_scopes) > 1 else []

        validation = validate_scopes(user_scopes)

        assert validation["valid"] is False
        assert len(validation["missing_scopes"]) > 0
        assert validation["required_scopes"] == required_scopes
        assert validation["user_scopes"] == user_scopes

    def test_validate_scopes_extra(self):
        """Test scope validation with extra scopes."""
        required_scopes = get_required_scopes()
        user_scopes = required_scopes + ["user", "admin:org"]

        validation = validate_scopes(user_scopes)

        assert validation["valid"] is True  # Extra scopes don't make it invalid
        assert len(validation["missing_scopes"]) == 0
        assert len(validation["extra_scopes"]) > 0
        assert (
            "user" in validation["extra_scopes"]
            or "admin:org" in validation["extra_scopes"]
        )

    def test_validate_scopes_empty(self):
        """Test scope validation with empty scopes."""
        validation = validate_scopes([])

        assert validation["valid"] is False
        assert len(validation["missing_scopes"]) > 0
        assert len(validation["user_scopes"]) == 0

    def test_business_auditability(self):
        """Test that the config provides business auditability."""
        # Check that each scope has business rationale
        for scope in GITHUB_TOKEN_CONFIG.scopes:
            assert scope.rationale, f"Scope {scope.name} must have business rationale"
            assert scope.description, f"Scope {scope.name} must have description"

            # Check that rationale is meaningful (not just placeholder text)
            assert len(scope.rationale) > 10, f"Scope {scope.name} rationale too short"
            assert not scope.rationale.lower().startswith(
                "todo"
            ), f"Scope {scope.name} has TODO rationale"

    def test_config_review_tracking(self):
        """Test that config review tracking is in place."""
        assert GITHUB_TOKEN_CONFIG.last_reviewed, "Config must have last review date"
        assert GITHUB_TOKEN_CONFIG.reviewed_by, "Config must have reviewer name"

        # Check that review date is in reasonable format
        import re

        date_pattern = r"\d{4}-\d{2}-\d{2}"
        assert re.match(
            date_pattern, GITHUB_TOKEN_CONFIG.last_reviewed
        ), "Review date should be YYYY-MM-DD format"


class TestGitHubTokenScopesIntegration:
    """Integration tests for GitHub token scopes configuration."""

    def test_config_imports_correctly(self):
        """Test that the config can be imported and used correctly."""
        from github_token_scopes import GITHUB_TOKEN_CONFIG, get_required_scopes

        # This should not raise any exceptions
        scopes = get_required_scopes()
        assert isinstance(scopes, list)
        assert len(scopes) > 0

    def test_config_consistency(self):
        """Test that the config is internally consistent."""
        required_scopes = get_required_scopes()
        all_scopes = get_all_scopes()

        # All required scopes should have details
        for scope_name in required_scopes:
            details = get_scope_details(scope_name)
            assert details is not None, f"Required scope {scope_name} missing details"
            assert (
                details["required"] is True
            ), f"Required scope {scope_name} marked as not required"
