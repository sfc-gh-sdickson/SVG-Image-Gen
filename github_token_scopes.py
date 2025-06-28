"""
GitHub Token Scopes Configuration

Business-auditable config for GitHub Personal Access Token scopes/permissions
used for Snowflake SVG-Image-Gen Git integration.

This is the single source of truth for token permissions. All changes must be reviewed.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Scope:
    """A GitHub token scope with business rationale."""

    name: str
    description: str
    rationale: str
    required: bool = True


@dataclass
class TokenConfig:
    """Configuration for GitHub Personal Access Token."""

    description: str
    rationale: str
    last_reviewed: str
    reviewed_by: str
    scopes: List[Scope]


# Business configuration for GitHub token scopes
GITHUB_TOKEN_CONFIG = TokenConfig(
    description="Scopes required for Snowflake SVG-Image-Gen Git integration",
    rationale="Only the minimum required scopes are granted. This prevents privilege creep and ensures business authority over integration security.",
    last_reviewed="2024-06-27",
    reviewed_by="lou",
    scopes=[
        Scope(
            name="repo",
            description="Full control of private repositories (required for clone/pull)",
            rationale="Needed for Snowflake to clone and sync the repo.",
            required=True,
        ),
        Scope(
            name="read:org",
            description="Read-only access to organization membership",
            rationale="Required for some GitHub orgs to validate repo access.",
            required=True,
        ),
    ],
)


def get_required_scopes() -> List[str]:
    """Get list of required scope names."""
    return [scope.name for scope in GITHUB_TOKEN_CONFIG.scopes if scope.required]


def get_all_scopes() -> List[str]:
    """Get list of all scope names."""
    return [scope.name for scope in GITHUB_TOKEN_CONFIG.scopes]


def get_scope_details(scope_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific scope."""
    for scope in GITHUB_TOKEN_CONFIG.scopes:
        if scope.name == scope_name:
            return {
                "name": scope.name,
                "description": scope.description,
                "rationale": scope.rationale,
                "required": scope.required,
            }
    return None


def validate_scopes(user_scopes: List[str]) -> Dict[str, Any]:
    """
    Validate user's token scopes against required configuration.

    Returns:
        Dict with validation results including missing and extra scopes.
    """
    required_scopes = set(get_required_scopes())
    user_scope_set = set(user_scopes)

    missing_scopes = required_scopes - user_scope_set
    extra_scopes = user_scope_set - required_scopes

    return {
        "valid": len(missing_scopes) == 0,
        "missing_scopes": list(missing_scopes),
        "extra_scopes": list(extra_scopes),
        "required_scopes": list(required_scopes),
        "user_scopes": user_scopes,
    }
