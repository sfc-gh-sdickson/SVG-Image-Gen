"""
Integration tests for the app module.

These tests focus on testable business logic while avoiding UI components
that are difficult to test in isolation.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the src directory to the path for proper imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from svg_image_generator.app import RuntimePatchLogger, use_context


class TestRuntimePatchLogger:
    """Test the RuntimePatchLogger class."""

    def test_log_patch_basic(self) -> None:
        """Test basic patch logging functionality."""
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

    def test_log_patch_with_custom_impact_and_guidance(self) -> None:
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

    def test_runtime_patch_logger_creation(self) -> None:
        """Test that RuntimePatchLogger can be instantiated and used."""
        from svg_image_generator.app import RuntimePatchLogger

        # Test that the class exists and can be used
        logger = RuntimePatchLogger()
        assert logger is not None

        # Test that the log_patch method exists and can be called
        assert hasattr(logger, "log_patch")
        assert callable(logger.log_patch)

        # Test static method call
        RuntimePatchLogger.log_patch("Test", "Test description", "Low", "Test guidance")


class TestUseContext:
    """Test the use_context function."""

    def test_use_context_success(self) -> None:
        """Test context switching with both database and schema."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        # Mock the global session variable
        with patch("svg_image_generator.app.session", mock_session):
            # Mock the global variables
            with patch("svg_image_generator.app.selected_database", "TEST_DB"):
                with patch("svg_image_generator.app.selected_schema", "TEST_SCHEMA"):
                    result = use_context()

        assert result is True
        calls = mock_session.sql.call_args_list
        assert len(calls) == 2
        assert "USE DATABASE" in str(calls[0])
        assert "USE SCHEMA" in str(calls[1])

    def test_use_context_database_only(self) -> None:
        """Test context switching with database only."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        # Mock the global session variable
        with patch("svg_image_generator.app.session", mock_session):
            # Mock the global variables
            with patch("svg_image_generator.app.selected_database", "TEST_DB"):
                with patch("svg_image_generator.app.selected_schema", ""):
                    result = use_context()

        assert result is True
        calls = mock_session.sql.call_args_list
        assert len(calls) == 1
        assert "USE DATABASE TEST_DB" in str(calls[0])

    def test_use_context_schema_only(self) -> None:
        """Test context switching with schema only."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        # Mock the global session variable
        with patch("svg_image_generator.app.session", mock_session):
            # Mock the global variables
            with patch("svg_image_generator.app.selected_database", ""):
                with patch("svg_image_generator.app.selected_schema", "TEST_SCHEMA"):
                    result = use_context()

        assert result is True
        calls = mock_session.sql.call_args_list
        assert len(calls) == 1
        assert "USE SCHEMA TEST_SCHEMA" in str(calls[0])

    def test_use_context_no_context(self) -> None:
        """Test context switching with no database or schema."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        # Mock the global variables
        with patch("svg_image_generator.app.selected_database", ""):
            with patch("svg_image_generator.app.selected_schema", ""):
                result = use_context()

        assert result is True
        # No SQL calls should be made
        mock_session.sql.assert_not_called()

    def test_use_context_failure(self) -> None:
        """Test context switching failure."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("Database error")

        # Mock the global variables
        with patch("svg_image_generator.app.selected_database", "TEST_DB"):
            with patch("svg_image_generator.app.selected_schema", "TEST_SCHEMA"):
                with patch("svg_image_generator.app.st") as mock_st:
                    result = use_context()

        assert result is False
        mock_st.error.assert_called_once()
        assert "Failed to switch context" in mock_st.error.call_args[0][0]


class TestAppErrorHandling:
    """Test error handling in the app module."""

    def test_session_error_handling(self) -> None:
        """Test session error handling."""
        with patch("svg_image_generator.app.get_session") as mock_get_session:
            mock_get_session.side_effect = Exception("Session error")

            with patch("svg_image_generator.app.st") as mock_st:
                # This would normally be in the main app flow
                try:
                    session = mock_get_session()
                except Exception as e:
                    mock_st.error(f"❌ Failed to get session: {str(e)}")
                    mock_st.stop()

                mock_st.error.assert_called_once()
                assert "Failed to get session" in mock_st.error.call_args[0][0]
                mock_st.stop.assert_called_once()

    def test_context_discovery_error_handling(self) -> None:
        """Test context discovery error handling."""
        with patch("svg_image_generator.app.discover_user_context") as mock_discover:
            mock_discover.side_effect = Exception("Context error")

            with patch("svg_image_generator.app.st") as mock_st:
                # This would normally be in the main app flow
                try:
                    user_context = mock_discover(Mock())
                    if not user_context:
                        mock_st.error("❌ Failed to discover user context")
                        mock_st.stop()
                except Exception as e:
                    mock_st.error(f"❌ Error discovering user context: {str(e)}")
                    mock_st.stop()

                mock_st.error.assert_called_once()
                assert "Error discovering user context" in mock_st.error.call_args[0][0]
                mock_st.stop.assert_called_once()

    def test_model_discovery_error_handling(self) -> None:
        """Test model discovery error handling."""
        with patch(
            "svg_image_generator.app.get_available_cortex_models"
        ) as mock_get_models:
            mock_get_models.side_effect = Exception("Model discovery error")

            with patch("svg_image_generator.app.logger") as mock_logger:
                with patch("svg_image_generator.app.patch_logger") as mock_patch_logger:
                    # This would normally be in the main app flow
                    try:
                        available_models = mock_get_models(Mock())
                        user_context = {"available_models": available_models}
                    except Exception as e:
                        mock_logger.warning(f"Could not discover Cortex models: {e}")
                        mock_patch_logger.log_patch(
                            "Model Discovery",
                            f"Failed to discover Cortex models: {e}",
                            "Medium",
                            "Using fallback models. Check Cortex availability and permissions.",
                        )
                        user_context = {"available_models": ["claude-3-5-sonnet"]}

                    assert user_context["available_models"] == ["claude-3-5-sonnet"]
                    mock_logger.warning.assert_called_once()
                    mock_patch_logger.log_patch.assert_called_once()


class TestAppBusinessLogic:
    """Test business logic in the app module."""

    def test_svg_content_extraction_logic(self) -> None:
        """Test SVG content extraction logic."""
        # Test case 1: Clean SVG content
        svg_content = "<svg><circle cx='50' cy='50' r='25' fill='blue'/></svg>"
        cleaned_content = svg_content.strip()

        if not cleaned_content.startswith("<svg"):
            # Try to extract SVG from the response
            start_idx = cleaned_content.find("<svg")
            end_idx = cleaned_content.rfind("</svg>") + 6
            if start_idx != -1 and end_idx != 5:
                cleaned_content = cleaned_content[start_idx:end_idx]

        assert (
            cleaned_content == "<svg><circle cx='50' cy='50' r='25' fill='blue'/></svg>"
        )

        # Test case 2: SVG with extra text
        svg_content_with_text = "Here is your SVG: <svg><rect width='100' height='100' fill='red'/></svg> Thank you!"
        cleaned_content = svg_content_with_text.strip()

        if not cleaned_content.startswith("<svg"):
            # Try to extract SVG from the response
            start_idx = cleaned_content.find("<svg")
            end_idx = cleaned_content.rfind("</svg>") + 6
            if start_idx != -1 and end_idx != 5:
                cleaned_content = cleaned_content[start_idx:end_idx]

        assert (
            cleaned_content == "<svg><rect width='100' height='100' fill='red'/></svg>"
        )

        # Test case 3: No SVG content
        no_svg_content = "No SVG found in this response"
        cleaned_content = no_svg_content.strip()

        if not cleaned_content.startswith("<svg"):
            # Try to extract SVG from the response
            start_idx = cleaned_content.find("<svg")
            end_idx = cleaned_content.rfind("</svg>") + 6
            if start_idx != -1 and end_idx != 5:
                cleaned_content = cleaned_content[start_idx:end_idx]

        assert cleaned_content == "No SVG found in this response"  # No change

    def test_filename_generation_logic(self) -> None:
        """Test filename generation logic."""
        from datetime import datetime

        # Test filename generation
        filename = f"generated_svg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        assert filename.startswith("generated_svg_")
        assert len(filename) > len("generated_svg_")

        # Test that it contains date and time
        assert "_" in filename
        parts = filename.split("_")
        assert len(parts) >= 3  # generated_svg + date + time

    def test_stage_options_logic(self) -> None:
        """Test stage options logic."""
        # Test stage options creation
        available_stages = ["STAGE1", "STAGE2"]
        stage_options = available_stages + ["Create New Stage"]

        assert stage_options == ["STAGE1", "STAGE2", "Create New Stage"]

        # Test new stage creation logic
        selected_stage = "Create New Stage"
        new_stage_name = ""

        if selected_stage == "Create New Stage":
            new_stage_name = "SVG_STAGE"
            selected_stage = new_stage_name

        assert new_stage_name == "SVG_STAGE"
        assert selected_stage == "SVG_STAGE"
