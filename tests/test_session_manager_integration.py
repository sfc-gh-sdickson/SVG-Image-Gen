"""
Integration tests for the session manager module.

These tests focus on the multi-tier authentication logic and error handling.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the src directory to the path for proper imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from svg_image_generator.session_manager import get_session


class TestSessionManagerTier1:
    """Test Tier 1 authentication (active session)."""

    def test_tier1_success(self) -> None:
        """Test successful Tier 1 authentication."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        mock_session = Mock()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                mock_get_active.return_value = mock_session

                result = get_session()

                assert result == mock_session
                mock_get_active.assert_called_once()
                mock_st.info.assert_called_once()
                assert "Using active Snowflake session" in mock_st.info.call_args[0][0]

    def test_tier1_failure_falls_back_to_tier2(self) -> None:
        """Test that Tier 1 failure falls back to Tier 2."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    with patch("svg_image_generator.session_manager.toml") as mock_toml:
                        # Mock Tier 1 failure
                        mock_get_active.side_effect = Exception("No active session")

                        # Mock Tier 2 success
                        mock_path_instance = Mock()
                        mock_path_instance.exists.return_value = True
                        mock_path.return_value = mock_path_instance

                        mock_toml.load.return_value = {
                            "default": {
                                "account": "test-account",
                                "user": "test-user",
                                "password": "test-password",
                                "warehouse": "test-warehouse",
                            }
                        }

                        mock_session = Mock()
                        with patch(
                            "svg_image_generator.session_manager.Session"
                        ) as mock_session_class:
                            mock_builder = Mock()
                            mock_builder.configs.return_value.create.return_value = (
                                mock_session
                            )
                            mock_session_class.builder = mock_builder

                            result = get_session()

                            assert result == mock_session
                            mock_st.warning.assert_called()
                            mock_st.success.assert_called_once()


class TestSessionManagerTier2:
    """Test Tier 2 authentication (connections.toml)."""

    def test_tier2_connections_toml_not_found(self) -> None:
        """Test Tier 2 failure when connections.toml doesn't exist."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    # Mock Tier 1 failure
                    mock_get_active.side_effect = Exception("No active session")

                    # Mock connections.toml not found
                    mock_path_instance = Mock()
                    mock_path_instance.exists.return_value = False
                    mock_path.return_value = mock_path_instance

                    # Should fall back to Tier 3
                    with patch(
                        "svg_image_generator.session_manager.os.environ"
                    ) as mock_env:
                        mock_env.get.side_effect = lambda x: {
                            "SNOWFLAKE_ACCOUNT": "test-account",
                            "SNOWFLAKE_USER": "test-user",
                            "SNOWFLAKE_PASSWORD": "test-password",
                            "SNOWFLAKE_WAREHOUSE": "test-warehouse",
                        }.get(x)

                        mock_session = Mock()
                        with patch(
                            "svg_image_generator.session_manager.Session"
                        ) as mock_session_class:
                            mock_builder = Mock()
                            mock_builder.configs.return_value.create.return_value = (
                                mock_session
                            )
                            mock_session_class.builder = mock_builder

                            result = get_session()

                            assert result == mock_session
                            mock_st.warning.assert_called()

    def test_tier2_no_default_profile(self) -> None:
        """Test Tier 2 failure when no default profile exists."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    with patch("svg_image_generator.session_manager.toml") as mock_toml:
                        # Mock Tier 1 failure
                        mock_get_active.side_effect = Exception("No active session")

                        # Mock connections.toml exists but no default profile
                        mock_path_instance = Mock()
                        mock_path_instance.exists.return_value = True
                        mock_path.return_value = mock_path_instance

                        mock_toml.load.return_value = {
                            "other_profile": {"account": "test-account"}
                        }

                        # Should fall back to Tier 3
                        with patch(
                            "svg_image_generator.session_manager.os.environ"
                        ) as mock_env:
                            mock_env.get.side_effect = lambda x: {
                                "SNOWFLAKE_ACCOUNT": "test-account",
                                "SNOWFLAKE_USER": "test-user",
                                "SNOWFLAKE_PASSWORD": "test-password",
                                "SNOWFLAKE_WAREHOUSE": "test-warehouse",
                            }.get(x)

                            mock_session = Mock()
                            with patch(
                                "svg_image_generator.session_manager.Session"
                            ) as mock_session_class:
                                mock_builder = Mock()
                                mock_builder.configs.return_value.create.return_value = (
                                    mock_session
                                )
                                mock_session_class.builder = mock_builder

                                result = get_session()

                                assert result == mock_session
                                mock_st.warning.assert_called()

    def test_tier2_connections_default_profile(self) -> None:
        """Test Tier 2 success with [connections.default] profile."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    with patch("svg_image_generator.session_manager.toml") as mock_toml:
                        # Mock Tier 1 failure
                        mock_get_active.side_effect = Exception("No active session")

                        # Mock connections.toml with [connections.default] profile
                        mock_path_instance = Mock()
                        mock_path_instance.exists.return_value = True
                        mock_path.return_value = mock_path_instance

                        mock_toml.load.return_value = {
                            "connections": {
                                "default": {
                                    "account": "test-account",
                                    "user": "test-user",
                                    "password": "test-password",
                                    "warehouse": "test-warehouse",
                                }
                            }
                        }

                        mock_session = Mock()
                        with patch(
                            "svg_image_generator.session_manager.Session"
                        ) as mock_session_class:
                            mock_builder = Mock()
                            mock_builder.configs.return_value.create.return_value = (
                                mock_session
                            )
                            mock_session_class.builder = mock_builder

                            result = get_session()

                            assert result == mock_session
                            mock_st.success.assert_called_once()
                            assert "connections.toml" in mock_st.success.call_args[0][0]


class TestSessionManagerTier3:
    """Test Tier 3 authentication (environment variables)."""

    def test_tier3_success(self) -> None:
        """Test successful Tier 3 authentication."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    # Mock Tier 1 and 2 failures
                    mock_get_active.side_effect = Exception("No active session")
                    mock_path_instance = Mock()
                    mock_path_instance.exists.return_value = False
                    mock_path.return_value = mock_path_instance

                    # Mock environment variables
                    with patch(
                        "svg_image_generator.session_manager.os.environ"
                    ) as mock_env:
                        mock_env.get.side_effect = lambda x: {
                            "SNOWFLAKE_ACCOUNT": "test-account",
                            "SNOWFLAKE_USER": "test-user",
                            "SNOWFLAKE_PASSWORD": "test-password",
                            "SNOWFLAKE_WAREHOUSE": "test-warehouse",
                            "SNOWFLAKE_DATABASE": "test-database",
                            "SNOWFLAKE_SCHEMA": "test-schema",
                            "SNOWFLAKE_ROLE": "test-role",
                        }.get(x)

                        mock_session = Mock()
                        with patch(
                            "svg_image_generator.session_manager.Session"
                        ) as mock_session_class:
                            mock_builder = Mock()
                            mock_builder.configs.return_value.create.return_value = (
                                mock_session
                            )
                            mock_session_class.builder = mock_builder

                            result = get_session()

                            assert result == mock_session
                            mock_st.success.assert_called_once()
                            assert (
                                "environment credentials"
                                in mock_st.success.call_args[0][0]
                            )

    def test_tier3_missing_required_variables(self) -> None:
        """Test Tier 3 failure when required environment variables are missing."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    # Mock Tier 1 and 2 failures
                    mock_get_active.side_effect = Exception("No active session")
                    mock_path_instance = Mock()
                    mock_path_instance.exists.return_value = False
                    mock_path.return_value = mock_path_instance

                    # Mock missing environment variables
                    with patch(
                        "svg_image_generator.session_manager.os.environ"
                    ) as mock_env:
                        mock_env.get.return_value = None

                        # Call get_session() - it should call st.stop() due to missing variables
                        try:
                            get_session()
                        except SystemExit:
                            pass  # st.stop() may raise SystemExit

                        # Check that st.error was called twice
                        assert mock_st.error.call_count == 2

                        # Check first error call (missing environment variables)
                        first_error_call = mock_st.error.call_args_list[0][0][0]
                        assert (
                            "Missing required environment variables" in first_error_call
                        )
                        assert "SNOWFLAKE_ACCOUNT" in first_error_call
                        assert "SNOWFLAKE_USER" in first_error_call
                        assert "SNOWFLAKE_PASSWORD" in first_error_call
                        assert "SNOWFLAKE_WAREHOUSE" in first_error_call

                        # Check second error call (final connection failure)
                        second_error_call = mock_st.error.call_args_list[1][0][0]
                        assert "All connection methods failed" in second_error_call

                        # Check that st.stop() was called twice
                        assert mock_st.stop.call_count == 2

    def test_tier3_connection_failure(self) -> None:
        """Test Tier 3 failure when connection fails."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    # Mock Tier 1 and 2 failures
                    mock_get_active.side_effect = Exception("No active session")
                    mock_path_instance = Mock()
                    mock_path_instance.exists.return_value = False
                    mock_path.return_value = mock_path_instance

                    # Mock environment variables
                    with patch(
                        "svg_image_generator.session_manager.os.environ"
                    ) as mock_env:
                        mock_env.get.side_effect = lambda x: {
                            "SNOWFLAKE_ACCOUNT": "test-account",
                            "SNOWFLAKE_USER": "test-user",
                            "SNOWFLAKE_PASSWORD": "test-password",
                            "SNOWFLAKE_WAREHOUSE": "test-warehouse",
                        }.get(x)

                        # Mock connection failure
                        with patch(
                            "svg_image_generator.session_manager.Session"
                        ) as mock_session_class:
                            mock_builder = Mock()
                            mock_builder.configs.return_value.create.side_effect = (
                                Exception("Connection failed")
                            )
                            mock_session_class.builder = mock_builder

                            # Call get_session() - it should call st.stop() due to connection failure
                            try:
                                get_session()
                            except SystemExit:
                                pass  # st.stop() may raise SystemExit

                            mock_st.error.assert_called_once()
                            assert (
                                "All connection methods failed"
                                in mock_st.error.call_args[0][0]
                            )
                            # Check that st.stop() was called once
                            assert mock_st.stop.call_count == 1


class TestSessionManagerErrorHandling:
    """Test error handling in session manager."""

    def test_tier2_toml_load_error(self) -> None:
        """Test Tier 2 failure when toml.load fails."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    with patch("svg_image_generator.session_manager.toml") as mock_toml:
                        # Mock Tier 1 failure
                        mock_get_active.side_effect = Exception("No active session")

                        # Mock connections.toml exists but toml.load fails
                        mock_path_instance = Mock()
                        mock_path_instance.exists.return_value = True
                        mock_path.return_value = mock_path_instance

                        mock_toml.load.side_effect = Exception("TOML parsing error")

                        # Should fall back to Tier 3
                        with patch(
                            "svg_image_generator.session_manager.os.environ"
                        ) as mock_env:
                            mock_env.get.side_effect = lambda x: {
                                "SNOWFLAKE_ACCOUNT": "test-account",
                                "SNOWFLAKE_USER": "test-user",
                                "SNOWFLAKE_PASSWORD": "test-password",
                                "SNOWFLAKE_WAREHOUSE": "test-warehouse",
                            }.get(x)

                            mock_session = Mock()
                            with patch(
                                "svg_image_generator.session_manager.Session"
                            ) as mock_session_class:
                                mock_builder = Mock()
                                mock_builder.configs.return_value.create.return_value = (
                                    mock_session
                                )
                                mock_session_class.builder = mock_builder

                                result = get_session()

                                assert result == mock_session
                                mock_st.warning.assert_called()

    def test_tier2_session_creation_error(self) -> None:
        """Test Tier 2 failure when session creation fails."""
        # Clear the cache to ensure fresh execution
        get_session.clear()

        with patch(
            "svg_image_generator.session_manager.get_active_session"
        ) as mock_get_active:
            with patch("svg_image_generator.session_manager.st") as mock_st:
                with patch("svg_image_generator.session_manager.Path") as mock_path:
                    with patch("svg_image_generator.session_manager.toml") as mock_toml:
                        # Mock Tier 1 failure
                        mock_get_active.side_effect = Exception("No active session")

                        # Mock connections.toml with valid config
                        mock_path_instance = Mock()
                        mock_path_instance.exists.return_value = True
                        mock_path.return_value = mock_path_instance

                        mock_toml.load.return_value = {
                            "default": {
                                "account": "test-account",
                                "user": "test-user",
                                "password": "test-password",
                                "warehouse": "test-warehouse",
                            }
                        }

                        # Mock session creation failure
                        with patch(
                            "svg_image_generator.session_manager.Session"
                        ) as mock_session_class:
                            mock_builder = Mock()
                            mock_builder.configs.return_value.create.side_effect = (
                                Exception("Session creation failed")
                            )
                            mock_session_class.builder = mock_builder

                            # Should fall back to Tier 3
                            with patch(
                                "svg_image_generator.session_manager.os.environ"
                            ) as mock_env:
                                mock_env.get.side_effect = lambda x: {
                                    "SNOWFLAKE_ACCOUNT": "test-account",
                                    "SNOWFLAKE_USER": "test-user",
                                    "SNOWFLAKE_PASSWORD": "test-password",
                                    "SNOWFLAKE_WAREHOUSE": "test-warehouse",
                                }.get(x)

                                mock_session = Mock()
                                with patch(
                                    "svg_image_generator.session_manager.Session"
                                ) as mock_session_class2:
                                    mock_builder2 = Mock()
                                    mock_builder2.configs.return_value.create.return_value = (
                                        mock_session
                                    )
                                    mock_session_class2.builder = mock_builder2

                                    result = get_session()

                                    assert result == mock_session
                                    mock_st.warning.assert_called()
