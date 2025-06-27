"""
PDCA Investigation Tests

This module contains diagnostic tests to investigate unclear test failures
and understand root causes before proposing fixes.

Following the principle: "Tests before fixes, no guessing"
"""

from unittest.mock import Mock, patch

from snowflake.snowpark.exceptions import SnowparkSessionException

# Import the modules we need to investigate
from src.svg_image_generator import core, cortex, session_manager


class TestAuthenticationExceptionInvestigation:
    """Investigate authentication exception handling failures"""

    def test_get_active_session_behavior_outside_snowflake(self):
        """Investigate what actually happens when get_active_session is called outside Snowflake"""
        with patch(
            "snowflake.snowpark.session.Session.get_active_session"
        ) as mock_get_active:
            # Test different scenarios
            scenarios = [
                (None, "Returns None"),
                (Mock(), "Returns Mock object"),
                (Exception("Connection failed"), "Raises generic Exception"),
                (
                    SnowparkSessionException("No active session"),
                    "Raises SnowparkSessionException",
                ),
            ]

            for expected_result, description in scenarios:
                if isinstance(expected_result, Exception):
                    mock_get_active.side_effect = expected_result
                else:
                    mock_get_active.return_value = expected_result

                try:
                    result = session_manager.get_session()
                    print(
                        f"Scenario '{description}': get_session() returned {type(result)}"
                    )
                except Exception as e:
                    print(
                        f"Scenario '{description}': get_session() raised {type(e).__name__}: {e}"
                    )

                mock_get_active.reset_mock()


class TestImportBehaviorInvestigation:
    """Investigate import behavior changes"""

    def test_importlib_behavior_with_hyphenated_names(self):
        """Investigate what importlib actually does with hyphenated module names"""
        test_cases = [
            ("SVG-Image-Gen", "Hyphenated filename"),
            ("SVG_Image_Gen", "Underscore filename"),
            ("svg_image_gen", "Lowercase underscore"),
            ("test-module", "Generic hyphenated"),
        ]

        for module_name, description in test_cases:
            print(f"\nTesting {description}: {module_name}")

            # Test importlib.util.spec_from_file_location
            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    module_name, f"{module_name}.py"
                )
                print(f"  spec_from_file_location: {spec is not None}")
            except Exception as e:
                print(f"  spec_from_file_location: ERROR - {type(e).__name__}: {e}")

            # Test importlib.import_module
            try:
                importlib.import_module(module_name)
                print("  import_module: SUCCESS")
            except Exception as e:
                print(f"  import_module: {type(e).__name__}: {e}")

            # Test regular import
            try:
                exec(f"import {module_name}")
                print("  regular import: SUCCESS")
            except Exception as e:
                print(f"  regular import: {type(e).__name__}: {e}")


class TestConfigManagerInvestigation:
    """Investigate ConfigManager attribute errors"""

    def test_config_manager_structure(self):
        """Investigate the actual structure of ConfigManager"""
        try:
            from src.svg_image_generator.session_manager import CONFIG_MANAGER

            print(f"CONFIG_MANAGER type: {type(CONFIG_MANAGER)}")
            print(f"CONFIG_MANAGER dir: {dir(CONFIG_MANAGER)}")

            # Check for connections attribute
            if hasattr(CONFIG_MANAGER, "connections"):
                print(f"connections attribute: {type(CONFIG_MANAGER.connections)}")
                if hasattr(CONFIG_MANAGER.connections, "keys"):
                    print(
                        f"connections.keys(): {list(CONFIG_MANAGER.connections.keys())}"
                    )
            else:
                print("No 'connections' attribute found")

            # Check for similar attributes
            for attr in dir(CONFIG_MANAGER):
                if "connect" in attr.lower() or "config" in attr.lower():
                    print(
                        f"Related attribute '{attr}': {getattr(CONFIG_MANAGER, attr)}"
                    )

        except Exception as e:
            print(f"Error investigating CONFIG_MANAGER: {type(e).__name__}: {e}")


class TestModelDiscoveryBehaviorInvestigation:
    """Investigate model discovery behavior changes"""

    def test_cortex_model_discovery_actual_behavior(self):
        """Investigate what get_available_cortex_models actually returns"""
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

            # Test the actual function
            result = cortex.get_available_cortex_models(mock_session)
            print(f"get_available_cortex_models returned: {result}")
            print(f"Length: {len(result)}")
            print("Expected: ['claude-3-5-sonnet']")
            print(f"Actual: {result}")


class TestInputValidationInvestigation:
    """Investigate input validation behavior"""

    def test_core_functions_with_empty_inputs(self):
        """Investigate what core functions actually do with empty inputs"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.sql.return_value.collect.return_value = []
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            # Test get_accessible_schemas with empty database
            print("\nTesting get_accessible_schemas with empty database:")
            try:
                result = core.get_accessible_schemas(mock_session, "")
                print(f"Result: {result}")
            except Exception as e:
                print(f"Exception: {type(e).__name__}: {e}")

            # Test get_accessible_schemas with None database
            print("\nTesting get_accessible_schemas with None database:")
            try:
                result = core.get_accessible_schemas(mock_session, None)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Exception: {type(e).__name__}: {e}")

            # Check if SQL was called
            print(f"SQL calls made: {mock_session.sql.call_count}")
            if mock_session.sql.call_count > 0:
                print(f"SQL calls: {mock_session.sql.call_args_list}")


class TestContextDiscoveryInvestigation:
    """Investigate context discovery data structure"""

    def test_discover_user_context_actual_structure(self):
        """Investigate what discover_user_context actually returns"""
        with patch("snowflake.snowpark.session.Session") as mock_session_class:
            mock_session = Mock()
            # Mock the session properties
            mock_session.sql.return_value.collect.return_value = [
                {"name": "TEST_ROLE", "value": "TEST_ROLE"},
                {"name": "TEST_WAREHOUSE", "value": "TEST_WAREHOUSE"},
                {"name": "TEST_DATABASE", "value": "TEST_DB"},
            ]
            mock_session_class.builder.configs.return_value.create.return_value = (
                mock_session
            )

            # Test the actual function
            result = core.discover_user_context(mock_session)
            print(f"discover_user_context returned: {result}")
            print(
                f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
            )
            print(
                f"Warehouse key exists: {'warehouse' in result if isinstance(result, dict) else False}"
            )
            print(
                f"Role key exists: {'role' in result if isinstance(result, dict) else False}"
            )


if __name__ == "__main__":
    # Run investigations
    print("=== PDCA INVESTIGATION TESTS ===")

    # Run each investigation
    test_classes = [
        TestAuthenticationExceptionInvestigation(),
        TestImportBehaviorInvestigation(),
        TestConfigManagerInvestigation(),
        TestModelDiscoveryBehaviorInvestigation(),
        TestInputValidationInvestigation(),
        TestContextDiscoveryInvestigation(),
    ]

    for test_class in test_classes:
        print(f"\n{'='*50}")
        print(f"Running {test_class.__class__.__name__}")
        print(f"{'='*50}")

        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                method = getattr(test_class, method_name)
                if callable(method):
                    try:
                        method()
                    except Exception as e:
                        print(f"Error in {method_name}: {type(e).__name__}: {e}")
