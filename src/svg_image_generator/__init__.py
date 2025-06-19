"""
SVG Image Generator with Snowflake Cortex AI.

A Streamlit-based web application for generating SVG images using Snowflake Cortex AI.
"""

__version__ = "1.0.0"
__author__ = "SVG Image Generator Team"
__email__ = "team@svg-generator.com"

# Import main components when available
try:
    from .app import (
        main,  # type: ignore  # TODO[0e1e7b2a]: Remove unused type: ignore (see TODO.md)
    )
except ImportError:
    main = None

try:
    from .services.ai_service import (
        AIGenerationService,  # type: ignore  # TODO[1a2c3d4e]: Remove unused type: ignore (see TODO.md)
    )
    from .services.session_service import (
        SessionService,  # type: ignore  # TODO[2b3c4d5e]: Remove unused type: ignore (see TODO.md)
    )
    from .services.storage_service import (
        StorageService,  # type: ignore  # TODO[3c4d5e6f]: Remove unused type: ignore (see TODO.md)
    )
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
