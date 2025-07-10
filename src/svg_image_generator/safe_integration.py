"""
Safe integration module for UI state management with graceful degradation.
Provides fail-safe integration of experimental features into the main Streamlit app.
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional

import streamlit as st

from .feature_flags import (
    feature_flags,
    feature_guard,
    is_dashboard_enabled,
    is_structured_logging_enabled,
    is_ui_tracking_enabled,
    require_feature,
    safe_feature_call,
)


class SafeUIStateManager:
    """
    Safe wrapper for UIStateManager with graceful degradation.
    Provides the same interface but fails safely when features are disabled.
    """

    def __init__(self):
        self._state_manager = None
        self._initialized = False
        self._init_error = None

        # Try to initialize the real state manager
        if is_ui_tracking_enabled():
            try:
                from .streamlit_integration import get_state_manager

                self._state_manager = get_state_manager()
                self._initialized = True
            except Exception as e:
                self._init_error = str(e)
                st.warning(f"⚠️ UI state tracking disabled: {e}")

    def is_available(self) -> bool:
        """Check if UI state management is available."""
        return self._initialized and self._state_manager is not None

    def get_status(self) -> Dict[str, Any]:
        """Get status of UI state management."""
        return {
            "available": self.is_available(),
            "feature_enabled": is_ui_tracking_enabled(),
            "initialized": self._initialized,
            "error": self._init_error,
        }

    def safe_call(self, method_name: str, *args, **kwargs):
        """Safely call a method on the state manager."""
        if not self.is_available():
            return None

        try:
            method = getattr(self._state_manager, method_name, None)
            if method and callable(method):
                return method(*args, **kwargs)
        except Exception as e:
            st.warning(f"⚠️ UI state method '{method_name}' failed: {e}")

        return None

    # Proxy methods for common operations
    def set_current_step(self, step: str):
        """Safely set current step."""
        return self.safe_call("set_current_step", step)

    def get_current_step(self) -> str:
        """Safely get current step."""
        result = self.safe_call("get_current_step")
        return result if result is not None else "setup"

    def set_loading_state(self, component: str, loading: bool):
        """Safely set loading state."""
        return self.safe_call("set_loading_state", component, loading)

    def get_loading_state(self, component: str) -> bool:
        """Safely get loading state."""
        result = self.safe_call("get_loading_state", component)
        return result if result is not None else False

    def set_form_data(self, data: Dict[str, Any]):
        """Safely set form data."""
        return self.safe_call("set_form_data", data)

    def get_form_data(self) -> Dict[str, Any]:
        """Safely get form data."""
        result = self.safe_call("get_form_data")
        return result if result is not None else {}

    def set_validation_error(self, field: str, message: str):
        """Safely set validation error."""
        return self.safe_call("set_validation_error", field, message)

    def get_validation_errors(self) -> Dict[str, str]:
        """Safely get validation errors."""
        result = self.safe_call("get_validation_errors")
        return result if result is not None else {}

    def clear_validation_errors(self):
        """Safely clear validation errors."""
        return self.safe_call("clear_validation_errors")

    def reset_state(self):
        """Safely reset state."""
        return self.safe_call("reset_state")

    def get_all_state(self) -> Dict[str, Any]:
        """Safely get all state."""
        result = self.safe_call("get_all_state")
        return result if result is not None else {}


# Global safe state manager instance
safe_ui_state = SafeUIStateManager()


def safe_track_step(step_name: str):
    """
    Safe decorator for tracking steps with graceful degradation.

    Usage:
        @safe_track_step("svg_generation")
        def generate_svg():
            # Your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set step if UI tracking is available
            if safe_ui_state.is_available():
                safe_ui_state.set_current_step(step_name)

            # Execute the function
            result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator


def safe_track_loading(component: str):
    """
    Safe decorator for tracking loading states with graceful degradation.

    Usage:
        @safe_track_loading("cortex_call")
        def call_cortex():
            # Your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set loading state if UI tracking is available
            if safe_ui_state.is_available():
                safe_ui_state.set_loading_state(component, True)

            try:
                # Execute the function
                result = func(*args, **kwargs)
                return result
            finally:
                # Clear loading state if UI tracking is available
                if safe_ui_state.is_available():
                    safe_ui_state.set_loading_state(component, False)

        return wrapper

    return decorator


def safe_track_form_data():
    """
    Safe decorator for tracking form data with graceful degradation.

    Usage:
        @safe_track_form_data()
        def process_form():
            # Your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Track form data if UI tracking is available
            if safe_ui_state.is_available():
                form_data = st.session_state.get("form_data", {})
                safe_ui_state.set_form_data(form_data)

            # Execute the function
            result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator


def safe_track_validation_errors():
    """
    Safe decorator for tracking validation errors with graceful degradation.

    Usage:
        @safe_track_validation_errors()
        def validate_form():
            # Your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Clear previous errors if UI tracking is available
            if safe_ui_state.is_available():
                safe_ui_state.clear_validation_errors()

            # Execute the function
            result = func(*args, **kwargs)

            # Track validation errors if UI tracking is available
            if safe_ui_state.is_available():
                errors = st.session_state.get("validation_errors", {})
                for field, message in errors.items():
                    safe_ui_state.set_validation_error(field, message)

            return result

        return wrapper

    return decorator


class SafeLoadingContext:
    """
    Safe context manager for loading states with graceful degradation.

    Usage:
        with SafeLoadingContext("svg_generation"):
            # Your loading code here
            generate_svg()
    """

    def __init__(self, component: str):
        self.component = component
        self.available = safe_ui_state.is_available()

    def __enter__(self):
        if self.available:
            safe_ui_state.set_loading_state(self.component, True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.available:
            safe_ui_state.set_loading_state(self.component, False)


class SafeStepContext:
    """
    Safe context manager for step tracking with graceful degradation.

    Usage:
        with SafeStepContext("svg_generation"):
            # Your step code here
            generate_svg()
    """

    def __init__(self, step_name: str):
        self.step_name = step_name
        self.available = safe_ui_state.is_available()

    def __enter__(self):
        if self.available:
            safe_ui_state.set_current_step(self.step_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Steps persist after context, so no cleanup needed
        pass


def show_feature_status():
    """Display current feature status in the Streamlit sidebar."""
    if st.sidebar.checkbox("🔧 Show Feature Status", value=False):
        st.sidebar.subheader("Feature Flags")

        status = safe_ui_state.get_status()

        for feature, enabled in feature_flags.get_status().items():
            status_text = "✅ Enabled" if enabled else "❌ Disabled"
            st.sidebar.text(f"{feature}: {status_text}")

        st.sidebar.subheader("UI State Management")
        ui_status = safe_ui_state.get_status()

        for key, value in ui_status.items():
            if key == "error" and value:
                st.sidebar.error(f"Error: {value}")
            else:
                status_text = "✅ Yes" if value else "❌ No"
                st.sidebar.text(f"{key}: {status_text}")


def initialize_safe_features():
    """Initialize safe features and show status."""
    # Show feature status if debug mode is enabled
    if feature_flags.debug_mode:
        show_feature_status()

    # Show warning if UI tracking is disabled but requested
    if not is_ui_tracking_enabled() and feature_flags.debug_mode:
        st.info(
            "ℹ️ UI state tracking is disabled. Enable with ENABLE_UI_STATE_TRACKING=true"
        )

    return safe_ui_state
