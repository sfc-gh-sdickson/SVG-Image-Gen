"""
Additional Investigation Tests

This module contains tests to investigate unclear failures and achieve >80% confidence
before proposing any fixes.
"""

from unittest.mock import Mock, patch

from snowflake.snowpark.exceptions import SnowparkSessionException

# Import the modules we need to investigate
from src.svg_image_generator import core, cortex


class TestAuthenticationExceptionDetailedInvestigation:
    """Detailed investigation of authentication exception handling"""

    def test_get_active_session_exception_types(self):
        """Investigate what types of exceptions get_active_session actually throws"""

        # Test scenarios
        scenarios = [
            ("No active session", "Outside Snowflake environment"),
            ("Connection timeout", "Network issues"),
            ("Authentication failed", "Invalid credentials"),
            ("Permission denied", "Insufficient privileges"),
        ]

        for scenario_name, description in scenarios:
            print(f"\nTesting scenario: {scenario_name} ({description})")

            # We can't easily trigger these in test environment, but we can document
            # what we expect based on Snowflake documentation
            expected_exceptions = {
                "No active session": SnowparkSessionException,
                "Connection timeout": Exception,  # Generic exception
                "Authentication failed": Exception,  # Generic exception
                "Permission denied": Exception,  # Generic exception
            }

            print(
                f"  Expected exception type: {expected_exceptions.get(scenario_name, 'Unknown')}"
            )
            print("  This would be tested in actual Snowflake environment")


class TestInputValidationDetailedInvestigation:
    """Detailed investigation of input validation behavior"""

    def test_get_accessible_schemas_edge_cases(self):
        """Investigate get_accessible_schemas with various edge cases"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            test_cases = [
                ("", "Empty string"),
                (None, "None value"),
                ("   ", "Whitespace only"),
                ("INVALID_DB", "Non-existent database"),
                ("SNOWFLAKE", "System database"),
            ]

            for test_input, description in test_cases:
                print(
                    f"\nTesting get_accessible_schemas with {description}: '{test_input}'"
                )

                # Mock different SQL responses
                if test_input == "" or test_input is None:
                    mock_session.sql.return_value.collect.return_value = []
                elif test_input == "INVALID_DB":
                    # Mock an error response
                    mock_session.sql.side_effect = Exception("Database does not exist")
                else:
                    mock_session.sql.return_value.collect.return_value = [
                        {"name": "INFORMATION_SCHEMA"},
                        {"name": "PUBLIC"},
                    ]

                try:
                    result = core.get_accessible_schemas(mock_session, test_input)
                    print(f"  Result: {result}")
                    print(f"  Type: {type(result)}")
                except Exception as e:
                    print(f"  Exception: {type(e).__name__}: {e}")

                # Reset mock
                mock_session.sql.reset_mock()

    def test_discover_user_context_actual_structure(self):
        """Investigate the actual structure returned by discover_user_context"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()

            # Mock session properties query
            mock_session.sql.return_value.collect.return_value = [
                {"name": "CURRENT_ROLE", "value": "ACCOUNTADMIN"},
                {"name": "CURRENT_WAREHOUSE", "value": "COMPUTE_WH"},
                {"name": "CURRENT_DATABASE", "value": "TEST_DB"},
                {"name": "CURRENT_SCHEMA", "value": "TEST_SCHEMA"},
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            print("\nTesting discover_user_context actual structure:")

            try:
                result = core.discover_user_context(mock_session)
                print(f"  Result type: {type(result)}")
                print(
                    f"  Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
                )

                if isinstance(result, dict):
                    for key, value in result.items():
                        print(f"  {key}: {type(value)} = {value}")

            except Exception as e:
                print(f"  Exception: {type(e).__name__}: {e}")


class TestContextDiscoveryDataStructureInvestigation:
    """Investigate context discovery data structure mismatches"""

    def test_context_discovery_key_mapping(self):
        """Investigate how context discovery maps Snowflake session properties to keys"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()

            # Test different property name formats
            property_formats = [
                # Format 1: Standard Snowflake properties
                [
                    {"name": "CURRENT_ROLE", "value": "ACCOUNTADMIN"},
                    {"name": "CURRENT_WAREHOUSE", "value": "COMPUTE_WH"},
                    {"name": "CURRENT_DATABASE", "value": "TEST_DB"},
                ],
                # Format 2: Alternative property names
                [
                    {"name": "ROLE", "value": "ACCOUNTADMIN"},
                    {"name": "WAREHOUSE", "value": "COMPUTE_WH"},
                    {"name": "DATABASE", "value": "TEST_DB"},
                ],
                # Format 3: Mixed format
                [
                    {"name": "CURRENT_ROLE", "value": "ACCOUNTADMIN"},
                    {"name": "WAREHOUSE", "value": "COMPUTE_WH"},
                    {"name": "CURRENT_DATABASE", "value": "TEST_DB"},
                ],
            ]

            for i, properties in enumerate(property_formats, 1):
                print(f"\nTesting property format {i}:")
                mock_session.sql.return_value.collect.return_value = properties
                mock_session_class.builder.configs.return_value.create.return_value = (
                    mock_session
                )

                try:
                    result = core.discover_user_context(mock_session)
                    print(f"  Result: {result}")

                    # Check for expected keys
                    expected_keys = ["role", "warehouse", "current_database"]
                    for key in expected_keys:
                        if key in result:
                            print(f"  ✓ Found key '{key}': {result[key]}")
                        else:
                            print(f"  ✗ Missing key '{key}'")

                except Exception as e:
                    print(f"  Exception: {type(e).__name__}: {e}")

                mock_session.sql.reset_mock()


class TestModelDiscoveryFilteringInvestigation:
    """Investigate model discovery filtering behavior"""

    def test_get_available_cortex_models_filtering(self):
        """Investigate if get_available_cortex_models should filter results"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()

            # Test with different model lists
            test_cases = [
                # Case 1: All models available
                [
                    {"name": "claude-3-5-sonnet"},
                    {"name": "claude-3-7-sonnet"},
                    {"name": "openai-gpt-4o"},
                ],
                # Case 2: Only one model available
                [{"name": "claude-3-5-sonnet"}],
                # Case 3: No models available
                [],
                # Case 4: Mixed availability
                [{"name": "claude-3-5-sonnet"}, {"name": "invalid-model"}],
            ]

            for i, models in enumerate(test_cases, 1):
                print(f"\nTesting model discovery case {i}:")
                mock_session.sql.return_value.collect.return_value = models
                mock_session_class.builder.configs.return_value.create.return_value = (
                    mock_session
                )

                try:
                    result = cortex.get_available_cortex_models(mock_session)
                    print(f"  Input models: {[m['name'] for m in models]}")
                    print(f"  Result: {result}")
                    print(f"  Length: {len(result)}")

                except Exception as e:
                    print(f"  Exception: {type(e).__name__}: {e}")

                mock_session.sql.reset_mock()


if __name__ == "__main__":
    # Run detailed investigations
    print("=== ADDITIONAL INVESTIGATION TESTS ===")

    test_classes = [
        TestAuthenticationExceptionDetailedInvestigation(),
        TestInputValidationDetailedInvestigation(),
        TestContextDiscoveryDataStructureInvestigation(),
        TestModelDiscoveryFilteringInvestigation(),
    ]

    for test_class in test_classes:
        print(f"\n{'='*60}")
        print(f"Running {test_class.__class__.__name__}")
        print(f"{'='*60}")

        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                method = getattr(test_class, method_name)
                if callable(method):
                    try:
                        method()
                    except Exception as e:
                        print(f"Error in {method_name}: {type(e).__name__}: {e}")
