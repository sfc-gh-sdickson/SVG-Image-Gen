"""
Feature flags for safe feature rollout and graceful degradation.
Provides centralized control over experimental and development features.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class FeatureFlags:
    """Centralized feature flag configuration."""

    # UI State Management Features
    ui_state_tracking: bool = False
    live_dashboard: bool = False
    structured_logging: bool = True  # Safe to enable by default

    # Development Features
    debug_mode: bool = False
    verbose_logging: bool = False

    # Integration Features
    fastapi_server: bool = False
    real_time_updates: bool = False

    # Override from environment variables
    def __post_init__(self):
        self.ui_state_tracking = self._get_env_bool(
            "ENABLE_UI_STATE_TRACKING", self.ui_state_tracking
        )
        self.live_dashboard = self._get_env_bool(
            "ENABLE_LIVE_DASHBOARD", self.live_dashboard
        )
        self.structured_logging = self._get_env_bool(
            "ENABLE_STRUCTURED_LOGGING", self.structured_logging
        )
        self.debug_mode = self._get_env_bool("DEBUG_MODE", self.debug_mode)
        self.verbose_logging = self._get_env_bool(
            "VERBOSE_LOGGING", self.verbose_logging
        )
        self.fastapi_server = self._get_env_bool(
            "ENABLE_FASTAPI_SERVER", self.fastapi_server
        )
        self.real_time_updates = self._get_env_bool(
            "ENABLE_REAL_TIME_UPDATES", self.real_time_updates
        )

    def _get_env_bool(self, env_var: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(env_var, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        return default

    def get_status(self) -> Dict[str, Any]:
        """Get current feature flag status."""
        return {
            "ui_state_tracking": self.ui_state_tracking,
            "live_dashboard": self.live_dashboard,
            "structured_logging": self.structured_logging,
            "debug_mode": self.debug_mode,
            "verbose_logging": self.verbose_logging,
            "fastapi_server": self.fastapi_server,
            "real_time_updates": self.real_time_updates,
        }

    def is_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        return getattr(self, feature, False)


# Global feature flags instance
feature_flags = FeatureFlags()


def safe_feature_call(feature_name: str, func: callable, *args, **kwargs):
    """
    Safely call a feature function with graceful degradation.

    Args:
        feature_name: Name of the feature for logging
        func: Function to call if feature is enabled
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Result of function call, or None if feature is disabled
    """
    if not feature_flags.is_enabled(feature_name):
        return None

    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Log the error but don't break the app
        print(f"⚠️ Feature '{feature_name}' failed: {e}")
        return None


def require_feature(feature_name: str):
    """
    Decorator to require a feature flag for function execution.

    Usage:
        @require_feature("ui_state_tracking")
        def my_function():
            # Only runs if ui_state_tracking is enabled
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not feature_flags.is_enabled(feature_name):
                print(
                    f"⚠️ Feature '{feature_name}' is disabled. Skipping {func.__name__}"
                )
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def feature_guard(feature_name: str, fallback=None):
    """
    Context manager for feature-flagged code blocks.

    Usage:
        with feature_guard("live_dashboard"):
            # Only executes if live_dashboard is enabled
            start_dashboard()
    """

    class FeatureGuard:
        def __init__(self, feature: str, fallback_value=None):
            self.feature = feature
            self.fallback = fallback_value
            self.enabled = feature_flags.is_enabled(feature)

        def __enter__(self):
            if not self.enabled:
                print(f"⚠️ Feature '{self.feature}' is disabled")
            return self.enabled

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type and self.enabled:
                print(f"⚠️ Feature '{self.feature}' encountered an error: {exc_val}")
            return False  # Don't suppress exceptions

    return FeatureGuard(feature_name, fallback)


def get_feature_status() -> Dict[str, Any]:
    """Get current status of all feature flags."""
    return feature_flags.get_status()


def enable_feature(feature_name: str, enabled: bool = True):
    """Dynamically enable/disable a feature flag."""
    if hasattr(feature_flags, feature_name):
        setattr(feature_flags, feature_name, enabled)
        print(f"🔧 Feature '{feature_name}' {'enabled' if enabled else 'disabled'}")
    else:
        print(f"❌ Unknown feature: {feature_name}")


# Convenience functions for common checks
def is_ui_tracking_enabled() -> bool:
    """Check if UI state tracking is enabled."""
    return feature_flags.ui_state_tracking


def is_dashboard_enabled() -> bool:
    """Check if live dashboard is enabled."""
    return feature_flags.live_dashboard


def is_structured_logging_enabled() -> bool:
    """Check if structured logging is enabled."""
    return feature_flags.structured_logging


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return feature_flags.debug_mode


def is_verbose_logging_enabled() -> bool:
    """Check if verbose logging is enabled."""
    return feature_flags.verbose_logging


def is_fastapi_enabled() -> bool:
    """Check if FastAPI server is enabled."""
    return feature_flags.fastapi_server


def is_real_time_enabled() -> bool:
    """Check if real-time updates are enabled."""
    return feature_flags.real_time_updates
