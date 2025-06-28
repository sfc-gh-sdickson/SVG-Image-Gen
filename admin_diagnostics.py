#!/usr/bin/env python3
"""
Admin Diagnostics Dashboard for SVG-Image-Gen

This is an ADMIN-ONLY tool for inspecting runtime capabilities, environment details,
and system diagnostics. Use with caution and only in authorized environments.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from github_token_scopes import (
    GITHUB_TOKEN_CONFIG,
    get_required_scopes,
    validate_scopes,
)
from src.svg_image_generator.git_integration import GitIntegration
from src.svg_image_generator.runtime_detection import RuntimeDetector
from src.svg_image_generator.session_manager import SessionManager


def check_snowflake_privileges(session) -> Dict[str, Any]:
    """Check actual Snowflake privileges, not just roles."""
    try:
        # Check if user can manage secrets
        can_manage_secrets = session.sql(
            """
            SELECT COUNT(*) > 0
            FROM TABLE(INFORMATION_SCHEMA.PRIVILEGES_GRANTED_TO_CURRENT_USER())
            WHERE PRIVILEGE_TYPE = 'USAGE'
            AND OBJECT_TYPE = 'SECRET'
        """
        ).collect()[0][0]

        # Check if user can manage API integrations
        can_manage_integrations = session.sql(
            """
            SELECT COUNT(*) > 0
            FROM TABLE(INFORMATION_SCHEMA.PRIVILEGES_GRANTED_TO_CURRENT_USER())
            WHERE PRIVILEGE_TYPE = 'USAGE'
            AND OBJECT_TYPE = 'API INTEGRATION'
        """
        ).collect()[0][0]

        # Check if user can manage databases
        can_manage_databases = session.sql(
            """
            SELECT COUNT(*) > 0
            FROM TABLE(INFORMATION_SCHEMA.PRIVILEGES_GRANTED_TO_CURRENT_USER())
            WHERE PRIVILEGE_TYPE IN ('CREATE', 'MODIFY', 'USAGE')
            AND OBJECT_TYPE = 'DATABASE'
        """
        ).collect()[0][0]

        # Check current role
        current_role = session.sql("SELECT CURRENT_ROLE()").collect()[0][0]

        return {
            "can_manage_secrets": can_manage_secrets,
            "can_manage_integrations": can_manage_integrations,
            "can_manage_databases": can_manage_databases,
            "current_role": current_role,
            "has_admin_privileges": can_manage_secrets
            and can_manage_integrations
            and can_manage_databases,
        }
    except Exception as e:
        return {
            "error": str(e),
            "can_manage_secrets": False,
            "can_manage_integrations": False,
            "can_manage_databases": False,
            "current_role": "UNKNOWN",
            "has_admin_privileges": False,
        }


def get_actionable_privilege_message(privileges: Dict[str, Any]) -> str:
    """Generate actionable message for privilege issues."""
    if privileges.get("error"):
        return f"❌ Error checking privileges: {privileges['error']}"

    missing_privileges = []
    if not privileges["can_manage_secrets"]:
        missing_privileges.append("USAGE ON SECRET")
    if not privileges["can_manage_integrations"]:
        missing_privileges.append("USAGE ON API INTEGRATION")
    if not privileges["can_manage_databases"]:
        missing_privileges.append("CREATE/MODIFY ON DATABASE")

    if missing_privileges:
        return f"""
❌ You need these privileges to configure Git integration:
   {', '.join(missing_privileges)}

🔧 To fix this, run these commands (requires ACCOUNTADMIN):
   GRANT USAGE ON SECRET svggen_git_secret TO ROLE {privileges['current_role']};
   GRANT USAGE ON API INTEGRATION git_api_integration TO ROLE {privileges['current_role']};
   GRANT CREATE ON DATABASE svggen_db TO ROLE {privileges['current_role']};

📞 Contact: lou@company.com (Snowflake Admin)
📧 Subject: "Need privileges for SVG-Image-Gen Git integration"
📋 Include: Your role name ({privileges['current_role']}) and the missing privileges above
"""
    else:
        return "✅ You have all required privileges for Git integration configuration."


def validate_github_token_scopes(token_scopes: List[str]) -> Dict[str, Any]:
    """Validate GitHub token scopes against business config."""
    validation = validate_scopes(token_scopes)

    if not validation["valid"]:
        missing_details = []
        for scope in validation["missing_scopes"]:
            scope_info = GITHUB_TOKEN_CONFIG.scopes[0]  # Get scope details
            missing_details.append(f"   • {scope}: {scope_info.description}")

        validation[
            "actionable_message"
        ] = f"""
❌ GitHub token has insufficient scopes
   Required: {', '.join(validation['required_scopes'])}
   Current: {', '.join(validation['user_scopes'])}

🔧 To fix this:
   1. Go to: https://github.com/settings/tokens
   2. Edit your "Snowflake Integration" token
   3. Add these missing scopes:
{chr(10).join(missing_details)}
   4. Click "Update token"
   5. Update your Snowflake secret with the new token

📞 Need help? Contact: lou@company.com (include this error message)
"""
    else:
        validation["actionable_message"] = "✅ GitHub token has all required scopes."

    return validation


def main():
    st.set_page_config(
        page_title="SVG-Image-Gen Admin Diagnostics", page_icon="🔧", layout="wide"
    )

    st.title("🔧 SVG-Image-Gen Admin Diagnostics")
    st.warning(
        "⚠️ **ADMIN-ONLY TOOL** - Use with caution and only in authorized environments."
    )

    # Initialize runtime detector
    runtime_detector = RuntimeDetector()

    # Create tabs for different diagnostic areas
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🏃 Runtime Detection",
            "🔐 Privileges & Security",
            "🔗 Git Integration",
            "📊 System Info",
        ]
    )

    with tab1:
        st.header("Runtime Detection")

        runtime_info = runtime_detector.get_runtime_info()
        st.json(runtime_info)

        if runtime_info.get("runtime_type") == "snowflake":
            st.success("✅ Running in Snowflake environment")
        else:
            st.info("ℹ️ Running in local development environment")

    with tab2:
        st.header("Privileges & Security")

        # Try to get Snowflake session
        try:
            session_manager = SessionManager()
            session = session_manager.get_session()

            if session:
                privileges = check_snowflake_privileges(session)

                st.subheader("Current Privileges")
                st.json(privileges)

                st.subheader("Actionable Status")
                st.markdown(get_actionable_privilege_message(privileges))

                # Show/hide admin features based on privileges
                if privileges.get("has_admin_privileges"):
                    st.success("🔓 Full admin access - all features available")

                    with st.expander("🔧 Admin Configuration"):
                        st.subheader("GitHub Token Configuration")
                        st.json(
                            {
                                "description": GITHUB_TOKEN_CONFIG.description,
                                "rationale": GITHUB_TOKEN_CONFIG.rationale,
                                "last_reviewed": GITHUB_TOKEN_CONFIG.last_reviewed,
                                "reviewed_by": GITHUB_TOKEN_CONFIG.reviewed_by,
                                "required_scopes": get_required_scopes(),
                            }
                        )

                        st.subheader("Required Scopes Details")
                        for scope in GITHUB_TOKEN_CONFIG.scopes:
                            st.markdown(
                                f"""
**{scope.name}**
- Description: {scope.description}
- Rationale: {scope.rationale}
- Required: {scope.required}
"""
                            )
                else:
                    st.warning("🔒 Limited access - admin features disabled")
                    st.info("Contact your Snowflake administrator for full access.")
            else:
                st.error("❌ Could not establish Snowflake session")
                st.markdown(
                    """
🔧 To fix this:
   1. Check your Snowflake connection parameters
   2. Verify your credentials are valid
   3. Ensure you have access to the Snowflake account
"""
                )

        except Exception as e:
            st.error(f"❌ Error checking privileges: {e}")
            st.markdown(
                """
🔧 This might be a connection or configuration issue.
   Check your Snowflake setup and try again.
"""
            )

    with tab3:
        st.header("Git Integration")

        try:
            git_integration = GitIntegration()

            # Check if Git integration is configured
            if git_integration.is_configured():
                st.success("✅ Git integration is configured")

                # Validate token scopes if we can get them
                try:
                    token_info = git_integration.get_token_info()
                    if token_info and "scopes" in token_info:
                        validation = validate_github_token_scopes(token_info["scopes"])

                        st.subheader("GitHub Token Validation")
                        st.json(validation)

                        st.subheader("Actionable Status")
                        st.markdown(validation["actionable_message"])
                    else:
                        st.info("ℹ️ Token scopes not available for validation")

                except Exception as e:
                    st.warning(f"⚠️ Could not validate token scopes: {e}")

                # Show Git repository status
                try:
                    repo_status = git_integration.get_repository_status()
                    st.subheader("Repository Status")
                    st.json(repo_status)
                except Exception as e:
                    st.warning(f"⚠️ Could not get repository status: {e}")

            else:
                st.warning("⚠️ Git integration is not configured")
                st.markdown(
                    """
🔧 To configure Git integration:
   1. Run: `uv run python scripts/generate_github_token.py`
   2. Follow the instructions to create a GitHub token
   3. Run the generated SQL script in Snowflake
   4. Test the integration with this dashboard
"""
                )

        except Exception as e:
            st.error(f"❌ Error checking Git integration: {e}")
            st.markdown(
                """
🔧 This might be a configuration or connection issue.
   Check your Git integration setup and try again.
"""
            )

    with tab4:
        st.header("System Information")

        # Environment info
        st.subheader("Environment")
        env_info = {
            "Python Version": sys.version,
            "Platform": sys.platform,
            "Working Directory": os.getcwd(),
            "Timestamp": datetime.now().isoformat(),
        }
        st.json(env_info)

        # Package versions
        st.subheader("Package Versions")
        try:
            import snowflake.snowpark
            import streamlit

            st.json(
                {
                    "snowflake-snowpark": snowflake.snowpark.__version__,
                    "streamlit": streamlit.__version__,
                }
            )
        except Exception as e:
            st.warning(f"⚠️ Could not get package versions: {e}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
    **Admin Diagnostics Dashboard** - For authorized personnel only.

    This tool provides diagnostic information and configuration capabilities for the SVG-Image-Gen system.
    All actions are logged and audited. Use responsibly.
    """
    )


if __name__ == "__main__":
    main()
