import os
from pathlib import Path

import streamlit as st

# ⚠️ ADMIN TOOL WARNING ⚠️
st.error(
    """
⚠️ **ADMIN DIAGNOSTICS DASHBOARD** ⚠️

This is an administrative tool for system diagnostics and environment inspection.
- **NOT for end-user access**
- **Requires admin/ops permissions**
- **Will fail if you don't have the right role**
- **You better know what you're doing if you're here!**

If you don't have admin rights, this will fail quickly. If you DO have rights,
understand that you're running diagnostic code that inspects the runtime environment.
"""
)

st.title("Snowflake Runtime Capability Test")

st.write(
    "This app detects and displays the current runtime environment and available capabilities."
)

# Runtime detection
try:
    from src.svg_image_generator.runtime_detection import (
        detect_runtime_environment,
        get_environment_capabilities,
        is_snowflake_runtime,
    )

    runtime_env = detect_runtime_environment()
    capabilities = get_environment_capabilities()
    is_snowflake = is_snowflake_runtime()
    st.subheader("Runtime Environment")
    st.write(f"**Environment:** {runtime_env}")
    st.write(f"**Is Snowflake Runtime:** {is_snowflake}")
    st.json(capabilities)
except Exception as e:
    st.error(f"Runtime detection failed: {e}")

# Session management
try:
    from src.svg_image_generator.session_manager import get_session

    session = get_session()
    st.subheader("Session Management")
    st.write(f"Session Type: {type(session).__name__}")
    try:
        result = session.sql(
            "SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()"
        ).collect()
        st.write(f"Current Role: {result[0][0]}")
        st.write(f"Current Database: {result[0][1]}")
        st.write(f"Current Schema: {result[0][2]}")
    except Exception as e:
        st.warning(f"SQL Error: {e}")
except Exception as e:
    st.error(f"Session management failed: {e}")

# Git integration
try:
    from src.svg_image_generator.git_integration import validate_git_integration

    git_available = validate_git_integration()
    st.subheader("Git Integration")
    st.write(f"Git Integration Available: {git_available}")
except Exception as e:
    st.error(f"Git integration check failed: {e}")

# LLM logging
try:
    from src.svg_image_generator.llm_logging import get_llm_logger

    llm_logger = get_llm_logger("streamlit_capability_test")
    llm_logger.info(
        "Testing LLM logging from Streamlit",
        context={
            "runtime_environment": str(runtime_env)
            if "runtime_env" in locals()
            else None,
            "capabilities": capabilities if "capabilities" in locals() else None,
            "git_available": git_available if "git_available" in locals() else None,
        },
    )
    st.success("LLM Logging: ✅ Working")
except Exception as e:
    st.warning(f"LLM logging failed: {e}")

# File system access
try:
    st.subheader("File System Access")
    current_dir = Path.cwd()
    st.write(f"Current Directory: {current_dir}")
    st.write(f"Directory Exists: {current_dir.exists()}")
    st.write(
        f"Directory Contents: {[str(p) for p in list(current_dir.iterdir())[:5]]} ..."
    )
except Exception as e:
    st.warning(f"File system access failed: {e}")

# Environment variables
try:
    st.subheader("Environment Variables")
    env_vars = {
        "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT"),
        "SNOWFLAKE_USER": os.getenv("SNOWFLAKE_USER"),
        "SNOWFLAKE_ROLE": os.getenv("SNOWFLAKE_ROLE"),
        "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE"),
        "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA"),
    }
    st.json(env_vars)
except Exception as e:
    st.warning(f"Environment variable check failed: {e}")
