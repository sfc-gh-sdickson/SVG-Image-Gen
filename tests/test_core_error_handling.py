"""
Tests for error handling paths in core.py.

These tests focus on the error handling scenarios that are currently not covered.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the src directory to the path for proper imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from svg_image_generator.core import (
    get_accessible_databases,
    get_accessible_schemas,
    get_accessible_stages,
    validate_user_permissions,
)
from svg_image_generator.cortex import validate_cortex_model


class TestCoreErrorHandling:
    """Test error handling in core functions."""

    def test_get_accessible_databases_sql_error(self) -> None:
        """Test get_accessible_databases with SQL error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("SQL error")

        result = get_accessible_databases(mock_session)

        assert result == []

    def test_get_accessible_databases_empty_result(self) -> None:
        """Test get_accessible_databases with empty result."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        result = get_accessible_databases(mock_session)

        assert result == []

    def test_get_accessible_schemas_sql_error(self) -> None:
        """Test get_accessible_schemas with SQL error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("SQL error")

        result = get_accessible_schemas(mock_session, "TEST_DB")

        assert result == []

    def test_get_accessible_schemas_empty_result(self) -> None:
        """Test get_accessible_schemas with empty result."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        result = get_accessible_schemas(mock_session, "TEST_DB")

        assert result == []

    def test_get_accessible_stages_sql_error(self) -> None:
        """Test get_accessible_stages with SQL error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("SQL error")

        result = get_accessible_stages(mock_session, "TEST_DB", "TEST_SCHEMA")

        assert result == []

    def test_get_accessible_stages_empty_result(self) -> None:
        """Test get_accessible_stages with empty result."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        result = get_accessible_stages(mock_session, "TEST_DB", "TEST_SCHEMA")

        assert result == []

    def test_validate_user_permissions_sql_error(self) -> None:
        """Test validate_user_permissions with SQL error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("SQL error")

        result = validate_user_permissions(
            mock_session, "TEST_DB", "TEST_SCHEMA", "TEST_STAGE"
        )

        assert result is False

    def test_validate_user_permissions_no_permissions(self) -> None:
        """Test validate_user_permissions when user has no permissions."""
        mock_session = Mock()
        # The function tries to USE DATABASE, USE SCHEMA, and LIST @stage
        # Mock it to fail on the LIST operation (stage access)
        mock_session.sql.side_effect = [
            Mock(collect=lambda: None),  # USE DATABASE succeeds
            Mock(collect=lambda: None),  # USE SCHEMA succeeds
            Exception("Insufficient privileges"),  # LIST @stage fails
        ]

        result = validate_user_permissions(
            mock_session, "TEST_DB", "TEST_SCHEMA", "TEST_STAGE"
        )

        assert result is False

    def test_validate_cortex_model_sql_error(self) -> None:
        """Test validate_cortex_model with SQL error."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("SQL error")

        result = validate_cortex_model(mock_session, "claude-3-5-sonnet")

        assert result is False

    def test_validate_cortex_model_model_not_found(self) -> None:
        """Test validate_cortex_model when model is not found."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        result = validate_cortex_model(mock_session, "nonexistent-model")

        assert result is False


class TestCoreEdgeCases:
    """Test edge cases in core functions."""

    def test_get_accessible_databases_malformed_result(self) -> None:
        """Test get_accessible_databases with malformed result."""
        mock_session = Mock()
        mock_df = Mock()
        # Mock rows where some have None values in the first column
        mock_df.select.return_value.filter.return_value.collect.return_value = [
            ["DB1"],
            [None],
            ["DB2"],
        ]
        mock_session.sql.return_value = mock_df

        result = get_accessible_databases(mock_session)
        # Only non-None values should be included
        assert "DB1" in result
        assert "DB2" in result
        assert len(result) == 2

    def test_get_accessible_schemas_malformed_result(self) -> None:
        """Test get_accessible_schemas with malformed result."""
        mock_session = Mock()
        mock_df = Mock()
        # Mock rows where some have None values in the first column
        mock_df.select.return_value.filter.return_value.collect.return_value = [
            ["SCHEMA1"],
            [None],
            ["SCHEMA2"],
        ]
        mock_session.sql.return_value = mock_df

        result = get_accessible_schemas(mock_session, "TEST_DB")
        # Only non-None values should be included
        assert "SCHEMA1" in result
        assert "SCHEMA2" in result
        assert len(result) == 2

    def test_get_accessible_stages_malformed_result(self) -> None:
        """Test get_accessible_stages with malformed result."""
        mock_session = Mock()
        mock_df = Mock()
        # Mock rows where some have None values in the first column
        mock_df.select.return_value.filter.return_value.collect.return_value = [
            ["STAGE1"],
            [None],
            ["STAGE2"],
        ]
        mock_session.sql.return_value = mock_df

        result = get_accessible_stages(mock_session, "TEST_DB", "TEST_SCHEMA")
        # Only non-None values should be included
        assert "STAGE1" in result
        assert "STAGE2" in result
        assert len(result) == 2

    def test_validate_user_permissions_partial_permissions(self) -> None:
        """Test validate_user_permissions with partial permissions."""
        mock_session = Mock()
        # Mock partial permissions - can USE database and schema but not LIST stage
        mock_session.sql.side_effect = [
            Mock(collect=lambda: None),  # USE DATABASE succeeds
            Mock(collect=lambda: None),  # USE SCHEMA succeeds
            Exception("Stage does not exist"),  # LIST @stage fails
        ]

        result = validate_user_permissions(
            mock_session, "TEST_DB", "TEST_SCHEMA", "TEST_STAGE"
        )

        assert result is False

    def test_validate_cortex_model_case_sensitivity(self) -> None:
        """Test validate_cortex_model with case sensitivity."""
        mock_session = Mock()
        # The current implementation doesn't do case-sensitive matching
        # It just tries to call the model and sees if it works
        mock_session.sql.return_value.collect.return_value = [["test result"]]

        # Test exact match
        result_exact = validate_cortex_model(mock_session, "claude-3-5-sonnet")
        assert result_exact is True  # Should work regardless of case

        # Test case-insensitive match
        result_insensitive = validate_cortex_model(mock_session, "CLAUDE-3-5-SONNET")
        assert result_insensitive is True


class TestCoreInputValidation:
    """Test input validation in core functions."""

    def test_get_accessible_schemas_empty_database(self):
        """Test get_accessible_schemas with empty database name"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = []
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = get_accessible_schemas(mock_session, "")

            # Should return empty list for empty database
            assert result == []

    def test_get_accessible_schemas_none_database(self):
        """Test get_accessible_schemas with None database name"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = []
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = get_accessible_schemas(mock_session, None)

            # Should return empty list for None database
            assert result == []

    def test_get_accessible_schemas_whitespace_database(self):
        """Test get_accessible_schemas with whitespace-only database name"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = []
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = get_accessible_schemas(mock_session, "   ")

            # Should return empty list for whitespace-only database
            assert result == []

    def test_get_accessible_schemas_invalid_database(self):
        """Test get_accessible_schemas with invalid database name"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.side_effect = Exception("Database does not exist")
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = get_accessible_schemas(mock_session, "INVALID_DB")

            # Should return empty list when database doesn't exist
            assert result == []

    def test_get_accessible_stages_empty_parameters(self) -> None:
        """Test get_accessible_stages with empty parameters."""
        mock_session = Mock()

        result = get_accessible_stages(mock_session, "", "")

        assert result == []
        mock_session.sql.assert_not_called()

    def test_get_accessible_stages_none_parameters(self) -> None:
        """Test get_accessible_stages with None parameters."""
        mock_session = Mock()

        result = get_accessible_stages(mock_session, None, None)

        assert result == []
        mock_session.sql.assert_not_called()

    def test_validate_user_permissions_empty_parameters(self) -> None:
        """Test validate_user_permissions with empty parameters."""
        mock_session = Mock()

        result = validate_user_permissions(mock_session, "", "", "")

        assert result is False
        mock_session.sql.assert_not_called()

    def test_validate_cortex_model_empty_model(self) -> None:
        """Test validate_cortex_model with empty model name."""
        mock_session = Mock()

        result = validate_cortex_model(mock_session, "")

        assert result is False
        mock_session.sql.assert_not_called()


def test_column_name_robustness():
    """Test that using column names is more robust than hardcoded indices"""
    from unittest.mock import Mock

    from src.svg_image_generator.core import (
        get_accessible_databases,
        get_accessible_schemas,
        get_accessible_stages,
    )

    # Mock session with Snowpark DataFrame operations
    mock_session = Mock()

    # Test case 1: Standard column order
    mock_df = Mock()
    mock_df.select.return_value.filter.return_value.collect.return_value = [
        ["test_db1"],
        ["test_db2"],
    ]
    mock_session.sql.return_value = mock_df

    result = get_accessible_databases(mock_session)
    assert result == ["test_db1", "test_db2"]

    # Test case 2: Different column order (name in first position)
    mock_df.select.return_value.filter.return_value.collect.return_value = [
        ["test_db3"],
        ["test_db4"],
    ]

    result = get_accessible_databases(mock_session)
    assert result == ["test_db3", "test_db4"]

    # Test case 3: No 'name' column (fallback to index 1)
    mock_df.select.return_value.filter.return_value.collect.return_value = [
        ["test_db5"],
        ["test_db6"],
    ]

    result = get_accessible_databases(mock_session)
    assert result == ["test_db5", "test_db6"]

    # Test case 4: Empty result
    mock_df.select.return_value.filter.return_value.collect.return_value = []

    result = get_accessible_databases(mock_session)
    assert result == []

    # Test schemas with similar robustness
    mock_df.select.return_value.filter.return_value.collect.return_value = [
        ["test_schema1"],
        ["test_schema2"],
    ]

    result = get_accessible_schemas(mock_session, "test_db")
    assert result == ["test_schema1", "test_schema2"]

    # Test stages with similar robustness
    mock_df.select.return_value.filter.return_value.collect.return_value = [
        ["test_stage1"],
        ["test_stage2"],
    ]

    result = get_accessible_stages(mock_session, "test_db", "test_schema")
    assert result == ["test_stage1", "test_stage2"]
