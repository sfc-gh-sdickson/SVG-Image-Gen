"""
UI State Manager for Streamlit UI state management.
Provides control, observability, and a state model for the application.
"""
import logging
from typing import Any, Dict, Optional

import streamlit as st


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

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._initialize_state()

    def _initialize_state(self):
        """Initialize all session state variables with defaults if not present."""
        for key, default_value in self.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
                self._log(f"Initialized state: {key} = {default_value}")

    def get(self, key: str) -> Any:
        """Get a state value, returning the default if not set."""
        return st.session_state.get(key, self.DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        """Set a state value and log the change."""
        old_value = st.session_state.get(key, None)
        st.session_state[key] = value
        self._log(f"State updated: {key} from {old_value} to {value}")

    def has_key(self, key: str) -> bool:
        """Check if a key exists in the managed state."""
        return key in self.DEFAULTS

    def get_all_state(self) -> Dict[str, Any]:
        """Get all managed state as a dictionary."""
        return {
            key: st.session_state.get(key, self.DEFAULTS.get(key))
            for key in self.DEFAULTS
        }

    def reset(self) -> None:
        """Reset all managed state to defaults."""
        for key in self.DEFAULTS:
            st.session_state[key] = self.DEFAULTS[key]
            self._log(f"State reset: {key} = {self.DEFAULTS[key]}")

    def _log(self, message: str) -> None:
        """Log a message with the UIStateManager prefix."""
        if self.logger:
            self.logger.info(f"[UIStateManager] {message}")
