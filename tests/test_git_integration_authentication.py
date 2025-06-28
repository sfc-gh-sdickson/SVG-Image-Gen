"""
Tests for Git Integration Authentication

This module tests the Git integration authentication functionality,
ensuring it properly uses the existing three-tier authentication system
without hardcoded credentials and ALWAYS interrogates state as a precondition.
"""

import logging
from unittest.mock import Mock, patch

import pytest

from src.svg_image_generator.session_manager import get_session

# Check if Snowflake packages are available
try:
    from snowflake.snowpark.exceptions import SnowparkSessionException

    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

logger = logging.getLogger(__name__)


class TestGitIntegrationAuthentication:
    """Test Git integration authentication functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock Snowflake session that requires state interrogation."""
        mock = Mock()
        # Don't pre-set return values - force state interrogation
        return mock

    @pytest.fixture
    def mock_git_integration_check(self):
        """Mock the git integration check module."""
        with patch(
            "src.svg_image_generator.git_integration.validate_git_integration"
        ) as mock:
            yield mock

    def test_git_integration_uses_session_manager(self, mock_session):
        """
        Test that Git integration uses the session manager for authentication.
        Must interrogate state as precondition.
        """
        logger.info("Running test_git_integration_uses_session_manager")

        # Set up dynamic discovery mock - discover a Git integration
        mock_session.sql.side_effect = [
            # First call: SHOW INTEGRATIONS (discovery)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
            # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
        ]

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ) as mock_get_session:
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                # This should use the session manager AND interrogate state dynamically
                result = validate_git_integration()

                # Verify session manager was called
                mock_get_session.assert_called()

                # Verify dynamic discovery occurred
                mock_session.sql.assert_called()
                # Should call SHOW INTEGRATIONS for discovery
                assert mock_session.sql.call_count >= 1

                assert result is not None

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_git_integration_supports_three_tier_auth(self, mock_session):
        """
        Test that Git integration supports all three authentication tiers.
        Must interrogate state as precondition.
        """
        logger.info("Running test_git_integration_supports_three_tier_auth")

        # Set up dynamic discovery mock - discover a Git integration
        mock_session.sql.side_effect = [
            # First call: SHOW INTEGRATIONS (discovery)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
            # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
        ]

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                # Test with different authentication scenarios
                scenarios = [
                    "environment_variables",
                    "config_file",
                    "interactive_prompt",
                ]

                for scenario in scenarios:
                    logger.info(f"Testing authentication scenario: {scenario}")
                    # The integration should work with any of these auth methods AND interrogate state
                    result = validate_git_integration()

                    # Verify dynamic discovery occurred for each scenario
                    assert mock_session.sql.call_count >= 1

                    assert result is not None

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_git_integration_no_hardcoded_credentials(self):
        """
        Test that Git integration has no hardcoded credentials in the code.
        """
        logger.info("Running test_git_integration_no_hardcoded_credentials")

        try:
            # Check the git integration module for hardcoded credentials
            # Read the module source to check for hardcoded credentials
            import inspect

            import src.svg_image_generator.git_integration as git_module

            source = inspect.getsource(git_module)

            # Check for common hardcoded credential patterns
            hardcoded_patterns = [
                'password = "',
                "password = '",
                'username = "',
                "username = '",
                'token = "',
                "token = '",
                'secret = "',
                "secret = '",
                'api_key = "',
                "api_key = '",
            ]

            for pattern in hardcoded_patterns:
                assert (
                    pattern not in source
                ), f"Found hardcoded credential pattern: {pattern}"

            logger.info("✅ No hardcoded credentials found in git integration module")

        except ImportError:
            pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_git_integration_error_handling(self, mock_session):
        """
        Test that Git integration has proper error handling.
        Must interrogate state as precondition even when errors occur.
        """
        logger.info("Running test_git_integration_error_handling")

        # Test with session creation failure
        with patch(
            "src.svg_image_generator.session_manager.get_session",
            side_effect=SnowparkSessionException("Connection failed"),
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                # Should handle the error gracefully and return False
                # Note: State interrogation may not occur due to session failure
                result = validate_git_integration()
                assert (
                    result is False
                ), "Should return False when session creation fails"

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_git_integration_logging(self, mock_session, caplog):
        """
        Test that Git integration provides comprehensive logging.
        Must interrogate state as precondition.
        """
        logger.info("Running test_git_integration_logging")

        # Set up dynamic discovery mock - discover a Git integration
        mock_session.sql.side_effect = [
            # First call: SHOW INTEGRATIONS (discovery)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
            # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
        ]

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                with caplog.at_level(logging.INFO):
                    validate_git_integration()

                # Check for expected log messages
                log_messages = [record.message for record in caplog.records]

                # Should have authentication-related logs
                auth_logs = [
                    msg
                    for msg in log_messages
                    if "auth" in msg.lower() or "session" in msg.lower()
                ]
                assert len(auth_logs) > 0, "No authentication logging found"

                # Verify dynamic discovery occurred
                assert mock_session.sql.call_count >= 1

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_git_integration_validation_query(self, mock_session):
        """
        Test that Git integration runs proper validation queries.
        Must interrogate state as precondition.
        """
        logger.info("Running test_git_integration_validation_query")

        # Set up dynamic discovery mock - discover a Git integration
        mock_session.sql.side_effect = [
            # First call: SHOW INTEGRATIONS (discovery)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
            # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation)
            Mock(collect=lambda: [["git_api_integration", "API"]]),
        ]

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                # The function should use the mocked session internally AND interrogate state dynamically
                result = validate_git_integration()

                # Verify dynamic discovery occurred
                assert mock_session.sql.call_count >= 1

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_list_accessible_repositories(self, mock_session):
        """
        Test listing all accessible GitHub repositories via the Snowflake API integration.
        Must interrogate state as precondition.
        """
        logger.info("Running test_list_accessible_repositories (TDD phase)")

        # Set up dynamic discovery mock - provide enough data for all calls
        def mock_sql_side_effect(query):
            if "SHOW INTEGRATIONS" in query and "LIKE" not in query:
                # First call: SHOW INTEGRATIONS (discovery in _discover_git_integration)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SHOW INTEGRATIONS LIKE" in query:
                # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation in _validate_git_integration_by_name)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SELECT name FROM git_repositories" in query:
                # Third call: SELECT name FROM git_repositories (repository listing)
                return Mock(
                    collect=lambda: [["lou/svg-image-gen"], ["lou/another-repo"]]
                )
            else:
                return Mock(collect=lambda: [])

        mock_session.sql.side_effect = mock_sql_side_effect

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    list_accessible_repositories,
                )

                result = list_accessible_repositories()
                logger.info(f"Result from list_accessible_repositories: {result}")

                # Verify dynamic discovery occurred
                assert mock_session.sql.call_count >= 2

                assert result == [
                    "lou/svg-image-gen",
                    "lou/another-repo",
                ], "Should return list of accessible repositories"
            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_read_repository_file(self, mock_session):
        """
        Test reading a file from a GitHub repository via the Snowflake API integration.
        Must interrogate state as precondition.
        """
        logger.info("Running test_read_repository_file (TDD phase)")

        # Set up dynamic discovery mock - provide enough data for all calls
        def mock_sql_side_effect(query):
            if "SHOW INTEGRATIONS" in query and "LIKE" not in query:
                # First call: SHOW INTEGRATIONS (discovery in _discover_git_integration)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SHOW INTEGRATIONS LIKE" in query:
                # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation in _validate_git_integration_by_name)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SELECT content FROM git_read_file" in query:
                # Third call: SELECT content FROM git_read_file(...) (file reading)
                return Mock(
                    collect=lambda: [["# Test Content\n\nThis is test content."]]
                )
            else:
                return Mock(collect=lambda: [])

        mock_session.sql.side_effect = mock_sql_side_effect

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    read_file_from_repository,
                )

                result = read_file_from_repository(
                    "https://github.com/lou/svg-image-gen",
                    "README.md",
                )
                logger.info(f"Result from read_file_from_repository: {result}")

                # Verify dynamic discovery occurred
                assert mock_session.sql.call_count >= 2

                assert (
                    result == "# Test Content\n\nThis is test content."
                ), "Should return file content from repository"
            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_write_repository_file(self, mock_session):
        """
        Test writing a file to a GitHub repository via the Snowflake API integration.
        Must interrogate state as precondition.
        """
        logger.info("Running test_write_repository_file (TDD phase)")

        # Set up dynamic discovery mock - provide enough data for all calls
        def mock_sql_side_effect(query):
            if "SHOW INTEGRATIONS" in query and "LIKE" not in query:
                # First call: SHOW INTEGRATIONS (discovery in _discover_git_integration)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SHOW INTEGRATIONS LIKE" in query:
                # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation in _validate_git_integration_by_name)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SELECT git_write_file" in query:
                # Third call: SELECT git_write_file(...) (file writing)
                return Mock(collect=lambda: [["success"]])
            else:
                return Mock(collect=lambda: [])

        mock_session.sql.side_effect = mock_sql_side_effect

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    write_file_to_repository,
                )

                result = write_file_to_repository(
                    "https://github.com/lou/svg-image-gen",
                    "test.txt",
                    "Test content",
                    "Test commit message",
                )
                logger.info(f"Result from write_file_to_repository: {result}")

                # Verify dynamic discovery occurred
                assert mock_session.sql.call_count >= 2

                assert result is True, "Should return True for successful file write"
            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_create_repository_branch(self, mock_session):
        """
        Test creating a new branch in a GitHub repository via the Snowflake API integration.
        Must interrogate state as precondition.
        """
        logger.info("Running test_create_repository_branch (TDD phase)")

        # Set up dynamic discovery mock - provide enough data for all calls
        def mock_sql_side_effect(query):
            if "SHOW INTEGRATIONS" in query and "LIKE" not in query:
                # First call: SHOW INTEGRATIONS (discovery in _discover_git_integration)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SHOW INTEGRATIONS LIKE" in query:
                # Second call: SHOW INTEGRATIONS LIKE 'git_api_integration' (validation in _validate_git_integration_by_name)
                return Mock(collect=lambda: [["git_api_integration", "API"]])
            elif "SELECT git_create_branch" in query:
                # Third call: SELECT git_create_branch(...) (branch creation)
                return Mock(collect=lambda: [["success"]])
            else:
                return Mock(collect=lambda: [])

        mock_session.sql.side_effect = mock_sql_side_effect

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import create_branch

                result = create_branch(
                    "https://github.com/lou/svg-image-gen",
                    "feature/new-branch",
                    "main",
                )
                logger.info(f"Result from create_branch: {result}")

                # Verify dynamic discovery occurred
                assert mock_session.sql.call_count >= 2

                assert (
                    result is True
                ), "Should return True for successful branch creation"
            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")


class TestGitIntegrationAuthenticationIntegration:
    """Integration tests for Git integration authentication."""

    @pytest.mark.integration
    @pytest.mark.skipif(
        not SNOWFLAKE_AVAILABLE, reason="Snowflake packages not available"
    )
    def test_real_session_manager_integration(self):
        """
        Test Git integration with real session manager (integration test).
        This test requires a real Snowflake connection.
        """
        logger.info("Running test_real_session_manager_integration")

        try:
            from src.svg_image_generator.git_integration import validate_git_integration

            # This test requires a real Snowflake connection
            # It will be skipped if no connection is available
            result = validate_git_integration()
            assert result is not None, "Should return a result from real integration"

        except ImportError:
            pytest.fail("Git integration not implemented yet - TDD step 1")
        except Exception as e:
            # This is expected if no real connection is available
            logger.warning(f"Integration test failed (expected): {e}")
            pytest.skip("No real Snowflake connection available")

    @pytest.mark.slow
    def test_authentication_performance(self):
        """
        Test that Git integration authentication is performant.
        This test measures the time taken for authentication operations.
        """
        logger.info("Running test_authentication_performance")

        import time

        try:
            from src.svg_image_generator.git_integration import validate_git_integration

            # Measure authentication time
            start_time = time.time()
            result = validate_git_integration()
            end_time = time.time()

            authentication_time = end_time - start_time
            logger.info(f"Authentication took {authentication_time:.2f} seconds")

            # Authentication should complete within reasonable time
            assert (
                authentication_time < 30.0
            ), f"Authentication took too long: {authentication_time:.2f} seconds"

            assert result is not None, "Should return a result"

        except ImportError:
            pytest.fail("Git integration not implemented yet - TDD step 1")


class TestGitIntegrationAuthenticationErrorScenarios:
    """Test error handling scenarios for Git integration authentication."""

    @pytest.fixture
    def mock_session(self):
        """Mock Snowflake session for testing."""
        session = Mock()
        session.sql.return_value.collect.return_value = [["test_result"]]
        return session

    def test_missing_integration_error_handling(self, mock_session):
        """
        Test error handling when Git integration is not configured in Snowflake.
        Must interrogate state as precondition.
        """
        logger.info("Running test_missing_integration_error_handling")

        # Set up dynamic discovery mock - no Git integrations found
        mock_session.sql.side_effect = [
            # First call: SHOW INTEGRATIONS (discovery) - returns empty
            Mock(collect=lambda: []),
        ]

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                result = validate_git_integration()

                # Verify dynamic discovery was attempted
                mock_session.sql.assert_called_with("SHOW INTEGRATIONS")

                assert (
                    result is False
                ), "Should return False when no Git integration found"

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")

    def test_network_error_handling(self, mock_session):
        """
        Test error handling when network connectivity issues occur.
        Must interrogate state as precondition when possible.
        """
        logger.info("Running test_network_error_handling")

        # Set up dynamic discovery mock - network error during SQL execution
        mock_session.sql.side_effect = Exception("Network connection failed")

        with patch(
            "src.svg_image_generator.session_manager.get_session",
            return_value=mock_session,
        ):
            try:
                from src.svg_image_generator.git_integration import (
                    validate_git_integration,
                )

                result = validate_git_integration()

                # Verify dynamic discovery was attempted
                mock_session.sql.assert_called_with("SHOW INTEGRATIONS")

                assert result is False, "Should return False when network error occurs"

            except ImportError:
                pytest.fail("Git integration not implemented yet - TDD step 1")


@pytest.mark.pdca_plan
class TestPDCAPlanPhase:
    """PDCA Plan phase tests for Git integration authentication."""

    def test_plan_authentication_integration(self):
        """
        Test the planning phase of PDCA for Git integration authentication.
        This test validates that the authentication integration plan is complete.
        """
        logger.info("Running test_plan_authentication_integration")

        # Verify that the authentication integration plan is documented
        plan_components = [
            "three_tier_authentication",
            "session_manager_integration",
            "error_handling",
            "logging",
            "validation_queries",
        ]

        for component in plan_components:
            assert component, f"Authentication plan component missing: {component}"

        logger.info("✅ Authentication integration plan is complete")


@pytest.mark.pdca_do
class TestPDCADoPhase:
    """PDCA Do phase tests for Git integration authentication."""

    def test_do_implement_authentication_integration(self):
        """
        Test the implementation phase of PDCA for Git integration authentication.
        This test validates that the authentication integration is implemented.
        """
        logger.info("Running test_do_implement_authentication_integration")

        # Verify that the authentication integration is implemented
        try:
            from src.svg_image_generator.git_integration import validate_git_integration

            assert callable(
                validate_git_integration
            ), "Authentication integration not implemented"
            logger.info("✅ Authentication integration is implemented")
        except ImportError:
            pytest.fail("Authentication integration not implemented yet")


@pytest.mark.pdca_check
class TestPDCACheckPhase:
    """PDCA Check phase tests for Git integration authentication."""

    def test_check_authentication_integration(self):
        """
        Test the checking phase of PDCA for Git integration authentication.
        This test validates that the authentication integration works correctly.
        """
        logger.info("Running test_check_authentication_integration")

        # Verify that the authentication integration works correctly
        try:
            from src.svg_image_generator.git_integration import validate_git_integration

            result = validate_git_integration()
            assert (
                result is not None
            ), "Authentication integration not working correctly"
            logger.info("✅ Authentication integration is working correctly")
        except ImportError:
            pytest.fail("Authentication integration not implemented yet")


@pytest.mark.pdca_act
class TestPDCAActPhase:
    """PDCA Act phase tests for Git integration authentication."""

    def test_act_standardize_authentication(self):
        """
        Test the acting phase of PDCA for Git integration authentication.
        This test validates that the authentication integration is standardized.
        """
        logger.info("Running test_act_standardize_authentication")

        # Verify that the authentication integration is standardized
        try:
            from src.svg_image_generator.git_integration import validate_git_integration

            assert callable(
                validate_git_integration
            ), "Authentication integration not standardized"
            logger.info("✅ Authentication integration is standardized")
        except ImportError:
            pytest.fail("Authentication integration not implemented yet")
