"""
Tests for SnowSQL installation management functionality.

This module tests the SnowSQL installation system that:
- Checks if SnowSQL is installed
- Installs SnowSQL if not present (unless -f flag is used)
- Handles different installation methods (pip, pipx, uv)
- Provides proper error handling and logging
"""

import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Set up logging
logger = logging.getLogger(__name__)


class TestSnowSQLInstallation:
    """Test SnowSQL installation management functionality."""

    @pytest.fixture
    def mock_subprocess(self):
        """Mock subprocess for testing installation commands."""
        with patch("subprocess.run") as mock_run:
            yield mock_run

    @pytest.fixture
    def mock_shutil(self):
        """Mock shutil for testing which command."""
        with patch("shutil.which") as mock_which:
            yield mock_which

    def test_snowsql_detection_when_installed(self, mock_shutil):
        """
        Test that SnowSQL is detected when properly installed.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_detection_when_installed (TDD phase)")

        # Mock that snowsql is found in PATH
        mock_shutil.return_value = "/usr/local/bin/snowsql"

        try:
            from src.svg_image_generator.snowsql_manager import is_snowsql_installed

            result = is_snowsql_installed(which_func=mock_shutil)
            logger.info(f"Result from is_snowsql_installed: {result}")
            assert result is True, "SnowSQL should be detected as installed"

        except ImportError:
            logger.error(
                "is_snowsql_installed function not implemented yet - expected TDD failure"
            )
            pytest.fail("is_snowsql_installed function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_detection_when_not_installed(self, mock_shutil):
        """
        Test that SnowSQL is not detected when not installed.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_detection_when_not_installed (TDD phase)")

        # Mock that snowsql is not found in PATH
        mock_shutil.return_value = None

        try:
            from src.svg_image_generator.snowsql_manager import is_snowsql_installed

            result = is_snowsql_installed(which_func=mock_shutil)
            logger.info(f"Result from is_snowsql_installed: {result}")
            assert result is False, "SnowSQL should be detected as not installed"

        except ImportError:
            logger.error(
                "is_snowsql_installed function not implemented yet - expected TDD failure"
            )
            pytest.fail("is_snowsql_installed function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_installation_with_pip(self, mock_subprocess, mock_shutil):
        """
        Test SnowSQL installation using pip.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_installation_with_pip (TDD phase)")

        # Mock that snowsql is not initially installed
        mock_shutil.side_effect = [None, "/usr/local/bin/snowsql"]

        # Mock successful pip installation
        mock_subprocess.return_value = Mock(returncode=0)

        try:
            from src.svg_image_generator.snowsql_manager import install_snowsql

            result = install_snowsql(
                method="pip", which_func=mock_shutil, run_func=mock_subprocess
            )
            logger.info(f"Result from install_snowsql: {result}")
            assert result is True, "SnowSQL installation should succeed with pip"

            # Verify pip install command was called
            mock_subprocess.assert_called_with(
                [sys.executable, "-m", "pip", "install", "snowflake-cli"],
                check=True,
                capture_output=True,
                text=True,
            )

        except ImportError:
            logger.error(
                "install_snowsql function not implemented yet - expected TDD failure"
            )
            pytest.fail("install_snowsql function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_installation_with_uv(self, mock_subprocess, mock_shutil):
        """
        Test SnowSQL installation using uv.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_installation_with_uv (TDD phase)")

        # Mock that snowsql is not initially installed, uv is available, snowsql is found after install
        def which_side_effect(name):
            if name == "snowsql":
                return (
                    None
                    if not hasattr(which_side_effect, "called")
                    else "/usr/local/bin/snowsql"
                )
            if name == "uv":
                return "/usr/local/bin/uv"
            return None

        which_side_effect.called = False

        def which_snowsql_then_uv(name):
            if name == "snowsql":
                if not which_snowsql_then_uv.called:
                    which_snowsql_then_uv.called = True
                    return None
                return "/usr/local/bin/snowsql"
            if name == "uv":
                return "/usr/local/bin/uv"
            return None

        which_snowsql_then_uv.called = False
        mock_shutil.side_effect = which_snowsql_then_uv

        # Mock successful uv installation
        mock_subprocess.return_value = Mock(returncode=0)

        try:
            from src.svg_image_generator.snowsql_manager import install_snowsql

            result = install_snowsql(
                method="uv", which_func=mock_shutil, run_func=mock_subprocess
            )
            logger.info(f"Result from install_snowsql: {result}")
            assert result is True, "SnowSQL installation should succeed with uv"

            # Verify uv pip install command was called
            mock_subprocess.assert_called_with(
                ["uv", "pip", "install", "snowflake-cli"],
                check=True,
                capture_output=True,
                text=True,
            )

        except ImportError:
            logger.error(
                "install_snowsql function not implemented yet - expected TDD failure"
            )
            pytest.fail("install_snowsql function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_installation_failure(self, mock_subprocess, mock_shutil):
        """
        Test SnowSQL installation failure handling.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_installation_failure (TDD phase)")

        # Mock that snowsql is not initially installed
        mock_shutil.return_value = None

        # Mock failed installation
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "pip install")

        try:
            from src.svg_image_generator.snowsql_manager import install_snowsql

            result = install_snowsql(
                method="pip", which_func=mock_shutil, run_func=mock_subprocess
            )
            logger.info(f"Result from install_snowsql: {result}")
            assert result is False, "SnowSQL installation should fail gracefully"

        except ImportError:
            logger.error(
                "install_snowsql function not implemented yet - expected TDD failure"
            )
            pytest.fail("install_snowsql function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_installation_with_force_flag(self, mock_subprocess, mock_shutil):
        """
        Test SnowSQL installation with force flag (-f).
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_installation_with_force_flag (TDD phase)")

        # Mock that snowsql is already installed
        mock_shutil.return_value = "/usr/local/bin/snowsql"

        # Mock successful reinstallation
        mock_subprocess.return_value = Mock(returncode=0)

        try:
            from src.svg_image_generator.snowsql_manager import install_snowsql

            result = install_snowsql(
                method="pip",
                force=True,
                which_func=mock_shutil,
                run_func=mock_subprocess,
            )
            logger.info(f"Result from install_snowsql with force: {result}")
            assert result is True, "SnowSQL installation should succeed with force flag"

            # Verify installation command was called even though it was already installed
            mock_subprocess.assert_called()

        except ImportError:
            logger.error(
                "install_snowsql function not implemented yet - expected TDD failure"
            )
            pytest.fail("install_snowsql function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_installation_skip_when_installed(
        self, mock_subprocess, mock_shutil
    ):
        """
        Test that SnowSQL installation is skipped when already installed.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_installation_skip_when_installed (TDD phase)")

        # Mock that snowsql is already installed
        mock_shutil.return_value = "/usr/local/bin/snowsql"

        try:
            from src.svg_image_generator.snowsql_manager import install_snowsql

            result = install_snowsql(
                method="pip",
                force=False,
                which_func=mock_shutil,
                run_func=mock_subprocess,
            )
            logger.info(f"Result from install_snowsql without force: {result}")
            assert result is True, "Should return True when already installed"

            # Verify installation command was NOT called
            mock_subprocess.assert_not_called()

        except ImportError:
            logger.error(
                "install_snowsql function not implemented yet - expected TDD failure"
            )
            pytest.fail("install_snowsql function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise

    def test_snowsql_installation_method_detection(self, mock_subprocess, mock_shutil):
        """
        Test automatic detection of best installation method.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_installation_method_detection (TDD phase)")

        # Mock that snowsql is not initially installed, uv is available, snowsql is found after install
        def which_side_effect(name):
            if name == "snowsql":
                if not hasattr(which_side_effect, "called"):
                    which_side_effect.called = True
                    return None
                return "/usr/local/bin/snowsql"
            if name == "uv":
                return "/usr/local/bin/uv"
            if name == "pip":
                return "/usr/local/bin/pip"
            if name == "pipx":
                return "/usr/local/bin/pipx"
            return None

        which_side_effect.called = False
        mock_shutil.side_effect = which_side_effect

        # Mock successful installation
        mock_subprocess.return_value = Mock(returncode=0)

        try:
            from src.svg_image_generator.snowsql_manager import install_snowsql

            result = install_snowsql(
                method="auto", which_func=mock_shutil, run_func=mock_subprocess
            )
            logger.info(f"Result from install_snowsql with auto method: {result}")
            assert (
                result is True
            ), "SnowSQL installation should succeed with auto method detection"

        except ImportError:
            logger.error(
                "install_snowsql function not implemented yet - expected TDD failure"
            )
            pytest.fail("install_snowsql function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise


class TestSnowSQLIntegration:
    """Integration tests for SnowSQL installation with real system calls."""

    @pytest.mark.integration
    def test_snowsql_installation_integration(self):
        """
        Integration test for SnowSQL installation.
        This test will be skipped in CI environments.
        """
        logger.info("Running test_snowsql_installation_integration")

        try:
            from src.svg_image_generator.snowsql_manager import (
                install_snowsql,
                is_snowsql_installed,
            )

            # Skip if already installed
            if is_snowsql_installed():
                pytest.skip("SnowSQL already installed")

            # Test installation
            result = install_snowsql(method="pip")
            assert (
                result is True
            ), "Integration test should install SnowSQL successfully"

            # Verify it's now installed
            assert (
                is_snowsql_installed()
            ), "SnowSQL should be installed after installation"

        except ImportError:
            pytest.skip("SnowSQL manager not implemented yet")


class TestSnowSQLCLI:
    """Test CLI integration for SnowSQL installation."""

    def test_snowsql_cli_help(self):
        """
        Test that SnowSQL CLI provides help information.
        This is a TDD test: it should fail until the feature is implemented.
        """
        logger.info("Running test_snowsql_cli_help (TDD phase)")

        try:
            from src.svg_image_generator.snowsql_manager import run_snowsql_command

            with patch(
                "shutil.which", return_value="/usr/local/bin/snowsql"
            ) as mock_which, patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=0, stdout="snowsql help output", stderr=""
                )
                result = run_snowsql_command(
                    ["--help"], which_func=mock_which, run_func=mock_run
                )
                logger.info(f"Result from run_snowsql_command --help: {result}")
                assert result.returncode == 0, "SnowSQL help command should succeed"
                assert (
                    "snowsql" in result.stdout.lower()
                ), "Help output should mention snowsql"
        except ImportError:
            logger.error(
                "run_snowsql_command function not implemented yet - expected TDD failure"
            )
            pytest.fail("run_snowsql_command function not implemented yet - TDD step")
        except AssertionError as e:
            logger.error(f"Assertion failed: {e}")
            raise
