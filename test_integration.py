#!/usr/bin/env python3
"""
Simple test script to verify the decorator-based state management integration.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

import time

from src.svg_image_generator.streamlit_integration import (
    get_state_manager,
    loading_context,
    step_context,
    track_form_data,
    track_loading,
    track_step,
    track_validation_errors,
)


def test_basic_integration():
    """Test basic decorator functionality."""
    print("🧪 Testing basic decorator integration...")

    # Initialize state manager
    state_manager = get_state_manager()

    # Test step tracking
    @track_step("test_step")
    def test_function():
        print("  ✅ Step tracking decorator works")
        return "success"

    result = test_function()
    assert result == "success"

    # Test loading tracking
    @track_loading("test_component")
    def test_loading():
        print("  ✅ Loading tracking decorator works")
        time.sleep(0.1)  # Simulate work
        return "done"

    result = test_loading()
    assert result == "done"

    # Test form data tracking
    @track_form_data()
    def test_form():
        print("  ✅ Form data tracking decorator works")
        return "processed"

    result = test_form()
    assert result == "processed"

    # Test validation error tracking
    @track_validation_errors()
    def test_validation():
        print("  ✅ Validation error tracking decorator works")
        return True

    result = test_validation()
    assert result == True

    print("✅ All basic decorators work correctly!")


def test_context_managers():
    """Test context manager functionality."""
    print("🧪 Testing context managers...")

    state_manager = get_state_manager()

    # Test loading context
    with loading_context("test_loading"):
        print("  ✅ Loading context manager works")
        time.sleep(0.1)

    # Test step context
    with step_context("test_step"):
        print("  ✅ Step context manager works")
        time.sleep(0.1)

    print("✅ All context managers work correctly!")


def test_manual_state_updates():
    """Test manual state update functionality."""
    print("🧪 Testing manual state updates...")

    state_manager = get_state_manager()

    # Test manual state updates
    state_manager.manual_state_update(
        step="manual_test", loading_states={"manual_component": True}
    )

    current_state = state_manager.get_current_state()
    assert current_state.get("current_step") == "manual_test"
    assert current_state.get("loading_states", {}).get("manual_component") == True

    print("✅ Manual state updates work correctly!")


def test_api_integration():
    """Test API integration functionality."""
    print("🧪 Testing API integration...")

    state_manager = get_state_manager()

    # Test API sync enable/disable
    state_manager.enable_api_sync(False)
    assert state_manager._enabled == False

    state_manager.enable_api_sync(True)
    assert state_manager._enabled == True

    print("✅ API integration works correctly!")


def test_state_reset():
    """Test state reset functionality."""
    print("🧪 Testing state reset...")

    state_manager = get_state_manager()

    # Set some state
    state_manager.manual_state_update(step="test_reset")

    # Reset state
    state_manager.reset_state()

    current_state = state_manager.get_current_state()
    assert current_state.get("current_step") is None

    print("✅ State reset works correctly!")


def main():
    """Run all integration tests."""
    print("🚀 Starting State Management Integration Tests")
    print("=" * 50)

    try:
        test_basic_integration()
        test_context_managers()
        test_manual_state_updates()
        test_api_integration()
        test_state_reset()

        print("\n🎉 All tests passed! Integration system is working correctly.")
        print("\n📋 Next steps:")
        print("1. Start the API server: python start_state_api.py")
        print(
            "2. Run the Streamlit example: streamlit run examples/streamlit_integration_example.py"
        )
        print("3. View the dashboard: http://localhost:8000")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
