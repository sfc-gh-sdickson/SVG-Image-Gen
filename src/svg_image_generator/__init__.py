"""
SVG Image Generator with Snowflake Cortex AI.

A Streamlit-based web application for generating SVG images using Snowflake Cortex AI.
"""

__version__ = "1.0.0"
__author__ = "SVG Image Generator Team"
__email__ = "team@svg-generator.com"

# Import main components when available
try:
    from .app import main  # type: ignore
except ImportError:
    main = None

try:
    from .services.session_service import SessionService  # type: ignore
    from .services.ai_service import AIGenerationService  # type: ignore
    from .services.storage_service import StorageService  # type: ignore
except ImportError:
    SessionService = None
    AIGenerationService = None
    StorageService = None

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "main",
    "SessionService",
    "AIGenerationService",
    "StorageService",
] 