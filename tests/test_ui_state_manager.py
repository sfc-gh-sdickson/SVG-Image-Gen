import logging
from unittest.mock import Mock, patch

import pytest
import streamlit as st

from src.svg_image_generator.ui_state_manager import UIStateManager


@pytest.fixture(autouse=True)
def clear_session_state():
    # Clear Streamlit session_state before each test
    st.session_state.clear()
    yield
    st.session_state.clear()


@pytest.fixture
def mock_llm_logger():
    """Mock LLM logger to avoid actual logging during tests."""
    with patch(
        "src.svg_image_generator.ui_state_manager.get_llm_logger"
    ) as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


def test_initialization_sets_defaults(mock_llm_logger):
    manager = UIStateManager()
    for key, value in manager.DEFAULTS.items():
        assert st.session_state[key] == value

    # Verify LLM logger was called for initialization
    mock_llm_logger.info.assert_called_once()
    call_args = mock_llm_logger.info.call_args
    assert "UI state initialized with defaults" in call_args[0][0]


def test_get_returns_value_or_default(mock_llm_logger):
    manager = UIStateManager()
    st.session_state["current_step"] = "test_step"
    assert manager.get("current_step") == "test_step"
    assert manager.get("nonexistent_key") is None  # default fallback

    # Verify debug logging for state access
    assert mock_llm_logger.debug.call_count >= 2


def test_set_updates_state_and_logs(mock_llm_logger):
    manager = UIStateManager()
    manager.set("current_step", "new_step")
    assert st.session_state["current_step"] == "new_step"

    # Verify info logging for state update
    mock_llm_logger.info.assert_called()
    call_args = mock_llm_logger.info.call_args
    assert "State update: current_step" in call_args[0][0]


def test_reset_restores_defaults_and_logs(mock_llm_logger):
    manager = UIStateManager()
    # Change some values
    manager.set("current_step", "custom_step")
    manager.set("form_data", {"test": "data"})

    # Reset
    manager.reset()

    # Verify defaults restored
    assert st.session_state["current_step"] == "setup"
    assert st.session_state["form_data"] == {}

    # Verify logging
    mock_llm_logger.info.assert_called()


def test_has_key_checks_managed_keys(mock_llm_logger):
    manager = UIStateManager()
    assert manager.has_key("current_step") == True
    assert manager.has_key("nonexistent_key") == False

    # Verify debug logging
    assert mock_llm_logger.debug.call_count >= 2


def test_get_all_state_returns_managed_state(mock_llm_logger):
    manager = UIStateManager()
    state = manager.get_all_state()

    # Verify all managed keys are present
    for key in manager.DEFAULTS:
        assert key in state

    # Verify debug logging
    mock_llm_logger.debug.assert_called()


def test_set_loading_state(mock_llm_logger):
    manager = UIStateManager()
    manager.set_loading_state("form_submit", True)

    assert manager.get_loading_state("form_submit") == True
    assert manager.get_loading_state("other_component") == False

    # Verify logging
    mock_llm_logger.info.assert_called()


def test_set_validation_error(mock_llm_logger):
    manager = UIStateManager()
    manager.set_validation_error("email", "Invalid email format")

    errors = manager.get_validation_errors()
    assert errors["email"] == "Invalid email format"

    # Verify warning logging
    mock_llm_logger.warning.assert_called()


def test_clear_validation_errors(mock_llm_logger):
    manager = UIStateManager()
    manager.set_validation_error("email", "Invalid email")
    manager.set_validation_error("name", "Name required")

    # Clear errors
    manager.clear_validation_errors()

    errors = manager.get_validation_errors()
    assert len(errors) == 0

    # Verify logging
    mock_llm_logger.info.assert_called()


def test_set_form_data(mock_llm_logger):
    manager = UIStateManager()
    form_data = {"name": "John", "email": "john@example.com"}
    manager.set_form_data(form_data)

    retrieved_data = manager.get_form_data()
    assert retrieved_data == form_data

    # Verify logging
    mock_llm_logger.info.assert_called()


def test_set_current_step(mock_llm_logger):
    manager = UIStateManager()
    manager.set_current_step("generation")

    assert manager.get_current_step() == "generation"

    # Verify logging
    mock_llm_logger.info.assert_called()


def test_log_state_summary(mock_llm_logger):
    manager = UIStateManager()
    manager.set_form_data({"test": "data"})
    manager.set_validation_error("field", "error")
    manager.set_loading_state("component", True)

    manager.log_state_summary()

    # Verify info logging for summary
    mock_llm_logger.info.assert_called()
    call_args = mock_llm_logger.info.call_args
    assert "UI State Summary" in call_args[0][0]


def test_edge_cases(mock_llm_logger):
    manager = UIStateManager()

    # Test with None values
    manager.set("user_context", None)
    assert manager.get("user_context") is None

    # Test with empty data
    manager.set_form_data({})
    assert manager.get_form_data() == {}

    # Test loading state edge cases
    assert manager.get_loading_state("nonexistent") == False
