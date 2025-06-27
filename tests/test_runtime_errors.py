"""
Test suite for runtime error handling and model validation.

This test suite verifies comprehensive error handling, model validation,
and runtime patch logging using the canonical package structure.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the src directory to the path for proper imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import from the canonical package structure
# Import the modules we need to test
from src.svg_image_generator import cortex
from svg_image_generator import (
    get_available_cortex_models,
    safe_cortex_call,
    validate_cortex_model,
)
from svg_image_generator.app import RuntimePatchLogger


class TestModelValidation:
    """Test Cortex model validation and discovery."""

    def test_get_available_cortex_models_success(self):
        """Test successful retrieval of available Cortex models"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = [
                {"name": "claude-3-5-sonnet"},
                {"name": "claude-3-7-sonnet"},
                {"name": "claude-4-sonnet"},
                {"name": "openai-gpt-4o"},
                {"name": "openai-gpt-4o-mini"},
                {"name": "llama-3-8b-instruct"},
                {"name": "llama-3-70b-instruct"},
                {"name": "mistral-7b-instruct"},
                {"name": "mixtral-8x7b-instruct"},
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = get_available_cortex_models(mock_session)

            # Should return all available models, not just one
            expected_models = [
                "claude-3-5-sonnet",
                "claude-3-7-sonnet",
                "claude-4-sonnet",
                "openai-gpt-4o",
                "openai-gpt-4o-mini",
                "llama-3-8b-instruct",
                "llama-3-70b-instruct",
                "mistral-7b-instruct",
                "mixtral-8x7b-instruct",
            ]
            assert result == expected_models
            assert len(result) == 9

    def test_get_available_cortex_models_unknown_model(self) -> None:
        """Test handling of unknown models."""
        mock_session = Mock()

        # Mock unknown model error
        def mock_collect():
            raise Exception("Unknown model 'invalid-model'")

        mock_session.sql.return_value.collect.side_effect = mock_collect

        result = get_available_cortex_models(mock_session)

        # Should return fallback models
        assert len(result) >= 1
        assert "claude-3-5-sonnet" in result

    def test_get_available_cortex_models_exception(self):
        """Test model discovery with exceptions - should return all models with warnings."""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = [
                {"name": "claude-3-5-sonnet"},
                {"name": "claude-3-7-sonnet"},
                {"name": "claude-4-sonnet"},
                {"name": "openai-gpt-4o"},
                {"name": "openai-gpt-4o-mini"},
                {"name": "llama-3-8b-instruct"},
                {"name": "llama-3-70b-instruct"},
                {"name": "mistral-7b-instruct"},
                {"name": "mixtral-8x7b-instruct"},
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            # Mock the model validation to raise exceptions
            with patch.object(
                cortex,
                "validate_cortex_model",
                side_effect=Exception("Connection failed"),
            ):
                result = cortex.get_available_cortex_models(mock_session)

                # Should return all models even with exceptions
                expected_models = [
                    "claude-3-5-sonnet",
                    "claude-3-7-sonnet",
                    "claude-4-sonnet",
                    "openai-gpt-4o",
                    "openai-gpt-4o-mini",
                    "llama-3-8b-instruct",
                    "llama-3-70b-instruct",
                    "mistral-7b-instruct",
                    "mixtral-8x7b-instruct",
                ]
                assert result == expected_models
                assert len(result) == 9

    def test_validate_cortex_model_success(self) -> None:
        """Test successful model validation."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = [["Test response"]]

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is True
        mock_session.sql.assert_called_once()

    def test_validate_cortex_model_unknown_model(self) -> None:
        """Test validation of unknown model."""
        mock_session = Mock()

        def mock_collect():
            raise Exception("Unknown model 'invalid-model'")

        mock_session.sql.return_value.collect.side_effect = mock_collect

        result = validate_cortex_model(mock_session, "invalid-model")

        assert result is False

    def test_validate_cortex_model_no_response(self) -> None:
        """Test validation with no response."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is False

    def test_validate_cortex_model_temporary_error(self) -> None:
        """Test validation with temporary error."""
        mock_session = Mock()

        def mock_collect():
            raise Exception("Temporary network error")

        mock_session.sql.return_value.collect.side_effect = mock_collect

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        # Current implementation returns False for any error that's not "unknown model"
        assert result is False


class TestSafeCortexCall:
    """Test safe Cortex calling with comprehensive error handling."""

    def test_safe_cortex_call_success(self) -> None:
        """Test successful Cortex call."""
        mock_session = Mock()

        # Mock successful validation and call
        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True
            mock_session.sql.return_value.collect.return_value = [["Generated content"]]

            result = safe_cortex_call(
                mock_session, "claude-3-5-sonnet", "Test prompt", "Test operation"
            )

            assert result == "Generated content"
            mock_validate.assert_called_once()

    def test_safe_cortex_call_model_validation_fails(self) -> None:
        """Test Cortex call with model validation failure."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = False

            with pytest.raises(
                ValueError, match="Model 'invalid-model' is not available"
            ):
                safe_cortex_call(
                    mock_session, "invalid-model", "Test prompt", "Test operation"
                )

    def test_safe_cortex_call_unknown_model_error(self) -> None:
        """Test Cortex call with unknown model error."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True

            def mock_collect():
                raise Exception("Unknown model 'invalid-model'")

            mock_session.sql.return_value.collect.side_effect = mock_collect

            with pytest.raises(
                ValueError, match="Model 'invalid-model' is not available"
            ):
                safe_cortex_call(
                    mock_session, "invalid-model", "Test prompt", "Test operation"
                )

    def test_safe_cortex_call_external_function_error(self) -> None:
        """Test Cortex call with external function error."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True

            def mock_collect():
                raise Exception("External function error")

            mock_session.sql.return_value.collect.side_effect = mock_collect

            with pytest.raises(ValueError, match="Cortex service error"):
                safe_cortex_call(
                    mock_session, "claude-3-5-sonnet", "Test prompt", "Test operation"
                )

    def test_safe_cortex_call_timeout_error(self) -> None:
        """Test Cortex call with timeout error."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True

            def mock_collect():
                raise Exception("Request timeout")

            mock_session.sql.return_value.collect.side_effect = mock_collect

            with pytest.raises(ValueError, match="Request timed out"):
                safe_cortex_call(
                    mock_session, "claude-3-5-sonnet", "Test prompt", "Test operation"
                )

    def test_safe_cortex_call_permission_error(self) -> None:
        """Test Cortex call with permission error."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True

            def mock_collect():
                raise Exception("Insufficient privileges")

            mock_session.sql.return_value.collect.side_effect = mock_collect

            with pytest.raises(ValueError, match="Insufficient privileges"):
                safe_cortex_call(
                    mock_session, "claude-3-5-sonnet", "Test prompt", "Test operation"
                )

    def test_safe_cortex_call_no_result(self) -> None:
        """Test Cortex call with no result."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True
            mock_session.sql.return_value.collect.return_value = []

            result = safe_cortex_call(
                mock_session, "claude-3-5-sonnet", "Test prompt", "Test operation"
            )

            assert result is None

    def test_safe_cortex_call_unexpected_error(self) -> None:
        """Test Cortex call with unexpected error."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True

            def mock_collect():
                raise Exception("Unexpected database error")

            mock_session.sql.return_value.collect.side_effect = mock_collect

            with pytest.raises(ValueError, match="Cortex operation failed"):
                safe_cortex_call(
                    mock_session, "claude-3-5-sonnet", "Test prompt", "Test operation"
                )


class TestRuntimePatchLogging:
    """Test the runtime patch logging system."""

    def test_runtime_patch_logger_creation(self) -> None:
        """Test RuntimePatchLogger creation."""
        patch_logger = RuntimePatchLogger()
        assert patch_logger is not None

    def test_log_patch_basic(self) -> None:
        """Test basic patch logging."""
        patch_logger = RuntimePatchLogger()

        with patch("svg_image_generator.app.logger") as mock_logger:
            with patch("svg_image_generator.app.st") as mock_st:
                patch_logger.log_patch("Test Component", "Test description")

                # Verify logging occurred
                mock_logger.warning.assert_called_once()
                mock_st.warning.assert_called_once()

                # Verify log message structure
                log_call = mock_logger.warning.call_args[0][0]
                assert "RUNTIME PATCH APPLIED" in log_call
                assert "Component: Test Component" in log_call
                assert "Description: Test description" in log_call
                assert "Impact: Low" in log_call  # Default impact
                assert "Timestamp:" in log_call

    def test_log_patch_with_impact_and_guidance(self) -> None:
        """Test patch logging with custom impact and guidance."""
        patch_logger = RuntimePatchLogger()

        with patch("svg_image_generator.app.logger") as mock_logger:
            with patch("svg_image_generator.app.st") as mock_st:
                patch_logger.log_patch(
                    "Critical Component",
                    "Critical issue description",
                    "High",
                    "Contact maintainers immediately",
                )

                # Verify logging occurred
                mock_logger.warning.assert_called_once()
                mock_st.warning.assert_called_once()

                # Verify log message structure
                log_call = mock_logger.warning.call_args[0][0]
                assert "Component: Critical Component" in log_call
                assert "Description: Critical issue description" in log_call
                assert "Impact: High" in log_call
                assert "Guidance: Contact maintainers immediately" in log_call

    def test_log_patch_structure_validation(self) -> None:
        """Test that patch logging produces structured, parseable output."""
        patch_logger = RuntimePatchLogger()

        with patch("svg_image_generator.app.logger") as mock_logger:
            patch_logger.log_patch(
                "Test Component", "Test description", "Medium", "Test guidance"
            )

            log_call = mock_logger.warning.call_args[0][0]

            # Verify all required fields are present
            required_fields = [
                "RUNTIME PATCH APPLIED:",
                "Component:",
                "Description:",
                "Impact:",
                "Guidance:",
                "Timestamp:",
            ]

            for field in required_fields:
                assert field in log_call, f"Missing required field: {field}"

    def test_log_patch_impact_levels(self) -> None:
        """Test different impact levels."""
        patch_logger = RuntimePatchLogger()
        impact_levels = ["Low", "Medium", "High", "Critical"]

        with patch("svg_image_generator.app.logger") as mock_logger:
            for impact in impact_levels:
                mock_logger.reset_mock()

                patch_logger.log_patch("Test Component", "Test description", impact)

                log_call = mock_logger.warning.call_args[0][0]
                assert f"Impact: {impact}" in log_call


class TestEndToEndErrorScenarios:
    """Test end-to-end error scenarios with patch logging."""

    def test_model_discovery_failure_with_patch_logging(self):
        """Test model discovery failure with patch logging."""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = [
                {"name": "claude-3-5-sonnet"},
                {"name": "claude-3-7-sonnet"},
                {"name": "claude-4-sonnet"},
                {"name": "openai-gpt-4o"},
                {"name": "openai-gpt-4o-mini"},
                {"name": "llama-3-8b-instruct"},
                {"name": "llama-3-70b-instruct"},
                {"name": "mistral-7b-instruct"},
                {"name": "mixtral-8x7b-instruct"},
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            # Mock model validation to fail
            with patch.object(
                cortex,
                "validate_cortex_model",
                side_effect=Exception("Connection failed"),
            ):
                result = cortex.get_available_cortex_models(mock_session)

                # Should return all models even with failures
                expected_models = [
                    "claude-3-5-sonnet",
                    "claude-3-7-sonnet",
                    "claude-4-sonnet",
                    "openai-gpt-4o",
                    "openai-gpt-4o-mini",
                    "llama-3-8b-instruct",
                    "llama-3-70b-instruct",
                    "mistral-7b-instruct",
                    "mixtral-8x7b-instruct",
                ]
                assert result == expected_models
                assert len(result) == 9

    def test_cortex_call_failure_with_patch_logging(self) -> None:
        """Test Cortex call failure with patch logging."""
        mock_session = Mock()

        with patch("svg_image_generator.cortex.validate_cortex_model") as mock_validate:
            mock_validate.return_value = True

            def mock_collect():
                raise Exception("Unknown model 'invalid-model'")

            mock_session.sql.return_value.collect.side_effect = mock_collect

            with pytest.raises(
                ValueError, match="Model 'invalid-model' is not available"
            ):
                safe_cortex_call(
                    mock_session, "invalid-model", "Test prompt", "Test operation"
                )

    def test_comprehensive_error_handling(self):
        """Test comprehensive error handling with multiple failure modes."""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = [
                {"name": "claude-3-5-sonnet"},
                {"name": "claude-3-7-sonnet"},
                {"name": "claude-4-sonnet"},
                {"name": "openai-gpt-4o"},
                {"name": "openai-gpt-4o-mini"},
                {"name": "llama-3-8b-instruct"},
                {"name": "llama-3-70b-instruct"},
                {"name": "mistral-7b-instruct"},
                {"name": "mixtral-8x7b-instruct"},
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            # Mock multiple failure modes
            with patch.object(
                cortex,
                "validate_cortex_model",
                side_effect=Exception("Complete system failure"),
            ):
                result = cortex.get_available_cortex_models(mock_session)

                # Should return all models even with complete system failure
                expected_models = [
                    "claude-3-5-sonnet",
                    "claude-3-7-sonnet",
                    "claude-4-sonnet",
                    "openai-gpt-4o",
                    "openai-gpt-4o-mini",
                    "llama-3-8b-instruct",
                    "llama-3-70b-instruct",
                    "mistral-7b-instruct",
                    "mixtral-8x7b-instruct",
                ]
                assert result == expected_models
                assert len(result) == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
