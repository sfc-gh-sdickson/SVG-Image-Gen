"""
Pytest configuration and common fixtures for SVG Image Generator tests.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


@pytest.fixture
def mock_snowflake_session():
    """Mock Snowflake session for testing."""
    session = Mock()
    session.sql.return_value.collect.return_value = [["test_result"]]
    return session


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing."""
    with patch("streamlit.set_page_config") as mock_config, \
         patch("streamlit.title") as mock_title, \
         patch("streamlit.sidebar") as mock_sidebar, \
         patch("streamlit.columns") as mock_columns, \
         patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.selectbox") as mock_selectbox, \
         patch("streamlit.text_input") as mock_text_input, \
         patch("streamlit.button") as mock_button, \
         patch("streamlit.success") as mock_success, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.info") as mock_info, \
         patch("streamlit.warning") as mock_warning, \
         patch("streamlit.spinner") as mock_spinner, \
         patch("streamlit.expander") as mock_expander, \
         patch("streamlit.components.v1.html") as mock_html, \
         patch("streamlit.code") as mock_code:
        
        # Setup mock return values
        mock_columns.return_value = [Mock(), Mock()]
        mock_text_area.return_value = "test prompt"
        mock_selectbox.return_value = "claude-3-5-sonnet"
        mock_text_input.return_value = "test_file"
        mock_button.return_value = True
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        
        yield {
            "config": mock_config,
            "title": mock_title,
            "sidebar": mock_sidebar,
            "columns": mock_columns,
            "text_area": mock_text_area,
            "selectbox": mock_selectbox,
            "text_input": mock_text_input,
            "button": mock_button,
            "success": mock_success,
            "error": mock_error,
            "info": mock_info,
            "warning": mock_warning,
            "spinner": mock_spinner,
            "expander": mock_expander,
            "html": mock_html,
            "code": mock_code,
        }


@pytest.fixture
def sample_svg_content():
    """Sample SVG content for testing."""
    return """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
    </svg>"""


@pytest.fixture
def sample_cortex_response():
    """Sample Cortex AI response for testing."""
    return {
        "content": """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
        </svg>""",
        "model": "claude-3-5-sonnet",
        "usage": {"prompt_tokens": 50, "completion_tokens": 100}
    }


@pytest.fixture
def test_config():
    """Test configuration for the application."""
    return {
        "stage_name": "TEST_SVG_STAGE",
        "database": "TEST_DB",
        "schema": "TEST_SCHEMA",
        "warehouse": "TEST_WH",
        "model": "claude-3-5-sonnet",
        "prompt": "Create a simple red circle",
        "filename": "test_svg"
    }


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
        mock_dt.strftime.return_value = "20240101_120000"
        yield mock_dt


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "snowflake: marks tests that require Snowflake connection"
    )
    config.addinivalue_line(
        "markers", "ai: marks tests that require AI service"
    )


# Skip slow tests by default
def pytest_collection_modifyitems(config, items):
    """Skip slow tests by default unless --runslow is passed."""
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow) 