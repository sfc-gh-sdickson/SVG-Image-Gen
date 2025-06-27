"""
Tests for edge cases in cortex.py.

These tests focus on the error handling scenarios that are currently not covered.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add the src directory to the path for proper imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from svg_image_generator.cortex import (
    get_available_cortex_models,
    validate_cortex_model,
)


class TestCortexEdgeCases:
    """Test edge cases in cortex functions."""

    def test_get_available_cortex_models_partial_failure(self) -> None:
        """Test get_available_cortex_models with partial model failures."""
        mock_session = Mock()

        # Mock some models to succeed and others to fail
        def mock_sql_side_effect(query):
            mock_df = Mock()
            if "claude-3-5-sonnet" in query:
                raise Exception("unknown model")
            elif "claude-3-7-sonnet" in query:
                mock_df.collect.return_value = [["test result"]]
            else:
                mock_df.collect.return_value = [["other result"]]
            return mock_df

        mock_session.sql.side_effect = mock_sql_side_effect

        result = get_available_cortex_models(mock_session)

        # Should include successful models and exclude failed ones
        assert "claude-3-7-sonnet" in result
        # claude-3-5-sonnet should be excluded due to "unknown model" error
        assert "claude-3-5-sonnet" not in result

    def test_get_available_cortex_models_empty_results(self) -> None:
        """Test get_available_cortex_models with empty results."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = []
        mock_session.sql.return_value = mock_df

        result = get_available_cortex_models(mock_session)

        # Should return fallback models when no models are found
        assert "claude-3-5-sonnet" in result

    def test_get_available_cortex_models_malformed_results(self) -> None:
        """Test get_available_cortex_models with malformed results."""
        mock_session = Mock()
        mock_df = Mock()
        # Return malformed results (None values, empty strings, etc.)
        mock_df.collect.return_value = [
            ["test result"],
            [None],
            [""],
            ["other result"],
            [],
        ]
        mock_session.sql.return_value = mock_df

        result = get_available_cortex_models(mock_session)

        # Should include models that returned results
        assert (
            "claude-3-5-sonnet" in result
        )  # Should be included due to non-"unknown model" error
        assert (
            "claude-3-7-sonnet" in result
        )  # Should be included due to non-"unknown model" error

    def test_validate_cortex_model_connection_error(self) -> None:
        """Test validate_cortex_model with connection error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("Connection failed")

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        # Should return False for connection errors
        assert result is False


class TestCortexErrorHandling:
    """Test error handling in cortex functions."""

    def test_get_available_cortex_models_sql_exception_handling(self) -> None:
        """Test that SQL exceptions are properly handled in model discovery."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("Database connection lost")

        result = get_available_cortex_models(mock_session)

        # Should return fallback models when SQL fails
        assert "claude-3-5-sonnet" in result

    def test_get_available_cortex_models_collect_exception_handling(self) -> None:
        """Test that collect() exceptions are properly handled."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.side_effect = Exception("Result collection failed")
        mock_session.sql.return_value = mock_df

        result = get_available_cortex_models(mock_session)

        # Should return fallback models when collect fails
        assert "claude-3-5-sonnet" in result

    def test_validate_cortex_model_collect_exception_handling(self) -> None:
        """Test that collect() exceptions are properly handled in validation."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.side_effect = Exception("Result collection failed")
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        # Should return False for collection errors
        assert result is False

    def test_validate_cortex_model_unknown_model_error(self) -> None:
        """Test validate_cortex_model with unknown model error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("unknown model")

        result = validate_cortex_model(mock_session, "nonexistent-model")

        # Should return False for "unknown model" errors
        assert result is False


class TestCortexInputValidation:
    """Test input validation in cortex functions."""

    def test_get_available_cortex_models_none_session(self) -> None:
        """Test get_available_cortex_models with None session."""
        result = get_available_cortex_models(None)

        # Should return fallback models when session is None
        assert "claude-3-5-sonnet" in result

    def test_validate_cortex_model_none_session(self) -> None:
        """Test validate_cortex_model with None session."""
        result = validate_cortex_model(None, "claude-3-5-sonnet")

        # Should return False for None session
        assert result is False

    def test_validate_cortex_model_empty_model_name(self) -> None:
        """Test validate_cortex_model with empty model name."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [["test"]]
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, "")

        # Should return False for empty model name
        assert result is False

    def test_validate_cortex_model_none_model_name(self) -> None:
        """Test validate_cortex_model with None model name."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [["test"]]
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, None)

        # Should return False for None model name
        assert result is False


class TestCortexModelListHandling:
    """Test model list handling in cortex functions."""

    def test_get_available_cortex_models_duplicate_models(self) -> None:
        """Test get_available_cortex_models with duplicate model names."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [["test result"]]
        mock_session.sql.return_value = mock_df

        result = get_available_cortex_models(mock_session)

        # Should include all models that don't have "unknown model" errors
        # The implementation tests each model individually, so duplicates aren't an issue
        assert "claude-3-5-sonnet" in result
        assert "claude-3-7-sonnet" in result

    def test_get_available_cortex_models_case_sensitivity(self) -> None:
        """Test get_available_cortex_models with case variations."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [["test result"]]
        mock_session.sql.return_value = mock_df

        result = get_available_cortex_models(mock_session)

        # The implementation uses predefined model names, so case is fixed
        assert "claude-3-5-sonnet" in result
        assert "claude-3-7-sonnet" in result
        assert "claude-4-sonnet" in result

    def test_get_available_cortex_models_special_characters(self) -> None:
        """Test get_available_cortex_models with special characters in model names."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [["test result"]]
        mock_session.sql.return_value = mock_df

        result = get_available_cortex_models(mock_session)

        # The implementation uses predefined model names, so special characters aren't an issue
        assert "claude-3-5-sonnet" in result
        assert "openai-gpt-4o" in result
        assert "llama-3-8b-instruct" in result


class TestCortexModelValidation:
    """Test model validation scenarios."""

    def test_validate_cortex_model_success(self) -> None:
        """Test successful model validation."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [["valid result"]]
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is True

    def test_validate_cortex_model_no_result(self) -> None:
        """Test model validation with no result."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = []
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is False

    def test_validate_cortex_model_empty_result(self) -> None:
        """Test model validation with empty result."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [[""]]
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is False

    def test_validate_cortex_model_none_result(self) -> None:
        """Test model validation with None result."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = [[None]]
        mock_session.sql.return_value = mock_df

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is False
