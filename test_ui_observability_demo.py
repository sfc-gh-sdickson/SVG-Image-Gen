#!/usr/bin/env python3
"""
Demonstration of UIStateManager observability features.

This script shows how the enhanced UIStateManager provides structured logging,
state transitions, and comprehensive observability for UI state management.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from svg_image_generator.llm_logging import get_llm_logger
from svg_image_generator.ui_state_manager import UIStateManager


def setup_logging():
    """Set up logging to see the structured LLM logs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def demo_basic_state_management():
    """Demonstrate basic state management with observability."""
    print("\n=== Basic State Management Demo ===")

    # Create state manager with LLM logging
    state_manager = UIStateManager()

    # Show initial state
    print("Initial state:", state_manager.get_all_state())

    # Demonstrate state transitions
    print("\n--- State Transitions ---")
    state_manager.set_current_step("form_fill")
    state_manager.set_current_step("validation")
    state_manager.set_current_step("generation")

    # Show form data management
    print("\n--- Form Data Management ---")
    form_data = {
        "prompt": "Create a blue circle",
        "model": "claude-3-5-sonnet",
        "output_format": "svg",
    }
    state_manager.set_form_data(form_data)

    # Show validation error handling
    print("\n--- Validation Error Handling ---")
    state_manager.set_validation_error("prompt", "Prompt is too short")
    state_manager.set_validation_error("model", "Model not available")

    # Show loading states
    print("\n--- Loading State Management ---")
    state_manager.set_loading_state("form_submit", True)
    state_manager.set_loading_state("cortex_call", True)
    state_manager.set_loading_state("form_submit", False)

    # Show final state
    print("\nFinal state:", state_manager.get_all_state())

    # Log comprehensive summary
    print("\n--- State Summary ---")
    state_manager.log_state_summary()


def demo_error_scenarios():
    """Demonstrate error scenarios and their observability."""
    print("\n=== Error Scenarios Demo ===")

    state_manager = UIStateManager()

    # Simulate form validation errors
    print("\n--- Form Validation Errors ---")
    state_manager.set_validation_error("email", "Invalid email format")
    state_manager.set_validation_error("prompt", "Prompt contains invalid characters")
    state_manager.set_validation_error("model", "Selected model is not available")

    # Show validation errors
    errors = state_manager.get_validation_errors()
    print(f"Current validation errors: {errors}")

    # Clear errors
    print("\n--- Clearing Errors ---")
    state_manager.clear_validation_errors()

    # Verify errors cleared
    errors = state_manager.get_validation_errors()
    print(f"Errors after clearing: {errors}")


def demo_complex_workflow():
    """Demonstrate a complex workflow with full observability."""
    print("\n=== Complex Workflow Demo ===")

    state_manager = UIStateManager()

    # Step 1: User starts form
    print("\n--- Step 1: Form Initialization ---")
    state_manager.set_current_step("form_init")
    state_manager.set_loading_state("form_load", True)

    # Step 2: User fills form
    print("\n--- Step 2: Form Filling ---")
    state_manager.set_current_step("form_fill")
    state_manager.set_loading_state("form_load", False)

    form_data = {
        "prompt": "Generate a red square with blue border",
        "model": "claude-3-5-sonnet",
        "size": "512x512",
        "style": "minimal",
    }
    state_manager.set_form_data(form_data)

    # Step 3: Validation
    print("\n--- Step 3: Validation ---")
    state_manager.set_current_step("validation")
    state_manager.set_loading_state("validation", True)

    # Simulate validation errors
    state_manager.set_validation_error("prompt", "Prompt too vague")
    state_manager.set_loading_state("validation", False)

    # Step 4: Fix errors and revalidate
    print("\n--- Step 4: Error Correction ---")
    updated_form_data = {
        "prompt": "Generate a red square with blue border, minimalist style",
        "model": "claude-3-5-sonnet",
        "size": "512x512",
        "style": "minimal",
    }
    state_manager.set_form_data(updated_form_data)
    state_manager.clear_validation_errors()

    # Step 5: Generation
    print("\n--- Step 5: Generation ---")
    state_manager.set_current_step("generation")
    state_manager.set_loading_state("cortex_call", True)
    state_manager.set_loading_state("svg_generation", True)

    # Simulate completion
    state_manager.set_loading_state("cortex_call", False)
    state_manager.set_loading_state("svg_generation", False)
    state_manager.set_current_step("complete")

    # Final summary
    print("\n--- Final Workflow Summary ---")
    state_manager.log_state_summary()


def main():
    """Run the observability demonstration."""
    print("🎨 UIStateManager Observability Demonstration")
    print("=" * 50)

    setup_logging()

    try:
        demo_basic_state_management()
        demo_error_scenarios()
        demo_complex_workflow()

        print("\n✅ All demonstrations completed successfully!")
        print("\n📊 Key Observability Features Demonstrated:")
        print("  • Structured LLM logging with context")
        print("  • State transition tracking")
        print("  • Form data change monitoring")
        print("  • Validation error management")
        print("  • Loading state tracking")
        print("  • Comprehensive state summaries")

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
