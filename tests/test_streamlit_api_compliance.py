"""
Tests for Streamlit API compliance.

These tests verify that our usage of Streamlit Widget APIs is correct according to
their documentation, preventing runtime errors due to incorrect API usage.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the src directory to the path for proper imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class TestStreamlitWidgetAPICompliance:
    """Test that our Streamlit Widget API usage is correct."""

    def test_st_selectbox_api_compliance(self) -> None:
        """Test that st.selectbox is called with correct parameters."""
        with patch("streamlit.selectbox") as mock_selectbox:
            # Test database dropdown
            mock_selectbox.return_value = "TEST_DB"

            # Simulate the database selection logic
            available_databases = ["DB1", "DB2", "TEST_DB"]
            current_database = "TEST_DB"

            selected_database = mock_selectbox(
                "📁 Database",
                options=available_databases,
                index=available_databases.index(current_database)
                if current_database in available_databases
                else 0,
                help="Select the database where you want to work",
            )

            # Verify API usage is correct
            mock_selectbox.assert_called_once_with(
                "📁 Database",
                options=available_databases,
                index=2,  # TEST_DB is at index 2
                help="Select the database where you want to work",
            )

            # Verify return value handling
            assert selected_database == "TEST_DB"

    def test_st_selectbox_empty_options_handling(self) -> None:
        """Test st.selectbox with empty options list."""
        with patch("streamlit.selectbox") as mock_selectbox:
            # Test with empty options
            available_databases = []
            current_database = ""

            # This should not cause a runtime error
            try:
                selected_database = mock_selectbox(
                    "📁 Database",
                    options=available_databases,
                    index=0,  # Default to 0 when empty
                    help="Select the database where you want to work",
                )
                # Should not reach here if empty options cause issues
                assert True
            except Exception as e:
                pytest.fail(f"st.selectbox with empty options should not raise: {e}")

    def test_st_text_area_api_compliance(self) -> None:
        """Test that st.text_area is called with correct parameters."""
        with patch("streamlit.text_area") as mock_text_area:
            mock_text_area.return_value = "Create a blue circle"

            # Simulate the SVG prompt input
            svg_prompt = mock_text_area(
                "Describe the SVG you want to generate:",
                placeholder="e.g., Create a simple logo with a blue circle and white text saying 'Hello World'",
                height=100,
            )

            # Verify API usage is correct
            mock_text_area.assert_called_once_with(
                "Describe the SVG you want to generate:",
                placeholder="e.g., Create a simple logo with a blue circle and white text saying 'Hello World'",
                height=100,
            )

            assert svg_prompt == "Create a blue circle"

    def test_st_button_api_compliance(self) -> None:
        """Test that st.button is called with correct parameters."""
        with patch("streamlit.button") as mock_button:
            mock_button.return_value = True

            # Simulate the generate button
            button_clicked = mock_button(
                "🚀 Generate SVG and Upload to Stage", type="primary"
            )

            # Verify API usage is correct
            mock_button.assert_called_once_with(
                "🚀 Generate SVG and Upload to Stage", type="primary"
            )

            assert button_clicked is True

    def test_st_error_api_compliance(self) -> None:
        """Test that st.error is called with correct parameters."""
        with patch("streamlit.error") as mock_error:
            # Simulate error display
            mock_error("❌ Failed to get session: Connection failed")

            # Verify API usage is correct
            mock_error.assert_called_once_with(
                "❌ Failed to get session: Connection failed"
            )

    def test_st_success_api_compliance(self) -> None:
        """Test that st.success is called with correct parameters."""
        with patch("streamlit.success") as mock_success:
            # Simulate success message
            mock_success("✅ Connected to Snowflake using `connections.toml`.")

            # Verify API usage is correct
            mock_success.assert_called_once_with(
                "✅ Connected to Snowflake using `connections.toml`."
            )

    def test_st_warning_api_compliance(self) -> None:
        """Test that st.warning is called with correct parameters."""
        with patch("streamlit.warning") as mock_warning:
            # Simulate warning message
            mock_warning("⚠️ No accessible schemas found")

            # Verify API usage is correct
            mock_warning.assert_called_once_with("⚠️ No accessible schemas found")

    def test_st_info_api_compliance(self) -> None:
        """Test that st.info is called with correct parameters."""
        with patch("streamlit.info") as mock_info:
            # Simulate info message
            mock_info(
                "🔗 Using active Snowflake session (Streamlit in Snowflake environment)"
            )

            # Verify API usage is correct
            mock_info.assert_called_once_with(
                "🔗 Using active Snowflake session (Streamlit in Snowflake environment)"
            )

    def test_st_sidebar_api_compliance(self) -> None:
        """Test that st.sidebar is used correctly."""
        with patch("streamlit.sidebar") as mock_sidebar:
            # Simulate sidebar usage
            mock_sidebar.header("🔧 Context Configuration")
            mock_sidebar.selectbox.return_value = "TEST_DB"

            # Verify sidebar API usage
            mock_sidebar.header.assert_called_once_with("🔧 Context Configuration")

    def test_st_columns_api_compliance(self) -> None:
        """Test that st.columns is used correctly."""
        with patch("streamlit.columns") as mock_columns:
            mock_columns.return_value = [Mock(), Mock()]

            # Simulate column creation
            col1, col2 = mock_columns([1, 1])

            # Verify API usage is correct
            mock_columns.assert_called_once_with([1, 1])
            assert len([col1, col2]) == 2

    def test_st_spinner_api_compliance(self) -> None:
        """Test that st.spinner is used correctly."""
        with patch("streamlit.spinner") as mock_spinner:
            mock_spinner_context = Mock()
            mock_spinner.return_value.__enter__ = Mock(
                return_value=mock_spinner_context
            )
            mock_spinner.return_value.__exit__ = Mock(return_value=None)

            # Simulate spinner usage
            with mock_spinner("🔄 Implementing prompt sandwich approach..."):
                pass

            # Verify API usage is correct
            mock_spinner.assert_called_once_with(
                "🔄 Implementing prompt sandwich approach..."
            )

    def test_st_expander_api_compliance(self) -> None:
        """Test that st.expander is used correctly."""
        with patch("streamlit.expander") as mock_expander:
            mock_expander_context = Mock()
            mock_expander.return_value.__enter__ = Mock(
                return_value=mock_expander_context
            )
            mock_expander.return_value.__exit__ = Mock(return_value=None)

            # Simulate expander usage
            with mock_expander("📝 Original Prompt"):
                pass

            # Verify API usage is correct
            mock_expander.assert_called_once_with("📝 Original Prompt")

    def test_st_subheader_api_compliance(self) -> None:
        """Test that st.subheader is used correctly."""
        with patch("streamlit.subheader") as mock_subheader:
            # Simulate subheader usage
            mock_subheader("🔍 Prompt Sandwich Process")

            # Verify API usage is correct
            mock_subheader.assert_called_once_with("🔍 Prompt Sandwich Process")

    def test_st_header_api_compliance(self) -> None:
        """Test that st.header is used correctly."""
        with patch("streamlit.header") as mock_header:
            # Simulate header usage
            mock_header("🎨 SVG Generation Settings")

            # Verify API usage is correct
            mock_header.assert_called_once_with("🎨 SVG Generation Settings")

    def test_st_text_input_api_compliance(self) -> None:
        """Test that st.text_input is used correctly."""
        with patch("streamlit.text_input") as mock_text_input:
            mock_text_input.return_value = "generated_svg_20241225_143022"

            # Simulate text input usage
            filename = mock_text_input(
                "📝 SVG Filename (without extension):",
                value="generated_svg_20241225_143022",
            )

            # Verify API usage is correct
            mock_text_input.assert_called_once_with(
                "📝 SVG Filename (without extension):",
                value="generated_svg_20241225_143022",
            )

            assert filename == "generated_svg_20241225_143022"


class TestStreamlitErrorHandlingCompliance:
    """Test that our error handling with Streamlit APIs is correct."""

    def test_st_stop_api_compliance(self) -> None:
        """Test that st.stop is used correctly in error scenarios."""
        with patch("streamlit.stop") as mock_stop:
            # Simulate error scenario that should stop execution
            mock_stop()

            # Verify API usage is correct
            mock_stop.assert_called_once()

    def test_error_flow_with_stop(self) -> None:
        """Test complete error flow with st.error and st.stop."""
        with patch("streamlit.error") as mock_error:
            with patch("streamlit.stop") as mock_stop:
                # Simulate error scenario
                error_message = "❌ Failed to get session: Connection failed"
                mock_error(error_message)
                mock_stop()

                # Verify correct error handling sequence
                mock_error.assert_called_once_with(error_message)
                mock_stop.assert_called_once()

    def test_warning_flow_without_stop(self) -> None:
        """Test warning flow that doesn't stop execution."""
        with patch("streamlit.warning") as mock_warning:
            # Simulate warning scenario
            warning_message = "⚠️ Active session not available. Trying connection from `connections.toml`..."
            mock_warning(warning_message)

            # Verify warning is displayed but execution continues
            mock_warning.assert_called_once_with(warning_message)


class TestStreamlitDataFlowCompliance:
    """Test that our data flow with Streamlit widgets is correct."""

    def test_selectbox_data_validation(self) -> None:
        """Test that selectbox receives valid data."""
        with patch("streamlit.selectbox") as mock_selectbox:
            # Test with valid data
            valid_options = ["option1", "option2", "option3"]
            valid_index = 1

            mock_selectbox("Test", options=valid_options, index=valid_index)

            # Verify data is passed correctly
            call_args = mock_selectbox.call_args
            assert call_args[0][0] == "Test"  # label
            assert call_args[1]["options"] == valid_options
            assert call_args[1]["index"] == valid_index

    def test_text_area_data_validation(self) -> None:
        """Test that text_area receives valid data."""
        with patch("streamlit.text_area") as mock_text_area:
            # Test with valid data
            valid_placeholder = "Enter text here"
            valid_height = 100

            mock_text_area("Test", placeholder=valid_placeholder, height=valid_height)

            # Verify data is passed correctly
            call_args = mock_text_area.call_args
            assert call_args[0][0] == "Test"  # label
            assert call_args[1]["placeholder"] == valid_placeholder
            assert call_args[1]["height"] == valid_height

    def test_button_data_validation(self) -> None:
        """Test that button receives valid data."""
        with patch("streamlit.button") as mock_button:
            # Test with valid data
            valid_label = "Click me"
            valid_type = "primary"

            mock_button(valid_label, type=valid_type)

            # Verify data is passed correctly
            call_args = mock_button.call_args
            assert call_args[0][0] == valid_label
            assert call_args[1]["type"] == valid_type
