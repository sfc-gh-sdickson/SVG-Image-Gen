import logging
from contextlib import contextmanager
from unittest.mock import MagicMock, Mock, patch

import pytest
import streamlit as st

from src.svg_image_generator.streamlit_integration import (
    get_state_manager,
    loading_context,
    step_context,
    track_form_data,
    track_loading,
    track_step,
    track_validation_errors,
)
from src.svg_image_generator.ui_state_manager import UIStateManager


@pytest.fixture(autouse=True)
def clear_session_state():
    """Clear Streamlit session_state before each test."""
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


@pytest.fixture
def state_manager():
    """Create a state manager instance for testing."""
    return get_state_manager()


class TestStreamlitStateManager:
    """Test the StreamlitStateManager class functionality."""

    def test_initialization(self, state_manager):
        """Test that StreamlitStateManager initializes correctly."""
        assert state_manager.state_manager is not None
        assert isinstance(state_manager.state_manager, UIStateManager)
        assert state_manager.api_url == "http://127.0.0.1:8000"

    def test_track_step_decorator(self, state_manager, mock_llm_logger):
        """Test that track_step decorator works correctly."""

        @state_manager.track_step("test_step")
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"
        assert state_manager.state_manager.get_current_step() == "test_step"
        mock_llm_logger.info.assert_called()

    def test_track_loading_decorator(self, state_manager, mock_llm_logger):
        """Test that track_loading decorator works correctly."""

        @state_manager.track_loading("test_component")
        def loading_function():
            return "loaded"

        result = loading_function()

        assert result == "loaded"
        # Loading should be False after completion
        assert state_manager.state_manager.get_loading_state("test_component") == False
        mock_llm_logger.info.assert_called()

    def test_track_form_data_decorator(self, state_manager, mock_llm_logger):
        """Test that track_form_data decorator works correctly."""

        # Set up form data in session state
        st.session_state["form_data"] = {"name": "John", "email": "john@example.com"}

        @state_manager.track_form_data()
        def form_function():
            return "processed"

        result = form_function()

        assert result == "processed"
        form_data = state_manager.state_manager.get_form_data()
        assert form_data == {"name": "John", "email": "john@example.com"}
        mock_llm_logger.info.assert_called()

    def test_track_validation_errors_decorator(self, state_manager, mock_llm_logger):
        """Test that track_validation_errors decorator works correctly."""

        # Set up validation errors in session state
        st.session_state["validation_errors"] = {"email": "Invalid email"}

        @state_manager.track_validation_errors()
        def validation_function():
            return "validated"

        result = validation_function()

        assert result == "validated"
        errors = state_manager.state_manager.get_validation_errors()
        assert errors == {"email": "Invalid email"}
        mock_llm_logger.warning.assert_called()

    def test_loading_context_manager(self, state_manager, mock_llm_logger):
        """Test that loading_context context manager works correctly."""

        with state_manager.loading_context("test_component"):
            # Inside context, loading should be True
            assert (
                state_manager.state_manager.get_loading_state("test_component") == True
            )

        # After context, loading should be False
        assert state_manager.state_manager.get_loading_state("test_component") == False
        mock_llm_logger.info.assert_called()

    def test_step_context_manager(self, state_manager, mock_llm_logger):
        """Test that step_context context manager works correctly."""

        with state_manager.step_context("test_step"):
            # Inside context, step should be set
            assert state_manager.state_manager.get_current_step() == "test_step"

        # After context, step should remain (not auto-clear)
        assert state_manager.state_manager.get_current_step() == "test_step"
        mock_llm_logger.info.assert_called()

    def test_exception_handling_in_decorators(self, state_manager, mock_llm_logger):
        """Test that decorators handle exceptions properly."""

        @state_manager.track_loading("error_component")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Loading state should be reset to False after exception
        assert state_manager.state_manager.get_loading_state("error_component") == False
        mock_llm_logger.error.assert_called()

    def test_manual_state_update(self, state_manager, mock_llm_logger):
        """Test that manual_state_update works correctly."""

        state_manager.manual_state_update(
            current_step="manual_step", form_data={"manual": "data"}
        )

        assert state_manager.state_manager.get_current_step() == "manual_step"
        assert state_manager.state_manager.get_form_data() == {"manual": "data"}
        mock_llm_logger.info.assert_called()

    def test_get_current_state(self, state_manager):
        """Test that get_current_state returns all state."""

        state_manager.state_manager.set_current_step("test_step")
        state_manager.state_manager.set_form_data({"test": "data"})

        current_state = state_manager.get_current_state()

        assert "current_step" in current_state
        assert "form_data" in current_state
        assert current_state["current_step"] == "test_step"
        assert current_state["form_data"] == {"test": "data"}

    def test_reset_state(self, state_manager, mock_llm_logger):
        """Test that reset_state works correctly."""

        # Set some state
        state_manager.state_manager.set_current_step("test_step")
        state_manager.state_manager.set_form_data({"test": "data"})

        # Reset
        state_manager.reset_state()

        # Should be back to defaults
        assert state_manager.state_manager.get_current_step() == "setup"
        assert state_manager.state_manager.get_form_data() == {}
        mock_llm_logger.info.assert_called()


class TestStandaloneDecorators:
    """Test the standalone decorator functions."""

    def test_standalone_track_step(self, mock_llm_logger):
        """Test the standalone track_step decorator."""

        @track_step("standalone_step")
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"
        # Note: standalone decorators don't have access to state manager
        # They just call the function without state tracking

    def test_standalone_track_loading(self, mock_llm_logger):
        """Test the standalone track_loading decorator."""

        @track_loading("standalone_component")
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"
        # Note: standalone decorators don't have access to state manager

    def test_standalone_track_form_data(self, mock_llm_logger):
        """Test the standalone track_form_data decorator."""

        @track_form_data()
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"

    def test_standalone_track_validation_errors(self, mock_llm_logger):
        """Test the standalone track_validation_errors decorator."""

        @track_validation_errors()
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"


class TestErrorHandling:
    """Test error handling in the integration system."""

    def test_api_sync_failure_does_not_break_functionality(
        self, state_manager, mock_llm_logger
    ):
        """Test that API sync failures don't break core functionality."""

        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("Network error")

            @state_manager.track_step("api_failure_test")
            def test_function():
                return "success"

            result = test_function()

            assert result == "success"
            assert state_manager.state_manager.get_current_step() == "api_failure_test"

    def test_invalid_api_url_handling(self):
        """Test that invalid API URLs are handled gracefully."""

        # Should not raise an exception
        state_manager = get_state_manager("http://invalid-url:9999")
        assert state_manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
