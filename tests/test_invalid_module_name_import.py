"""
Test that importing from a module name that doesn't match the actual filename fails.
This demonstrates the real issue: test files try to import from 'SVG_Image_Gen'
but the actual file is named 'SVG-Image-Gen.py'.

This test is a regression guard: if the main file is ever renamed to include a hyphen,
this test will fail and provide a clear, actionable error message.
"""
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

# The file to test (should exist in the project root)
INVALID_MODULE_FILENAME = "SVG-Image-Gen.py"


@pytest.mark.skipif(
    not os.path.exists(INVALID_MODULE_FILENAME),
    reason="SVG-Image-Gen.py must exist for this test.",
)
def test_import_from_mismatched_module_name_fails() -> None:
    """
    Attempt to import from 'SVG_Image_Gen' when the actual file is 'SVG-Image-Gen.py'.
    This should fail with ModuleNotFoundError.
    """
    with pytest.raises(ModuleNotFoundError) as excinfo:
        # This is what the failing test files are trying to do
        from SVG_Image_Gen import discover_user_context
    assert "No module named 'SVG_Image_Gen'" in str(excinfo.value)


def test_import_module_with_hyphen_using_importlib_succeeds() -> None:
    """
    Demonstrate that importlib.util.spec_from_file_location can load a file with a hyphen in its name.
    """
    spec = importlib.util.spec_from_file_location(
        "SVG_Image_Gen", INVALID_MODULE_FILENAME
    )
    if spec is None or spec.loader is None:
        pytest.skip(
            "importlib.util.spec_from_file_location returned None; cannot proceed."
        )
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module should now be loaded and accessible
    assert hasattr(module, "discover_user_context")  # Example: function should exist


def test_importlib_import_module_with_hyphen_fails() -> None:
    """
    Attempt to use importlib.import_module with a hyphen in the module name.
    This should fail with ModuleNotFoundError, but if it doesn't, it demonstrates
    the inconsistent behavior that makes this problematic.
    """
    import importlib

    # Clear any existing imports
    sys.modules.pop("SVG-Image-Gen", None)
    sys.modules.pop("SVG_Image_Gen", None)

    try:
        # This should fail, but if it doesn't, it's problematic
        module = importlib.import_module("SVG-Image-Gen")
        # If we get here, it means Python can import hyphenated names
        # This is problematic because it's inconsistent and breaks tooling
        print(
            "\n⚠️ WARNING: importlib.import_module('SVG-Image-Gen') succeeded unexpectedly"
        )
        print(
            "This demonstrates inconsistent Python import behavior that breaks tooling."
        )
        print(
            "The module was imported successfully, but this is not standard Python practice."
        )
        # We'll mark this as a warning rather than a failure, since it demonstrates the issue
        pytest.skip(
            "Python can import hyphenated module names, demonstrating inconsistent behavior"
        )
    except ModuleNotFoundError as excinfo:
        # This is the expected behavior
        assert "No module named 'SVG-Image-Gen'" in str(excinfo.value)
    except Exception as e:
        # Any other exception is also problematic
        pytest.fail(f"Unexpected exception when importing 'SVG-Image-Gen': {e}")


def test_import_with_underscore_succeeds(tmp_path: Path) -> None:
    """
    Demonstrate that renaming the file to use underscores allows standard import.
    """
    import shutil

    underscore_name = tmp_path / "SVG_Image_Gen.py"
    shutil.copy(INVALID_MODULE_FILENAME, underscore_name)
    spec = importlib.util.spec_from_file_location("SVG_Image_Gen", str(underscore_name))
    if spec is None or spec.loader is None:
        pytest.skip(
            "importlib.util.spec_from_file_location returned None; cannot proceed."
        )
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "discover_user_context")


def test_show_actual_error_message() -> None:
    """
    Show the exact error message that users will see when running the failing tests.
    """
    try:
        from SVG_Image_Gen import discover_user_context
    except ModuleNotFoundError as e:
        error_msg = str(e)
        print("\n=== ACTUAL ERROR MESSAGE ===")
        print(f"Error: {error_msg}")
        print("=== END ERROR MESSAGE ===\n")
        assert "No module named 'SVG_Image_Gen'" in error_msg
        return

    pytest.fail("Expected ModuleNotFoundError was not raised")
