"""
Cortex AI operations for SVG Image Generator.

This module handles all interactions with Snowflake Cortex AI including
model discovery, validation, and safe calling with comprehensive error handling.
"""

import logging
from typing import List, Optional

from snowflake.snowpark import Session

# Set up logging
logger = logging.getLogger(__name__)


def get_available_cortex_models(session: Session) -> List[str]:
    """Get list of available Cortex models for the current user using Snowpark operations"""
    try:
        logger.info("Discovering available Cortex models...")

        # Common Cortex models - we'll validate these exist
        potential_models = [
            "claude-3-5-sonnet",
            "claude-3-7-sonnet",
            "claude-4-sonnet",
            "openai-gpt-4o",
            "openai-gpt-4o-mini",
            "llama-3-8b-instruct",
            "llama-3-70b-instruct",
            "mistral-7b-instruct",
            "mixtral-8x7b-instruct",
        ]

        available_models = []

        # Test each model with a simple query using Snowpark operations
        for model in potential_models:
            try:
                test_query = (
                    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', 'Hello') as test"
                )
                result = session.sql(test_query).collect()
                if result and result[0][0]:
                    available_models.append(model)
                    logger.info(f"Model {model} is available")
                else:
                    logger.warning(f"Model {model} returned no result")
            except Exception as e:
                error_msg = str(e).lower()
                if "unknown model" in error_msg or "model not found" in error_msg:
                    logger.info(f"Model {model} is not available: {e}")
                else:
                    # Other errors might be temporary, so we'll include the model
                    available_models.append(model)
                    logger.warning(f"Model {model} had error but including it: {e}")

        if not available_models:
            # Fallback to basic models that should be available
            logger.warning("No models discovered, using fallback models")
            available_models = ["claude-3-5-sonnet"]

        logger.info(
            f"Found {len(available_models)} available models: {available_models}"
        )
        return available_models

    except Exception as e:
        logger.error(f"Error discovering Cortex models: {e}")
        # Return a safe fallback
        return ["claude-3-5-sonnet"]


def validate_cortex_model(session: Session, model: str) -> bool:
    """Validate that a specific Cortex model is available using Snowpark operations"""
    try:
        # Input validation
        if not model or not model.strip():
            logger.warning("Empty or None model name provided")
            return False

        logger.info(f"Validating Cortex model: {model}")

        # Simple test query using Snowpark operations
        test_query = (
            f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', 'Test') as validation"
        )
        result = session.sql(test_query).collect()

        if result and result[0][0]:
            logger.info(f"Model {model} is valid")
            return True
        else:
            logger.warning(f"Model {model} returned no result")
            return False

    except Exception as e:
        error_msg = str(e).lower()
        if "unknown model" in error_msg or "model not found" in error_msg:
            logger.error(f"Model {model} is not available: {e}")
            return False
        else:
            # For any other error (including SQL errors), return False
            logger.error(f"Model {model} validation failed: {e}")
            return False


def safe_cortex_call(
    session: Session, model: str, prompt: str, operation_name: str = "Cortex operation"
) -> Optional[str]:
    """Safely make a Cortex call with comprehensive error handling using Snowpark operations"""
    try:
        logger.info(f"Making safe Cortex call for {operation_name} with model {model}")

        # Validate model first
        if not validate_cortex_model(session, model):
            raise ValueError(f"Model '{model}' is not available")

        # Make the Cortex call using Snowpark operations
        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', $${prompt}$$) as result"
        result = session.sql(query).collect()

        if result and result[0][0]:
            logger.info(f"{operation_name} completed successfully")
            return result[0][0]
        else:
            logger.warning(f"{operation_name} returned no result")
            return None

    except Exception as e:
        error_msg = str(e).lower()

        if "unknown model" in error_msg:
            logger.error(f"Model validation failed for {operation_name}: {e}")
            raise ValueError(
                f"Model '{model}' is not available in this Snowflake environment"
            )
        elif "external function" in error_msg:
            logger.error(f"External function error for {operation_name}: {e}")
            raise ValueError(f"Cortex service error: {e}")
        elif "timeout" in error_msg:
            logger.error(f"Timeout for {operation_name}: {e}")
            raise ValueError(f"Request timed out: {e}")
        elif "insufficient privileges" in error_msg:
            logger.error(f"Permission error for {operation_name}: {e}")
            raise ValueError(f"Insufficient privileges for Cortex operations: {e}")
        else:
            logger.error(f"Unexpected error for {operation_name}: {e}")
            raise ValueError(f"Cortex operation failed: {e}")
