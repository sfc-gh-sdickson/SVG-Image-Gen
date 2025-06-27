"""
Session management for SVG Image Generator.

This module handles multi-tier authentication for Snowflake connections,
supporting Streamlit in Snowflake (SiS), connections.toml, and environment variables.
"""

import logging
import os
from pathlib import Path

import streamlit as st
import toml
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session

# Set up logging
logger = logging.getLogger(__name__)


@st.cache_resource
def get_session() -> Session:
    """Get Snowflake session - supports both SiS environment and local development"""
    logger.info("=== SESSION MANAGER START ===")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info("Environment variables check:")
    snowflake_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_ROLE",
    ]
    for var in snowflake_vars:
        value = os.environ.get(var)
        logger.info(f"  {var}: {'SET' if value else 'NOT SET'}")

    # Tier 1: Active Session (Streamlit in Snowflake)
    try:
        logger.info("Auth Tier 1: Attempting to get active session (for SiS)...")
        session = get_active_session()
        logger.info(f"Auth Tier 1 Succeeded: Session type: {type(session)}")
        st.info("🔗 Using active Snowflake session (Streamlit in Snowflake environment)")
        logger.info("Auth Tier 1 Succeeded: Using active Snowflake session.")
        return session
    except Exception as e1:
        logger.info(
            f"Auth Tier 1 Failed: get_active_session() not available. Error: {e1}"
        )

        # Tier 2: Connection Parameters (connections.toml)
        st.warning(
            "⚠️ Active session not available. Trying connection from `connections.toml`..."
        )
        try:
            logger.info("Auth Tier 2: Attempting to use `connections.toml`...")

            snowflake_conn_path = Path.home() / ".snowflake" / "connections.toml"
            logger.info(f"Connections.toml path: {snowflake_conn_path}")
            logger.info(f"Connections.toml exists: {snowflake_conn_path.exists()}")

            if not snowflake_conn_path.exists():
                raise FileNotFoundError("connections.toml not found")

            config = toml.load(snowflake_conn_path)
            logger.info(f"Connections.toml config keys: {list(config.keys())}")

            # Be robust: check for 'default' or 'connections.default'
            conn_params = {}
            if "default" in config:
                conn_params = config["default"]
                logger.info("Found 'default' profile in connections.toml")
            elif "connections" in config and "default" in config["connections"]:
                conn_params = config["connections"]["default"]
                logger.info("Found 'connections.default' profile in connections.toml")

            if not conn_params:
                raise ValueError("No [default] profile found in connections.toml")

            logger.info(f"Connections.toml params: {list(conn_params.keys())}")
            logger.info(
                "Found [default] profile in `connections.toml`. Creating session."
            )
            session = Session.builder.configs(conn_params).create()
            st.success("✅ Connected to Snowflake using `connections.toml`.")
            logger.info("Auth Tier 2 Succeeded: Connected using `connections.toml`.")
            return session

        except Exception as conn_param_error:
            logger.warning(
                f"Auth Tier 2 Failed: Could not connect using `connections.toml`. Error: {conn_param_error}"
            )

            st.warning(
                """
            ⚠️ `connections.toml` authentication failed. Attempting local connection via environment variables...

            > **Hint:** Could not connect using `~/.snowflake/connections.toml`. Please ensure a `[default]` profile is correctly configured.
            > See browser console for detailed logs.
            """
            )

            # Tier 3: Environment Variables
            logger.info(
                "Auth Tier 3: Attempting to connect using environment variables..."
            )
            account = os.environ.get("SNOWFLAKE_ACCOUNT")
            user = os.environ.get("SNOWFLAKE_USER")
            password = os.environ.get("SNOWFLAKE_PASSWORD")
            warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE")
            database = os.environ.get("SNOWFLAKE_DATABASE")
            schema = os.environ.get("SNOWFLAKE_SCHEMA")
            role = os.environ.get("SNOWFLAKE_ROLE")

            logger.info("Tier 3 env vars check:")
            logger.info(f"  account: {'SET' if account else 'NOT SET'}")
            logger.info(f"  user: {'SET' if user else 'NOT SET'}")
            logger.info(f"  password: {'SET' if password else 'NOT SET'}")
            logger.info(f"  warehouse: {'SET' if warehouse else 'NOT SET'}")
            logger.info(f"  database: {'SET' if database else 'NOT SET'}")
            logger.info(f"  schema: {'SET' if schema else 'NOT SET'}")
            logger.info(f"  role: {'SET' if role else 'NOT SET'}")

            required_vars = [account, user, password, warehouse]
            missing_vars = [
                var
                for var, val in zip(
                    ["account", "user", "password", "warehouse"], required_vars
                )
                if not val
            ]
            logger.info(f"Missing required vars: {missing_vars}")

            if not all([account, user, password, warehouse]):
                logger.critical(
                    "Auth Tier 3 Failed: Missing required environment variables."
                )
                logger.critical(f"Missing variables: {missing_vars}")
                st.error(
                    """
                ❌ Cannot connect to Snowflake. Missing required environment variables:

                **Required:**
                - SNOWFLAKE_ACCOUNT
                - SNOWFLAKE_USER
                - SNOWFLAKE_PASSWORD
                - SNOWFLAKE_WAREHOUSE

                **Optional:**
                - SNOWFLAKE_DATABASE
                - SNOWFLAKE_SCHEMA
                - SNOWFLAKE_ROLE

                **For local development, set these in your environment or create a .env file.**
                """
                )
                logger.critical(
                    "Calling st.stop() due to missing environment variables"
                )
                st.stop()

            try:
                logger.info(
                    "Auth Tier 3: Creating session with environment variables..."
                )
                session_config = {
                    "account": account,
                    "user": user,
                    "password": password,
                    "warehouse": warehouse,
                    "database": database,
                    "schema": schema,
                    "role": role,
                }
                logger.info(f"Session config keys: {list(session_config.keys())}")
                session = Session.builder.configs(session_config).create()
                st.success("✅ Connected to Snowflake using environment credentials.")
                logger.info(
                    "Auth Tier 3 Succeeded: Connected using environment credentials."
                )
                return session
            except Exception as conn_error:
                logger.critical(
                    f"Auth Tier 3 Failed: Could not connect using environment variables. Error: {conn_error}"
                )
                st.error(
                    f"❌ All connection methods failed. Please check your configuration. Final error: {conn_error}"
                )
                logger.critical("Calling st.stop() due to connection failure")
                st.stop()
