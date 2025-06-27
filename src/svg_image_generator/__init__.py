"""
SVG Image Generator Package

A comprehensive Streamlit application for generating SVG files using Snowflake Cortex AI
and storing them in Snowflake stages with dynamic context discovery and prompt sandwich approach.

This package provides:
- Dynamic context discovery for Snowflake resources
- Prompt sandwich implementation for improved SVG generation
- Comprehensive error handling and logging
- Model validation and fallback mechanisms
- Secure authentication with multiple tiers
"""

__version__ = "1.0.0"
__author__ = "SVG Image Generator Team"
__description__ = (
    "SVG generation using Snowflake Cortex AI with dynamic context discovery"
)

# Import main components for easy access
from .core import (
    discover_user_context,
    get_accessible_databases,
    get_accessible_schemas,
    get_accessible_stages,
    handle_context_errors,
    validate_user_permissions,
)
from .cortex import get_available_cortex_models, safe_cortex_call, validate_cortex_model
from .prompt_sandwich import (
    generate_svg_with_refined_prompt,
    implement_prompt_sandwich,
    refine_prompt_with_cortex,
)
from .session_manager import get_session

__all__ = [
    # Core context discovery
    "discover_user_context",
    "get_accessible_databases",
    "get_accessible_schemas",
    "get_accessible_stages",
    "validate_user_permissions",
    "handle_context_errors",
    # Cortex operations
    "get_available_cortex_models",
    "validate_cortex_model",
    "safe_cortex_call",
    # Prompt sandwich
    "refine_prompt_with_cortex",
    "generate_svg_with_refined_prompt",
    "implement_prompt_sandwich",
    # Session management
    "get_session",
]
