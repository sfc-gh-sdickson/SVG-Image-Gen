"""
Test suite for context discovery and prompt sandwich functionality.

This test suite verifies the context discovery, resource access, and prompt sandwich
implementation using the canonical package structure.
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
from svg_image_generator import (
    discover_user_context,
    generate_svg_with_refined_prompt,
    get_accessible_databases,
    get_accessible_schemas,
    get_accessible_stages,
    handle_context_errors,
    implement_prompt_sandwich,
    refine_prompt_with_cortex,
    validate_user_permissions,
)


class TestContextDiscovery:
    """Test context discovery functionality."""

    def test_discover_user_context_success(self) -> None:
        """Test successful user context discovery."""
        mock_session = Mock()
        # Mock individual SQL queries for each property
        mock_session.sql.side_effect = [
            Mock(collect=lambda: [["TEST_ROLE"]]),
            Mock(collect=lambda: [["TEST_WAREHOUSE"]]),
            # SHOW DATABASES
            Mock(
                select=Mock(
                    return_value=Mock(
                        filter=Mock(
                            return_value=Mock(
                                collect=Mock(return_value=[["DB1"], ["DB2"]])
                            )
                        )
                    )
                )
            ),
            Mock(collect=lambda: [["TEST_DB"]]),
            Mock(collect=lambda: [["TEST_SCHEMA"]]),
            # SHOW SCHEMAS IN DATABASE TEST_DB
            Mock(
                select=Mock(
                    return_value=Mock(
                        filter=Mock(
                            return_value=Mock(
                                collect=Mock(return_value=[["SCHEMA1"], ["SCHEMA2"]])
                            )
                        )
                    )
                )
            ),
            # SHOW STAGES IN SCHEMA TEST_DB.TEST_SCHEMA
            Mock(
                select=Mock(
                    return_value=Mock(
                        filter=Mock(
                            return_value=Mock(
                                collect=Mock(return_value=[["STAGE1"], ["STAGE2"]])
                            )
                        )
                    )
                )
            ),
        ]

        result = discover_user_context(mock_session)

        assert result["role"] == "TEST_ROLE"
        assert result["warehouse"] == "TEST_WAREHOUSE"
        assert result["current_database"] == "TEST_DB"
        assert result["current_schema"] == "TEST_SCHEMA"
        assert result["accessible_databases"] == ["DB1", "DB2"]
        assert result["accessible_schemas"] == ["SCHEMA1", "SCHEMA2"]
        assert result["accessible_stages"] == ["STAGE1", "STAGE2"]

    def test_discover_user_context_error_handling(self):
        """Test discover_user_context error handling"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.side_effect = Exception("Database error")
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = discover_user_context(mock_session)

            # Should return empty dict when there's an error
            assert result == {}

    def test_discover_user_context_empty_result(self):
        """Test discover_user_context with empty result"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = []
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = discover_user_context(mock_session)

            # Should return empty dict when no properties found
            assert result == {}

    def test_discover_user_context_missing_properties(self):
        """Test discover_user_context with missing properties"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            # Mock session properties query with missing expected properties
            mock_session.sql.return_value.collect.return_value = [
                {"name": "UNKNOWN_PROPERTY", "value": "some_value"}
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            result = discover_user_context(mock_session)

            # Should return empty dict when expected properties are missing
            assert result == {}

    def test_get_accessible_databases(self) -> None:
        """Test database discovery."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.select.return_value.filter.return_value.collect.return_value = [
            ["DB1"],
            ["DB2"],
            [""],
        ]
        mock_session.sql.return_value = mock_df

        result = get_accessible_databases(mock_session)
        assert result == ["DB1", "DB2"]

    def test_get_accessible_schemas(self) -> None:
        """Test schema discovery."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.select.return_value.filter.return_value.collect.return_value = [
            ["SCHEMA1"],
            ["SCHEMA2"],
        ]
        mock_session.sql.return_value = mock_df

        result = get_accessible_schemas(mock_session, "TEST_DB")
        assert result == ["SCHEMA1", "SCHEMA2"]

    def test_get_accessible_stages(self) -> None:
        """Test stage discovery."""
        mock_session = Mock()
        mock_df = Mock()
        mock_df.select.return_value.filter.return_value.collect.return_value = [
            ["STAGE1"],
            ["STAGE2"],
        ]
        mock_session.sql.return_value = mock_df

        result = get_accessible_stages(mock_session, "TEST_DB", "TEST_SCHEMA")
        assert result == ["STAGE1", "STAGE2"]

    def test_validate_user_permissions_success(self) -> None:
        """Test successful permission validation."""
        mock_session = Mock()
        mock_session.sql.return_value.collect.return_value = []

        result = validate_user_permissions(mock_session, "DB", "SCHEMA", "STAGE")
        assert result is True

        # Verify all required operations were attempted
        calls = mock_session.sql.call_args_list
        assert len(calls) == 3
        assert "USE DATABASE DB" in str(calls[0])
        assert "USE SCHEMA SCHEMA" in str(calls[1])
        assert "LIST @STAGE" in str(calls[2])

    def test_validate_user_permissions_failure(self) -> None:
        """Test permission validation failure."""
        mock_session = Mock()
        mock_session.sql.side_effect = Exception("Permission denied")

        result = validate_user_permissions(mock_session, "DB", "SCHEMA", "STAGE")
        assert result is False

    def test_handle_context_errors(self) -> None:
        """Test context error handling."""
        # Test insufficient privileges
        error = Exception("insufficient privileges")
        result = handle_context_errors(error)
        assert "Insufficient permissions" in result

        # Test resource not found
        error = Exception("does not exist")
        result = handle_context_errors(error)
        assert "does not exist" in result

        # Test generic error
        error = Exception("unknown error")
        result = handle_context_errors(error)
        assert "Context error" in result


class TestPromptSandwich:
    """Test prompt sandwich functionality."""

    def test_refine_prompt_with_cortex_success(self) -> None:
        """Test successful prompt refinement."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.safe_cortex_call"
        ) as mock_cortex:
            mock_cortex.return_value = "Refined prompt content"

            result = refine_prompt_with_cortex(
                mock_session, "Original prompt", "test-model"
            )

            assert result == "Refined prompt content"
            mock_cortex.assert_called_once()

    def test_refine_prompt_with_cortex_fallback(self) -> None:
        """Test prompt refinement fallback to original."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.safe_cortex_call"
        ) as mock_cortex:
            mock_cortex.return_value = None

            result = refine_prompt_with_cortex(
                mock_session, "Original prompt", "test-model"
            )

            assert result == "Original prompt"

    def test_refine_prompt_with_cortex_exception(self) -> None:
        """Test prompt refinement exception handling."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.safe_cortex_call"
        ) as mock_cortex:
            mock_cortex.side_effect = Exception("Cortex error")

            result = refine_prompt_with_cortex(
                mock_session, "Original prompt", "test-model"
            )

            assert result == "Original prompt"

    def test_generate_svg_with_refined_prompt_success(self) -> None:
        """Test successful SVG generation."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.safe_cortex_call"
        ) as mock_cortex:
            mock_cortex.return_value = "<svg>test</svg>"

            result = generate_svg_with_refined_prompt(
                mock_session, "Refined prompt", "test-model"
            )

            assert result == "<svg>test</svg>"
            mock_cortex.assert_called_once()

    def test_generate_svg_with_refined_prompt_no_content(self) -> None:
        """Test SVG generation with no content."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.safe_cortex_call"
        ) as mock_cortex:
            mock_cortex.return_value = None

            with pytest.raises(ValueError, match="SVG generation returned no content"):
                generate_svg_with_refined_prompt(
                    mock_session, "Refined prompt", "test-model"
                )

    def test_implement_prompt_sandwich_success(self) -> None:
        """Test successful prompt sandwich implementation."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.refine_prompt_with_cortex"
        ) as mock_refine:
            with patch(
                "svg_image_generator.prompt_sandwich.generate_svg_with_refined_prompt"
            ) as mock_generate:
                mock_refine.return_value = "Refined prompt"
                mock_generate.return_value = "<svg>test</svg>"

                raw, refined, svg = implement_prompt_sandwich(
                    mock_session, "Original prompt", "test-model"
                )

                assert raw == "Original prompt"
                assert refined == "Refined prompt"
                assert svg == "<svg>test</svg>"

    def test_implement_prompt_sandwich_exception(self) -> None:
        """Test prompt sandwich exception handling."""
        mock_session = Mock()

        with patch(
            "svg_image_generator.prompt_sandwich.refine_prompt_with_cortex"
        ) as mock_refine:
            mock_refine.side_effect = Exception("Refinement error")

            with pytest.raises(Exception, match="Refinement error"):
                implement_prompt_sandwich(mock_session, "Original prompt", "test-model")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
