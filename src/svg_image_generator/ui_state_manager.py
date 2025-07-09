"""
UI State Manager for Streamlit UI state management.
Provides control, observability, and a state model for the application.
"""
import logging
from typing import Any, Dict, Optional

import streamlit as st

from .llm_logging import LLMLogger, get_llm_logger


class UIStateManager:
    """
    Manages UI state using Streamlit's session_state, with structured access,
    initialization, mutation, and observability/logging hooks.
    """

    DEFAULTS = {
        "current_step": "setup",
        "form_data": {},
        "validation_errors": {},
        "loading_states": {},
        "user_context": None,
    }

    def __init__(self, logger: Optional[LLMLogger] = None):
        self.llm_logger = logger or get_llm_logger("ui_state_manager")
        self._initialize_state()

    def _initialize_state(self):
        """Initialize all session state variables with defaults if not present."""
        initialized_keys = []
        for key, default_value in self.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
                initialized_keys.append(key)

        if initialized_keys:
            self.llm_logger.info(
                "UI state initialized with defaults",
                context={
                    "initialized_keys": initialized_keys,
                    "default_values": {
                        key: self.DEFAULTS[key] for key in initialized_keys
                    },
                    "total_managed_keys": len(self.DEFAULTS),
                },
            )

    def get(self, key: str) -> Any:
        """Get a state value, returning the default if not set."""
        value = st.session_state.get(key, self.DEFAULTS.get(key))
        self.llm_logger.debug(
            f"State accessed: {key}",
            context={
                "key": key,
                "value": value,
                "is_default": key not in st.session_state,
                "available_keys": list(self.DEFAULTS.keys()),
            },
        )
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a state value and log the change with structured context."""
        old_value = st.session_state.get(key, None)
        st.session_state[key] = value

        # Determine change type for better observability
        change_type = "initialization" if old_value is None else "update"

        self.llm_logger.info(
            f"State {change_type}: {key}",
            context={
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "change_type": change_type,
                "is_managed_key": key in self.DEFAULTS,
                "session_state_keys": list(st.session_state.keys()),
            },
        )

    def has_key(self, key: str) -> bool:
        """Check if a key exists in the managed state."""
        exists = key in self.DEFAULTS
        self.llm_logger.debug(
            f"Key existence check: {key}",
            context={
                "key": key,
                "exists": exists,
                "managed_keys": list(self.DEFAULTS.keys()),
            },
        )
        return exists

    def get_all_state(self) -> Dict[str, Any]:
        """Get all managed state as a dictionary."""
        state = {
            key: st.session_state.get(key, self.DEFAULTS.get(key))
            for key in self.DEFAULTS
        }

        self.llm_logger.debug(
            "Retrieved all managed state",
            context={
                "state_keys": list(state.keys()),
                "state_values": state,
                "session_state_keys": list(st.session_state.keys()),
            },
        )
        return state

    def reset(self) -> None:
        """Reset all managed state to defaults with structured logging."""
        reset_keys = []
        for key in self.DEFAULTS:
            old_value = st.session_state.get(key, None)
            st.session_state[key] = self.DEFAULTS[key]
            reset_keys.append(key)

        self.llm_logger.info(
            "State reset to defaults",
            context={
                "reset_keys": reset_keys,
                "default_values": {key: self.DEFAULTS[key] for key in reset_keys},
                "total_reset_keys": len(reset_keys),
            },
        )

    def set_loading_state(self, component: str, is_loading: bool) -> None:
        """Set loading state for a specific component with structured logging."""
        loading_states = st.session_state.get("loading_states", {})
        old_state = loading_states.get(component, False)
        loading_states[component] = is_loading
        st.session_state["loading_states"] = loading_states

        self.llm_logger.info(
            f"Loading state changed: {component}",
            context={
                "component": component,
                "old_state": old_state,
                "new_state": is_loading,
                "all_loading_states": loading_states,
            },
        )

    def get_loading_state(self, component: str) -> bool:
        """Get loading state for a specific component."""
        loading_states = st.session_state.get("loading_states", {})
        return loading_states.get(component, False)

    def set_validation_error(self, field: str, error_message: str) -> None:
        """Set validation error for a specific field with structured logging."""
        validation_errors = st.session_state.get("validation_errors", {})
        validation_errors[field] = error_message
        st.session_state["validation_errors"] = validation_errors

        self.llm_logger.warning(
            f"Validation error set: {field}",
            context={
                "field": field,
                "error_message": error_message,
                "all_validation_errors": validation_errors,
            },
        )

    def clear_validation_errors(self) -> None:
        """Clear all validation errors with structured logging."""
        old_errors = st.session_state.get("validation_errors", {})
        st.session_state["validation_errors"] = {}

        if old_errors:
            self.llm_logger.info(
                "Validation errors cleared",
                context={
                    "cleared_errors": old_errors,
                    "error_count": len(old_errors),
                },
            )

    def get_validation_errors(self) -> Dict[str, str]:
        """Get all validation errors."""
        return st.session_state.get("validation_errors", {})

    def set_form_data(self, data: Dict[str, Any]) -> None:
        """Set form data with structured logging."""
        old_data = st.session_state.get("form_data", {})
        st.session_state["form_data"] = data

        self.llm_logger.info(
            "Form data updated",
            context={
                "old_data_keys": list(old_data.keys()),
                "new_data_keys": list(data.keys()),
                "data_changes": {
                    key: {"old": old_data.get(key), "new": data.get(key)}
                    for key in set(old_data.keys()) | set(data.keys())
                },
            },
        )

    def get_form_data(self) -> Dict[str, Any]:
        """Get current form data."""
        return st.session_state.get("form_data", {})

    def set_current_step(self, step: str) -> None:
        """Set current step with structured logging."""
        old_step = st.session_state.get("current_step", "setup")
        st.session_state["current_step"] = step

        self.llm_logger.info(
            f"Step transition: {old_step} -> {step}",
            context={
                "old_step": old_step,
                "new_step": step,
                "step_transition": True,
            },
        )

    def get_current_step(self) -> str:
        """Get current step."""
        return st.session_state.get("current_step", "setup")

    def log_state_summary(self) -> None:
        """Log a comprehensive state summary for debugging."""
        current_state = self.get_all_state()

        self.llm_logger.info(
            "UI State Summary",
            context={
                "current_step": current_state.get("current_step"),
                "form_data_keys": list(current_state.get("form_data", {}).keys()),
                "validation_error_count": len(
                    current_state.get("validation_errors", {})
                ),
                "loading_states": current_state.get("loading_states", {}),
                "has_user_context": current_state.get("user_context") is not None,
                "total_session_keys": len(st.session_state),
            },
        )
