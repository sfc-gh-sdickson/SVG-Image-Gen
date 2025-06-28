"""
SnowSQL Installation Manager

This module provides functionality to:
- Check if SnowSQL is installed
- Install SnowSQL using different methods (pip, uv, pipx)
- Handle force installation with -f flag
- Execute SnowSQL CLI commands
- Provide proper error handling and logging
"""

import logging
import subprocess
import sys
from pathlib import Path
from shutil import which as std_which
from typing import Any, Callable, List, Optional

from .llm_logging import ErrorCode, get_llm_logger
from .runtime_detection import is_snowflake_runtime, validate_operation_for_environment

logger = logging.getLogger(__name__)
llm_logger = get_llm_logger("snowsql_manager")


def _validate_snowsql_operation(operation_name: str) -> bool:
    """
    Validate if a SnowSQL operation can be performed in the current environment.

    Args:
        operation_name (str): Name of the operation being attempted

    Returns:
        bool: True if operation is valid, False otherwise
    """
    required_capabilities = ["cli_tools", "subprocess_execution"]

    if not validate_operation_for_environment(operation_name, required_capabilities):
        llm_logger.snowsql_unavailable(
            operation_name,
            context={
                "required_capabilities": required_capabilities,
                "operation_type": "cli_command",
                "suggested_alternatives": [
                    "session.sql() for SQL operations",
                    "Snowflake stages for file operations",
                    "Snowflake external functions for API calls",
                ],
            },
        )
        return False

    return True


def is_snowsql_installed(
    which_func: Callable[[str], Optional[str]] = std_which
) -> bool:
    """
    Check if SnowSQL is installed and accessible in PATH.
    Args:
        which_func: Function to use for checking PATH (for testability)
    Returns:
        bool: True if SnowSQL is installed and accessible, False otherwise
    """
    if not _validate_snowsql_operation("is_snowsql_installed"):
        return False

    llm_logger.info("Checking SnowSQL installation status")
    snowsql_path = which_func("snowsql")
    if snowsql_path:
        llm_logger.info(
            "SnowSQL installation found",
            context={"snowsql_path": snowsql_path, "installation_status": "installed"},
        )
        return True
    else:
        llm_logger.warning(
            "SnowSQL not found in PATH",
            context={
                "installation_status": "not_installed",
                "search_path": "PATH environment variable",
            },
        )
        return False


def _check_installation_method(
    method: str, which_func: Callable[[str], Optional[str]] = std_which
) -> bool:
    if not _validate_snowsql_operation("_check_installation_method"):
        return False

    llm_logger.info(
        f"Checking installation method availability", context={"method": method}
    )

    if method == "pip":
        return True
    elif method == "uv":
        uv_path = which_func("uv")
        if uv_path:
            llm_logger.info("UV package manager found", context={"uv_path": uv_path})
            return True
        else:
            llm_logger.warning(
                "UV package manager not found", context={"method": method}
            )
            return False
    elif method == "pipx":
        pipx_path = which_func("pipx")
        if pipx_path:
            llm_logger.info("Pipx found", context={"pipx_path": pipx_path})
            return True
        else:
            llm_logger.warning("Pipx not found", context={"method": method})
            return False
    else:
        llm_logger.warning(
            f"Unknown installation method",
            context={"method": method, "supported_methods": ["pip", "uv", "pipx"]},
        )
        return False


def _get_installation_command(method: str) -> List[str]:
    if method == "pip":
        return [sys.executable, "-m", "pip", "install", "snowflake-cli"]
    elif method == "uv":
        return ["uv", "pip", "install", "snowflake-cli"]
    elif method == "pipx":
        return ["pipx", "install", "snowflake-cli"]
    else:
        raise ValueError(f"Unsupported installation method: {method}")


def install_snowsql(
    method: str = "auto",
    force: bool = False,
    which_func: Callable[[str], Optional[str]] = std_which,
    run_func: Callable[..., Any] = subprocess.run,
    logger_: logging.Logger = logger,
) -> bool:
    """
    Install SnowSQL using the specified method.
    Args:
        method: Installation method (pip, uv, pipx, auto)
        force: Force installation even if already installed
        which_func: Function to use for checking PATH (for testability)
        run_func: Function to use for running subprocesses (for testability)
        logger_: Logger to use (for testability)
    Returns:
        bool: True if installation succeeded or already installed, False otherwise
    """
    if not _validate_snowsql_operation("install_snowsql"):
        return False

    llm_logger.info(
        "Starting SnowSQL installation",
        context={"method": method, "force": force, "auto_detection": method == "auto"},
    )

    if is_snowsql_installed(which_func) and not force:
        llm_logger.info(
            "SnowSQL already installed, skipping installation",
            context={"installation_status": "already_installed"},
        )
        return True

    if method == "auto":
        for preferred_method in ["uv", "pip", "pipx"]:
            if _check_installation_method(preferred_method, which_func):
                method = preferred_method
                llm_logger.info(
                    "Auto-selected installation method",
                    context={"selected_method": method},
                )
                break
        else:
            llm_logger.error(
                "No suitable installation method found",
                error_code=ErrorCode.SNOWSQL_INSTALLATION_FAILED,
                context={
                    "available_methods": [],
                    "required_methods": ["uv", "pip", "pipx"],
                },
                action_guidance=[
                    "Install 'uv', 'pip', or 'pipx' package manager",
                    "Run 'make install-dev' to install development dependencies",
                    "Install Snowflake CLI manually from official sources",
                ],
            )
            return False

    if not _check_installation_method(method, which_func):
        llm_logger.error(
            f"Installation method '{method}' is not available",
            error_code=ErrorCode.SNOWSQL_INSTALLATION_FAILED,
            context={"requested_method": method},
            action_guidance=[
                f"Install {method} package manager",
                "Run 'make install-dev' to install development dependencies",
                "Use alternative installation method (pip, uv, pipx)",
            ],
        )
        return False

    try:
        cmd = _get_installation_command(method)
        llm_logger.info(
            "Executing SnowSQL installation command",
            context={"command": " ".join(cmd), "method": method},
        )

        result = run_func(cmd, check=True, capture_output=True, text=True)

        llm_logger.info(
            "SnowSQL installation completed successfully",
            context={
                "return_code": result.returncode,
                "stdout_length": len(result.stdout) if result.stdout else 0,
            },
        )

        if is_snowsql_installed(which_func):
            llm_logger.info(
                "SnowSQL installation verified successfully",
                context={"verification_status": "success"},
            )
            return True
        else:
            llm_logger.error(
                "SnowSQL installation completed but not found in PATH",
                error_code=ErrorCode.SNOWSQL_INSTALLATION_FAILED,
                context={
                    "installation_status": "completed_but_not_found",
                    "verification_status": "failed",
                },
                action_guidance=[
                    "Check PATH environment variable",
                    "Restart terminal/shell to refresh PATH",
                    "Run 'make install-dev' or 'make install -f' to force reinstallation",
                ],
            )
            return False

    except subprocess.CalledProcessError as e:
        llm_logger.error(
            "SnowSQL installation failed with subprocess error",
            error_code=ErrorCode.SNOWSQL_INSTALLATION_FAILED,
            exception=e,
            context={
                "return_code": e.returncode,
                "command": " ".join(cmd),
                "stderr": getattr(e, "stderr", ""),
            },
            action_guidance=[
                "Check network connectivity",
                "Verify package manager permissions",
                "Run 'make install-dev' or 'make install -f' to force reinstallation",
            ],
        )
        return False

    except Exception as e:
        llm_logger.error(
            "Unexpected error during SnowSQL installation",
            error_code=ErrorCode.UNEXPECTED_ERROR,
            exception=e,
            context={
                "method": method,
                "command": " ".join(cmd) if "cmd" in locals() else "unknown",
            },
            action_guidance=[
                "Check system requirements",
                "Verify Python environment",
                "Run 'make install-dev' or 'make install -f' to force reinstallation",
            ],
        )
        return False


def run_snowsql_command(
    args: List[str],
    which_func: Callable[[str], Optional[str]] = std_which,
    run_func: Callable[..., Any] = subprocess.run,
    logger_: logging.Logger = logger,
) -> subprocess.CompletedProcess[Any]:
    if not _validate_snowsql_operation("run_snowsql_command"):
        raise RuntimeError(
            "SnowSQL CLI operations are not available in Snowflake runtime environment. "
            "Use Snowflake SQL commands directly instead."
        )

    llm_logger.info(
        "Executing SnowSQL command",
        context={"command": f"snowsql {' '.join(args)}", "args": args},
    )

    if not is_snowsql_installed(which_func):
        llm_logger.error(
            "SnowSQL is not installed",
            error_code=ErrorCode.SNOWSQL_NOT_INSTALLED,
            context={"command": f"snowsql {' '.join(args)}"},
            action_guidance=[
                "Install SnowSQL with: make install-dev",
                "Install SnowSQL with: make install",
                "Install Snowflake CLI manually",
            ],
        )
        raise FileNotFoundError(
            "SnowSQL is not installed. Try running 'make install-dev' or 'make install'."
        )

    try:
        cmd = ["snowsql"] + args
        result = run_func(cmd, capture_output=True, text=True, check=False)

        llm_logger.info(
            "SnowSQL command completed",
            context={
                "return_code": result.returncode,
                "stdout_length": len(result.stdout) if result.stdout else 0,
                "stderr_length": len(result.stderr) if result.stderr else 0,
            },
        )

        if result.returncode != 0:
            llm_logger.warning(
                "SnowSQL command completed with non-zero return code",
                context={
                    "return_code": result.returncode,
                    "stderr": result.stderr if result.stderr else None,
                },
            )

        return result

    except Exception as e:
        llm_logger.error(
            "Error running SnowSQL command",
            error_code=ErrorCode.SNOWSQL_COMMAND_FAILED,
            exception=e,
            context={"command": " ".join(cmd), "args": args},
            action_guidance=[
                "Check SnowSQL installation",
                "Verify command syntax",
                "Run 'make install-dev' or 'make install' to reinstall",
            ],
        )
        raise


def get_snowsql_version(
    which_func: Callable[[str], Optional[str]] = std_which,
    run_func: Callable[..., Any] = subprocess.run,
    logger_: logging.Logger = logger,
) -> Optional[str]:
    if not _validate_snowsql_operation("get_snowsql_version"):
        return None

    llm_logger.info("Getting SnowSQL version")

    try:
        result = run_snowsql_command(
            ["--version"], which_func=which_func, run_func=run_func, logger_=logger_
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            llm_logger.info(
                "SnowSQL version retrieved successfully", context={"version": version}
            )
            return version
        else:
            llm_logger.warning(
                "Failed to get SnowSQL version",
                context={
                    "return_code": result.returncode,
                    "stderr": result.stderr if result.stderr else None,
                },
            )
            return None
    except Exception as e:
        llm_logger.error(
            "Error getting SnowSQL version",
            error_code=ErrorCode.SNOWSQL_COMMAND_FAILED,
            exception=e,
        )
        return None


def validate_snowsql_installation(
    which_func: Callable[[str], Optional[str]] = std_which,
    run_func: Callable[..., Any] = subprocess.run,
    logger_: logging.Logger = logger,
) -> bool:
    if not _validate_snowsql_operation("validate_snowsql_installation"):
        return False

    llm_logger.info("Validating SnowSQL installation")

    if not is_snowsql_installed(which_func):
        llm_logger.error(
            "SnowSQL is not installed",
            error_code=ErrorCode.SNOWSQL_NOT_INSTALLED,
            action_guidance=[
                "Install SnowSQL with: make install-dev",
                "Install SnowSQL with: make install",
                "Install Snowflake CLI manually",
            ],
        )
        return False

    version = get_snowsql_version(
        which_func=which_func, run_func=run_func, logger_=logger_
    )
    if not version:
        llm_logger.error(
            "Cannot get SnowSQL version",
            error_code=ErrorCode.SNOWSQL_COMMAND_FAILED,
            action_guidance=[
                "Check SnowSQL installation",
                "Run 'make install-dev' or 'make install' to reinstall",
                "Verify PATH environment variable",
            ],
        )
        return False

    try:
        result = run_snowsql_command(
            ["--help"], which_func=which_func, run_func=run_func, logger_=logger_
        )
        if result.returncode == 0:
            llm_logger.info(
                "SnowSQL installation validated successfully",
                context={"version": version, "help_command_success": True},
            )
            return True
        else:
            llm_logger.error(
                "SnowSQL help command failed",
                error_code=ErrorCode.SNOWSQL_COMMAND_FAILED,
                context={
                    "return_code": result.returncode,
                    "stderr": result.stderr if result.stderr else None,
                },
                action_guidance=[
                    "Check SnowSQL installation",
                    "Run 'make install-dev' or 'make install' to reinstall",
                ],
            )
            return False
    except Exception as e:
        llm_logger.error(
            "Error validating SnowSQL installation",
            error_code=ErrorCode.SNOWSQL_COMMAND_FAILED,
            exception=e,
            action_guidance=[
                "Check SnowSQL installation",
                "Run 'make install-dev' or 'make install' to reinstall",
            ],
        )
        return False


def ensure_snowsql_installed(
    method: str = "auto",
    force: bool = False,
    which_func: Callable[[str], Optional[str]] = std_which,
    run_func: Callable[..., Any] = subprocess.run,
    logger_: logging.Logger = logger,
) -> bool:
    if not _validate_snowsql_operation("ensure_snowsql_installed"):
        return False

    llm_logger.info(
        "Ensuring SnowSQL is installed", context={"method": method, "force": force}
    )

    if is_snowsql_installed(which_func) and not force:
        llm_logger.info("SnowSQL already installed")
        return True

    llm_logger.info("SnowSQL not installed, attempting installation")
    return install_snowsql(
        method=method,
        force=force,
        which_func=which_func,
        run_func=run_func,
        logger_=logger_,
    )


def setup_snowsql_for_dev(
    force: bool = False,
    which_func: Callable[[str], Optional[str]] = std_which,
    run_func: Callable[..., Any] = subprocess.run,
    logger_: logging.Logger = logger,
) -> bool:
    if not _validate_snowsql_operation("setup_snowsql_for_dev"):
        return False

    llm_logger.info(
        "Setting up SnowSQL for development environment", context={"force": force}
    )

    if _check_installation_method("uv", which_func):
        llm_logger.info("Using uv for SnowSQL installation")
        return install_snowsql(
            method="uv",
            force=force,
            which_func=which_func,
            run_func=run_func,
            logger_=logger_,
        )
    else:
        llm_logger.info("uv not available, falling back to pip")
        return install_snowsql(
            method="pip",
            force=force,
            which_func=which_func,
            run_func=run_func,
            logger_=logger_,
        )
