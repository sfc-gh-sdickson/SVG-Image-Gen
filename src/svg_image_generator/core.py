"""
Core functionality for SVG Image Generator.

This module contains context discovery, permission validation, and error handling
functions that are essential for the application's operation.
"""

import logging
from typing import Dict, List

from snowflake.snowpark import Session

# Set up logging
logger = logging.getLogger(__name__)


def discover_user_context(session: Session) -> Dict:
    """Discover user's accessible databases, schemas, and stages"""
    try:
        logger.info("Discovering user context...")

        # Get current user role and permissions - use Snowpark operations
        current_role = session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
        current_warehouse = session.sql("SELECT CURRENT_WAREHOUSE()").collect()[0][0]

        # Get accessible databases
        databases = get_accessible_databases(session)

        # Get current database and schema
        current_database = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
        current_schema = session.sql("SELECT CURRENT_SCHEMA()").collect()[0][0]

        # Get schemas for current database
        schemas = (
            get_accessible_schemas(session, current_database)
            if current_database
            else []
        )

        # Get stages for current database/schema
        stages = (
            get_accessible_stages(session, current_database, current_schema)
            if current_database and current_schema
            else []
        )

        context = {
            "role": current_role,
            "warehouse": current_warehouse,
            "current_database": current_database,
            "current_schema": current_schema,
            "accessible_databases": databases,
            "accessible_schemas": schemas,
            "accessible_stages": stages,
        }

        logger.info(f"User context discovered: {context}")
        return context

    except Exception as e:
        logger.error(f"Error discovering user context: {e}")
        return {}


def get_accessible_databases(session: Session) -> List[str]:
    """Get list of databases accessible to current user using Snowpark operations"""
    try:
        logger.info("Discovering accessible databases...")

        # Use Snowpark DataFrame operations
        result_df = session.sql("SHOW DATABASES")

        # Filter and select only the name column, then collect
        databases = result_df.select('"name"').filter('"name" IS NOT NULL').collect()
        database_names = [row[0] for row in databases if row[0]]

        logger.info(
            f"Found {len(database_names)} accessible databases: {database_names}"
        )
        return database_names
    except Exception as e:
        logger.error(f"Error getting accessible databases: {e}")
        return []


def get_accessible_schemas(session: Session, database: str) -> List[str]:
    """Get list of schemas accessible in given database using Snowpark operations"""
    try:
        # Input validation
        if not database or not database.strip():
            logger.warning("Empty or None database name provided")
            return []

        logger.info(f"Discovering accessible schemas in database: {database}")

        # Use Snowpark DataFrame operations
        result_df = session.sql(f"SHOW SCHEMAS IN DATABASE {database}")

        # Filter and select only the name column, then collect
        schemas = result_df.select('"name"').filter('"name" IS NOT NULL').collect()
        schema_names = [row[0] for row in schemas if row[0]]

        logger.info(
            f"Found {len(schema_names)} accessible schemas in {database}: {schema_names}"
        )
        return schema_names
    except Exception as e:
        logger.error(f"Error getting accessible schemas for {database}: {e}")
        return []


def get_accessible_stages(session: Session, database: str, schema: str) -> List[str]:
    """Get list of stages accessible in given database/schema using Snowpark operations"""
    try:
        # Input validation
        if not database or not database.strip() or not schema or not schema.strip():
            logger.warning("Empty or None database/schema name provided")
            return []

        logger.info(f"Discovering accessible stages in {database}.{schema}")

        # Use Snowpark DataFrame operations
        result_df = session.sql(f"SHOW STAGES IN SCHEMA {database}.{schema}")

        # Filter and select only the name column, then collect
        stages = result_df.select('"name"').filter('"name" IS NOT NULL').collect()
        stage_names = [row[0] for row in stages if row[0]]

        logger.info(
            f"Found {len(stage_names)} accessible stages in {database}.{schema}: {stage_names}"
        )
        return stage_names
    except Exception as e:
        logger.error(f"Error getting accessible stages for {database}.{schema}: {e}")
        return []


def validate_user_permissions(
    session: Session, database: str, schema: str, stage: str
) -> bool:
    """Validate user has required permissions using Snowpark operations"""
    try:
        # Input validation
        if (
            not database
            or not database.strip()
            or not schema
            or not schema.strip()
            or not stage
            or not stage.strip()
        ):
            logger.warning(
                "Empty or None parameters provided for permission validation"
            )
            return False

        logger.info(f"Validating permissions for {database}.{schema}.{stage}")

        # Test database access - use Snowpark operations
        session.sql(f"USE DATABASE {database}").collect()

        # Test schema access
        session.sql(f"USE SCHEMA {schema}").collect()

        # Test stage access (try to list contents)
        session.sql(f"LIST @{stage}").collect()

        logger.info("Permission validation successful")
        return True

    except Exception as e:
        logger.error(f"Permission validation failed: {e}")
        return False


def handle_context_errors(error: Exception) -> str:
    """Handle context-related errors gracefully"""
    error_msg = str(error).lower()

    if "insufficient privileges" in error_msg or "access denied" in error_msg:
        return "❌ Insufficient permissions for the selected context. Please contact your administrator."
    elif "does not exist" in error_msg:
        return "❌ The selected resource does not exist or is not accessible."
    elif "not found" in error_msg:
        return "❌ Resource not found. Please check your selection."
    else:
        return f"❌ Context error: {str(error)}"
