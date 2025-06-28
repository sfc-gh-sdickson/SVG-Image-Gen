#!/usr/bin/env python3
"""
Generate GitHub Personal Access Token for Snowflake Integration

This script uses GitHub CLI to create a Personal Access Token with the correct
scopes for Snowflake Git integration, avoiding the garbage GUI approach.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from github_token_scopes import (
    GITHUB_TOKEN_CONFIG,
    get_required_scopes,
    get_scope_details,
)


def get_github_token() -> Optional[str]:
    """Get the current GitHub token from gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Failed to get GitHub token from gh CLI")
        print("🔧 To fix this:")
        print("   1. Install GitHub CLI: https://cli.github.com/")
        print("   2. Run: gh auth login")
        print("   3. Follow the authentication prompts")
        return None


def create_personal_access_token(
    name: str = "Snowflake SVG-Image-Gen Integration",
    scopes: list = None,
    expires_in_days: int = 90,
) -> Optional[Dict[str, Any]]:
    """
    Create a GitHub Personal Access Token using GitHub CLI.

    Args:
        name: Name for the new token
        scopes: List of scopes to grant
        expires_in_days: Token expiration in days

    Returns:
        Dict containing the new token info, or None if failed
    """
    if scopes is None:
        scopes = get_required_scopes()
        print("\n🔒 Token Scopes/Permissions Config:")
        print(f"   Description: {GITHUB_TOKEN_CONFIG.description}")
        print(f"   Rationale: {GITHUB_TOKEN_CONFIG.rationale}")
        print(
            f"   Last Reviewed: {GITHUB_TOKEN_CONFIG.last_reviewed} by {GITHUB_TOKEN_CONFIG.reviewed_by}"
        )
        print(f"   Required Scopes: {', '.join(scopes)}")

        for scope in GITHUB_TOKEN_CONFIG.scopes:
            print(f"     • {scope.name}: {scope.description}")
            print(f"       Rationale: {scope.rationale}")

    # Calculate expiration date
    expires_at = datetime.now() + timedelta(days=expires_in_days)
    expires_str = expires_at.strftime("%Y-%m-%d")

    try:
        print(f"\n🔑 Creating GitHub Personal Access Token...")
        print(f"   Name: {name}")
        print(f"   Scopes: {', '.join(scopes)}")
        print(f"   Expires: {expires_str}")

        # Use GitHub CLI to create the token
        cmd = [
            "gh",
            "auth",
            "token",
            "create",
            "--scopes",
            ",".join(scopes),
            "--expiry",
            expires_str,
            "--note",
            name,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the output to extract the token
        output = result.stdout.strip()

        # The token should be the last line of output
        token = output.split("\n")[-1].strip()

        if token.startswith("ghp_"):
            print(f"✅ Token created successfully!")
            print(f"   Token: {token}")
            print(f"   Expires: {expires_str}")

            return {
                "token": token,
                "expires_at": expires_at.isoformat(),
                "scopes": scopes,
            }
        else:
            print(f"❌ Unexpected token format: {token}")
            print("🔧 This might be a GitHub CLI version issue.")
            print("   Try updating GitHub CLI: gh upgrade")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create token: {e}")
        print(f"   Error output: {e.stderr}")

        # Provide actionable error message
        print("\n🔧 To create the token manually:")
        print("   1. Go to: https://github.com/settings/tokens")
        print("   2. Click 'Generate new token (classic)'")
        print("   3. Set Note: 'Snowflake SVG-Image-Gen Integration'")
        print("   4. Set Expiration: 90 days")
        print("   5. Select these scopes:")
        for scope in scopes:
            scope_details = get_scope_details(scope)
            if scope_details:
                print(f"      • {scope}: {scope_details['description']}")
        print("   6. Click 'Generate token'")
        print("   7. Copy the token and update svggen_git_integration.sql")

        return None
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        print("🔧 This is an unexpected error. Check your GitHub CLI installation.")
        return None


def update_sql_script(token: str, username: str = "louspringer"):
    """
    Update the SQL integration script with the new token.

    Args:
        token: The GitHub Personal Access Token
        username: GitHub username
    """
    sql_template = f"""-- Snowflake Git Integration Setup
-- Generated automatically for SVG-Image-Gen deployment
-- Token created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Config: {GITHUB_TOKEN_CONFIG.last_reviewed} by {GITHUB_TOKEN_CONFIG.reviewed_by}

-- Step 1: Create database and schema
CREATE DATABASE IF NOT EXISTS svggen_db;
USE DATABASE svggen_db;
CREATE SCHEMA IF NOT EXISTS integrations;

-- Step 2: Create secret for GitHub token
CREATE OR REPLACE SECRET svggen_git_secret
  TYPE = password
  USERNAME = '{username}'
  PASSWORD = '{token}';

-- Step 3: Create API integration for GitHub
USE SCHEMA svggen_db.integrations;

CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/sfc-gh-sdickson/')
  ALLOWED_AUTHENTICATION_SECRETS = (svggen_git_secret)
  ENABLED = TRUE;

-- Step 4: Create Git repository clone
CREATE OR REPLACE GIT REPOSITORY svg_image_gen
  API_INTEGRATION = git_api_integration
  GIT_CREDENTIALS = svggen_git_secret
  ORIGIN = 'https://github.com/sfc-gh-sdickson/SVG-Image-Gen.git';

-- Step 5: Grant necessary privileges
GRANT USAGE ON DATABASE svggen_db TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA svggen_db.integrations TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SECRET svggen_git_secret TO ROLE ACCOUNTADMIN;
GRANT USAGE ON API INTEGRATION git_api_integration TO ROLE ACCOUNTADMIN;
GRANT USAGE ON GIT REPOSITORY svg_image_gen TO ROLE ACCOUNTADMIN;
"""

    # Write the updated SQL script
    with open("svggen_git_integration.sql", "w") as f:
        f.write(sql_template)

    print(f"✅ Updated svggen_git_integration.sql with new token")


def main():
    """Main function to generate token and update SQL script."""
    print("🚀 GitHub Personal Access Token Generator for Snowflake Integration")
    print("=" * 60)

    # Check if GitHub CLI is authenticated
    current_token = get_github_token()
    if not current_token:
        print("❌ No GitHub token available. Please run 'gh auth login' first.")
        return

    print(f"✅ Using GitHub CLI for token creation")

    # Create new Personal Access Token
    token_data = create_personal_access_token()
    if not token_data:
        print("❌ Failed to create Personal Access Token")
        return

    # Extract the new token
    new_token = token_data.get("token")
    if not new_token:
        print("❌ No token returned from GitHub CLI")
        return

    # Update SQL script
    update_sql_script(new_token)

    print("\n🎉 Success! Your Snowflake Git integration is ready.")
    print("📝 Next steps:")
    print("   1. Run the updated svggen_git_integration.sql in Snowflake")
    print("   2. Test the Git integration with admin_diagnostics.py")
    print("   3. Deploy your app to Snowflake workspace")


if __name__ == "__main__":
    main()
