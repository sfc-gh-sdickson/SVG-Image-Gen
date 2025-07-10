"""
Streamlit integration for UIStateManager with decorator-based state tracking.
Provides easy-to-use decorators for automatic state management in Streamlit apps.
"""

import functools
import logging
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, Union

import requests
import streamlit as st

from .llm_logging import get_llm_logger
from .ui_state_manager import UIStateManager

logger = logging.getLogger(__name__)
llm_logger = get_llm_logger("streamlit_integration")


class StreamlitStateManager:
    """
    Enhanced UIStateManager with Streamlit integration and decorator support.
    Provides easy-to-use decorators for automatic state tracking.
    """

    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.state_manager = UIStateManager()
        self.api_url = api_url
        self._lock = threading.Lock()
        self._enabled = True

    def _sync_to_api(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Sync state changes to API server."""
        if not self._enabled:
            return True

        try:
            response = requests.post(
                f"{self.api_url}/api/state/{endpoint}", json=data, timeout=1.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to sync to API: {e}")
            return False

    def track_step(self, step_name: str):
        """
        Decorator to track step transitions.

        Usage:
            @state_manager.track_step("form_fill")
            def handle_form_submit():
                # Your Streamlit logic here
                pass
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Set step before function execution
                self.state_manager.set_current_step(step_name)
                self._sync_to_api("step", {"step": step_name})

                # Execute the function
                result = func(*args, **kwargs)

                # Log completion
                llm_logger.info(
                    f"Step completed: {step_name}",
                    context={
                        "step": step_name,
                        "function": func.__name__,
                        "result": "success",
                    },
                )

                return result

            return wrapper

        return decorator

    def track_loading(self, component: str, auto_clear: bool = True):
        """
        Decorator to track loading states.

        Usage:
            @state_manager.track_loading("cortex_call")
            def call_cortex_api():
                # Your API call logic here
                pass
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Set loading state
                self.state_manager.set_loading_state(component, True)
                self._sync_to_api(
                    "loading", {"component": component, "is_loading": True}
                )

                try:
                    # Execute the function
                    result = func(*args, **kwargs)

                    # Clear loading state if auto_clear is True
                    if auto_clear:
                        self.state_manager.set_loading_state(component, False)
                        self._sync_to_api(
                            "loading", {"component": component, "is_loading": False}
                        )

                    return result

                except Exception as e:
                    # Clear loading state on error
                    if auto_clear:
                        self.state_manager.set_loading_state(component, False)
                        self._sync_to_api(
                            "loading", {"component": component, "is_loading": False}
                        )

                    # Re-raise the exception
                    raise

            return wrapper

        return decorator

    def track_form_data(self, form_key: str = "form_data"):
        """
        Decorator to track form data changes.

        Usage:
            @state_manager.track_form_data()
            def handle_form_submit():
                form_data = st.session_state.get("form_data", {})
                # Your form processing logic
                pass
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Get current form data from Streamlit session state
                form_data = st.session_state.get(form_key, {})

                # Update state manager
                self.state_manager.set_form_data(form_data)
                self._sync_to_api("form", form_data)

                # Execute the function
                result = func(*args, **kwargs)

                return result

            return wrapper

        return decorator

    def track_validation_errors(self, error_key: str = "validation_errors"):
        """
        Decorator to track validation errors.

        Usage:
            @state_manager.track_validation_errors()
            def validate_form():
                errors = validate_form_data()
                # Errors will be automatically tracked
                pass
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Clear previous errors
                self.state_manager.clear_validation_errors()
                self._sync_to_api("validation-errors", {})

                # Execute the function
                result = func(*args, **kwargs)

                # Get validation errors from session state
                errors = st.session_state.get(error_key, {})

                # Add errors to state manager
                for field, message in errors.items():
                    self.state_manager.set_validation_error(field, message)
                    self._sync_to_api(
                        "validation-error", {"field": field, "message": message}
                    )

                return result

            return wrapper

        return decorator

    @contextmanager
    def loading_context(self, component: str):
        """
        Context manager for loading states.

        Usage:
            with state_manager.loading_context("svg_generation"):
                # Your loading logic here
                generate_svg()
        """
        try:
            self.state_manager.set_loading_state(component, True)
            self._sync_to_api("loading", {"component": component, "is_loading": True})
            yield
        finally:
            self.state_manager.set_loading_state(component, False)
            self._sync_to_api("loading", {"component": component, "is_loading": False})

    def step_context(self, step_name: str):
        """
        Context manager for step transitions.

        Usage:
            with state_manager.step_context("validation"):
                # Your validation logic here
                validate_form()
        """

        class StepContext:
            def __init__(self, manager, step):
                self.manager = manager
                self.step = step

            def __enter__(self):
                self.manager.state_manager.set_current_step(self.step)
                self.manager._sync_to_api("step", {"step": self.step})
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    # Log error if exception occurred
                    llm_logger.error(
                        f"Step failed: {self.step}",
                        context={"step": self.step, "error": str(exc_val)},
                    )
                else:
                    # Log successful completion
                    llm_logger.info(
                        f"Step completed: {self.step}",
                        context={"step": self.step, "result": "success"},
                    )

        return StepContext(self, step_name)

    def manual_state_update(self, **kwargs):
        """
        Manually update state and sync to API.

        Usage:
            state_manager.manual_state_update(
                step="generation",
                loading_states={"cortex_call": True}
            )
        """
        with self._lock:
            for key, value in kwargs.items():
                if key == "step":
                    self.state_manager.set_current_step(value)
                    self._sync_to_api("step", {"step": value})
                elif key == "form_data":
                    self.state_manager.set_form_data(value)
                    self._sync_to_api("form", value)
                elif key == "loading_states":
                    for component, is_loading in value.items():
                        self.state_manager.set_loading_state(component, is_loading)
                        self._sync_to_api(
                            "loading",
                            {"component": component, "is_loading": is_loading},
                        )
                elif key == "validation_errors":
                    self.state_manager.clear_validation_errors()
                    for field, message in value.items():
                        self.state_manager.set_validation_error(field, message)
                        self._sync_to_api(
                            "validation-error", {"field": field, "message": message}
                        )

    def enable_api_sync(self, enabled: bool = True):
        """Enable or disable API synchronization."""
        self._enabled = enabled

    def get_current_state(self) -> Dict[str, Any]:
        """Get current state for debugging."""
        return {
            "current_step": self.state_manager.get_current_step(),
            "form_data": self.state_manager.get_form_data(),
            "validation_errors": self.state_manager.get_validation_errors(),
            "loading_states": self.state_manager.get_all_state().get(
                "loading_states", {}
            ),
            "user_context": self.state_manager.get("user_context"),
        }

    def reset_state(self):
        """Reset all state to defaults."""
        self.state_manager.reset()
        self._sync_to_api("reset", {})


# Global instance for easy access
_state_manager: Optional[StreamlitStateManager] = None


def get_state_manager(api_url: str = "http://127.0.0.1:8000") -> StreamlitStateManager:
    """Get or create the global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StreamlitStateManager(api_url)
    return _state_manager


# Convenience functions for common operations
def track_step(step_name: str):
    """Convenience decorator for step tracking."""
    return get_state_manager().track_step(step_name)


def track_loading(component: str, auto_clear: bool = True):
    """Convenience decorator for loading tracking."""
    return get_state_manager().track_loading(component, auto_clear)


def track_form_data(form_key: str = "form_data"):
    """Convenience decorator for form data tracking."""
    return get_state_manager().track_form_data(form_key)


def track_validation_errors(error_key: str = "validation_errors"):
    """Convenience decorator for validation error tracking."""
    return get_state_manager().track_validation_errors(error_key)


def loading_context(component: str):
    """Convenience context manager for loading states."""
    return get_state_manager().loading_context(component)


def step_context(step_name: str):
    """Convenience context manager for step transitions."""
    return get_state_manager().step_context(step_name)
