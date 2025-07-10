"""
Example Streamlit app demonstrating decorator-based state management integration.
Shows how to easily add state tracking to existing Streamlit functions.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import random
import time
from typing import Any, Dict

import streamlit as st

# Import our state management system
from src.svg_image_generator.streamlit_integration import (
    get_state_manager,
    loading_context,
    step_context,
    track_form_data,
    track_loading,
    track_step,
    track_validation_errors,
)

# Initialize state manager
state_manager = get_state_manager()


def main():
    st.title("SVG Image Generator - State Management Demo")
    st.write("This demo shows how decorators automatically track state changes.")

    # Sidebar for state display
    with st.sidebar:
        st.header("Current State")
        current_state = state_manager.get_current_state()

        st.subheader("Current Step")
        st.write(current_state.get("current_step", "None"))

        st.subheader("Loading States")
        loading_states = current_state.get("loading_states", {})
        for component, is_loading in loading_states.items():
            status = "🔄 Loading" if is_loading else "✅ Ready"
            st.write(f"{component}: {status}")

        st.subheader("Form Data")
        form_data = current_state.get("form_data", {})
        if form_data:
            for key, value in form_data.items():
                st.write(f"{key}: {value}")
        else:
            st.write("No form data")

        st.subheader("Validation Errors")
        errors = current_state.get("validation_errors", {})
        if errors:
            for field, message in errors.items():
                st.error(f"{field}: {message}")
        else:
            st.write("No validation errors")

        # Manual state controls
        st.header("Manual Controls")
        if st.button("Reset State"):
            state_manager.reset_state()
            st.rerun()

        if st.button("Toggle API Sync"):
            current_enabled = getattr(state_manager, "_enabled", True)
            state_manager.enable_api_sync(not current_enabled)
            st.rerun()

    # Main content area
    st.header("Form Demo")

    # Example 1: Step tracking with decorator
    @track_step("form_fill")
    def handle_form_submit():
        st.success("Form submitted successfully!")
        time.sleep(1)  # Simulate processing

    # Example 2: Loading tracking with decorator
    @track_loading("cortex_call")
    def simulate_cortex_call():
        st.info("Calling Cortex API...")
        time.sleep(2)  # Simulate API call
        return {"result": "success", "svg_data": "mock_svg_content"}

    # Example 3: Form data tracking
    @track_form_data()
    def process_form_data():
        # This will automatically track form data from session state
        st.info("Processing form data...")
        time.sleep(1)

    # Example 4: Validation error tracking
    @track_validation_errors()
    def validate_form():
        errors = {}

        # Simulate validation
        if not st.session_state.get("user_name", ""):
            errors["user_name"] = "Name is required"

        if not st.session_state.get("email", ""):
            errors["email"] = "Email is required"
        elif "@" not in st.session_state.get("email", ""):
            errors["email"] = "Invalid email format"

        # Store errors in session state (will be picked up by decorator)
        st.session_state["validation_errors"] = errors

        return len(errors) == 0

    # Form inputs
    with st.form("demo_form"):
        st.text_input("Name", key="user_name", placeholder="Enter your name")
        st.text_input("Email", key="email", placeholder="Enter your email")
        st.text_area("Description", key="description", placeholder="Enter description")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.form_submit_button("Submit Form"):
                # This will automatically track the step
                handle_form_submit()

        with col2:
            if st.form_submit_button("Call Cortex"):
                # This will automatically track loading state
                result = simulate_cortex_call()
                st.json(result)

        with col3:
            if st.form_submit_button("Validate"):
                # This will automatically track validation errors
                if validate_form():
                    st.success("Form is valid!")
                else:
                    st.error("Form has validation errors")

    # Example 5: Context managers
    st.header("Context Manager Examples")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Loading Context Demo"):
            with loading_context("svg_generation"):
                st.info("Generating SVG...")
                time.sleep(2)
                st.success("SVG generated!")

    with col2:
        if st.button("Step Context Demo"):
            with step_context("generation"):
                st.info("Processing generation step...")
                time.sleep(1.5)
                st.success("Generation complete!")

    # Example 6: Manual state updates
    st.header("Manual State Updates")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Set Step: Planning"):
            state_manager.manual_state_update(step="planning")
            st.rerun()

    with col2:
        if st.button("Set Step: Generation"):
            state_manager.manual_state_update(step="generation")
            st.rerun()

    with col3:
        if st.button("Set Step: Review"):
            state_manager.manual_state_update(step="review")
            st.rerun()

    # Example 7: Complex state updates
    st.header("Complex State Updates")

    if st.button("Simulate Complex Workflow"):
        # Simulate a complex workflow with multiple state changes
        state_manager.manual_state_update(
            step="initialization",
            loading_states={"data_loading": True, "model_loading": True},
        )
        st.rerun()

        time.sleep(1)

        state_manager.manual_state_update(loading_states={"data_loading": False})
        st.rerun()

        time.sleep(1)

        state_manager.manual_state_update(
            step="processing",
            loading_states={"model_loading": False, "processing": True},
        )
        st.rerun()

        time.sleep(1)

        state_manager.manual_state_update(
            step="complete", loading_states={"processing": False}
        )
        st.rerun()


if __name__ == "__main__":
    main()
